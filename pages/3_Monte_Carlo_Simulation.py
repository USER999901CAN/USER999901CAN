import streamlit as st
import pandas as pd
import sys
import hashlib
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))
from monte_carlo import MonteCarloSimulator
from charts import create_monte_carlo_percentile_chart, create_failure_age_histogram

st.set_page_config(
    page_title="Monte Carlo Simulation",
    page_icon="🎲",
    layout="wide"
)

# Responsive styling
st.markdown("""
    <style>
        /* Base styles - COMPACT for desktop/tablet */
        .block-container {
            padding-top: 0.2rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        .stMetric {
            background-color: transparent;
            padding: 1px 3px;
            border-radius: 2px;
            margin: 0;
        }
        div[data-testid="stMetricValue"] {
            font-size: 13px;
            font-weight: 600;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 10px;
        }
        h1 {
            margin-top: 0.1rem;
            margin-bottom: 0.2rem;
            padding-top: 0.1rem;
            font-size: 1.4rem;
            line-height: 1.1;
        }
        h2 {
            margin-top: 0.2rem;
            margin-bottom: 0.2rem;
            font-size: 1.1rem;
        }
        h3 {
            margin-top: 0;
            margin-bottom: 0.15rem;
            font-size: 0.75rem;
            font-weight: 600;
        }
        label {
            font-size: 0.75rem;
            margin-bottom: 0.05rem;
        }
        .stButton button {
            padding: 0.2rem 0.6rem;
            width: 100%;
            font-size: 0.8rem;
            min-height: 28px;
        }
        p {
            margin-bottom: 0.15rem;
            font-size: 0.85rem;
        }
        
        /* MOBILE FIRST - Phones (portrait) - Keep mobile-friendly */
        @media (max-width: 480px) {
            .block-container {
                padding: 0.5rem 0.5rem;
            }
            h1 {
                font-size: 1.3rem;
                text-align: center;
            }
            h2 {
                font-size: 1.1rem;
            }
            label {
                font-size: 0.8rem;
            }
            .stButton button {
                padding: 0.6rem 1rem;
                font-size: 0.9rem;
                min-height: 44px;
            }
            div[data-testid="stMetricValue"] {
                font-size: 18px;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 12px;
            }
        }
        
        /* Responsive adjustments for smaller laptops */
        @media (max-width: 1440px) {
            .block-container {
                padding-left: 0.6rem;
                padding-right: 0.6rem;
            }
            h1 {
                font-size: 1.3rem;
            }
            h2 {
                font-size: 1.05rem;
            }
        }
        
        @media (max-width: 1366px) {
            .block-container {
                padding-left: 0.4rem;
                padding-right: 0.4rem;
            }
            h1 {
                font-size: 1.2rem;
            }
            h2 {
                font-size: 1rem;
            }
        }
        
        /* Optimizations for large displays */
        @media (min-width: 1920px) {
            .block-container {
                max-width: 1800px;
                margin: 0 auto;
            }
        }
        
        @media (min-width: 2560px) {
            .block-container {
                max-width: 2200px;
                margin: 0 auto;
            }
        }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Monte Carlo Stress Test")

# Check if we have inputs from the main page
if 'inputs' not in st.session_state or 'results' not in st.session_state:
    st.warning("⚠️ Please calculate your retirement plan on the main page first!")
    st.markdown("Go back to the main page and click 'Calculate Retirement Plan' to generate your baseline projection.")
    st.stop()

inputs = st.session_state.inputs
results = st.session_state.results

# Check if inputs have changed since last Monte Carlo run
if 'mc_inputs_hash' not in st.session_state:
    st.session_state.mc_inputs_hash = None

# Create a hash of current inputs to detect changes
import hashlib
import json
current_hash = hashlib.md5(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

# If inputs changed, clear old Monte Carlo results
if st.session_state.mc_inputs_hash != current_hash:
    if 'mc_results' in st.session_state:
        del st.session_state.mc_results
    st.session_state.mc_inputs_hash = current_hash
    if st.session_state.mc_inputs_hash is not None:
        st.info("ℹ️ Your inputs have changed. Please run a new Monte Carlo simulation.")

# Display current inputs summary
with st.expander("📋 Current Plan Summary", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Personal:**")
        st.markdown(f"- Current Age: {inputs['current_age']}")
        st.markdown(f"- Retirement Age: {inputs['retirement_age']}")
        st.markdown(f"- Total Investments: ${inputs['total_investments']:,.0f}")
    with col2:
        st.markdown("**Contributions:**")
        st.markdown(f"- Monthly: ${inputs['monthly_investments']:,.0f}")
        st.markdown(f"- Stop at Age: {inputs['stop_investments_age']}")
        st.markdown(f"- Expected Return: {inputs['investment_return']:.1f}%")
    with col3:
        st.markdown("**Retirement:**")
        st.markdown(f"- Monthly Income Target: ${inputs['retirement_year_one_income']:,.0f}")
        st.markdown(f"- Part-Time Income: ${inputs['part_time_income']:,.0f}")
        st.markdown(f"- Pension: ${inputs['monthly_pension']:,.0f}")

st.markdown("---")

st.markdown("""
### 🎯 What This Simulation Tests

This Monte Carlo analysis runs 10,000 scenarios to test whether your retirement savings will **last until age 100** 
under realistic market conditions. It's testing the **sustainability** of your withdrawals, not just whether you'll 
have money at retirement.

**Key Point:** Even if you have $5.6M at retirement, you could still run out of money if:
- Market crashes occur early in retirement (sequence of returns risk)
- Your withdrawal rate is too high relative to portfolio size
- Inflation erodes purchasing power faster than expected

The simulation accounts for all of these risks to give you a realistic success probability.
""")

st.markdown("---")

st.markdown("""
Test your retirement plan against 10,000 different market scenarios to assess robustness.

**Why might Monte Carlo show lower success than the baseline projection?**

Your baseline projection assumes a **constant 5.5% return every year** - this never happens in real markets!

The Monte Carlo simulation uses **realistic variable returns**:
- Some years: +20% (bull markets)
- Some years: -10% (bear markets)  
- Average: 5.5% (same as baseline)

**Sequence of Returns Risk:** If you get bad returns early in retirement (when withdrawing), you can run out of money even if the long-term average is good. This is why a 35% success rate with a $2.5M baseline is possible - 65% of scenarios hit bad markets at the wrong time.

**What the simulation tests:**
- **Market volatility** (18% standard deviation - historical S&P 500)
- **Sequence of returns risk** (crashes during withdrawal phase)
- **Real-world market patterns** (not constant returns)

A success rate of **80% or higher** is considered robust for retirement planning.
""")

# Simulation parameters
col1, col2 = st.columns(2)
with col1:
    num_simulations = st.number_input("Number of Simulations", 1000, 50000, 10000, step=1000,
                                      help="More simulations = more accurate but slower")
with col2:
    std_dev = st.number_input("Market Volatility (Standard Deviation)", 0.10, 0.30, 0.18, step=0.01,
                              help="Historical S&P 500 volatility is ~18%")

if st.button("Run Monte Carlo Simulation", type="primary"):
    with st.spinner(f"Running {num_simulations:,} simulations... This may take a moment."):
        simulator = MonteCarloSimulator(inputs, num_simulations=num_simulations)
        # Override std_dev if user changed it
        mc_results = simulator.run_simulation()
        st.session_state.mc_results = mc_results
        st.success("✅ Simulation complete!")

# Display results if they exist
if 'mc_results' in st.session_state and st.session_state.mc_results:
    mc_results = st.session_state.mc_results
    simulator = MonteCarloSimulator(inputs, num_simulations=num_simulations)
    
    success_rate = mc_results['success_rate']
    rating, interpretation = simulator.get_interpretation(success_rate)
    
    # Success rate display
    st.header("Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col2:
        st.metric("Rating", rating)
    with col3:
        st.metric("Successful Scenarios", f"{mc_results['successes']:,} / {num_simulations:,}")
    
    # Interpretation
    if success_rate >= 80:
        st.success(f"✅ {interpretation}")
    elif success_rate >= 70:
        st.warning(f"⚠️ {interpretation}")
    else:
        st.error(f"❌ {interpretation}")
    
    # Failure analysis
    if mc_results['failures'] > 0:
        st.subheader("Failure Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Failed Scenarios", f"{mc_results['failures']:,}")
        with col2:
            st.metric("Average Failure Age", f"{mc_results['avg_failure_age']:.1f}")
        
        # Failure age distribution
        st.markdown("#### Distribution of Failure Ages")
        st.markdown("""
        This histogram shows **when** your money runs out in the scenarios that failed. 
        If most failures cluster in your 80s-90s, that's less concerning than failures in your 70s. 
        Early failures (70s) suggest you need significant plan adjustments, while late failures (90s) 
        might be acceptable given the low probability of living that long.
        """)
        
        st.plotly_chart(
            create_failure_age_histogram(mc_results),
            use_container_width=True
        )
    else:
        st.success("🎉 No failures! Your plan succeeded in all simulated scenarios.")
    
    # Balance percentiles chart
    st.subheader("Balance Projections Across Scenarios")
    st.markdown("""
    This chart shows how your investment balance evolves across 10,000 different market scenarios:
    
    - **Blue line (median)**: The middle outcome - half of scenarios do better, half do worse
    - **Dark blue band (25th-75th percentile)**: Where 50% of scenarios fall - the "typical" range
    - **Light blue band (10th-90th percentile)**: Where 80% of scenarios fall - includes most outcomes
    - **Green line**: Your retirement age - when withdrawals begin
    - **Red line**: Zero balance - scenarios below this line have run out of money
    
    The wider the bands, the more uncertainty in your plan. Bands narrowing over time is normal as 
    withdrawals reduce balance. If the median line stays well above zero, your plan is robust.
    """)
    
    ages = list(mc_results['percentile_data'].keys())
    
    st.plotly_chart(
        create_monte_carlo_percentile_chart(mc_results, inputs['retirement_age']),
        use_container_width=True
    )
    
    # Key insights
    st.subheader("Key Insights")
    
    st.markdown("""
    These statistics summarize the 10,000 scenarios to help you understand the range of possible outcomes:
    
    - **Median final balance**: The middle outcome at age 100 - half of scenarios end with more, half with less
    - **Best case**: The most optimistic scenario (top 1%) - everything goes right with markets
    - **Worst case**: The most pessimistic scenario (bottom 1%) - multiple market crashes at bad times
    - **Sequence of returns risk**: How vulnerable you are to market crashes early in retirement
    - **Plan robustness**: Overall assessment of whether your plan can withstand market volatility
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Final Balance Statistics:**")
        st.markdown(f"- Median: ${mc_results['median_final_balance']:,.0f}")
        st.markdown(f"- Best case: ${mc_results['best_case_balance']:,.0f}")
        st.markdown(f"- Worst case: ${mc_results['worst_case_balance']:,.0f}")
    
    with col2:
        st.markdown("**Risk Assessment:**")
        if success_rate >= 90:
            risk_level = "Low"
            risk_color = "🟢"
        elif success_rate >= 80:
            risk_level = "Moderate"
            risk_color = "🟡"
        else:
            risk_level = "High"
            risk_color = "🔴"
        
        st.markdown(f"- Sequence of returns risk: {risk_color} {risk_level}")
        st.markdown(f"- Plan robustness: {rating}")
        st.markdown(f"- Confidence level: {success_rate:.1f}%")
    
    # Detailed insights
    st.markdown("---")
    detailed_insights = simulator.get_detailed_insights(mc_results)
    st.markdown(detailed_insights)
    
    st.markdown("---")
    
    # Legacy improvement suggestions (keeping for now but insights above are more comprehensive)
    if False and success_rate < 80:
        st.subheader("🔧 How to Improve Your Success Rate")
        
        st.markdown("""
        Your plan has a **{:.1f}% success rate**, which is below the recommended 80%. Here are strategies to improve it:
        """.format(success_rate))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Reduce Risk:**")
            st.markdown("- Reduce retirement spending by 10-20%")
            st.markdown("- Delay retirement by 2-3 years")
            st.markdown("- Work part-time longer (to age 67-70)")
            st.markdown("- Delay CPP/OAS to age 70 (increases payments)")
            st.markdown("- Build larger emergency fund (2-3 years expenses)")
        
        with col2:
            st.markdown("**Increase Resources:**")
            st.markdown("- Increase current savings rate by 20-30%")
            st.markdown("- Maximize TFSA contributions")
            st.markdown("- Consider downsizing home in retirement")
            st.markdown("- Explore annuities for guaranteed income")
            st.markdown("- Review investment allocation (too conservative?)")
        
        st.markdown("""
        ---
        **Quick Impact Estimates:**
        - Delay retirement 2 years: +15-20% success rate
        - Reduce spending 15%: +20-25% success rate  
        - Increase savings $500/month: +10-15% success rate
        - Combine strategies: Can reach 80%+ success rate
        """)
    
    # Comparison with baseline
    st.subheader("📊 Baseline vs Monte Carlo Comparison")
    
    baseline_final = results['final_balance']
    mc_median = mc_results['median_final_balance']
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Baseline Projection (Constant Returns):**")
        st.markdown(f"- Assumes: {inputs['investment_return']:.1f}% return every year")
        st.markdown(f"- Final balance at 100: ${baseline_final:,.0f}")
        st.markdown(f"- Success rate: 100% (no variability)")
        st.markdown("- ⚠️ Unrealistic - markets never return constant amounts")
    
    with col2:
        st.markdown("**Monte Carlo (Variable Returns):**")
        st.markdown(f"- Average return: {inputs['investment_return']:.1f}% (with 18% volatility)")
        st.markdown(f"- Median final balance: ${mc_median:,.0f}")
        st.markdown(f"- Success rate: {success_rate:.1f}%")
        st.markdown("- ✅ Realistic - accounts for market ups and downs")
    
    st.markdown("""
    ---
    **Why the difference?**
    
    The baseline uses **constant returns** (5.5% every year), which is like assuming perfect weather every day.
    
    Monte Carlo uses **variable returns** (sometimes +20%, sometimes -10%, averaging 5.5%), which is like real weather - some sunny days, some rainy days.
    
    **The danger:** If you retire and the market crashes in year 1-5 (while you're withdrawing), you can run out of money even though the long-term average is good. This is called **sequence of returns risk**.
    
    **Example:**
    - Scenario A: +5.5% every year → $2.5M at age 100 ✅
    - Scenario B: -20%, -10%, +5%, +15%, +25%, then +5.5% average → $0 at age 85 ❌
    
    Both have the same average return, but Scenario B fails because of bad timing!
    """)
