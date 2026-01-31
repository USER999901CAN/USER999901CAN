# Retirement Planner Rating System

## Overview
The retirement planner uses two complementary rating systems to assess the health and viability of your retirement plan:

1. **Financial Health Score** (0-100) - Based on minimum balance thresholds
2. **Monte Carlo Success Rate** (0-100%) - Based on simulation outcomes

---

## 1. Financial Health Score (Deterministic)

### How It Works
The Financial Health Score evaluates your retirement plan based on the **minimum investment balance** maintained throughout retirement (from retirement age to age 95) in the deterministic projection.

### Rating Scale

| Score | Rating | Emoji | Criteria | Meaning |
|-------|--------|-------|----------|---------|
| **100** | Excellent | 🟢 | Minimum balance ≥ $1,600,000 | Your portfolio stays above $1.6M throughout retirement - excellent cushion |
| **75** | Good | 🟡 | Minimum balance ≥ $1,200,000 | Your portfolio stays above $1.2M - good financial security |
| **50** | Fair | 🟠 | Minimum balance ≥ $500,000 | Your portfolio stays above $500K - adequate but limited margin |
| **25** | Poor | 🔴 | Minimum balance < $500,000 | Portfolio drops below $500K at some point - concerning |
| **0** | Fail | ❌ | Balance reaches $0 before age 100 | Portfolio depletes - plan fails |

### Key Points
- **Critical Rule**: If your portfolio runs out of money before age 100, the score is automatically 0 (Fail)
- The score is based on the **worst point** in your retirement, not the average
- Uses deterministic projection with steady investment returns (no market volatility)
- Provides a baseline assessment assuming consistent market performance

### Where You'll See It
- Main calculator page: Top metrics row showing "Financial Health" and "Rating"
- Scenario Comparison page: First column in comparison table

---

## 2. Monte Carlo Success Rate (Probabilistic)

### How It Works
The Monte Carlo simulation runs **10,000 different scenarios** with realistic market volatility to test whether your retirement plan survives real-world market conditions including crashes, bear markets, and varying sequences of returns.

### Simulation Parameters
- **Number of simulations**: 10,000 scenarios
- **Market volatility**: 18% standard deviation (based on historical S&P 500)
- **Return distribution**: Normal distribution around your expected return rate
- **What it tests**: Portfolio survival to age 100 under varying market conditions

### Rating Scale

| Success Rate | Rating | Interpretation |
|--------------|--------|----------------|
| **≥ 90%** | Excellent | Your plan is very robust and likely to succeed even in poor market conditions |
| **80-89%** | Good | Your plan is robust with a high probability of success |
| **70-79%** | Moderate | Your plan has reasonable success but consider reducing expenses or increasing savings |
| **60-69%** | Concerning | Your plan has significant risk. Consider major adjustments |
| **< 60%** | High Risk | Your plan is unlikely to succeed. Significant changes needed |

### What the Percentages Mean
- **90% success rate** = In 9,000 out of 10,000 simulations, your portfolio lasted to age 100
- **70% success rate** = In 3,000 out of 10,000 simulations, your portfolio ran out before age 100
- The simulation accounts for **sequence of returns risk** - the danger of market crashes early in retirement

### Key Insights Provided
1. **Success Rate**: Overall probability your plan succeeds
2. **Failure Ages**: When portfolio depletes in failed scenarios
3. **Percentile Outcomes**: 10th, 25th, 50th, 75th, 90th percentile balances by age
4. **Best/Worst Cases**: Range of possible outcomes
5. **Median Final Balance**: Middle outcome at age 100

### Where You'll See It
- Main calculator page: "Monte Carlo Success Rate" metric
- Monte Carlo Simulation page (dedicated page): Full analysis with charts and detailed insights

---

## Why Two Rating Systems?

### Financial Health Score (Deterministic)
- **Pros**: Simple, easy to understand, shows baseline scenario
- **Cons**: Assumes steady returns every year (unrealistic)
- **Best for**: Quick assessment and comparing scenarios

### Monte Carlo Success Rate (Probabilistic)
- **Pros**: Tests real-world market volatility, reveals sequence of returns risk
- **Cons**: More complex to understand, requires interpretation
- **Best for**: Understanding true risk and making informed decisions

### Common Scenario
You might see:
- **Financial Health Score**: 75 (Good) - deterministic projection shows success
- **Monte Carlo Success Rate**: 65% (Concerning) - reveals hidden risks

This gap indicates **sequence of returns risk**: your plan works with steady returns but struggles when markets crash early in retirement.

---

## Understanding the Gap Between Ratings

### Why They Can Differ

**Example Scenario:**
- Deterministic projection: Portfolio grows from $1.76M to $2.5M by age 95 ✅
- Monte Carlo: Only 65% success rate ⚠️

**What's happening:**
1. The deterministic calculator assumes 6% return every single year
2. Monte Carlo tests what happens with realistic volatility:
   - Some years: +25% returns
   - Some years: -30% returns (like 2008)
   - **Critical**: If crashes happen early in retirement (ages 62-70), you're forced to sell at low prices
   - This creates a "hole" your portfolio may never recover from

