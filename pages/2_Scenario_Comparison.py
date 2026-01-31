import streamlit as st
import pandas as pd
import json
from pathlib import Path
from calculator import RetirementCalculator
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Scenario Comparison",
    page_icon="📊",
    layout="wide"
)

# Responsive styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            max-width: 100%;
        }
        
        /* Responsive adjustments for smaller laptops */
        @media (max-width: 1440px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            h1 {
                font-size: 1.5rem;
            }
            h2 {
                font-size: 1.2rem;
            }
        }
        
        @media (max-width: 1366px) {
            .block-container {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            h1 {
                font-size: 1.3rem;
            }
            h2 {
                font-size: 1.1rem;
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

st.title("📊 Scenario Comparison")
st.markdown("Compare up to 10 retirement scenarios side-by-side")

# Check if scenarios exist in session state
if 'saved_scenarios' not in st.session_state or not st.session_state.saved_scenarios:
    st.warning("⚠️ No saved scenarios found. Please save some scenarios from the main page first.")
    st.info("💡 **How to save scenarios:**\n1. Go to the Main page\n2. Enter your inputs and click Calculate\n3. Give your scenario a name in the sidebar\n4. Click 'Save Scenario'")
    st.stop()

# Show calculation status
if 'calculated_scenarios' in st.session_state and st.session_state.calculated_scenarios:
    num_calculated = len(st.session_state.calculated_scenarios)
    num_total = len(st.session_state.saved_scenarios)
    st.success(f"⚡ {num_calculated} of {num_total} scenarios pre-calculated (instant comparison)")
else:
    st.info("💡 Tip: Use '⚡ Calculate All Scenarios' on the Main page for instant comparisons")

# Scenario selection
st.subheader("Select Scenarios to Compare")

# Add indicators for pre-calculated scenarios
available_scenarios = list(st.session_state.saved_scenarios.keys())
calculated_set = set(st.session_state.get('calculated_scenarios', {}).keys())

# Create display names with indicators
scenario_display_names = []
scenario_name_map = {}
for name in available_scenarios:
    if name in calculated_set:
        display_name = f"⚡ {name}"
    else:
        display_name = f"   {name}"
    scenario_display_names.append(display_name)
    scenario_name_map[display_name] = name

selected_display = st.multiselect(
    "Choose up to 10 scenarios (⚡ = pre-calculated):",
    scenario_display_names,
    max_selections=10,
    help="Pre-calculated scenarios (⚡) load instantly. Others will be calculated on demand."
)

# Convert display names back to actual names
selected_scenarios = [scenario_name_map[display] for display in selected_display]

if len(selected_scenarios) < 2:
    st.info("ℹ️ Please select at least 2 scenarios to compare.")
    st.stop()

# Load and calculate scenarios
if st.button("🔄 Compare Scenarios", type="primary"):
    with st.spinner("Calculating scenarios..."):
        comparison_data = []
        scenario_projections = {}  # Store full projections for line charts
        failed_scenarios = []
        
        # Check if we have pre-calculated results
        use_cached = 'calculated_scenarios' in st.session_state
        
        for scenario_name in selected_scenarios:
            try:
                # Try to use cached calculation first
                if use_cached and scenario_name in st.session_state.calculated_scenarios:
                    cached = st.session_state.calculated_scenarios[scenario_name]
                    inputs = cached['inputs']
                    results = cached['results']
                    df = cached['projection_df']
                else:
                    # Load scenario from session state and calculate
                    inputs = st.session_state.saved_scenarios.get(scenario_name)
                    if not inputs:
                        failed_scenarios.append(f"{scenario_name} (not found in session)")
                        continue
                    
                    # Migrate old field names to new couple-mode field names
                    inputs = inputs.copy()  # Don't modify original
                    
                    # Check if this is an old scenario (has pension_start_age instead of oas_start_age)
                    if 'pension_start_age' in inputs and 'oas_start_age' not in inputs:
                        # Migrate OAS fields
                        inputs['oas_start_age'] = inputs.get('pension_start_age', 65)
                        inputs['monthly_oas'] = inputs.get('monthly_pension', 0)
                        inputs['oas_inflation_adjusted'] = inputs.get('pension_inflation_adjusted', True)
                        
                        # Set Person 2 to defaults (old scenarios were single-person)
                        inputs['oas_start_age_p2'] = 999
                        inputs['monthly_oas_p2'] = 0
                        inputs['oas_inflation_adjusted_p2'] = True
                        
                        # Migrate CPP fields (old scenarios didn't have separate CPP)
                        # Assume CPP was included in the pension amount, so set to 0
                        inputs['cpp_start_age'] = 70
                        inputs['monthly_cpp'] = 0
                        inputs['cpp_inflation_adjusted'] = True
                        inputs['cpp_start_age_p2'] = 999
                        inputs['monthly_cpp_p2'] = 0
                        inputs['cpp_inflation_adjusted_p2'] = True
                        
                        # Couple mode defaults
                        inputs.setdefault('couple_mode', False)
                    
                    # Ensure all required fields exist with defaults
                    inputs.setdefault('oas_start_age', 65)
                    inputs.setdefault('monthly_oas', 0)
                    inputs.setdefault('oas_inflation_adjusted', True)
                    inputs.setdefault('oas_start_age_p2', 999)
                    inputs.setdefault('monthly_oas_p2', 0)
                    inputs.setdefault('oas_inflation_adjusted_p2', True)
                    inputs.setdefault('cpp_start_age', 70)
                    inputs.setdefault('monthly_cpp', 0)
                    inputs.setdefault('cpp_inflation_adjusted', True)
                    inputs.setdefault('cpp_start_age_p2', 999)
                    inputs.setdefault('monthly_cpp_p2', 0)
                    inputs.setdefault('cpp_inflation_adjusted_p2', True)
                    inputs.setdefault('couple_mode', False)
                    
                    # CRITICAL: Ensure current_age exists
                    if 'current_age' not in inputs or inputs['current_age'] is None:
                        # Try to calculate from birthdate
                        if inputs.get('birthdate'):
                            from datetime import datetime
                            birthdate = datetime.strptime(inputs['birthdate'], '%Y-%m-%d')
                            today = datetime.today()
                            inputs['current_age'] = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                        else:
                            # Use retirement_age - 5 as a reasonable default
                            inputs['current_age'] = inputs.get('retirement_age', 65) - 5
                    
                    # Calculate results
                    calculator = RetirementCalculator(inputs)
                    results = calculator.calculate()
                    df = pd.DataFrame(results['projection'])
                retirement_age = inputs['retirement_age']
                current_age = inputs['current_age']
                
                # Store full projection for line charts
                scenario_projections[scenario_name] = df
                
                # Get balance at retirement
                retirement_row = df[df['Age'] == retirement_age]
                balance_at_retirement = retirement_row['Investment Balance Start'].iloc[0] if not retirement_row.empty else 0
                
                # Get balance at age 75
                age_75_row = df[df['Age'] == 75]
                balance_at_75 = age_75_row['Investment Balance End'].iloc[0] if not age_75_row.empty else 0
                
                # Get balance at age 85
                age_85_row = df[df['Age'] == 85]
                balance_at_85 = age_85_row['Investment Balance End'].iloc[0] if not age_85_row.empty else 0
                
                # Get balance at age 95
                age_95_row = df[df['Age'] == 95]
                balance_at_95 = age_95_row['Investment Balance End'].iloc[0] if not age_95_row.empty else 0
                
                # Detect shortfall (when balance hits zero before age 100)
                shortfall_age = None
                initial_shortfall = 0
                for idx, row in df.iterrows():
                    if row['Age'] >= retirement_age and row['Investment Balance End'] <= 0 and row['Age'] < 100:
                        shortfall_age = int(row['Age'])
                        # Initial shortfall is the required withdrawal that couldn't be met
                        # Look at the monthly shortfall or the withdrawal amount that year
                        if 'Monthly Shortfall' in row and row['Monthly Shortfall'] > 0:
                            initial_shortfall = row['Monthly Shortfall']
                        elif row['Investment Withdrawal'] > 0:
                            # If balance is 0 but withdrawal was needed, that's the shortfall
                            initial_shortfall = row['Investment Withdrawal']
                        break
                
                # Calculate Financial Health Score (0-100)
                # Based on financial planning best practices
                score = 100
                
                # Factor 1: Longevity of funds (40 points max)
                # Ideal: Funds last to age 100+ with positive balance
                if shortfall_age:
                    years_short = 100 - shortfall_age
                    score -= min(40, years_short * 2)  # Lose 2 points per year short of 100
                elif balance_at_95 <= 0:
                    score -= 40  # No funds at 95
                elif balance_at_95 < balance_at_retirement * 0.25:
                    score -= 20  # Low balance at 95 (less than 25% of retirement balance)
                
                # Factor 2: Balance trajectory (30 points max)
                # Ideal: Maintain or grow balance through retirement
                if balance_at_75 > 0 and balance_at_85 > 0:
                    # Check if balance is declining too rapidly
                    decline_75_to_85 = (balance_at_75 - balance_at_85) / balance_at_75 if balance_at_75 > 0 else 0
                    if decline_75_to_85 > 0.5:  # Lost more than 50% in 10 years
                        score -= 15
                    elif decline_75_to_85 > 0.3:  # Lost 30-50%
                        score -= 10
                    
                    # Check balance at 85 relative to retirement
                    if balance_at_85 < balance_at_retirement * 0.3:
                        score -= 15  # Less than 30% of retirement balance at 85
                elif balance_at_85 <= 0:
                    score -= 30  # No funds at 85
                
                # Factor 3: Retirement readiness (30 points max)
                # Ideal: Strong balance at retirement relative to needs
                years_in_retirement = 95 - retirement_age
                if balance_at_retirement > 0 and years_in_retirement > 0:
                    # Rough estimate: need 25x annual expenses for safe withdrawal
                    # If balance at 95 is still positive, that's good
                    if balance_at_95 > balance_at_retirement * 0.5:
                        pass  # Excellent - no deduction
                    elif balance_at_95 > balance_at_retirement * 0.25:
                        score -= 10  # Good but declining
                    elif balance_at_95 > 0:
                        score -= 20  # Marginal
                    else:
                        score -= 30  # Insufficient
                else:
                    score -= 30  # No retirement balance
                
                # Ensure score stays in 0-100 range
                score = max(0, min(100, score))
                
                comparison_data.append({
                    'Scenario': scenario_name,
                    'Financial Health Score': score,
                    'Years Until Retirement': retirement_age - current_age,
                    'Retirement Age': retirement_age,
                    'Balance at Retirement': balance_at_retirement,
                    'Balance at Age 75': balance_at_75,
                    'Balance at Age 85': balance_at_85,
                    'Balance at Age 95': balance_at_95,
                    'Shortfall Age': shortfall_age if shortfall_age else 'N/A',
                    'Initial Shortfall': initial_shortfall if shortfall_age else 0
                })
            except Exception as e:
                failed_scenarios.append(f"{scenario_name} ({str(e)})")
        
        # Show warnings for failed scenarios
        if failed_scenarios:
            st.warning(f"⚠️ Could not load the following scenarios:\n" + "\n".join([f"- {s}" for s in failed_scenarios]))
        
        # Store in session state
        if comparison_data:
            st.session_state.comparison_data = comparison_data
            st.session_state.scenario_projections = scenario_projections
        else:
            st.error("❌ No scenarios could be loaded. Please check that the scenario files exist.")
            st.stop()

# Display comparison if data exists
if 'comparison_data' in st.session_state and st.session_state.comparison_data:
    comparison_df = pd.DataFrame(st.session_state.comparison_data)
    
    # Display comparison table
    st.subheader("📋 Comparison Table")
    
    # Format currency columns
    formatted_df = comparison_df.copy()
    currency_cols = ['Balance at Retirement', 'Balance at Age 75', 'Balance at Age 85', 'Balance at Age 95', 'Initial Shortfall']
    
    for col in currency_cols:
        if col == 'Initial Shortfall':
            formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.0f}" if x > 0 else '-')
        else:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Add color coding to Financial Health Score
    def color_score(val):
        if val >= 80:
            return '🟢'  # Green - Excellent
        elif val >= 60:
            return '🟡'  # Yellow - Good
        elif val >= 40:
            return '🟠'  # Orange - Fair
        else:
            return '🔴'  # Red - Poor
    
    formatted_df['Rating'] = formatted_df['Financial Health Score'].apply(color_score)
    formatted_df['Financial Health Score'] = formatted_df['Financial Health Score'].apply(lambda x: f"{x:.0f}/100")
    
    # Reorder columns to put score first after scenario name
    cols = ['Scenario', 'Financial Health Score', 'Rating'] + [col for col in formatted_df.columns if col not in ['Scenario', 'Financial Health Score', 'Rating']]
    formatted_df = formatted_df[cols]
    
    st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
    st.caption("💡 **Financial Health Score:** 🟢 80-100 (Excellent) | 🟡 60-79 (Good) | 🟠 40-59 (Fair) | 🔴 0-39 (Poor)")
    st.caption("Score based on: fund longevity (40%), balance trajectory (30%), retirement readiness (30%)")
    
    # Visual comparisons
    st.subheader("📊 Visual Comparison")
    
    # Get scenario projections
    scenario_projections = st.session_state.get('scenario_projections', {})
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Balance Over Time", "Income & Withdrawals", "Income Sources", "Key Milestones"])
    
    with tab1:
        # Balance progression line chart
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for idx, (scenario_name, df) in enumerate(scenario_projections.items()):
            fig.add_trace(go.Scatter(
                x=df['Age'],
                y=df['Investment Balance End'],
                mode='lines',
                name=scenario_name,
                line=dict(width=2, color=colors[idx % len(colors)]),
                hovertemplate='<b>%{fullData.name}</b><br>Age: %{x}<br>Balance: $%{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Investment Balance Progression Over Time',
            xaxis_title='Age',
            yaxis_title='Balance ($)',
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 This chart shows how your investment balance changes over time for each scenario. Compare trajectories to see which scenarios maintain wealth longer.")
    
    with tab2:
        # Income and withdrawals comparison
        fig = go.Figure()
        
        for idx, (scenario_name, df) in enumerate(scenario_projections.items()):
            # Total monthly income
            fig.add_trace(go.Scatter(
                x=df['Age'],
                y=df['Total Monthly Income'],
                mode='lines',
                name=f"{scenario_name} - Income",
                line=dict(width=2, color=colors[idx % len(colors)], dash='solid'),
                hovertemplate='<b>%{fullData.name}</b><br>Age: %{x}<br>Income: $%{y:,.0f}<extra></extra>'
            ))
            
            # Investment withdrawals
            fig.add_trace(go.Scatter(
                x=df['Age'],
                y=df['Investment Withdrawal'],
                mode='lines',
                name=f"{scenario_name} - Withdrawal",
                line=dict(width=1, color=colors[idx % len(colors)], dash='dot'),
                hovertemplate='<b>%{fullData.name}</b><br>Age: %{x}<br>Withdrawal: $%{y:,.0f}<extra></extra>',
                visible='legendonly'  # Hidden by default
            ))
        
        fig.update_layout(
            title='Monthly Income & Withdrawals Over Time',
            xaxis_title='Age',
            yaxis_title='Amount ($)',
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 Solid lines show total monthly income. Dotted lines (click legend to show) display investment withdrawals. Compare how different scenarios balance income sources.")
    
    with tab3:
        # Income sources comparison - stacked area chart for each scenario
        st.markdown("### Income Sources Breakdown by Scenario")
        
        # Create a subplot for each scenario or combined view
        view_option = st.radio(
            "View Mode:",
            ["Combined View", "Individual Scenarios"],
            horizontal=True,
            help="Combined shows all scenarios in one chart, Individual shows separate charts per scenario"
        )
        
        if view_option == "Combined View":
            # Create subplots - one per scenario, arranged in a grid
            from plotly.subplots import make_subplots
            
            num_scenarios = len(scenario_projections)
            cols = min(2, num_scenarios)  # Max 2 columns
            rows = (num_scenarios + cols - 1) // cols  # Calculate rows needed
            
            fig = make_subplots(
                rows=rows, 
                cols=cols,
                subplot_titles=list(scenario_projections.keys()),
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Define consistent colors for income types
            income_colors = {
                'Pension': '#ADD8E6',  # Light blue
                'Part-Time': '#A23B72', 
                'Withdrawals': '#FFB6C1'  # Light pink
            }
            
            for idx, (scenario_name, df) in enumerate(scenario_projections.items()):
                row = (idx // cols) + 1
                col = (idx % cols) + 1
                
                retirement_df = df[df['Age'] >= df[df['Investment Withdrawal'] > 0]['Age'].min()].copy() if (df['Investment Withdrawal'] > 0).any() else df[df['Age'] >= retirement_age].copy()
                
                if not retirement_df.empty:
                    # Add stacked area traces for this scenario
                    show_legend = (idx == 0)  # Only show legend for first scenario
                    
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=retirement_df['Monthly Pension'],
                        mode='lines',
                        name='Pension',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor=income_colors['Pension'],
                        legendgroup='Pension',
                        showlegend=show_legend,
                        hovertemplate='<b>Pension</b><br>Age: %{x}<br>$%{y:,.0f}<extra></extra>'
                    ), row=row, col=col)
                    
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=retirement_df['Part-Time Income'],
                        mode='lines',
                        name='Part-Time',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor=income_colors['Part-Time'],
                        legendgroup='Part-Time',
                        showlegend=show_legend,
                        hovertemplate='<b>Part-Time</b><br>Age: %{x}<br>$%{y:,.0f}<extra></extra>'
                    ), row=row, col=col)
                    
                    # Cap investment withdrawal at what's actually available
                    capped_withdrawals = []
                    for _, r in retirement_df.iterrows():
                        if r['Investment Balance Start'] > 0:
                            capped_withdrawals.append(r['Investment Withdrawal'])
                        else:
                            capped_withdrawals.append(0)
                    
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=capped_withdrawals,
                        mode='lines',
                        name='Withdrawals',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor=income_colors['Withdrawals'],
                        legendgroup='Withdrawals',
                        showlegend=show_legend,
                        hovertemplate='<b>Withdrawals</b><br>Age: %{x}<br>$%{y:,.0f}<extra></extra>'
                    ), row=row, col=col)
                    
                    # Add required income line - color based on whether needs are met
                    if 'Required Income' in retirement_df.columns:
                        # Calculate if needs are met for each age
                        total_income = retirement_df['Monthly Pension'] + retirement_df['Part-Time Income'] + pd.Series(capped_withdrawals, index=retirement_df.index)
                        needs_met = total_income >= retirement_df['Required Income']
                        
                        # Split into segments where needs are met vs not met
                        ages = retirement_df['Age'].values
                        required = retirement_df['Required Income'].values
                        
                        # Track which colors we've seen for legend (only show once per scenario)
                        colors_used = set()
                        
                        # Add line segments with appropriate colors
                        for i in range(len(ages)):
                            if i == 0:
                                continue
                            
                            # Determine color based on situation
                            if needs_met.iloc[i-1] and needs_met.iloc[i]:
                                color = 'green'  # Needs fully met
                                label = 'Needs Met'
                            elif retirement_df['Investment Balance Start'].iloc[i] > 0:
                                color = 'gold'  # Needs not met but investments available
                                label = 'Using Extra Investments'
                            else:
                                color = 'red'  # Needs not met and no investments (true shortfall)
                                label = 'Shortfall'
                            
                            # Show in legend only once per color per scenario
                            show_in_legend = (label not in colors_used and show_legend)
                            colors_used.add(label)
                            
                            fig.add_trace(go.Scatter(
                                x=[ages[i-1], ages[i]],
                                y=[required[i-1], required[i]],
                                mode='lines',
                                name=label if show_in_legend else None,
                                line=dict(color=color, width=4),
                                legendgroup=label,
                                showlegend=show_in_legend,
                                opacity=1.0,
                                hovertemplate=f'<b>{label}</b><br>Age: %{{x}}<br>$%{{y:,.0f}}<extra></extra>'
                            ), row=row, col=col)
            
            # Update layout
            fig.update_xaxes(title_text="Age")
            fig.update_yaxes(title_text="Monthly Income ($)")
            
            fig.update_layout(
                title_text='Income Sources Comparison - All Scenarios',
                height=400 * rows,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("💡 Pension (blue), part-time (purple), and withdrawals (orange) stack to show total income. Dashed line = required income: 🟢 green (needs met), 🟡 yellow (using investments), 🔴 red (funds depleted).")
        
        else:
            # Individual charts per scenario
            for idx, (scenario_name, df) in enumerate(scenario_projections.items()):
                retirement_df = df[df['Age'] >= df[df['Investment Withdrawal'] > 0]['Age'].min()].copy() if (df['Investment Withdrawal'] > 0).any() else df[df['Age'] >= retirement_age].copy()
                
                if not retirement_df.empty:
                    fig = go.Figure()
                    
                    # Stacked area chart for this scenario
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=retirement_df['Monthly Pension'],
                        mode='lines',
                        name='Pension',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor='#ADD8E6',  # Light blue
                        hovertemplate='<b>Pension</b><br>Age: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=retirement_df['Part-Time Income'],
                        mode='lines',
                        name='Part-Time Income',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor='#A23B72',
                        hovertemplate='<b>Part-Time</b><br>Age: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
                    ))
                    
                    # Cap investment withdrawal at what's actually available (when balance > 0)
                    capped_withdrawals = []
                    for _, row in retirement_df.iterrows():
                        if row['Investment Balance Start'] > 0:
                            capped_withdrawals.append(row['Investment Withdrawal'])
                        else:
                            capped_withdrawals.append(0)
                    
                    fig.add_trace(go.Scatter(
                        x=retirement_df['Age'],
                        y=capped_withdrawals,
                        mode='lines',
                        name='Investment Withdrawals',
                        line=dict(width=0),
                        stackgroup='one',
                        fillcolor='#FFB6C1',  # Light pink
                        hovertemplate='<b>Withdrawals</b><br>Age: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
                    ))
                    
                    # Add required income line - color based on whether needs are met
                    if 'Required Income' in retirement_df.columns:
                        # Calculate if needs are met for each age
                        total_income = retirement_df['Monthly Pension'] + retirement_df['Part-Time Income'] + pd.Series(capped_withdrawals, index=retirement_df.index)
                        needs_met = total_income >= retirement_df['Required Income']
                        
                        # Split into segments where needs are met vs not met
                        ages = retirement_df['Age'].values
                        required = retirement_df['Required Income'].values
                        
                        # Track which colors we've seen for legend
                        colors_used = set()
                        
                        # Add line segments with appropriate colors
                        for i in range(len(ages)):
                            if i == 0:
                                continue
                            
                            # Determine color based on situation
                            if needs_met.iloc[i-1] and needs_met.iloc[i]:
                                color = 'green'  # Needs fully met
                                label = 'Needs Met'
                            elif retirement_df['Investment Balance Start'].iloc[i] > 0:
                                color = 'gold'  # Needs not met but investments available
                                label = 'Using Extra Investments'
                            else:
                                color = 'red'  # Needs not met and no investments (true shortfall)
                                label = 'Shortfall'
                            
                            # Show in legend only once per color
                            show_in_legend = (label not in colors_used)
                            colors_used.add(label)
                            
                            fig.add_trace(go.Scatter(
                                x=[ages[i-1], ages[i]],
                                y=[required[i-1], required[i]],
                                mode='lines',
                                name=label if show_in_legend else None,
                                line=dict(color=color, width=4),
                                legendgroup=label,
                                showlegend=show_in_legend,
                                opacity=1.0,
                                hovertemplate=f'<b>{label}</b><br>Age: %{{x}}<br>Amount: $%{{y:,.0f}}<extra></extra>'
                            ))
                    
                    fig.update_layout(
                        title=f'{scenario_name} - Income Sources Breakdown',
                        xaxis_title='Age',
                        yaxis_title='Monthly Income ($)',
                        height=400,
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            st.caption("💡 Pension (light blue), part-time (purple), and withdrawals (pink) stack to show total income. Solid line = required income: 🟢 green (needs met), 🟡 yellow (using extra investments), 🔴 red (funds depleted).")
    
    with tab4:
        # Key milestone comparison - bar chart for specific ages
        milestone_data = []
        
        for scenario_name, df in scenario_projections.items():
            # Get retirement age from first scenario data
            retirement_row = df[df['Investment Withdrawal'] > 0].head(1)
            retirement_age = retirement_row['Age'].iloc[0] if not retirement_row.empty else 65
            
            # Get balances at key ages
            ages_to_check = [retirement_age, 75, 85, 95, 100]
            
            for age in ages_to_check:
                age_row = df[df['Age'] == age]
                if not age_row.empty:
                    balance = age_row['Investment Balance End'].iloc[0]
                    milestone_data.append({
                        'Scenario': scenario_name,
                        'Age': f"Age {int(age)}",
                        'Balance': balance
                    })
        
        milestone_df = pd.DataFrame(milestone_data)
        
        fig = go.Figure()
        
        for idx, scenario_name in enumerate(scenario_projections.keys()):
            scenario_data = milestone_df[milestone_df['Scenario'] == scenario_name]
            
            fig.add_trace(go.Scatter(
                x=scenario_data['Age'],
                y=scenario_data['Balance'],
                mode='lines+markers',
                name=scenario_name,
                line=dict(width=3, color=colors[idx % len(colors)]),
                marker=dict(size=10),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Balance: $%{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Balance at Key Retirement Milestones',
            xaxis_title='Milestone',
            yaxis_title='Balance ($)',
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("💡 Compare balances at critical retirement ages. See which scenarios provide better financial security at different life stages.")
    
    # Key insights
    st.subheader("🔍 Key Insights")
    
    # Find best/worst scenarios
    best_score = comparison_df.loc[comparison_df['Financial Health Score'].idxmax()]
    worst_score = comparison_df.loc[comparison_df['Financial Health Score'].idxmin()]
    best_balance_95 = comparison_df.loc[comparison_df['Balance at Age 95'].idxmax()]
    worst_balance_95 = comparison_df.loc[comparison_df['Balance at Age 95'].idxmin()]
    earliest_retirement = comparison_df.loc[comparison_df['Retirement Age'].idxmin()]
    latest_retirement = comparison_df.loc[comparison_df['Retirement Age'].idxmax()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Best Financial Health Score:**
        - Scenario: **{best_score['Scenario']}**
        - Score: **{best_score['Financial Health Score']:.0f}/100**
        
        **Worst Financial Health Score:**
        - Scenario: **{worst_score['Scenario']}**
        - Score: **{worst_score['Financial Health Score']:.0f}/100**
        """)
    
    with col2:
        st.markdown(f"""
        **Best Balance at Age 95:**
        - Scenario: **{best_balance_95['Scenario']}**
        - Balance: **${best_balance_95['Balance at Age 95']:,.0f}**
        
        **Earliest Retirement:**
        - Scenario: **{earliest_retirement['Scenario']}**
        - Age: **{earliest_retirement['Retirement Age']:.0f}**
        """)
    
    # Export comparison
    st.subheader("💾 Export Comparison")
    
    csv_data = comparison_df.to_csv(index=False)
    st.download_button(
        "📄 Download Comparison (CSV)",
        csv_data,
        "scenario_comparison.csv",
        "text/csv"
    )
