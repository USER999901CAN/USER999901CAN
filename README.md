# 🇨🇦 Canadian Retirement Planning Calculator

A comprehensive Streamlit application for planning your retirement with Canadian tax considerations (TFSA, RRSP, LIRA, Non-Registered accounts), government pensions (CPP/OAS), and Monte Carlo stress testing.

**🚀 [Live Demo](https://your-app-name.streamlit.app)** (Coming soon)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## Features

### 💰 Comprehensive Planning
- **Year-by-year projections** from current age to 100
- **Multiple account types**: TFSA, RRSP, Non-Registered, LIRA with tax-optimized withdrawal advice
- **Inflation adjustment**: Income targets in today's dollars, automatically inflated to retirement
- **Part-time work**: Configurable start/end ages and income
- **Government & private pensions**: CPP/OAS and employer pensions with inflation indexing
- **Lump sum events**: Up to 10 deposits (inheritance, property sales) and 10 withdrawals (major expenses)
- **Age-based income reductions**: Model reduced spending at ages 77 and 83

### 📊 Advanced Analysis
- **Monte Carlo simulation**: 10,000 scenarios testing sequence of returns risk
- **Interactive visualizations**: Balance projections, income sources, 4% rule comparison, purchasing power
- **Scenario management**: Save, load, and compare up to 10 different retirement plans
- **Batch calculations**: Calculate all scenarios at once for instant comparisons
- **Export options**: CSV, Excel, PDF

### 🎯 Canadian-Specific Advice
- Tax-optimized withdrawal strategies (RRSP/TFSA/LIRA/Non-Registered)
- OAS clawback management
- Income splitting strategies
- Estate planning considerations
- RRIF conversion timing

## Quick Start

### Local Installation

```bash
# Clone the repository
git clone https://github.com/USER999901CAN/retirement-planner.git
cd retirement-planner

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Cloud Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for instructions on deploying to Streamlit Community Cloud.

## Usage Guide

### 1. Main Page - Enter Your Information

Fill out the three-column input form:

**Column 1: Personal & Investments**
- Current age, birthdate, retirement age
- Yearly inflation rate
- TFSA, RRSP, Non-Registered, LIRA balances (total calculated automatically)

**Column 2: Contributions & Income Needs**
- Monthly contributions and stop age
- Expected annual return rate
- Monthly income target in today's dollars
- Inflation adjustment toggle
- Age-based income reductions (77, 83)

**Column 3: Part-Time Work & Pension**
- Part-time work start/end ages and income
- Government pension start age and monthly amount
- Pension inflation indexing

### 2. Calculate Your Plan

Click **"📊 Calculate Retirement Plan"** to generate:
- Summary metrics (years to retirement, final balance, total withdrawals)
- Year-by-year projection table
- Comprehensive Canadian retirement planning advice
- Export options (CSV, Excel, PDF)

### 3. Monte Carlo Stress Test

Navigate to **"Monte Carlo Simulation"** in the sidebar to:
- Test your plan against 10,000 market scenarios
- See success rate (% of scenarios where money lasts to age 100)
- View failure analysis and balance percentile charts
- Get improvement suggestions if success rate < 80%

**Important:** Monte Carlo uses realistic variable returns (sometimes +20%, sometimes -10%) while the baseline assumes constant returns. A 35% success rate with $2.5M baseline is possible due to sequence of returns risk!

### 4. Scenario Management (New!)

**Save Scenarios:**
1. Enter scenario name in sidebar (e.g., "Base Case", "Early Retirement")
2. Click "💾 Save Scenario"
3. Scenario stored in session (persists during your session)

**Upload Multiple Scenarios:**
1. Click "📂 Upload Scenarios"
2. Select multiple JSON files
3. All scenarios load instantly

**Calculate All at Once:**
1. Click "⚡ Calculate All Scenarios" (appears when 2+ scenarios saved)
2. All scenarios pre-calculated for instant comparison
3. Go to "Scenario Comparison" page

**Download Scenarios:**
- **Single**: "⬇️ Download Current" (saves as `Scenario_Name.json`)
- **All**: "📦 Download All (ZIP)" (saves all scenarios in one ZIP)

**Compare Scenarios:**
1. Go to "Scenario Comparison" page
2. Select 2-10 scenarios (⚡ = pre-calculated, instant loading)
3. Click "Compare Scenarios"
4. View side-by-side analysis with interactive charts

### 5. Scenario Comparison Page

Compare multiple retirement plans with:
- **Balance Over Time**: See how different scenarios perform
- **Income & Withdrawals**: Compare income sources and withdrawal rates
- **Income Sources Breakdown**: Stacked area charts showing pension, part-time, and withdrawals
- **Key Milestones**: Balance at ages 65, 75, 85, 95, 100
- **Key Insights**: Best/worst scenarios, earliest/latest retirement
- **Export**: Download comparison as CSV

## Understanding Results

### Baseline vs Monte Carlo

| Baseline | Monte Carlo |
|----------|-------------|
| Constant returns (e.g., 5.5% every year) | Variable returns (avg 5.5%, std dev 18%) |
| Optimistic but unrealistic | Realistic market conditions |
| Always shows success | Tests sequence of returns risk |

### Success Rate Guidelines

- **90%+**: Excellent - very robust plan
- **80-89%**: Good - robust with high probability of success  
- **70-79%**: Moderate - reasonable but consider adjustments
- **60-69%**: Concerning - significant risk
- **<60%**: High Risk - major changes needed

### Improving Success Rate

- Delay retirement 2 years: **+15-20%**
- Reduce spending 15%: **+20-25%**
- Increase savings $500/month: **+10-15%**
- Combine strategies: **Can reach 80%+**

## Technical Details

### Calculation Logic

**Accumulation Phase:**
1. Returns calculated on starting balance
2. Monthly contributions added with mid-year return convention
3. Continues until retirement age

**Retirement Phase:**
1. Income target inflated from today's dollars to retirement year
2. Continues inflating each year (if enabled)
3. Age-based reductions applied (77, 83)
4. Withdrawals calculated after part-time work and pension
5. Returns applied to remaining balance

### Monte Carlo Methodology

- Normal distribution with 18% standard deviation (historical S&P 500 volatility)
- 10,000 unique return sequences
- Tracks success/failure and balance percentiles
- Identifies sequence of returns risk (market crashes during withdrawal phase)

## Canadian Tax Considerations

The calculator provides advice on:
- **RRSP/RRIF**: Mandatory conversion at 71, minimum withdrawals, strategic timing
- **TFSA**: Tax-free growth and withdrawals, use as emergency fund
- **Non-Registered**: Capital gains treatment, tax-loss harvesting
- **LIRA**: Conversion to LIF, withdrawal limits
- **OAS Clawback**: Threshold management ($86,912 in 2024)
- **Pension Splitting**: Up to 50% with spouse at age 65+
- **Estate Planning**: Tax implications, beneficiary designations

## Files

- `app.py` - Main Streamlit application
- `calculator.py` - Retirement calculation engine
- `monte_carlo.py` - Monte Carlo simulator  
- `export.py` - CSV/Excel/PDF export functions
- `pages/1_Monte_Carlo_Simulation.py` - Monte Carlo stress test page
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.8+
- streamlit
- pandas
- numpy
- matplotlib
- openpyxl
- fpdf

## License

MIT-0 License
