class RetirementCalculator:
    def __init__(self, inputs):
        self.inputs = inputs
        
    def calculate(self):
        """Calculate year-by-year retirement projection from current age to 100"""
        projection = []
        
        current_age = self.inputs['current_age']
        retirement_age = self.inputs['retirement_age']
        balance = float(self.inputs['total_investments'])
        
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
        
        # Calculate 4% rule baseline (for comparison in retirement years)
        balance_at_retirement = None
        four_percent_baseline = None
        
        for age in range(current_age, 101):
            year_start_balance = round(balance, 2)
            
            # Capture balance at retirement for 4% rule calculation
            if age == retirement_age:
                balance_at_retirement = year_start_balance
                four_percent_baseline = balance_at_retirement * 0.04 / 12  # Monthly amount
            
            year_data = {
                'Age': age,
                'Income (Today\'s $)': 0,
                'Total Monthly Income': 0,
                'Required Income': 0,
                'Monthly Shortfall': 0,
                'Monthly Surplus': 0,
                'Investment Balance Start': year_start_balance,
                'Monthly Investment': 0,
                'Investment Withdrawal': 0,
                'Surplus Reinvested': 0,
                'Investment Balance End': year_start_balance,
                'Yearly Investment Return': 0,
                'OAS': 0,
                'OAS P1': 0,
                'OAS P2': 0,
                'CPP': 0,
                'CPP P1': 0,
                'CPP P2': 0,
                'Employer Pension': 0,
                'Employer Pension P1': 0,
                'Employer Pension P2': 0,
                'Monthly Pension': 0,
                'Yearly Pension Amount': 0,
                'Part-Time Income': 0,
                'Lump Sum': 0,
                'Lump Sum Withdrawal': 0,
                'OAS Clawback': 0,
                '4% Rule Amount': 0,
                'Withdrawal vs 4% Rule': 0,
                '% Over 4% Rule': 0
            }
            
            # Add lump sum if applicable (at beginning of year, BEFORE returns)
            # ISSUE 3 FIX: Lump sums now added before returns so they earn returns in the year added
            if age in lump_sum_by_age:
                lump_sum_amount = lump_sum_by_age[age]
                balance += lump_sum_amount
                year_data['Lump Sum'] = round(lump_sum_amount, 2)
            
            # Subtract lump sum withdrawal if applicable (at beginning of year, BEFORE returns)
            if age in lump_withdrawal_by_age:
                lump_withdrawal_amount = lump_withdrawal_by_age[age]
                balance -= lump_withdrawal_amount
                year_data['Lump Sum Withdrawal'] = round(lump_withdrawal_amount, 2)
            
            # Investment returns on balance (including any lump sums added this year)
            annual_return = balance * (self.inputs['investment_return'] / 100)
            
            # Monthly investments (before retirement and before stop age)
            # Use mid-year convention: contributions earn half-year return on average
            if age < retirement_age and age <= self.inputs['stop_investments_age']:
                monthly_inv = self.inputs['monthly_investments']
                year_data['Monthly Investment'] = round(monthly_inv, 2)
                
                annual_contributions = monthly_inv * 12
                # Mid-year convention: assume contributions earn half a year's return
                contribution_returns = annual_contributions * (self.inputs['investment_return'] / 100) / 2
                
                balance += annual_contributions + contribution_returns
                year_data['Yearly Investment Return'] = round(annual_return + contribution_returns, 2)
            
            # Retirement income calculations
            if age >= retirement_age:
                # Calculate 4% rule amount for this year (inflated from baseline)
                years_in_retirement = age - retirement_age
                four_percent_amount = four_percent_baseline * ((1 + self.inputs['yearly_inflation'] / 100) ** years_in_retirement)
                year_data['4% Rule Amount'] = round(four_percent_amount, 2)
                
                # Calculate required income with inflation
                # ISSUE 7 FIX: Required income is entered in TODAY'S dollars, so inflate from current age to this age
                # This gives consistent purchasing power throughout retirement
                years_from_now = age - current_age
                
                if self.inputs['inflation_adjustment_enabled']:
                    required_income = self.inputs['retirement_year_one_income'] * ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                else:
                    # If inflation adjustment disabled, still need to inflate to retirement year, then hold constant
                    years_until_retirement = retirement_age - current_age
                    required_income = self.inputs['retirement_year_one_income'] * ((1 + self.inputs['yearly_inflation'] / 100) ** years_until_retirement)
                
                # Apply age-based reductions
                age_77_threshold = self.inputs.get('age_77_threshold', 77)
                age_83_threshold = self.inputs.get('age_83_threshold', 83)
                reduction_1_enabled = self.inputs.get('reduction_1_enabled', True)
                reduction_2_enabled = self.inputs.get('reduction_2_enabled', True)
                
                if reduction_1_enabled and age >= age_77_threshold:
                    required_income *= (1 - self.inputs['age_77_reduction'] / 100)
                if reduction_2_enabled and age >= age_83_threshold:
                    required_income *= (1 - self.inputs['age_83_reduction'] / 100)
                
                # Part-time work income
                # ISSUE 6 FIX: Add inflation adjustment for part-time income
                if age >= self.inputs.get('part_time_start_age', retirement_age) and age <= self.inputs['part_time_end_age']:
                    part_time = self.inputs['part_time_income']
                    if self.inputs.get('part_time_inflation_adjusted', False):
                        years_since_part_time_start = age - self.inputs.get('part_time_start_age', retirement_age)
                        part_time *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_since_part_time_start)
                    year_data['Part-Time Income'] = round(part_time, 2)
                else:
                    part_time = 0
                
                # Old Age Security (OAS) - Person 1
                # OAS amount is entered in today's dollars, so inflate from current age
                oas_p1 = 0
                if age >= self.inputs.get('oas_start_age', 65):
                    oas_p1 = self.inputs.get('monthly_oas', 0)
                    if self.inputs.get('oas_inflation_adjusted', True):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        oas_p1 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Old Age Security (OAS) - Person 2
                oas_p2 = 0
                if age >= self.inputs.get('oas_start_age_p2', 999):
                    oas_p2 = self.inputs.get('monthly_oas_p2', 0)
                    if self.inputs.get('oas_inflation_adjusted_p2', True):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        oas_p2 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Total OAS before clawback
                oas = oas_p1 + oas_p2
                oas_before_clawback = oas
                
                # Store individual OAS amounts
                year_data['OAS P1'] = round(oas_p1, 2)
                year_data['OAS P2'] = round(oas_p2, 2)
                
                # Canada Pension Plan (CPP) - Person 1
                # CPP amount is entered in today's dollars, so inflate from current age
                cpp_p1 = 0
                if age >= self.inputs.get('cpp_start_age', 65):
                    cpp_p1 = self.inputs.get('monthly_cpp', 0)
                    if self.inputs.get('cpp_inflation_adjusted', True):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        cpp_p1 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Canada Pension Plan (CPP) - Person 2
                cpp_p2 = 0
                if age >= self.inputs.get('cpp_start_age_p2', 999):
                    cpp_p2 = self.inputs.get('monthly_cpp_p2', 0)
                    if self.inputs.get('cpp_inflation_adjusted_p2', True):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        cpp_p2 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Total CPP
                cpp = cpp_p1 + cpp_p2
                year_data['CPP'] = round(cpp, 2)
                year_data['CPP P1'] = round(cpp_p1, 2)
                year_data['CPP P2'] = round(cpp_p2, 2)
                
                # Employer/Private pension - Person 1
                employer_pension_p1 = 0
                if age >= self.inputs.get('private_pension_start_age', 999):
                    employer_pension_p1 = self.inputs.get('monthly_private_pension', 0)
                    if self.inputs.get('private_pension_inflation_adjusted', False):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        employer_pension_p1 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Add bridged amount for Person 1 if applicable
                if self.inputs.get('bridged_enabled_p1', False):
                    bridged_start = self.inputs.get('bridged_start_age_p1', 999)
                    bridged_end = self.inputs.get('bridged_end_age_p1', 999)
                    if bridged_start <= age <= bridged_end:
                        bridged_amount = self.inputs.get('bridged_amount_p1', 0)
                        if self.inputs.get('private_pension_inflation_adjusted', False):
                            # Inflate bridged amount same as main pension
                            years_from_now = age - current_age
                            bridged_amount *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                        employer_pension_p1 += bridged_amount
                
                # Employer/Private pension - Person 2
                employer_pension_p2 = 0
                if age >= self.inputs.get('private_pension_start_age_p2', 999):
                    employer_pension_p2 = self.inputs.get('monthly_private_pension_p2', 0)
                    if self.inputs.get('private_pension_inflation_adjusted_p2', False):
                        # Inflate from current age to this age
                        years_from_now = age - current_age
                        employer_pension_p2 *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                
                # Add bridged amount for Person 2 if applicable
                if self.inputs.get('bridged_enabled_p2', False):
                    bridged_start = self.inputs.get('bridged_start_age_p2', 999)
                    bridged_end = self.inputs.get('bridged_end_age_p2', 999)
                    if bridged_start <= age <= bridged_end:
                        bridged_amount = self.inputs.get('bridged_amount_p2', 0)
                        if self.inputs.get('private_pension_inflation_adjusted_p2', False):
                            # Inflate bridged amount same as main pension
                            years_from_now = age - current_age
                            bridged_amount *= ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_now)
                        employer_pension_p2 += bridged_amount
                
                # Total Employer Pension
                employer_pension = employer_pension_p1 + employer_pension_p2
                year_data['Employer Pension'] = round(employer_pension, 2)
                year_data['Employer Pension P1'] = round(employer_pension_p1, 2)
                year_data['Employer Pension P2'] = round(employer_pension_p2, 2)
                
                # Total pension (OAS + CPP + Employer) - will be adjusted for OAS clawback later
                total_pension_before_clawback = oas_before_clawback + cpp + employer_pension
                
                # Add required income column (what you need each month with inflation)
                year_data['Required Income'] = round(required_income, 2)
                
                # STEP 1: Calculate initial investment withdrawal needed (before considering clawback)
                monthly_from_other = part_time + total_pension_before_clawback
                monthly_needed = required_income
                
                if monthly_from_other < monthly_needed:
                    monthly_withdrawal_needed = monthly_needed - monthly_from_other
                    annual_withdrawal_needed = monthly_withdrawal_needed * 12
                    
                    # Cap withdrawal at available balance
                    actual_annual_withdrawal = min(annual_withdrawal_needed, max(0, balance))
                    actual_monthly_withdrawal = actual_annual_withdrawal / 12
                    
                    monthly_withdrawal = actual_monthly_withdrawal
                else:
                    monthly_withdrawal = 0
                
                # STEP 2: Calculate OAS clawback based on total income (before withdrawal adjustment)
                # OAS clawback threshold is $95,323 in 2026, indexed to inflation annually
                # Clawback rate is 15%
                # Skip clawback if ignore_oas_clawback is enabled (income splitting scenario)
                oas_clawback_monthly = 0
                
                if not self.inputs.get('ignore_oas_clawback', False):
                    OAS_CLAWBACK_THRESHOLD_2026 = 95323
                    OAS_CLAWBACK_RATE = 0.15
                    
                    # Inflate threshold from 2026 to current year
                    years_from_2026 = age - current_age  # Years from now (2026 is current year)
                    oas_threshold_this_year = OAS_CLAWBACK_THRESHOLD_2026 * ((1 + self.inputs['yearly_inflation'] / 100) ** years_from_2026)
                    
                    # Calculate total annual income for clawback purposes
                    annual_income = (monthly_from_other + monthly_withdrawal) * 12
                    
                    # Calculate OAS clawback (monthly amount) - only applies to OAS, not CPP or employer pension
                    if annual_income > oas_threshold_this_year:
                        excess_income = annual_income - oas_threshold_this_year
                        annual_clawback = excess_income * OAS_CLAWBACK_RATE
                        # Clawback cannot exceed the OAS amount
                        max_clawback = oas_before_clawback * 12  # Annual OAS amount
                        annual_clawback = min(annual_clawback, max_clawback)
                        oas_clawback_monthly = annual_clawback / 12
                
                year_data['OAS Clawback'] = round(oas_clawback_monthly, 2)
                
                # Calculate OAS after clawback for display in OAS column
                oas_after_clawback = max(0, oas_before_clawback - oas_clawback_monthly)
                year_data['OAS'] = round(oas_after_clawback, 2)
                
                # STEP 3: If clawback creates a shortfall, withdraw additional funds from investments
                if oas_clawback_monthly > 0:
                    # After clawback, effective income from pensions/part-time is reduced
                    effective_monthly_from_other = monthly_from_other - oas_clawback_monthly
                    
                    # Check if we need additional withdrawal to cover the clawback shortfall
                    if effective_monthly_from_other + monthly_withdrawal < monthly_needed:
                        additional_withdrawal_needed = monthly_needed - (effective_monthly_from_other + monthly_withdrawal)
                        additional_annual_withdrawal = additional_withdrawal_needed * 12
                        
                        # Cap additional withdrawal at remaining balance
                        actual_additional_annual = min(additional_annual_withdrawal, max(0, balance))
                        additional_monthly = actual_additional_annual / 12
                        
                        # Add to total withdrawal
                        monthly_withdrawal += additional_monthly
                        actual_annual_withdrawal = monthly_withdrawal * 12
                
                # STEP 4: Deduct total withdrawal from balance
                actual_annual_withdrawal = monthly_withdrawal * 12
                balance -= actual_annual_withdrawal
                
                year_data['Investment Withdrawal'] = round(monthly_withdrawal, 2)
                
                # Calculate how far off from 4% rule (based on what was actually withdrawn)
                year_data['Withdrawal vs 4% Rule'] = round(monthly_withdrawal - four_percent_amount, 2)
                if four_percent_amount > 0:
                    year_data['% Over 4% Rule'] = round(((monthly_withdrawal - four_percent_amount) / four_percent_amount) * 100, 1)
                
                # STEP 5: Calculate Monthly Pension (total of all pensions after OAS clawback)
                # OAS is reduced by clawback, CPP and Employer pension are not affected
                # Note: oas_after_clawback is already calculated above
                total_pension_after_clawback = oas_after_clawback + cpp + employer_pension
                year_data['Monthly Pension'] = round(total_pension_after_clawback, 2)
                year_data['Yearly Pension Amount'] = round(total_pension_after_clawback * 12, 2)
                
                # STEP 6: Calculate final Total Monthly Income (after clawback)
                # Total Monthly Income = Part-Time + Monthly Pension (after clawback) + Investment Withdrawal
                final_total_monthly_income = part_time + total_pension_after_clawback + monthly_withdrawal
                year_data['Total Monthly Income'] = round(final_total_monthly_income, 2)
                
                # Calculate monthly shortfall (only show if positive = shortfall exists)
                effective_income = part_time + total_pension_after_clawback + monthly_withdrawal
                monthly_shortfall = required_income - effective_income
                year_data['Monthly Shortfall'] = round(monthly_shortfall, 2) if monthly_shortfall > 0 else 0
                
                # STEP 7: Calculate and reinvest surplus if income exceeds required
                monthly_surplus = 0
                if effective_income > required_income:
                    monthly_surplus = effective_income - required_income
                    annual_surplus = monthly_surplus * 12
                    balance += annual_surplus  # Reinvest surplus back into investments
                    year_data['Monthly Surplus'] = round(monthly_surplus, 2)
                    year_data['Surplus Reinvested'] = round(annual_surplus, 2)
                
                # Calculate income in today's dollars (deflate by inflation)
                years_from_now = age - current_age
                inflation_factor = (1 + self.inputs['yearly_inflation'] / 100) ** years_from_now
                income_todays_dollars = effective_income / inflation_factor
                year_data['Income (Today\'s $)'] = round(income_todays_dollars, 2)
                
                # Calculate returns on balance AFTER withdrawals and surplus reinvestment
                annual_return = balance * (self.inputs['investment_return'] / 100)
                balance += annual_return
                year_data['Yearly Investment Return'] = round(annual_return, 2)
            else:
                # Before retirement, add returns and contributions
                balance += annual_return
                year_data['Yearly Investment Return'] = round(annual_return, 2)
            
            year_data['Investment Balance End'] = round(max(0, balance), 2)
            projection.append(year_data)
            
            # Update balance for next year
            balance = year_data['Investment Balance End']
        
        # Calculate summary statistics
        total_withdrawals = sum(row['Investment Withdrawal'] * 12 for row in projection)
        total_pension = sum(row['Yearly Pension Amount'] for row in projection)
        total_lump_sums = sum(row['Lump Sum'] for row in projection)
        total_lump_withdrawals = sum(row['Lump Sum Withdrawal'] for row in projection)
        final_balance = projection[-1]['Investment Balance End']
        
        # Generate advice
        advice = self._generate_advice(projection)
        
        return {
            'projection': projection,
            'total_withdrawals': total_withdrawals,
            'total_pension': total_pension,
            'total_lump_sums': total_lump_sums,
            'total_lump_withdrawals': total_lump_withdrawals,
            'final_balance': final_balance,
            'advice': advice
        }
    
    def _generate_advice(self, projection):
        """Generate comprehensive retirement planning advice based on Canadian tax rules and account types"""
        advice_parts = []
        
        # Get account balances
        tfsa = self.inputs.get('tfsa', 0)
        rrsp = self.inputs.get('rrsp', 0)
        non_registered = self.inputs.get('non_registered', 0)
        lira = self.inputs.get('lira', 0)
        total = tfsa + rrsp + non_registered + lira
        
        retirement_age = self.inputs['retirement_age']
        current_age = self.inputs['current_age']
        
        # Analyze projection data for detailed insights
        retirement_rows = [r for r in projection if r['Age'] >= retirement_age]
        
        # Check if running out of money
        depleted = False
        depletion_age = None
        for row in projection:
            if row['Investment Balance End'] <= 0 and row['Age'] < 100:
                depleted = True
                depletion_age = row['Age']
                break
        
        if depleted:
            advice_parts.append(f"### ⚠️ Critical: Funding Shortfall Detected\n")
            advice_parts.append(f"**Your investments are projected to deplete at age {depletion_age}.**\n\n")
            
            # Calculate how much needs to change
            years_short = 100 - depletion_age
            current_monthly = self.inputs['retirement_year_one_income']
            
            advice_parts.append(f"**Immediate Actions Required:**\n\n")
            advice_parts.append(f"**Option 1: Reduce Retirement Spending**\n")
            advice_parts.append(f"- Current target: ${current_monthly:,.0f}/month\n")
            advice_parts.append(f"- Reduce by 15%: ${current_monthly * 0.85:,.0f}/month (saves ${current_monthly * 0.15 * 12:,.0f}/year)\n")
            advice_parts.append(f"- Reduce by 20%: ${current_monthly * 0.80:,.0f}/month (saves ${current_monthly * 0.20 * 12:,.0f}/year)\n\n")
            
            advice_parts.append(f"**Option 2: Delay Retirement**\n")
            advice_parts.append(f"- Current plan: Retire at {retirement_age}\n")
            advice_parts.append(f"- Working until {retirement_age + 2} adds ~${self.inputs['monthly_investments'] * 24:,.0f} to portfolio\n")
            advice_parts.append(f"- Working until {retirement_age + 3} adds ~${self.inputs['monthly_investments'] * 36:,.0f} to portfolio\n\n")
            
            if current_age < retirement_age:
                advice_parts.append(f"**Option 3: Increase Current Savings**\n")
                current_savings = self.inputs.get('monthly_investments', 0)
                years_to_retirement = retirement_age - current_age
                advice_parts.append(f"- Current: ${current_savings:,.0f}/month\n")
                advice_parts.append(f"- Increase by $500/month = ${500 * 12 * years_to_retirement:,.0f} more by retirement\n")
                advice_parts.append(f"- Increase by $1,000/month = ${1000 * 12 * years_to_retirement:,.0f} more by retirement\n\n")
            
            advice_parts.append(f"**Option 4: Extend Part-Time Work**\n")
            part_time = self.inputs.get('part_time_income', 0)
            part_time_end = self.inputs.get('part_time_end_age', 65)
            advice_parts.append(f"- Current part-time income: ${part_time:,.0f}/month until age {part_time_end}\n")
            advice_parts.append(f"- Extending to age {part_time_end + 3} reduces portfolio withdrawals by ${part_time * 12 * 3:,.0f}\n")
            advice_parts.append(f"- Extending to age {part_time_end + 5} reduces portfolio withdrawals by ${part_time * 12 * 5:,.0f}\n\n")
        else:
            final_balance = projection[-1]['Investment Balance End']
            advice_parts.append(f"### ✅ Plan Sustainability\n")
            advice_parts.append(f"Your plan is sustainable with a projected balance of **${final_balance:,.0f}** at age 100.\n\n")
            
            # Analyze balance trajectory
            retirement_start_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == retirement_age), 0)
            age_75_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == 75), 0)
            age_85_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == 85), 0)
            
            advice_parts.append(f"**Balance Trajectory:**\n")
            advice_parts.append(f"- Age {retirement_age} (retirement): ${retirement_start_balance:,.0f}\n")
            advice_parts.append(f"- Age 75: ${age_75_balance:,.0f} ({((age_75_balance - retirement_start_balance) / retirement_start_balance * 100):+.1f}%)\n")
            advice_parts.append(f"- Age 85: ${age_85_balance:,.0f} ({((age_85_balance - retirement_start_balance) / retirement_start_balance * 100):+.1f}%)\n")
            advice_parts.append(f"- Age 100: ${final_balance:,.0f} ({((final_balance - retirement_start_balance) / retirement_start_balance * 100):+.1f}%)\n\n")
            
            # Assess if balance is growing or declining
            if age_85_balance < retirement_start_balance * 0.5:
                advice_parts.append(
                    "⚠️ **Note:** Your balance declines significantly over time. While sustainable, "
                    "consider running Monte Carlo simulation to test resilience to market volatility.\n\n"
                )
            elif final_balance > retirement_start_balance * 1.5:
                advice_parts.append(
                    "💡 **Opportunity:** Your balance grows substantially. You may have room to:\n"
                    "- Increase retirement spending by 10-15%\n"
                    "- Retire 1-2 years earlier\n"
                    "- Allocate more to legacy/charitable giving\n\n"
                )
        
        # Analyze 4% rule compliance
        if retirement_rows:
            violations = [r for r in retirement_rows if r['% Over 4% Rule'] > 0]
            
            if violations:
                advice_parts.append(f"### ⚠️ Withdrawal Rate Analysis\n")
                advice_parts.append(
                    f"Your plan **exceeds the 4% safe withdrawal rule** in {len(violations)} years "
                    f"({len(violations) / len(retirement_rows) * 100:.0f}% of retirement).\n\n"
                )
                
                # Find worst violations
                worst_violations = sorted(violations, key=lambda x: x['% Over 4% Rule'], reverse=True)[:3]
                advice_parts.append(f"**Highest withdrawal rates:**\n")
                for v in worst_violations:
                    withdrawal_rate = (v['Investment Withdrawal'] * 12 / v['Investment Balance Start'] * 100) if v['Investment Balance Start'] > 0 else 0
                    advice_parts.append(
                        f"- Age {v['Age']}: ${v['Investment Withdrawal']:,.0f}/month "
                        f"({withdrawal_rate:.2f}% annual rate, {v['% Over 4% Rule']:.1f}% over safe limit)\n"
                    )
                
                advice_parts.append(
                    f"\n**Why this matters:** Withdrawing above 4% increases risk of portfolio depletion, "
                    f"especially if markets underperform. The 4% rule has a 95% historical success rate over 30 years.\n\n"
                )
                
                # Calculate average withdrawal rate
                avg_rate = sum(
                    (r['Investment Withdrawal'] * 12 / r['Investment Balance Start'] * 100) 
                    for r in retirement_rows if r['Investment Balance Start'] > 0 and r['Investment Withdrawal'] > 0
                ) / len([r for r in retirement_rows if r['Investment Withdrawal'] > 0])
                
                advice_parts.append(f"**Your average withdrawal rate:** {avg_rate:.2f}% annually\n")
                
                if avg_rate > 5:
                    advice_parts.append(
                        f"⚠️ This is significantly above the 4% safe guideline. **Strongly recommend** "
                        f"reducing expenses or increasing portfolio size.\n\n"
                    )
                elif avg_rate > 4.5:
                    advice_parts.append(
                        f"⚠️ This is moderately above the 4% safe guideline. Consider reducing expenses "
                        f"or running Monte Carlo simulation to assess risk.\n\n"
                    )
            else:
                advice_parts.append(f"### ✅ Withdrawal Rate Analysis\n")
                advice_parts.append(
                    f"Your plan stays **within the 4% safe withdrawal rule** throughout retirement. "
                    f"This provides strong protection against market volatility.\n\n"
                )
        
        # Tax-Optimized Withdrawal Strategy
        advice_parts.append("\n### 💰 Tax-Optimized Withdrawal Strategy\n")
        
        if rrsp > 0 or lira > 0:
            advice_parts.append("**RRSP/LIRA Withdrawals:**")
            advice_parts.append("- Age 65-71: Withdraw strategically to stay below OAS clawback threshold ($95,323 in 2026, indexed to inflation)")
            advice_parts.append("- Age 71: Convert RRSP to RRIF (mandatory)")
            advice_parts.append("- Age 72+: Take RRIF minimum withdrawals (starts at 5.4%, increases with age)")
            if lira > 0:
                advice_parts.append("- LIRA: Convert to LIF at retirement, subject to minimum/maximum withdrawal limits\n")
            else:
                advice_parts.append("")
        
        if non_registered > 0:
            advice_parts.append("**Non-Registered Accounts:**")
            advice_parts.append("- Withdraw first (ages 65-71) to preserve RRSP tax deferral")
            advice_parts.append("- Capital gains taxed at 50% inclusion rate (more tax-efficient)")
            advice_parts.append("- Consider tax-loss harvesting to offset gains\n")
        
        if tfsa > 0:
            advice_parts.append("**TFSA:**")
            advice_parts.append("- Withdraw last - completely tax-free")
            advice_parts.append("- Use as emergency fund in retirement")
            advice_parts.append("- Contribution room restored in following year after withdrawal\n")
        
        # Account allocation advice
        advice_parts.append("\n### 📊 Account Allocation Strategy\n")
        
        if total > 0:
            tfsa_pct = (tfsa / total) * 100
            rrsp_pct = (rrsp / total) * 100
            non_reg_pct = (non_registered / total) * 100
            lira_pct = (lira / total) * 100
            
            advice_parts.append(f"**Current Allocation:**")
            if tfsa > 0:
                advice_parts.append(f"- TFSA: ${tfsa:,.0f} ({tfsa_pct:.1f}%)")
            if rrsp > 0:
                advice_parts.append(f"- RRSP: ${rrsp:,.0f} ({rrsp_pct:.1f}%)")
            if non_registered > 0:
                advice_parts.append(f"- Non-Registered: ${non_registered:,.0f} ({non_reg_pct:.1f}%)")
            if lira > 0:
                advice_parts.append(f"- LIRA: ${lira:,.0f} ({lira_pct:.1f}%)\n")
            
            # Recommendations based on allocation
            if tfsa_pct < 10 and tfsa < 95000:  # 2024 TFSA limit
                advice_parts.append("💡 **Recommendation:** Maximize TFSA contributions for tax-free growth\n")
            
            if rrsp_pct > 80:
                advice_parts.append("⚠️ **Consideration:** Heavy RRSP concentration may create large tax burden in retirement. Consider TFSA contributions.\n")
        
        # OAS Clawback Management
        advice_parts.append("\n### 🏛️ OAS Clawback Management\n")
        oas_threshold = 95323  # 2026
        oas_max = 176708  # Full clawback (2026)
        advice_parts.append(f"**OAS Clawback Thresholds (2026, indexed to inflation):**")
        advice_parts.append(f"- Clawback starts: ${oas_threshold:,}")
        advice_parts.append(f"- Full clawback: ${oas_max:,}")
        advice_parts.append(f"- Rate: 15% of income above threshold\n")
        advice_parts.append("**Strategies to avoid clawback:**")
        advice_parts.append("- Withdraw from TFSA (not counted as income)")
        advice_parts.append("- Split pension income with spouse (if applicable)")
        advice_parts.append("- Time RRSP withdrawals before age 65")
        advice_parts.append("- Consider prescribed rate loans for income splitting\n")
        
        # Income Splitting
        advice_parts.append("\n### 👥 Income Splitting Opportunities\n")
        advice_parts.append("**Pension Income Splitting (Age 65+):**")
        advice_parts.append("- Split up to 50% of eligible pension income with spouse")
        advice_parts.append("- Includes: RRIF, LIF, annuity payments")
        advice_parts.append("- Can reduce overall family tax burden by 20-30%")
        advice_parts.append("- File Form T1032 annually\n")
        
        # Estate Planning
        advice_parts.append("\n### 🏠 Estate Planning Considerations\n")
        if rrsp > 0 or lira > 0:
            advice_parts.append("**RRSP/RRIF/LIRA:**")
            advice_parts.append("- Fully taxable on death (unless transferred to spouse)")
            advice_parts.append("- Consider naming spouse as successor annuitant")
            advice_parts.append("- May face 40-50% tax on remaining balance\n")
        
        if tfsa > 0:
            advice_parts.append("**TFSA:**")
            advice_parts.append("- Tax-free transfer to spouse (name as successor holder)")
            advice_parts.append("- Otherwise, fair market value at death goes to beneficiary tax-free\n")
        
        advice_parts.append("**General Estate Planning:**")
        advice_parts.append("- Update beneficiary designations regularly")
        advice_parts.append("- Consider life insurance to cover final tax bill")
        advice_parts.append("- Consult with estate lawyer for will and power of attorney\n")
        
        # Healthcare and Longevity
        advice_parts.append("\n### 🏥 Healthcare and Longevity Planning\n")
        advice_parts.append("**Healthcare Costs:**")
        advice_parts.append("- Budget $5,000-$10,000/year for healthcare not covered by provincial plans")
        advice_parts.append("- Consider long-term care insurance (costs increase significantly after age 70)")
        advice_parts.append("- Dental, vision, prescriptions add up in retirement\n")
        
        advice_parts.append("**Longevity Risk:**")
        advice_parts.append("- Plan to age 95-100 (Canadians living longer)")
        advice_parts.append("- Consider annuity for guaranteed lifetime income")
        advice_parts.append("- Keep 2-3 years expenses in liquid accounts\n")
        
        # Inflation Protection
        advice_parts.append("\n### 📈 Inflation Protection\n")
        advice_parts.append("**Maintaining Purchasing Power:**")
        advice_parts.append("- CPP/OAS indexed to inflation automatically")
        advice_parts.append("- Keep 30-40% in equities even in retirement for growth")
        advice_parts.append("- Review and adjust withdrawal amounts annually")
        advice_parts.append("- Consider inflation-protected annuities for portion of portfolio\n")
        
        # Asset Allocation Strategy - NEW COMPREHENSIVE SECTION
        advice_parts.append("\n### 📊 Personalized Asset Allocation Strategy\n")
        advice_parts.append("**Your Investment Glide Path: A Decade-by-Decade Plan**\n")
        
        # Calculate current allocation recommendation
        years_to_retirement = retirement_age - current_age
        
        # Current age allocation
        if years_to_retirement > 10:
            current_equity = min(90, 110 - current_age)
            current_bonds = 100 - current_equity
            advice_parts.append(f"**TODAY (Age {current_age}, {years_to_retirement} years to retirement):**")
            advice_parts.append(f"- Equities: {current_equity}% (${total * current_equity / 100:,.0f})")
            advice_parts.append(f"- Bonds/Fixed Income: {current_bonds}% (${total * current_bonds / 100:,.0f})")
            advice_parts.append(f"- Rationale: Maximize growth with {years_to_retirement} years to recover from market downturns\n")
        
        # 10 years before retirement
        if years_to_retirement >= 10:
            age_minus_10 = retirement_age - 10
            equity_minus_10 = min(80, 110 - age_minus_10)
            bonds_minus_10 = 100 - equity_minus_10
            
            # Project portfolio value 10 years before retirement
            years_until = age_minus_10 - current_age
            if years_until > 0:
                projected_balance = total
                for _ in range(years_until):
                    projected_balance += self.inputs['monthly_investments'] * 12
                    projected_balance *= (1 + self.inputs['investment_return'] / 100)
                
                advice_parts.append(f"**AGE {age_minus_10} (10 years before retirement):**")
                advice_parts.append(f"- Projected Portfolio: ${projected_balance:,.0f}")
                advice_parts.append(f"- Target Allocation: {equity_minus_10}% equities / {bonds_minus_10}% bonds")
                advice_parts.append(f"  - Equities: ${projected_balance * equity_minus_10 / 100:,.0f}")
                advice_parts.append(f"  - Bonds: ${projected_balance * bonds_minus_10 / 100:,.0f}")
                advice_parts.append(f"- Action: Begin gradual shift to bonds, reduce equity by 1-2% per year")
                advice_parts.append(f"- Focus: Balance growth with capital preservation\n")
        
        # 5 years before retirement
        if years_to_retirement >= 5:
            age_minus_5 = retirement_age - 5
            equity_minus_5 = min(70, 110 - age_minus_5)
            bonds_minus_5 = 100 - equity_minus_5
            
            years_until = age_minus_5 - current_age
            if years_until > 0:
                projected_balance = total
                for _ in range(years_until):
                    projected_balance += self.inputs['monthly_investments'] * 12
                    projected_balance *= (1 + self.inputs['investment_return'] / 100)
                
                advice_parts.append(f"**AGE {age_minus_5} (5 years before retirement):**")
                advice_parts.append(f"- Projected Portfolio: ${projected_balance:,.0f}")
                advice_parts.append(f"- Target Allocation: {equity_minus_5}% equities / {bonds_minus_5}% bonds")
                advice_parts.append(f"  - Equities: ${projected_balance * equity_minus_5 / 100:,.0f}")
                advice_parts.append(f"  - Bonds: ${projected_balance * bonds_minus_5 / 100:,.0f}")
                advice_parts.append(f"- Action: Accelerate bond allocation, build 2-year cash reserve")
                advice_parts.append(f"- Cash Reserve Target: ${self.inputs['retirement_year_one_income'] * 24:,.0f} (2 years expenses)\n")
        
        # At retirement
        retirement_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == retirement_age), total)
        equity_at_retirement = max(40, min(60, 110 - retirement_age))
        bonds_at_retirement = 100 - equity_at_retirement
        
        advice_parts.append(f"**AGE {retirement_age} (RETIREMENT DAY):**")
        advice_parts.append(f"- Projected Portfolio: ${retirement_balance:,.0f}")
        advice_parts.append(f"- Target Allocation: {equity_at_retirement}% equities / {bonds_at_retirement}% bonds")
        advice_parts.append(f"  - Equities: ${retirement_balance * equity_at_retirement / 100:,.0f}")
        advice_parts.append(f"  - Bonds: ${retirement_balance * bonds_at_retirement / 100:,.0f}")
        advice_parts.append(f"- Cash Reserve: ${self.inputs['retirement_year_one_income'] * 24:,.0f} (2 years)")
        advice_parts.append(f"- Strategy: Maintain growth potential while protecting principal\n")
        
        # Age 70 (CPP/OAS typically start)
        age_70_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == 70), retirement_balance)
        equity_70 = max(35, min(50, 110 - 70))
        bonds_70 = 100 - equity_70
        
        advice_parts.append(f"**AGE 70 (CPP/OAS Income Begins):**")
        advice_parts.append(f"- Projected Portfolio: ${age_70_balance:,.0f}")
        advice_parts.append(f"- Target Allocation: {equity_70}% equities / {bonds_70}% bonds")
        advice_parts.append(f"  - Equities: ${age_70_balance * equity_70 / 100:,.0f}")
        advice_parts.append(f"  - Bonds: ${age_70_balance * bonds_70 / 100:,.0f}")
        advice_parts.append(f"- Rationale: Government income reduces portfolio withdrawal pressure")
        advice_parts.append(f"- Action: Can maintain higher equity allocation with guaranteed income floor\n")
        
        # Age 75 (RRIF minimum withdrawals)
        age_75_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == 75), age_70_balance)
        equity_75 = max(30, min(45, 110 - 75))
        bonds_75 = 100 - equity_75
        
        advice_parts.append(f"**AGE 75 (RRIF Minimum Withdrawals):**")
        advice_parts.append(f"- Projected Portfolio: ${age_75_balance:,.0f}")
        advice_parts.append(f"- Target Allocation: {equity_75}% equities / {bonds_75}% bonds")
        advice_parts.append(f"  - Equities: ${age_75_balance * equity_75 / 100:,.0f}")
        advice_parts.append(f"  - Bonds: ${age_75_balance * bonds_75 / 100:,.0f}")
        advice_parts.append(f"- RRIF Minimum: {5.82}% (increases annually)")
        advice_parts.append(f"- Strategy: Balance mandatory withdrawals with longevity risk\n")
        
        # Age 85 (Late retirement)
        age_85_balance = next((r['Investment Balance Start'] for r in projection if r['Age'] == 85), age_75_balance)
        equity_85 = max(25, min(35, 110 - 85))
        bonds_85 = 100 - equity_85
        
        advice_parts.append(f"**AGE 85 (Late Retirement Phase):**")
        advice_parts.append(f"- Projected Portfolio: ${age_85_balance:,.0f}")
        advice_parts.append(f"- Target Allocation: {equity_85}% equities / {bonds_85}% bonds")
        advice_parts.append(f"  - Equities: ${age_85_balance * equity_85 / 100:,.0f}")
        advice_parts.append(f"  - Bonds: ${age_85_balance * bonds_85 / 100:,.0f}")
        advice_parts.append(f"- Focus: Capital preservation with inflation protection")
        advice_parts.append(f"- Consider: Annuity for portion of portfolio for guaranteed income\n")
        
        # Account-Specific Allocation Strategy
        advice_parts.append("\n**Account-Specific Investment Strategy:**\n")
        
        if tfsa > 0:
            advice_parts.append(f"**TFSA (${tfsa:,.0f}):**")
            advice_parts.append(f"- Hold: Growth equities (Canadian/US/International stocks)")
            advice_parts.append(f"- Rationale: Tax-free growth maximizes long-term value")
            advice_parts.append(f"- Suggested: 80-100% equities regardless of age")
            advice_parts.append(f"- Withdraw last in retirement (preserve tax-free growth)\n")
        
        if rrsp > 0:
            advice_parts.append(f"**RRSP/RRIF (${rrsp:,.0f}):**")
            advice_parts.append(f"- Hold: Mix of equities and bonds per age-based allocation")
            advice_parts.append(f"- Before 71: Balanced portfolio matching overall target")
            advice_parts.append(f"- After 71: Shift to bonds/GICs to meet RRIF minimums")
            advice_parts.append(f"- Suggested: {equity_at_retirement}% equities / {bonds_at_retirement}% bonds at retirement")
            advice_parts.append(f"- Withdraw strategically to minimize tax (ages 65-71)\n")
        
        if non_registered > 0:
            advice_parts.append(f"**Non-Registered (${non_registered:,.0f}):**")
            advice_parts.append(f"- Hold: Canadian dividend stocks, growth stocks")
            advice_parts.append(f"- Rationale: Dividend tax credit and capital gains treatment")
            advice_parts.append(f"- Avoid: Interest-bearing investments (fully taxable)")
            advice_parts.append(f"- Strategy: Tax-loss harvesting to offset gains")
            advice_parts.append(f"- Withdraw first in retirement (ages 65-71)\n")
        
        if lira > 0:
            advice_parts.append(f"**LIRA/LIF (${lira:,.0f}):**")
            advice_parts.append(f"- Hold: Balanced portfolio with focus on income")
            advice_parts.append(f"- Constraint: Maximum annual withdrawal limits")
            advice_parts.append(f"- Suggested: {equity_at_retirement}% equities / {bonds_at_retirement}% bonds")
            advice_parts.append(f"- Convert to LIF at retirement for income access\n")
        
        # Rebalancing Strategy
        advice_parts.append("\n**Rebalancing Strategy:**\n")
        advice_parts.append(f"- **Frequency:** Review quarterly, rebalance when allocation drifts >5%")
        advice_parts.append(f"- **Method:** Sell high performers, buy underperformers")
        advice_parts.append(f"- **Tax-Efficient:** Rebalance within TFSA/RRSP first (no tax impact)")
        advice_parts.append(f"- **Contributions:** Direct new money to underweight assets")
        advice_parts.append(f"- **Withdrawals:** Take from overweight assets in retirement\n")
        
        # Specific Product Recommendations
        advice_parts.append("\n**Recommended Investment Products (Canadian):**\n")
        advice_parts.append("**Equity Allocation:**")
        advice_parts.append("- 40% Canadian Equity: VCN (Vanguard Canada All Cap) or XIC (iShares Core S&P/TSX)")
        advice_parts.append("- 35% US Equity: VFV (Vanguard S&P 500) or XUU (iShares Core S&P US)")
        advice_parts.append("- 25% International: VIU (Vanguard FTSE Developed ex NA) or XEF (iShares MSCI EAFE)\n")
        
        advice_parts.append("**Bond Allocation:**")
        advice_parts.append("- 60% Canadian Bonds: VAB (Vanguard Canadian Aggregate) or XBB (iShares Core Canadian)")
        advice_parts.append("- 30% Short-Term Bonds: VSB (Vanguard Canadian Short-Term) for stability")
        advice_parts.append("- 10% Real Return Bonds: XRB (iShares Real Return) for inflation protection\n")
        
        advice_parts.append("**All-in-One Options (Automatic Rebalancing):**")
        advice_parts.append(f"- Conservative (30/70): VCNS (Vanguard) or XCNS (iShares)")
        advice_parts.append(f"- Balanced (60/40): VBAL (Vanguard) or XBAL (iShares)")
        advice_parts.append(f"- Growth (80/20): VGRO (Vanguard) or XGRO (iShares)")
        advice_parts.append(f"- Aggressive (100/0): VEQT (Vanguard) or XEQT (iShares)\n")
        
        # Transition Milestones
        advice_parts.append("\n**Key Transition Milestones & Actions:**\n")
        
        if years_to_retirement > 10:
            advice_parts.append(f"**{retirement_age - 10} (10 years out):**")
            advice_parts.append(f"- Review and update retirement income needs")
            advice_parts.append(f"- Begin shifting 1-2% annually from equities to bonds")
            advice_parts.append(f"- Maximize TFSA contributions (${7000}/year in 2024)")
            advice_parts.append(f"- Consider topping up RRSP to maximize deduction\n")
        
        if years_to_retirement > 5:
            advice_parts.append(f"**{retirement_age - 5} (5 years out):**")
            advice_parts.append(f"- Build 2-year cash reserve: ${self.inputs['retirement_year_one_income'] * 24:,.0f}")
            advice_parts.append(f"- Accelerate bond allocation to target {bonds_at_retirement}%")
            advice_parts.append(f"- Review CPP/OAS start age strategy (60-70 for CPP, 65-70 for OAS)")
            advice_parts.append(f"- Consolidate accounts for easier management\n")
        
        advice_parts.append(f"**{retirement_age} (Retirement):**")
        advice_parts.append(f"- Implement systematic withdrawal plan")
        advice_parts.append(f"- Set up monthly transfers from investments to chequing")
        advice_parts.append(f"- Apply for CPP/OAS if starting at 65")
        advice_parts.append(f"- Review and adjust asset allocation to {equity_at_retirement}/{bonds_at_retirement}\n")
        
        advice_parts.append(f"**71 (RRSP to RRIF Conversion):**")
        advice_parts.append(f"- Convert RRSP to RRIF by December 31")
        advice_parts.append(f"- Set up RRIF minimum withdrawal schedule")
        advice_parts.append(f"- Consider pension income splitting with spouse")
        advice_parts.append(f"- Review withholding tax strategy\n")
        
        # Risk Management
        advice_parts.append("\n**Risk Management Throughout Retirement:**\n")
        advice_parts.append("**Sequence of Returns Risk:**")
        advice_parts.append("- Most dangerous: Poor returns in first 5 years of retirement")
        advice_parts.append("- Protection: 2-year cash reserve + bond ladder")
        advice_parts.append("- Strategy: Don't sell equities in down markets, use cash/bonds\n")
        
        advice_parts.append("**Longevity Risk:**")
        advice_parts.append("- Canadians living to 90+ increasingly common")
        advice_parts.append("- Solution: Maintain 30-40% equities throughout retirement")
        advice_parts.append("- Consider: Annuity at age 75-80 for guaranteed lifetime income\n")
        
        advice_parts.append("**Inflation Risk:**")
        advice_parts.append("- Historical average: 2-3% annually")
        advice_parts.append("- Impact: Purchasing power halves every 24 years at 3%")
        advice_parts.append("- Protection: Equities, real return bonds, indexed pensions\n")
        
        return "\n".join(advice_parts)
