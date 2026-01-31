import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class MonteCarloSimulator:
    def __init__(self, inputs: Dict, num_simulations: int = 10000):
        self.inputs = inputs
        self.num_simulations = num_simulations
        
    def run_simulation(self) -> Dict:
        """Run Monte Carlo simulation with variable returns"""
        
        # Historical market statistics (based on S&P 500)
        mean_return = self.inputs['investment_return'] / 100
        std_dev = 0.18  # ~18% standard deviation (historical volatility)
        
        current_age = self.inputs['current_age']
        retirement_age = self.inputs['retirement_age']
        max_age = 100
        
        # Get lump sums and create lookup dict - SAFETY CHECK
        lump_sums = self.inputs.get('lump_sums', [])
        if not isinstance(lump_sums, list):
            lump_sums = []
        lump_sum_by_age = {ls['age']: ls['amount'] for ls in lump_sums if isinstance(ls, dict) and ls.get('amount', 0) > 0}
        
        # Get lump sum withdrawals and create lookup dict - SAFETY CHECK
        lump_withdrawals = self.inputs.get('lump_sum_withdrawals', [])
        if not isinstance(lump_withdrawals, list):
            lump_withdrawals = []
        lump_withdrawal_by_age = {lw['age']: lw['amount'] for lw in lump_withdrawals if isinstance(lw, dict) and lw.get('amount', 0) > 0}
        
        successes = 0
        failures = 0
        failure_ages = []
        final_balances = []
        worst_case_balance = float('inf')
        best_case_balance = 0
        
        # Track percentile outcomes
        all_year_balances = {age: [] for age in range(current_age, max_age + 1)}
        
        for sim in range(self.num_simulations):
            balance = float(self.inputs['total_investments'])
            failed = False
            failure_age = None
            
            for age in range(current_age, max_age + 1):
                # Generate random return (normal distribution)
                annual_return_rate = np.random.normal(mean_return, std_dev)
                
                # Add lump sum if applicable (at beginning of year, BEFORE returns)
                if age in lump_sum_by_age:
                    balance += lump_sum_by_age[age]
                
                # Subtract lump sum withdrawal if applicable (at beginning of year, BEFORE returns)
                if age in lump_withdrawal_by_age:
                    balance -= lump_withdrawal_by_age[age]
                
                # Accumulation phase
                if age < retirement_age:
                    # Returns on starting balance
                    returns = balance * annual_return_rate
                    balance += returns
                    
                    # Contributions
                    if age <= self.inputs['stop_investments_age']:
                        annual_contrib = self.inputs['monthly_investments'] * 12
                        contrib_returns = annual_contrib * (annual_return_rate / 2)
                        balance += annual_contrib + contrib_returns
                
                # Retirement phase
                else:
                    # Calculate required income - entered in TODAY'S dollars, inflate from current age
                    years_from_now = age - current_age
                    
                    if self.inputs['inflation_adjustment_enabled']:
                        required_income = self.inputs['retirement_year_one_income'] * \
                            ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                    else:
                        # If inflation adjustment disabled, inflate to retirement year then hold constant
                        years_until_retirement = retirement_age - current_age
                        required_income = self.inputs['retirement_year_one_income'] * \
                            ((1 + self.inputs['yearly_inflation'] / 100) ** years_until_retirement)
                    
                    # Age-based reductions
                    age_77_threshold = self.inputs.get('age_77_threshold', 77)
                    age_83_threshold = self.inputs.get('age_83_threshold', 83)
                    reduction_1_enabled = self.inputs.get('reduction_1_enabled', True)
                    reduction_2_enabled = self.inputs.get('reduction_2_enabled', True)
                    
                    if reduction_1_enabled and age >= age_77_threshold:
                        required_income *= (1 - self.inputs['age_77_reduction'] / 100)
                    if reduction_2_enabled and age >= age_83_threshold:
                        required_income *= (1 - self.inputs['age_83_reduction'] / 100)
                    
                    # Other income sources
                    part_time_start = self.inputs.get('part_time_start_age', retirement_age)
                    if age >= part_time_start and age <= self.inputs['part_time_end_age']:
                        part_time = self.inputs['part_time_income']
                        if self.inputs.get('part_time_inflation_adjusted', False):
                            years_since_part_time_start = age - part_time_start
                            part_time *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_since_part_time_start)
                    else:
                        part_time = 0
                    
                    if age >= self.inputs['pension_start_age']:
                        pension = self.inputs['monthly_pension']
                        if self.inputs['pension_inflation_adjusted']:
                            years_since_pension = age - self.inputs['pension_start_age']
                            pension *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_since_pension)
                    else:
                        pension = 0
                    
                    # Private pension
                    private_pension = 0
                    if age >= self.inputs.get('private_pension_start_age', 999):
                        private_pension = self.inputs.get('monthly_private_pension', 0)
                        if self.inputs.get('private_pension_inflation_adjusted', False):
                            years_since_private = age - self.inputs['private_pension_start_age']
                            private_pension *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_since_private)
                    
                    total_pension = pension + private_pension
                    
                    # Withdrawals
                    monthly_from_other = part_time + total_pension
                    if monthly_from_other < required_income:
                        monthly_withdrawal = required_income - monthly_from_other
                        annual_withdrawal = monthly_withdrawal * 12
                        balance -= annual_withdrawal
                    
                    # Returns on balance after withdrawal
                    if balance > 0:
                        returns = balance * annual_return_rate
                        balance += returns
                    
                    # Check for failure
                    if balance <= 0 and not failed:
                        failed = True
                        failure_age = age
                        failures += 1
                        failure_ages.append(age)
                
                # Track balance for this age across all simulations
                all_year_balances[age].append(max(0, balance))
            
            # End of simulation
            if not failed:
                successes += 1
            
            final_balances.append(max(0, balance))
            worst_case_balance = min(worst_case_balance, balance)
            best_case_balance = max(best_case_balance, balance)
        
        # Calculate percentiles for each year
        percentile_data = {}
        for age in range(current_age, max_age + 1):
            balances = all_year_balances[age]
            percentile_data[age] = {
                'p10': np.percentile(balances, 10),
                'p25': np.percentile(balances, 25),
                'p50': np.percentile(balances, 50),
                'p75': np.percentile(balances, 75),
                'p90': np.percentile(balances, 90)
            }
        
        success_rate = (successes / self.num_simulations) * 100
        
        return {
            'success_rate': success_rate,
            'successes': successes,
            'failures': failures,
            'failure_ages': failure_ages,
            'avg_failure_age': np.mean(failure_ages) if failure_ages else None,
            'final_balances': final_balances,
            'median_final_balance': np.median(final_balances),
            'worst_case_balance': worst_case_balance,
            'best_case_balance': best_case_balance,
            'percentile_data': percentile_data
        }
    
    def get_interpretation(self, success_rate: float) -> Tuple[str, str]:
        """Get interpretation of success rate"""
        if success_rate >= 90:
            return "Excellent", "Your plan is very robust and likely to succeed even in poor market conditions."
        elif success_rate >= 80:
            return "Good", "Your plan is robust with a high probability of success."
        elif success_rate >= 70:
            return "Moderate", "Your plan has reasonable success but consider reducing expenses or increasing savings."
        elif success_rate >= 60:
            return "Concerning", "Your plan has significant risk. Consider major adjustments."
        else:
            return "High Risk", "Your plan is unlikely to succeed. Significant changes needed."
    
    def get_detailed_insights(self, results: Dict) -> str:
        """Generate detailed insights about the Monte Carlo results"""
        success_rate = results['success_rate']
        median_final = results['median_final_balance']
        avg_failure_age = results['avg_failure_age']
        
        insights = []
        
        # Header
        insights.append("## 📊 Understanding Your Monte Carlo Results\n")
        
        # Explain what Monte Carlo tests
        insights.append("### What This Simulation Tests\n")
        insights.append(
            "The Monte Carlo simulation runs 10,000 different scenarios with realistic market volatility "
            "(18% standard deviation based on historical S&P 500 data). Unlike the deterministic calculator "
            "which assumes steady returns every year, this tests whether your retirement plan survives "
            "**real-world market conditions** including crashes, bear markets, and varying sequences of returns.\n"
        )
        
        # Success rate context
        insights.append(f"### Your Success Rate: {success_rate:.1f}%\n")
        
        if success_rate < 70:
            insights.append(
                f"In {100 - success_rate:.1f}% of simulations, your portfolio depleted before age 100. "
                f"This doesn't mean you'll definitely run out of money, but it indicates **significant risk** "
                f"that requires attention.\n"
            )
            
            if avg_failure_age:
                insights.append(
                    f"**Average depletion age:** {avg_failure_age:.0f} years old\n"
                )
            
            insights.append("#### Why Success Rate Differs from Deterministic Projection\n")
            insights.append(
                "The deterministic calculator may show your balance growing throughout retirement with steady "
                f"{self.inputs['investment_return']}% returns. However, the Monte Carlo reveals the critical risk: "
                "**sequence of returns risk**.\n"
            )
            
            insights.append("**Sequence of Returns Risk Explained:**\n")
            insights.append(
                "- If you experience poor market returns early in retirement (ages 62-70), you're forced to "
                "sell investments at depressed prices to fund withdrawals\n"
                "- Example: Start with $1.76M → Market drops 30% → Portfolio now $1.23M → Still need to "
                "withdraw $54k → Down to $1.18M\n"
                "- Your portfolio now needs to recover from a much smaller base while expenses continue "
                "inflating at 2.1% annually\n"
                "- Even if markets recover later, the early damage is often irreversible\n"
            )
            
            insights.append("This is why **timing matters** - the same average returns in different orders "
                          "produce vastly different outcomes.\n")
            
        elif success_rate < 85:
            insights.append(
                f"Your plan succeeds in {success_rate:.1f}% of scenarios, which is moderate but leaves room "
                f"for improvement. In {100 - success_rate:.1f}% of simulations, market volatility causes "
                f"portfolio depletion before age 100.\n"
            )
            if avg_failure_age:
                insights.append(f"**Average depletion age in failed scenarios:** {avg_failure_age:.0f} years old\n")
        else:
            insights.append(
                f"Your plan is robust with a {success_rate:.1f}% success rate. You're well-positioned to "
                f"handle market volatility throughout retirement.\n"
            )
        
        # Actionable recommendations
        if success_rate < 85:
            insights.append("\n### 🎯 Strategies to Improve Your Success Rate\n")
            
            insights.append("#### 1. Reduce Early Retirement Spending (Ages 62-70)\n")
            insights.append(
                "**Most impactful change.** The first 8 years of retirement are critical. Even a 10-15% "
                "reduction in spending during this period dramatically improves outcomes by:\n"
                "- Preserving more capital during vulnerable early years\n"
                "- Allowing portfolio to grow before larger withdrawals begin\n"
                "- Providing buffer against early market downturns\n"
            )
            
            insights.append("**Action:** Review discretionary expenses and identify $900-1,350/month in "
                          "reductions for ages 62-70 only.\n")
            
            insights.append("\n#### 2. Implement Dynamic Withdrawal Strategy\n")
            insights.append(
                "Instead of fixed inflation-adjusted withdrawals, adjust spending based on portfolio performance:\n"
                "- **Good years** (portfolio up 10%+): Take full planned amount or slightly more\n"
                "- **Bad years** (portfolio down 10%+): Reduce discretionary spending by 10-20%\n"
                "- **Guardrails approach**: Set upper/lower portfolio thresholds that trigger spending adjustments\n"
            )
            
            insights.append("This prevents the worst-case scenario: selling stocks at market bottoms to fund "
                          "fixed expenses.\n")
            
            insights.append("\n#### 3. Delay Retirement by 2-3 Years\n")
            insights.append(
                "Working until age 64-65 provides multiple benefits:\n"
                "- Larger starting portfolio ($2M+ vs $1.76M)\n"
                "- Fewer years of withdrawals needed\n"
                "- Higher government pension (if applicable)\n"
                "- Reduced sequence of returns risk\n"
            )
            
            insights.append("\n#### 4. Bridge the Income Gap at Age 65\n")
            current_age = self.inputs['current_age']
            retirement_age = self.inputs['retirement_age']
            part_time_income = self.inputs.get('part_time_income', 0)
            pension = self.inputs.get('monthly_pension', 0)
            
            if part_time_income > pension:
                gap = part_time_income - pension
                insights.append(
                    f"Your part-time income (${part_time_income:,.0f}/month) drops to pension "
                    f"(${pension:,.0f}/month) at age 65, increasing portfolio withdrawals by "
                    f"~${gap * 12:,.0f}/year. Consider:\n"
                    "- Extending part-time work to age 67-70\n"
                    "- Finding additional income sources\n"
                    "- Reducing expenses to match lower income\n"
                )
            
            insights.append("\n#### 5. Increase Pre-Retirement Savings\n")
            if self.inputs['current_age'] < self.inputs['retirement_age'] - 5:
                insights.append(
                    f"You have {self.inputs['retirement_age'] - self.inputs['current_age']} years until retirement. "
                    f"Increasing monthly investments by even $200-500 compounds significantly:\n"
                    f"- Extra $300/month = ~$50,000+ more at retirement\n"
                    f"- Reduces withdrawal rate and improves success rate by 5-10%\n"
                )
            
            insights.append("\n#### 6. Consider Annuity for Base Expenses\n")
            insights.append(
                "Using 20-30% of portfolio to purchase an inflation-adjusted annuity at retirement provides:\n"
                "- Guaranteed lifetime income covering essential expenses\n"
                "- Protection against sequence of returns risk\n"
                "- Peace of mind during market downturns\n"
                "- Remaining portfolio can be invested more aggressively\n"
            )
        
        # Market volatility context
        insights.append("\n### 📈 Understanding Market Volatility Impact\n")
        insights.append(
            f"**Historical context:** The simulation uses 18% standard deviation, meaning:\n"
            f"- 68% of years: returns between {self.inputs['investment_return'] - 18:.1f}% and "
            f"{self.inputs['investment_return'] + 18:.1f}%\n"
            f"- 95% of years: returns between {self.inputs['investment_return'] - 36:.1f}% and "
            f"{self.inputs['investment_return'] + 36:.1f}%\n"
            f"- Occasional years with -30% to -40% returns (like 2008)\n\n"
            f"This volatility is based on actual S&P 500 historical data and represents realistic market behavior.\n"
        )
        
        # Percentile insights
        insights.append("\n### 📊 Outcome Distribution\n")
        insights.append(
            f"**Median final balance:** ${median_final:,.0f}\n"
            f"**Best case:** ${results['best_case_balance']:,.0f}\n"
            f"**Worst case:** ${results['worst_case_balance']:,.0f}\n\n"
            f"The wide range of outcomes illustrates how market timing affects results. "
            f"Your planning should account for below-median scenarios, not just the average case.\n"
        )
        
        # Final recommendation
        insights.append("\n### ✅ Next Steps\n")
        if success_rate < 70:
            insights.append(
                "1. **Immediate action recommended.** Review the strategies above and implement 2-3 changes\n"
                "2. Run new simulations with adjusted parameters to see improvement\n"
                "3. Consider consulting a fee-only financial planner for personalized advice\n"
                "4. Re-evaluate annually and adjust as needed\n"
            )
        elif success_rate < 85:
            insights.append(
                "1. Implement 1-2 of the strategies above to improve robustness\n"
                "2. Monitor portfolio performance and adjust spending if needed\n"
                "3. Re-run simulation annually to track progress\n"
            )
        else:
            insights.append(
                "1. Your plan is solid - maintain discipline and avoid lifestyle inflation\n"
                "2. Consider dynamic withdrawal strategy to optimize spending\n"
                "3. Re-evaluate every 2-3 years or after major life changes\n"
            )
        
        return "".join(insights)