### Sequence of Returns Risk Explained

**Good Sequence** (Lucky):
- Age 62-65: Market up 15-20% → Portfolio grows
- Age 66-70: Market down 20% → Still have cushion
- Age 71+: Market recovers → Plan succeeds

**Bad Sequence** (Unlucky):
- Age 62-65: Market down 30% → Portfolio drops to $1.2M
- Still need to withdraw $54k/year → Down to $1.15M
- Age 66-70: Market recovers → But recovering from smaller base
- Age 71+: Portfolio depleted → Plan fails

**Same average returns, different order = vastly different outcomes**

---

## How to Use These Ratings

### Step 1: Check Financial Health Score
- **100 (Excellent)**: You have significant margin for error
- **75 (Good)**: Solid plan, maintain course
- **50 (Fair)**: Limited cushion, be cautious
- **25 (Poor)**: Needs improvement
- **0 (Fail)**: Major changes required

### Step 2: Check Monte Carlo Success Rate
- **≥ 90%**: Plan is robust against market volatility
- **80-89%**: Good but could be stronger
- **70-79%**: Moderate risk, consider improvements
- **< 70%**: Significant risk, action needed

### Step 3: Compare the Two
- **Both high**: Excellent - your plan is solid
- **Health high, MC low**: Sequence of returns risk - vulnerable to early market crashes
- **Both low**: Serious concerns - multiple issues to address

### Step 4: Take Action
If either rating is concerning, review the detailed recommendations provided in:
- Monte Carlo Simulation page: Comprehensive strategies to improve success rate
- Main calculator: Withdrawal rate analysis and balance projections

---

## Improvement Strategies by Rating

### If Financial Health Score < 75
1. Increase pre-retirement savings
2. Delay retirement by 1-3 years
3. Reduce retirement spending target
4. Work part-time longer in retirement

### If Monte Carlo Success Rate < 85%
1. **Reduce early retirement spending** (ages 62-70) - Most impactful
2. **Implement dynamic withdrawal strategy** - Adjust spending based on market performance
3. **Bridge income gaps** - Extend part-time work or find additional income
4. **Increase pre-retirement savings** - Even $200-500/month helps significantly
5. **Consider annuity** - Guarantee base expenses with 20-30% of portfolio
6. **Delay retirement** - Working 2-3 years longer dramatically improves outcomes

---

## Technical Details

### Financial Health Score Calculation
```python
if shortfall_exists:
    score = 0  # Automatic fail
else:
    min_balance = minimum balance from retirement to age 95
    if min_balance >= 1_600_000:
        score = 100
    elif min_balance >= 1_200_000:
        score = 75
    elif min_balance >= 500_000:
        score = 50
    else:
        score = 25
```

### Monte Carlo Simulation Details
- **Simulations**: 10,000 independent scenarios
- **Return model**: Normal distribution with mean = your expected return, std dev = 18%
- **Volatility basis**: Historical S&P 500 standard deviation
- **Success criteria**: Portfolio balance > $0 at age 100
- **Failure tracking**: Records age when portfolio depletes in failed scenarios

### Market Volatility Context
With 18% standard deviation:
- **68% of years**: Returns between (expected - 18%) and (expected + 18%)
  - Example with 6% expected: -12% to +24%
- **95% of years**: Returns between (expected - 36%) and (expected + 36%)
  - Example with 6% expected: -30% to +42%
- **Occasional years**: -30% to -40% returns (like 2008 financial crisis)

---

## Frequently Asked Questions

### Q: Why is my Monte Carlo rate lower than my Financial Health Score?
**A:** The Financial Health Score assumes steady returns every year. Monte Carlo reveals the risk of market crashes, especially early in retirement (sequence of returns risk).

### Q: What's a "good" Monte Carlo success rate?
**A:** 
- **85%+**: Very good - robust plan
- **75-84%**: Acceptable - some risk remains
- **< 75%**: Concerning - improvements recommended

### Q: Can I trust the deterministic projection if Monte Carlo shows risk?
**A:** No. The deterministic projection is useful for comparison but doesn't account for real-world market volatility. Trust the Monte Carlo results for risk assessment.

### Q: How often should I re-run these calculations?
**A:**
- **Annually**: Check progress and adjust as needed
- **After major life changes**: Job change, inheritance, major expense
- **Market crashes**: Reassess and potentially adjust spending

### Q: What if both ratings are low?
**A:** This indicates serious concerns requiring immediate action:
1. Review all improvement strategies
2. Implement 2-3 major changes
3. Consider consulting a fee-only financial planner
4. Re-run simulations with adjusted parameters

---

## Summary

The retirement planner provides two complementary views:

1. **Financial Health Score**: Quick baseline assessment assuming steady returns
2. **Monte Carlo Success Rate**: Realistic risk assessment with market volatility

**Use both together** to get a complete picture of your retirement plan's viability. The Monte Carlo rate is generally more reliable for understanding true risk, while the Financial Health Score provides an easy-to-understand baseline.

**Remember**: A plan that looks good in deterministic projection but fails Monte Carlo testing needs attention - it's vulnerable to sequence of returns risk.