def generate_monte_carlo_advice(mc_results: Dict, inputs: Dict, projection_results: Dict) -> str:
    """Generate comprehensive advice integrating Monte Carlo results with projection analysis"""
    advice_parts = []
    
    success_rate = mc_results['success_rate']
    projection = projection_results['projection']
    retirement_age = inputs['retirement_age']
    
    advice_parts.append("\n\n---\n\n## 🎲 Monte Carlo Risk Analysis\n")
    
    # Success rate assessment
    if success_rate >= 90:
        advice_parts.append(f"### ✅ Excellent Success Rate: {success_rate:.1f}%\n")
        advice_parts.append("Your retirement plan is highly robust and can withstand significant market volatility. ")
        advice_parts.append("You have substantial margin for error and could potentially:\n")
        advice_parts.append("- Increase discretionary spending by 5-10%\n")
        advice_parts.append("- Retire 1-2 years earlier if desired\n")
        advice_parts.append("- Allocate more to legacy/estate planning\n")
    elif success_rate >= 80:
        advice_parts.append(f"### ✅ Good Success Rate: {success_rate:.1f}%\n")
        advice_parts.append("Your plan is solid with good resilience to market volatility. ")
        advice_parts.append("Maintain your current strategy and monitor annually.\n")
    elif success_rate >= 70:
        advice_parts.append(f"### ⚠️ Moderate Success Rate: {success_rate:.1f}%\n")
        advice_parts.append("Your plan has reasonable success but improvements would increase security. ")
        advice_parts.append("Consider the recommendations below to strengthen your plan.\n")
    else:
        advice_parts.append(f"### ❌ Concerning Success Rate: {success_rate:.1f}%\n")
        advice_parts.append("Your plan faces significant risk of depletion. ")
        advice_parts.append("**Immediate action recommended** - review and implement multiple strategies below.\n")
    
    # Analyze projection data for specific issues
    advice_parts.append("\n### 📊 Projection Analysis\n")
    
    # Find years exceeding 4% rule
    high_withdrawal_years = []
    for row in projection:
        if row['Age'] >= retirement_age and row['% Over 4% Rule'] > 0:
            high_withdrawal_years.append({
                'age': row['Age'],
                'pct_over': row['% Over 4% Rule'],
                'withdrawal': row['Investment Withdrawal'],
                'balance': row['Investment Balance Start']
            })
    
    if high_withdrawal_years:
        advice_parts.append(f"\n**⚠️ Withdrawal Rate Concerns:**\n")
        advice_parts.append(f"Your plan exceeds the safe 4% withdrawal rule in {len(high_withdrawal_years)} years:\n\n")
        
        # Show worst offenders
        worst_years = sorted(high_withdrawal_years, key=lambda x: x['pct_over'], reverse=True)[:5]
        for year in worst_years:
            advice_parts.append(
                f"- Age {year['age']}: Withdrawing ${year['withdrawal']:,.0f}/month "
                f"({year['pct_over']:.1f}% over safe rate) from ${year['balance']:,.0f}\n"
            )
        
        # Calculate average withdrawal rate during retirement
        retirement_rows = [r for r in projection if r['Age'] >= retirement_age and r['Investment Withdrawal'] > 0]
        if retirement_rows:
            avg_withdrawal_rate = np.mean([
                (r['Investment Withdrawal'] * 12 / r['Investment Balance Start'] * 100) 
                for r in retirement_rows if r['Investment Balance Start'] > 0
            ])
            advice_parts.append(f"\n**Average withdrawal rate:** {avg_withdrawal_rate:.2f}% annually\n")
            
            if avg_withdrawal_rate > 4.5:
                advice_parts.append(
                    "⚠️ Your average withdrawal rate significantly exceeds the 4% safe guideline. "
                    "This increases portfolio depletion risk, especially during market downturns.\n"
                )
    else:
        advice_parts.append("\n✅ **Withdrawal rates:** Your plan stays within the safe 4% rule throughout retirement.\n")
    
    # Analyze balance trajectory
    retirement_start_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == retirement_age), 0)
    mid_retirement_age = retirement_age + 15
    mid_retirement_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == mid_retirement_age), 0)
    
    if mid_retirement_balance < retirement_start_balance * 0.7:
        advice_parts.append(
            f"\n**⚠️ Balance decline:** Your portfolio drops to ${mid_retirement_balance:,.0f} "
            f"by age {mid_retirement_age} (down {((retirement_start_balance - mid_retirement_balance) / retirement_start_balance * 100):.1f}% from retirement start). "
            f"This rapid decline increases vulnerability to market downturns.\n"
        )
    
    # Specific recommendations based on success rate
    if success_rate < 85:
        advice_parts.append("\n### 🎯 Priority Actions to Improve Success Rate\n")
        
        # Calculate specific numbers for recommendations
        current_monthly_income = inputs['retirement_year_one_income']
        part_time_income = inputs.get('part_time_income', 0)
        pension = inputs.get('monthly_pension', 0)
        
        advice_parts.append("\n**1. Reduce Early Retirement Spending (Most Impactful)**\n")
        reduction_10pct = current_monthly_income * 0.10
        reduction_15pct = current_monthly_income * 0.15
        advice_parts.append(
            f"- Reduce monthly target from ${current_monthly_income:,.0f} to "
            f"${current_monthly_income - reduction_10pct:,.0f} (10% cut) for ages {retirement_age}-{retirement_age + 8}\n"
            f"- Or reduce to ${current_monthly_income - reduction_15pct:,.0f} (15% cut) for even better outcomes\n"
            f"- This protects your portfolio during the critical early retirement years\n"
        )
        
        if part_time_income > pension:
            advice_parts.append("\n**2. Bridge the Income Gap**\n")
            gap = part_time_income - pension
            advice_parts.append(
                f"- Your income drops ${gap:,.0f}/month when part-time work ends\n"
                f"- Consider extending part-time work 2-3 years longer\n"
                f"- Or reduce expenses by ${gap:,.0f}/month to match pension income\n"
            )
        
        if inputs['current_age'] < retirement_age - 3:
            advice_parts.append("\n**3. Increase Pre-Retirement Savings**\n")
            current_monthly = inputs.get('monthly_investments', 0)
            extra_300 = 300 * 12 * (retirement_age - inputs['current_age'])
            advice_parts.append(
                f"- Current monthly savings: ${current_monthly:,.0f}\n"
                f"- Increasing by $300/month adds ~${extra_300:,.0f} by retirement\n"
                f"- This could improve success rate by 5-10 percentage points\n"
            )
        
        advice_parts.append("\n**4. Implement Dynamic Withdrawal Strategy**\n")
        advice_parts.append(
            "- In years when portfolio is down 10%+: Reduce discretionary spending by 10-15%\n"
            "- In years when portfolio is up 15%+: Take full planned amount\n"
            "- This prevents selling stocks at market bottoms to fund fixed expenses\n"
        )
        
        if success_rate < 70:
            advice_parts.append("\n**5. Consider Delaying Retirement**\n")
            advice_parts.append(
                f"- Working until age {retirement_age + 2} or {retirement_age + 3} significantly improves outcomes\n"
                f"- Provides larger starting portfolio and fewer withdrawal years\n"
                f"- Could improve success rate by 15-20 percentage points\n"
            )
    
    # Sequence of returns risk explanation
    if success_rate < 80:
        advice_parts.append("\n### 📉 Understanding Your Risk: Sequence of Returns\n")
        advice_parts.append(
            "The gap between your deterministic projection (which may show success) and Monte Carlo results "
            "reveals **sequence of returns risk**:\n\n"
            "**Why timing matters:**\n"
            "- Poor returns early in retirement (ages 62-70) force you to sell investments at low prices\n"
            "- Your portfolio never recovers because you're withdrawing throughout the downturn\n"
            "- Example: 2008-style crash in year 1 of retirement can reduce success rate by 30%+\n\n"
            "**Protection strategies:**\n"
            "- Keep 2-3 years of expenses in cash/bonds (don't sell stocks in downturns)\n"
            "- Reduce spending 10-20% during bear markets\n"
            "- Consider annuity for 30-40% of essential expenses\n"
        )
    
    # Failure age analysis
    if mc_results['failures'] > 0:
        avg_failure_age = mc_results['avg_failure_age']
        advice_parts.append(f"\n### ⏰ Depletion Risk Timeline\n")
        advice_parts.append(
            f"In failed scenarios, portfolio typically depletes around age {avg_failure_age:.0f}. "
            f"This gives you a {avg_failure_age - retirement_age:.0f}-year window to:\n"
            "- Monitor portfolio performance vs. projections\n"
            "- Adjust spending if returns underperform\n"
            "- Implement contingency plans before depletion\n"
        )
    
    # Positive reinforcement for good plans
    if success_rate >= 85:
        advice_parts.append("\n### ✅ Your Plan's Strengths\n")
        advice_parts.append(
            "Your retirement plan demonstrates:\n"
            "- Strong resilience to market volatility\n"
            "- Sustainable withdrawal rates\n"
            "- Adequate portfolio size for your retirement goals\n\n"
            "**Maintain success by:**\n"
            "- Staying disciplined during market downturns (don't panic sell)\n"
            "- Rebalancing annually to maintain target allocation\n"
            "- Reviewing plan every 2-3 years or after major life changes\n"
        )
    
    return "".join(advice_parts)
