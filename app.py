import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from calculator import RetirementCalculator
from monte_carlo import MonteCarloSimulator, generate_monte_carlo_advice
from export import export_to_pdf, export_to_excel, export_to_csv
from charts import (
    create_balance_projection_chart,
    create_income_sources_chart,
    create_withdrawal_vs_4pct_chart,
    create_purchasing_power_chart,
    create_monte_carlo_percentile_chart,
    create_failure_age_histogram,
    create_dashboard_summary
)

# Page config
st.set_page_config(
    page_title="Main",
    page_icon="💰",
    layout="wide"
)

# Responsive styling for all devices (desktop, tablet, mobile)
st.markdown("""
    <style>
        /* Base styles */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        .stMetric {
            background-color: transparent;
            padding: 2px 5px;
            border-radius: 3px;
            margin: 0;
        }
        div[data-testid="stMetricValue"] {
            font-size: 16px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 12px;
        }
        h1 {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
            padding-top: 0.5rem;
            font-size: 1.8rem;
            line-height: 1.3;
        }
        h2 {
            margin-top: 0.3rem;
            margin-bottom: 0.3rem;
            font-size: 1.3rem;
        }
        h3 {
            margin-top: 0;
            margin-bottom: 0.2rem;
            font-size: 0.95rem;
            font-weight: 600;
        }
        h4 {
            margin-top: 0;
            margin-bottom: 0.1rem;
            font-size: 0.85rem;
        }
        .stNumberInput, .stCheckbox, .stDateInput, .stSelectbox {
            margin-bottom: 0;
        }
        div[data-baseweb="input"] {
            margin-bottom: 0;
            min-height: 32px;
        }
        div[data-baseweb="select"] {
            margin-bottom: 0;
            min-height: 32px;
        }
        label {
            font-size: 0.85rem;
            margin-bottom: 0.1rem;
        }
        .stButton button {
            padding: 0.3rem 1rem;
            width: 100%;
        }
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            gap: 0.1rem;
        }
        [data-testid="column"] {
            padding: 0.2rem;
        }
        div[data-testid="stExpander"] {
            margin-top: 0.2rem;
            margin-bottom: 0.2rem;
        }
        .element-container {
            margin-bottom: 0;
        }
        p {
            margin-bottom: 0.2rem;
        }
        .stCaption {
            font-size: 0.75rem;
            margin-bottom: 0.1rem;
        }
        
        /* Force equal height for all bordered containers */
        div[style*="border: 1px solid"] {
            min-height: 180px;
            display: flex;
            flex-direction: column;
        }
        
        /* Vertically center checkboxes with input fields */
        .stCheckbox {
            display: flex;
            align-items: center;
            padding-top: 1.5rem;
        }
        
        /* MOBILE FIRST - Phones (portrait) */
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
            h3 {
                font-size: 0.95rem;
            }
            label {
                font-size: 0.8rem;
            }
            div[data-baseweb="input"] {
                min-height: 44px; /* Larger touch targets */
            }
            div[data-baseweb="select"] {
                min-height: 44px;
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
            /* Stack columns vertically on mobile */
            [data-testid="column"] {
                width: 100% !important;
                padding: 0.3rem 0;
            }
            /* Make tabs scrollable horizontally */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            .stTabs [data-baseweb="tab"] {
                white-space: nowrap;
                font-size: 0.85rem;
                padding: 0.5rem 0.8rem;
            }
        }
        
        /* TABLETS (portrait) */
        @media (min-width: 481px) and (max-width: 768px) {
            .block-container {
                padding: 0.75rem;
            }
            h1 {
                font-size: 1.5rem;
            }
            h2 {
                font-size: 1.2rem;
            }
            label {
                font-size: 0.85rem;
            }
            div[data-baseweb="input"] {
                min-height: 40px;
            }
            .stButton button {
                padding: 0.5rem 1rem;
                min-height: 40px;
            }
            [data-testid="column"] {
                padding: 0.25rem;
            }
        }
        
        /* TABLETS (landscape) and small laptops */
        @media (min-width: 769px) and (max-width: 1024px) {
            .block-container {
                padding: 1rem;
            }
            h1 {
                font-size: 1.6rem;
            }
            h2 {
                font-size: 1.25rem;
            }
        }
        
        /* Small laptops (1280x720, 1366x768) */
        @media (min-width: 1025px) and (max-width: 1366px) {
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
            h3 {
                font-size: 0.9rem;
            }
            label {
                font-size: 0.75rem;
            }
            div[data-baseweb="input"] {
                min-height: 28px;
            }
            .stButton button {
                padding: 0.2rem 0.8rem;
                font-size: 0.85rem;
            }
            [data-testid="column"] {
                padding: 0.1rem;
            }
        }
        
        /* Standard laptops (1440x900, 1600x900) */
        @media (min-width: 1367px) and (max-width: 1600px) {
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
            label {
                font-size: 0.8rem;
            }
            div[data-testid="stMetricValue"] {
                font-size: 14px;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 11px;
            }
        }
        
        /* Large laptops (1920x1080+) */
        @media (min-width: 1920px) {
            .block-container {
                max-width: 1800px;
                margin: 0 auto;
            }
        }
        
        /* Ultra-wide displays (2560x1440+) */
        @media (min-width: 2560px) {
            .block-container {
                max-width: 2200px;
                margin: 0 auto;
            }
            h1 {
                font-size: 2rem;
            }
            h2 {
                font-size: 1.5rem;
            }
        }
        
        /* Touch-friendly improvements for all mobile devices */
        @media (hover: none) and (pointer: coarse) {
            /* Increase touch target sizes */
            .stButton button,
            div[data-baseweb="input"],
            div[data-baseweb="select"],
            .stCheckbox {
                min-height: 44px;
            }
            /* Add more spacing between interactive elements */
            .stNumberInput,
            .stCheckbox,
            .stDateInput,
            .stSelectbox {
                margin-bottom: 0.5rem;
            }
            /* Prevent zoom on input focus (iOS) */
            input, select, textarea {
                font-size: 16px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for scenarios
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = {}
if 'loaded_scenario' not in st.session_state:
    st.session_state.loaded_scenario = None
if 'scenario_loaded' not in st.session_state:
    st.session_state.scenario_loaded = False
if 'current_loaded_file' not in st.session_state:
    st.session_state.current_loaded_file = None

# Initialize widget keys with defaults if not present
if 'monthly_inv' not in st.session_state:
    st.session_state['monthly_inv'] = 0
if 'gov_start' not in st.session_state:
    st.session_state['gov_start'] = 65
if 'gov_amt' not in st.session_state:
    st.session_state['gov_amt'] = 0
if 'gov_idx' not in st.session_state:
    st.session_state['gov_idx'] = True
if 'priv_start' not in st.session_state:
    st.session_state['priv_start'] = 65
if 'priv_amt' not in st.session_state:
    st.session_state['priv_amt'] = 0
if 'priv_idx' not in st.session_state:
    st.session_state['priv_idx'] = True
if 'pt_income' not in st.session_state:
    st.session_state['pt_income'] = 0
if 'pt_idx' not in st.session_state:
    st.session_state['pt_idx'] = False
if 'reduction_1_enabled' not in st.session_state:
    st.session_state['reduction_1_enabled'] = True
if 'age_reduction_1_age' not in st.session_state:
    st.session_state['age_reduction_1_age'] = 77
if 'age_reduction_1_pct' not in st.session_state:
    st.session_state['age_reduction_1_pct'] = 10
if 'reduction_2_enabled' not in st.session_state:
    st.session_state['reduction_2_enabled'] = True
if 'age_reduction_2_age' not in st.session_state:
    st.session_state['age_reduction_2_age'] = 83
if 'age_reduction_2_pct' not in st.session_state:
    st.session_state['age_reduction_2_pct'] = 10

st.title("🇨🇦 Canadian Retirement Planning Calculator")
st.markdown("Plan your retirement with pension, and investment projections")

# Sidebar for scenario management
with st.sidebar:
    st.header("💾 Scenarios")
    
    # Initialize saved scenarios in session state
    if 'saved_scenarios' not in st.session_state:
        st.session_state.saved_scenarios = {}
    
    # Scenario name input
    scenario_name = st.text_input(
        "Scenario Name:",
        value=st.session_state.get('current_scenario_name', ''),
        placeholder="e.g., Base Case, Early Retirement, etc.",
        help="Give this scenario a memorable name"
    )
    
    # Save scenario button
    if st.button("💾 Save Scenario", use_container_width=True, disabled=not scenario_name, help="Save scenario to memory"):
        if 'inputs' in st.session_state and scenario_name:
            from datetime import datetime
            download_data = st.session_state.inputs.copy()
            download_data['scenario_name'] = scenario_name
            download_data['last_saved'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to memory
            st.session_state.saved_scenarios[scenario_name] = download_data.copy()
            st.session_state.current_scenario_name = scenario_name
            st.success(f"✅ Saved '{scenario_name}'")
    
    if not scenario_name:
        st.caption("⚠️ Enter a scenario name")
    
    # Download scenario button (separate from save)
    if 'inputs' in st.session_state and scenario_name:
        from datetime import datetime
        download_data = st.session_state.inputs.copy()
        download_data['scenario_name'] = scenario_name
        download_data['last_saved'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        scenario_json = json.dumps(download_data, indent=2)
        
        # Use scenario name for filename (no timestamp - allows overwrite)
        safe_filename = scenario_name.replace(' ', '_').replace('/', '-').replace('\\', '-')
        download_filename = f"{safe_filename}.json"
        
        # Download button
        st.download_button(
            "⬇️ Download Scenario",
            data=scenario_json,
            file_name=download_filename,
            mime="application/json",
            use_container_width=True,
            help="Download scenario file to your computer"
        )
    
    # Show saved scenarios
    if st.session_state.saved_scenarios:
        st.markdown("---")
        st.caption(f"**Saved Scenarios ({len(st.session_state.saved_scenarios)}):**")
        
        # List saved scenarios with load/delete buttons
        for name in list(st.session_state.saved_scenarios.keys()):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.caption(f"📋 {name}")
            with col2:
                if st.button("📂", key=f"load_{name}", help="Load", use_container_width=True):
                    loaded_scenario = st.session_state.saved_scenarios[name]
                    
                    # Set defaults for any missing fields
                    loaded_scenario.setdefault('reduction_1_enabled', True)
                    loaded_scenario.setdefault('reduction_2_enabled', True)
                    loaded_scenario.setdefault('age_77_threshold', 77)
                    loaded_scenario.setdefault('age_83_threshold', 83)
                    loaded_scenario.setdefault('age_77_reduction', 10)
                    loaded_scenario.setdefault('age_83_reduction', 10)
                    loaded_scenario.setdefault('lump_sums', [])
                    loaded_scenario.setdefault('lump_sum_withdrawals', [])
                    loaded_scenario.setdefault('inflation_adjustment_enabled', True)
                    loaded_scenario.setdefault('pension_inflation_adjusted', True)
                    loaded_scenario.setdefault('private_pension_inflation_adjusted', True)
                    
                    # Store loaded scenario
                    st.session_state.loaded_scenario = loaded_scenario
                    st.session_state.scenario_loaded = True
                    st.session_state.current_loaded_file = name
                    st.session_state.current_scenario_name = name
                    
                    # Set widget values
                    st.session_state['monthly_inv'] = loaded_scenario.get('monthly_investments', 0)
                    st.session_state['gov_start'] = loaded_scenario.get('pension_start_age', 65)
                    st.session_state['gov_amt'] = loaded_scenario.get('monthly_pension', 0)
                    st.session_state['gov_idx'] = loaded_scenario.get('pension_inflation_adjusted', True)
                    st.session_state['priv_start'] = loaded_scenario.get('private_pension_start_age', 65)
                    st.session_state['priv_amt'] = loaded_scenario.get('monthly_private_pension', 0)
                    st.session_state['priv_idx'] = loaded_scenario.get('private_pension_inflation_adjusted', True)
                    st.session_state['pt_income'] = loaded_scenario.get('part_time_income', 0)
                    st.session_state['pt_idx'] = loaded_scenario.get('part_time_inflation_adjusted', False)
                    st.session_state['reduction_1_enabled'] = loaded_scenario.get('reduction_1_enabled', True)
                    st.session_state['age_reduction_1_age'] = loaded_scenario.get('age_77_threshold', 77)
                    st.session_state['age_reduction_1_pct'] = loaded_scenario.get('age_77_reduction', 10)
                    st.session_state['reduction_2_enabled'] = loaded_scenario.get('reduction_2_enabled', True)
                    st.session_state['age_reduction_2_age'] = loaded_scenario.get('age_83_threshold', 83)
                    st.session_state['age_reduction_2_pct'] = loaded_scenario.get('age_83_reduction', 10)
                    
                    # Reload lump sums
                    st.session_state.lump_sums = loaded_scenario.get('lump_sums', [])
                    st.session_state.lump_sum_withdrawals = loaded_scenario.get('lump_sum_withdrawals', [])
                    st.session_state['num_deposits'] = len(st.session_state.lump_sums)
                    st.session_state['num_withdrawals'] = len(st.session_state.lump_sum_withdrawals)
                    
                    # Clear dynamic keys
                    keys_to_clear = [k for k in list(st.session_state.keys()) 
                                    if k.startswith('lump_age_') or k.startswith('lump_amount_') 
                                    or k.startswith('lump_withdrawal_age_') or k.startswith('lump_withdrawal_amount_')]
                    for key in keys_to_clear:
                        del st.session_state[key]
                    
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{name}", help="Delete", use_container_width=True):
                    del st.session_state.saved_scenarios[name]
                    if st.session_state.get('current_scenario_name') == name:
                        st.session_state.current_scenario_name = ''
                    st.rerun()
    
    st.markdown("---")
    
    # Upload multiple scenarios
    uploaded_files = st.file_uploader(
        "📂 Upload Scenarios",
        type=['json'],
        accept_multiple_files=True,
        help="Upload one or more scenario JSON files"
    )
    
    if uploaded_files:
        # Check if we've already processed these files
        uploaded_file_names = [f.name for f in uploaded_files]
        if 'last_uploaded_files' not in st.session_state or st.session_state.last_uploaded_files != uploaded_file_names:
            st.session_state.last_uploaded_files = uploaded_file_names
            
            first_scenario_name = None
            for uploaded_file in uploaded_files:
                try:
                    loaded_scenario = json.loads(uploaded_file.getvalue().decode('utf-8'))
                    
                    # Get scenario name from file or filename
                    scenario_name_from_file = loaded_scenario.get('scenario_name', uploaded_file.name.replace('.json', ''))
                    
                    # Set defaults
                    loaded_scenario.setdefault('reduction_1_enabled', True)
                    loaded_scenario.setdefault('reduction_2_enabled', True)
                    loaded_scenario.setdefault('age_77_threshold', 77)
                    loaded_scenario.setdefault('age_83_threshold', 83)
                    loaded_scenario.setdefault('age_77_reduction', 10)
                    loaded_scenario.setdefault('age_83_reduction', 10)
                    loaded_scenario.setdefault('lump_sums', [])
                    loaded_scenario.setdefault('lump_sum_withdrawals', [])
                    loaded_scenario.setdefault('inflation_adjustment_enabled', True)
                    loaded_scenario.setdefault('pension_inflation_adjusted', True)
                    loaded_scenario.setdefault('private_pension_inflation_adjusted', True)
                    loaded_scenario.setdefault('part_time_inflation_adjusted', False)
                    loaded_scenario['scenario_name'] = scenario_name_from_file
                    
                    # Add to saved scenarios
                    st.session_state.saved_scenarios[scenario_name_from_file] = loaded_scenario
                    
                    # Remember first scenario name
                    if first_scenario_name is None:
                        first_scenario_name = scenario_name_from_file
                    
                except Exception as e:
                    st.error(f"❌ Error loading {uploaded_file.name}: {str(e)}")
            
            st.success(f"✅ Uploaded {len(uploaded_files)} scenario(s)")
            
            # Auto-load the first uploaded scenario
            if first_scenario_name and first_scenario_name in st.session_state.saved_scenarios:
                loaded_scenario = st.session_state.saved_scenarios[first_scenario_name]
                
                # Store loaded scenario
                st.session_state.loaded_scenario = loaded_scenario
                st.session_state.scenario_loaded = True
                st.session_state.current_loaded_file = first_scenario_name
                st.session_state.current_scenario_name = first_scenario_name
                
                # Set widget values
                st.session_state['monthly_inv'] = loaded_scenario.get('monthly_investments', 0)
                st.session_state['gov_start'] = loaded_scenario.get('pension_start_age', 65)
                st.session_state['gov_amt'] = loaded_scenario.get('monthly_pension', 0)
                st.session_state['gov_idx'] = loaded_scenario.get('pension_inflation_adjusted', True)
                st.session_state['priv_start'] = loaded_scenario.get('private_pension_start_age', 65)
                st.session_state['priv_amt'] = loaded_scenario.get('monthly_private_pension', 0)
                st.session_state['priv_idx'] = loaded_scenario.get('private_pension_inflation_adjusted', True)
                st.session_state['pt_income'] = loaded_scenario.get('part_time_income', 0)
                st.session_state['pt_idx'] = loaded_scenario.get('part_time_inflation_adjusted', False)
                st.session_state['reduction_1_enabled'] = loaded_scenario.get('reduction_1_enabled', True)
                st.session_state['age_reduction_1_age'] = loaded_scenario.get('age_77_threshold', 77)
                st.session_state['age_reduction_1_pct'] = loaded_scenario.get('age_77_reduction', 10)
                st.session_state['reduction_2_enabled'] = loaded_scenario.get('reduction_2_enabled', True)
                st.session_state['age_reduction_2_age'] = loaded_scenario.get('age_83_threshold', 83)
                st.session_state['age_reduction_2_pct'] = loaded_scenario.get('age_83_reduction', 10)
                
                # Reload lump sums
                st.session_state.lump_sums = loaded_scenario.get('lump_sums', [])
                st.session_state.lump_sum_withdrawals = loaded_scenario.get('lump_sum_withdrawals', [])
                st.session_state['num_deposits'] = len(st.session_state.lump_sums)
                st.session_state['num_withdrawals'] = len(st.session_state.lump_sum_withdrawals)
                
                # Clear dynamic keys
                keys_to_clear = [k for k in list(st.session_state.keys()) 
                                if k.startswith('lump_age_') or k.startswith('lump_amount_') 
                                or k.startswith('lump_withdrawal_age_') or k.startswith('lump_withdrawal_amount_')]
                for key in keys_to_clear:
                    del st.session_state[key]
                
                st.info(f"📂 Auto-loaded: {first_scenario_name}")
            
            st.rerun()
    
    # Calculate all scenarios button
    if st.session_state.saved_scenarios and len(st.session_state.saved_scenarios) >= 2:
        if st.button("⚡ Calculate All Scenarios", use_container_width=True, help="Pre-calculate all scenarios for quick comparison"):
            with st.spinner(f"Calculating {len(st.session_state.saved_scenarios)} scenarios..."):
                if 'calculated_scenarios' not in st.session_state:
                    st.session_state.calculated_scenarios = {}
                
                success_count = 0
                for scenario_name, scenario_inputs in st.session_state.saved_scenarios.items():
                    try:
                        calculator = RetirementCalculator(scenario_inputs)
                        results = calculator.calculate()
                        
                        # Store calculated results
                        st.session_state.calculated_scenarios[scenario_name] = {
                            'inputs': scenario_inputs,
                            'results': results,
                            'projection_df': pd.DataFrame(results['projection'])
                        }
                        success_count += 1
                    except Exception as e:
                        st.error(f"❌ Error calculating {scenario_name}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"✅ Calculated {success_count} scenario(s)")
                    st.info("💡 Go to 'Scenario Comparison' page to view results")
    
    
    # Download all scenarios as ZIP
    if st.session_state.saved_scenarios:
        if st.button("📦 Download All (ZIP)", use_container_width=True, help="Download all saved scenarios as a ZIP file"):
            import io
            import zipfile
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for name, scenario_data in st.session_state.saved_scenarios.items():
                    safe_filename = name.replace(' ', '_').replace('/', '-').replace('\\', '-')
                    json_str = json.dumps(scenario_data, indent=2)
                    zip_file.writestr(f"{safe_filename}.json", json_str)
            
            zip_buffer.seek(0)
            st.download_button(
                "💾 Save ZIP",
                data=zip_buffer.getvalue(),
                file_name="retirement_scenarios.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    # Clear form button
    if st.button("🔄 Clear Form", use_container_width=True, help="Reset all inputs"):
        st.session_state.loaded_scenario = None
        st.session_state.scenario_loaded = False
        st.session_state.current_loaded_file = None
        st.session_state.current_scenario_name = ''
        
        # Clear all widget keys
        widget_keys = [
            'monthly_inv', 'gov_start', 'gov_amt', 'gov_idx', 
            'priv_start', 'priv_amt', 'priv_idx', 'pt_income', 'pt_idx',
            'reduction_1_enabled', 'age_reduction_1_age', 'age_reduction_1_pct',
            'reduction_2_enabled', 'age_reduction_2_age', 'age_reduction_2_pct',
            'num_deposits', 'num_withdrawals'
        ]
        for key in widget_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear lump sums
        if 'lump_sums' in st.session_state:
            del st.session_state.lump_sums
        if 'lump_sum_withdrawals' in st.session_state:
            del st.session_state.lump_sum_withdrawals
        
        # Clear all dynamic lump sum keys
        keys_to_clear = [k for k in st.session_state.keys() 
                        if k.startswith('lump_age_') or k.startswith('lump_amount_') 
                        or k.startswith('lump_withdrawal_age_') or k.startswith('lump_withdrawal_amount_')]
        for key in keys_to_clear:
            del st.session_state[key]
        
        st.success("✅ Cleared")
        st.rerun()
    
    # Status indicator
    if st.session_state.get('current_scenario_name'):
        st.caption(f"📋 Current: {st.session_state.current_scenario_name}")

# Main input form
st.header("Input Parameters")

# Helper function to get default value
def get_default(key, default_value):
    if st.session_state.loaded_scenario:
        return st.session_state.loaded_scenario.get(key, default_value)
    return default_value

# Helper function to calculate age from birthdate
def calculate_age(birthdate):
    from datetime import datetime
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Use tabs for better organization on all screen sizes
tab1, tab2, tab3, tab4 = st.tabs(["1. 👤 Personal & Basic", "2. 💰 Investments", "3. 🏛️ Pensions & Income", "4. 📉 Spending Adjustments"])

with tab1:
    st.markdown("### Personal Information")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        birthdate_str = get_default('birthdate', None)
        if birthdate_str:
            birthdate = st.date_input("Birthdate", datetime.strptime(birthdate_str, '%Y-%m-%d'), 
                                       min_value=datetime(1900, 1, 1), 
                                       max_value=datetime.today())
        else:
            birthdate = st.date_input("Birthdate", value=None, 
                                       min_value=datetime(1900, 1, 1), 
                                       max_value=datetime.today())
    
    with col2:
        if birthdate:
            current_age = calculate_age(birthdate)
            st.number_input("Current Age", 18, 100, current_age, disabled=True, help="Auto-calculated from birthdate")
        else:
            st.number_input("Current Age", 18, 100, value=None, disabled=True, help="Enter birthdate first")
            current_age = 65  # Default fallback
            st.caption("⚠️ Enter birthdate to calculate age")
    
    with col3:
        retirement_age = st.number_input("Retirement Age", 50, 100, get_default('retirement_age', 65))
    
    with col4:
        retirement_year_one_income = st.number_input("Required Monthly Income (Today's $)", 0, 500000, get_default('retirement_year_one_income', 0), step=100, help="Monthly income needed in today's dollars")
        inflation_adjustment_enabled = st.checkbox("Adjust Required Income for Inflation", get_default('inflation_adjustment_enabled', True), help="Increase required income each year with inflation")
    
    st.markdown("### Financial Assumptions")
    col1, col2 = st.columns(2)
    
    with col1:
        yearly_inflation = st.number_input("Annual Inflation Rate (%)", 0.0, 10.0, get_default('yearly_inflation', 2.1), step=0.1)
    
    with col2:
        investment_return = st.number_input("Expected Investment Return (%)", 0.0, 20.0, get_default('investment_return', 6.5), step=0.1)

with tab2:
    st.markdown("### Current Investment Balances")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tfsa = st.number_input("TFSA Balance ($)", 0, 10000000, get_default('tfsa', 0), step=1000)
    
    with col2:
        rrsp = st.number_input("RRSP Balance ($)", 0, 10000000, get_default('rrsp', 0), step=1000)
    
    with col3:
        non_registered = st.number_input("Non-Registered ($)", 0, 10000000, get_default('non_registered', 0), step=1000)
    
    with col4:
        lira = st.number_input("LIRA Balance ($)", 0, 10000000, get_default('lira', 0), step=1000)
    
    total_investments = tfsa + rrsp + non_registered + lira
    st.metric("Total Current Investments", f"${total_investments:,.0f}")
    
    st.markdown("### Ongoing Contributions")
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_investments = st.number_input("Monthly Contribution Amount ($)", 0, 50000, step=100, key="monthly_inv", help="Amount you'll contribute each month")
    
    with col2:
        stop_investments_age = st.number_input("Stop Contributions at Age", current_age, retirement_age, get_default('stop_investments_age', retirement_age), help="Age when you'll stop making monthly contributions")

with tab3:
    st.markdown("### Government Pension (CPP/OAS)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pension_start_age = st.number_input("Start Age", 60, 70, key="gov_start", help="Age when government pension starts")
    
    with col2:
        monthly_pension = st.number_input("Monthly Amount ($)", 0, 10000, step=100, key="gov_amt", help="Monthly pension amount at start age")
    
    with col3:
        pension_inflation_adjusted = st.checkbox("Indexed to Inflation", key="gov_idx", value=get_default('pension_inflation_adjusted', True))
    
    st.markdown("### Employer/Private Pension")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        private_pension_start_age = st.number_input("Start Age", 50, 100, key="priv_start", help="Age when employer pension starts")
    
    with col2:
        monthly_private_pension = st.number_input("Monthly Amount ($)", 0, 50000, step=100, key="priv_amt", help="Monthly pension amount at start age")
    
    with col3:
        private_pension_inflation_adjusted = st.checkbox("Indexed to Inflation", key="priv_idx", value=get_default('private_pension_inflation_adjusted', True))
    
    st.markdown("### Part-Time Work & Lump Sums")
    
    # Row: Part-Time + Lump Sums
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            # Title row with checkbox on the right
            title_col, checkbox_col = st.columns([3, 1])
            with title_col:
                st.markdown("**💼 Part-Time Work**")
            with checkbox_col:
                part_time_inflation_adjusted = st.checkbox("Indexed", get_default('part_time_inflation_adjusted', False), key="pt_idx", help="Adjust part-time income for inflation")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                default_part_time_start = get_default('part_time_start_age', retirement_age)
                part_time_start_age = st.number_input("Start Age", retirement_age, 100, default_part_time_start if default_part_time_start >= retirement_age else retirement_age)
            with c2:
                default_part_time_end = get_default('part_time_end_age', retirement_age)
                part_time_end_age = st.number_input("End Age", part_time_start_age, 100, default_part_time_end if default_part_time_end >= part_time_start_age else retirement_age)
            with c3:
                part_time_income = st.number_input("$/Mo", 0, 20000, step=100, key="pt_income", help="Monthly part-time income in today's dollars")
    
    with col2:
        with st.container(border=True):
            st.markdown("**💵 Lump Sums**")
            
            # Add 3 empty columns to match Part-Time Work input row
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("")
            with c2:
                st.markdown("")
            with c3:
                st.markdown("")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.caption("Deposits")
                # Initialize lump_sums from loaded_scenario if available
                if 'lump_sums' not in st.session_state:
                    st.session_state.lump_sums = get_default('lump_sums', [])
                
                num_lump_sums = st.number_input("#", 0, 10, len(st.session_state.lump_sums), key="num_deposits", label_visibility="collapsed")
                
                while len(st.session_state.lump_sums) < num_lump_sums:
                    st.session_state.lump_sums.append({'age': current_age, 'amount': 0})
                while len(st.session_state.lump_sums) > num_lump_sums:
                    st.session_state.lump_sums.pop()
                
                lump_sums = []
                if num_lump_sums > 0:
                    # Show only first item to keep height reasonable
                    display_count = min(num_lump_sums, 1)
                    for i in range(display_count):
                        c_a, c_b = st.columns([1, 2])
                        with c_a:
                            age = st.number_input(f"Age", current_age, 100, 
                                st.session_state.lump_sums[i].get('age', current_age),
                                key=f"lump_age_{i}", label_visibility="collapsed")
                        with c_b:
                            amount = st.number_input(f"$", 0, 10000000,
                                st.session_state.lump_sums[i].get('amount', 0),
                                step=1000, key=f"lump_amount_{i}", label_visibility="collapsed")
                        lump_sums.append({'age': age, 'amount': amount})
                        st.session_state.lump_sums[i] = {'age': age, 'amount': amount}
                    
                    # Handle remaining items without displaying
                    for i in range(display_count, num_lump_sums):
                        lump_sums.append(st.session_state.lump_sums[i])
                    
                    if num_lump_sums > 1:
                        st.caption(f"+ {num_lump_sums - 1} more")
            
            with c2:
                st.caption("Withdrawals")
                # Initialize lump_sum_withdrawals from loaded_scenario if available
                if 'lump_sum_withdrawals' not in st.session_state:
                    st.session_state.lump_sum_withdrawals = get_default('lump_sum_withdrawals', [])
                
                num_lump_withdrawals = st.number_input("#", 0, 10, len(st.session_state.lump_sum_withdrawals), key="num_withdrawals", label_visibility="collapsed")
                
                while len(st.session_state.lump_sum_withdrawals) < num_lump_withdrawals:
                    st.session_state.lump_sum_withdrawals.append({'age': current_age, 'amount': 0})
                while len(st.session_state.lump_sum_withdrawals) > num_lump_withdrawals:
                    st.session_state.lump_sum_withdrawals.pop()
                
                lump_withdrawals = []
                if num_lump_withdrawals > 0:
                    # Show only first item to keep height reasonable
                    display_count = min(num_lump_withdrawals, 1)
                    for i in range(display_count):
                        c_a, c_b = st.columns([1, 2])
                        with c_a:
                            age = st.number_input(f"Age", current_age, 100, 
                                st.session_state.lump_sum_withdrawals[i].get('age', current_age),
                                key=f"lump_withdrawal_age_{i}", label_visibility="collapsed")
                        with c_b:
                            amount = st.number_input(f"$", 0, 10000000,
                                st.session_state.lump_sum_withdrawals[i].get('amount', 0),
                                step=1000, key=f"lump_withdrawal_amount_{i}", label_visibility="collapsed")
                        lump_withdrawals.append({'age': age, 'amount': amount})
                        st.session_state.lump_sum_withdrawals[i] = {'age': age, 'amount': amount}
                    
                    # Handle remaining items without displaying
                    for i in range(display_count, num_lump_withdrawals):
                        lump_withdrawals.append(st.session_state.lump_sum_withdrawals[i])
                    
                    if num_lump_withdrawals > 1:
                        st.caption(f"+ {num_lump_withdrawals - 1} more")

with tab4:
    st.markdown("### Age-Based Spending Reductions")
    st.caption("Reduce your required income at specific ages to reflect lower spending in later retirement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### First Reduction")
        reduction_1_enabled = st.checkbox("Enable First Reduction", key="reduction_1_enabled", value=get_default('reduction_1_enabled', True))
        
        c1, c2 = st.columns(2)
        with c1:
            age_77_threshold = st.number_input("At Age", retirement_age, 100, key="age_reduction_1_age", disabled=not reduction_1_enabled, value=get_default('age_77_threshold', 77))
        with c2:
            age_77_reduction = st.number_input("Reduce By (%)", 0, 100, key="age_reduction_1_pct", disabled=not reduction_1_enabled, value=get_default('age_77_reduction', 10))
    
    with col2:
        st.markdown("#### Second Reduction")
        reduction_2_enabled = st.checkbox("Enable Second Reduction", key="reduction_2_enabled", value=get_default('reduction_2_enabled', True))
        
        c1, c2 = st.columns(2)
        with c1:
            age_83_threshold = st.number_input("At Age", retirement_age, 100, key="age_reduction_2_age", disabled=not reduction_2_enabled, value=get_default('age_83_threshold', 83))
        with c2:
            age_83_reduction = st.number_input("Reduce By (%)", 0, 100, key="age_reduction_2_pct", disabled=not reduction_2_enabled, value=get_default('age_83_reduction', 10))

# Store inputs
inputs = {
    'current_age': current_age,
    'birthdate': birthdate.strftime('%Y-%m-%d') if birthdate else None,
    'retirement_age': retirement_age,
    'tfsa': tfsa,
    'rrsp': rrsp,
    'non_registered': non_registered,
    'lira': lira,
    'total_investments': total_investments,
    'monthly_investments': monthly_investments,
    'investment_return': investment_return,
    'yearly_inflation': yearly_inflation,
    'retirement_year_one_income': retirement_year_one_income,
    'reduction_1_enabled': reduction_1_enabled,
    'age_77_threshold': age_77_threshold,
    'age_77_reduction': age_77_reduction,
    'reduction_2_enabled': reduction_2_enabled,
    'age_83_threshold': age_83_threshold,
    'age_83_reduction': age_83_reduction,
    'pension_start_age': pension_start_age,
    'monthly_pension': monthly_pension,
    'private_pension_start_age': private_pension_start_age,
    'monthly_private_pension': monthly_private_pension,
    'private_pension_inflation_adjusted': private_pension_inflation_adjusted,
    'part_time_income': part_time_income,
    'part_time_start_age': part_time_start_age,
    'part_time_end_age': part_time_end_age,
    'part_time_inflation_adjusted': part_time_inflation_adjusted,
    'stop_investments_age': stop_investments_age,
    'pension_inflation_adjusted': pension_inflation_adjusted,
    'inflation_adjustment_enabled': inflation_adjustment_enabled,
    'lump_sums': st.session_state.get('lump_sums', []),
    'lump_sum_withdrawals': st.session_state.get('lump_sum_withdrawals', [])
}
st.session_state.inputs = inputs

# Calculate button with better styling
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    calculate_button = st.button("📊 Calculate", type="primary", use_container_width=True)

if calculate_button:
    calculator = RetirementCalculator(inputs)
    results = calculator.calculate()
    
    st.session_state.results = results
    st.session_state.inputs = inputs  # Save inputs too

# Display results if they exist in session state
if 'results' in st.session_state and st.session_state.results:
    results = st.session_state.results
    inputs = st.session_state.inputs  # Restore inputs
    
    # Display results
    st.header("Retirement Projection")
    
    # Summary metrics - single row
    df = pd.DataFrame(results['projection'])
    
    # Get balance at retirement (first retirement year)
    retirement_row = df[df['Age'] == retirement_age]
    balance_at_retirement = retirement_row['Investment Balance Start'].iloc[0] if not retirement_row.empty else 0
    
    # Get balance at age 95
    age_95_row = df[df['Age'] == 95]
    balance_at_95 = age_95_row['Investment Balance End'].iloc[0] if not age_95_row.empty else 0
    
    # Check if there are any monthly shortfalls
    has_shortfall = (df['Monthly Shortfall'] > 0).any() if 'Monthly Shortfall' in df.columns else False
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Years Until Retirement", retirement_age - current_age)
    with col2:
        st.metric("Retirement Age", retirement_age)
    with col3:
        st.metric("Balance at Retirement", f"${balance_at_retirement:,.0f}")
    with col4:
        st.metric("Balance at Age 95", f"${balance_at_95:,.0f}")
    with col5:
        st.metric("Balance at Age 100", f"${results['final_balance']:,.0f}")
    with col6:
        st.metric("Any Monthly Shortfall?", "Yes" if has_shortfall else "No")
    
    # Projection table
    st.subheader("Year-by-Year Projection")
    df = pd.DataFrame(results['projection'])
    
    # Explicitly set column order
    column_order = [
        'Age',
        'Investment Balance Start',
        'Investment Balance End',
        'Income (Today\'s $)',
        'Total Monthly Income',
        'Required Income',
        'Monthly Shortfall',
        'Monthly Investment',
        'Investment Withdrawal',
        'Yearly Investment Return',
        'Monthly Pension',
        'Yearly Pension Amount',
        'Part-Time Income',
        'Lump Sum',
        'Lump Sum Withdrawal',
        '4% Rule Amount',
        'Withdrawal vs 4% Rule',
        '% Over 4% Rule'
    ]
    
    # Reorder columns to match desired order
    df = df[[col for col in column_order if col in df.columns]]
    
    # Format currency columns
    currency_cols = ['Investment Balance Start', 'Monthly Investment', 'Investment Withdrawal', 
                     'Monthly Pension', 'Part-Time Income', 'Lump Sum', 'Lump Sum Withdrawal', 
                     'Required Income', 'Total Monthly Income', 'Monthly Shortfall', 'Income (Today\'s $)',
                     'Yearly Investment Return', 'Yearly Pension Amount', 'Investment Balance End',
                     '4% Rule Amount', 'Withdrawal vs 4% Rule']
    
    df_display = df.copy()
    for col in currency_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")
    
    # Format percentage column
    if '% Over 4% Rule' in df_display.columns:
        df_display['% Over 4% Rule'] = df_display['% Over 4% Rule'].apply(
            lambda x: f"{x:,.1f}%" if x != 0 else "-"
        )
    
    # Add styling to highlight rows where withdrawal exceeds 4% rule or has shortfall
    def highlight_issues(row):
        styles = [''] * len(row)
        
        has_shortfall = False
        has_4pct_violation = False
        
        # Check for shortfall (darker red - more critical)
        if 'Monthly Shortfall' in row.index:
            try:
                shortfall_str = str(row['Monthly Shortfall']).replace('$', '').replace(',', '')
                shortfall_val = float(shortfall_str)
                if shortfall_val > 0:
                    has_shortfall = True
            except (ValueError, AttributeError):
                pass
        
        # Check for 4% rule violation (light yellow)
        if row['Age'] >= retirement_age and row['Investment Withdrawal'] != '$0.00':
            try:
                withdrawal_str = str(row['Withdrawal vs 4% Rule']).replace('$', '').replace(',', '')
                withdrawal_vs_rule = float(withdrawal_str)
                if withdrawal_vs_rule > 0:
                    has_4pct_violation = True
            except (ValueError, AttributeError):
                pass
        
        # Apply colors based on conditions
        if has_shortfall and has_4pct_violation:
            return ['background-color: #ffcc99'] * len(row)  # Orange for both issues
        elif has_shortfall:
            return ['background-color: #ffcccc'] * len(row)  # Red for shortfall only
        elif has_4pct_violation:
            return ['background-color: #ffffcc'] * len(row)  # Yellow for 4% rule only
        
        return styles
    
    styled_df = df_display.style.apply(highlight_issues, axis=1)
    
    # Custom CSS to make table wider and extend closer to window edges
    st.markdown("""
        <style>
        /* Make projections table wider */
        div[data-testid="stDataFrame"] {
            width: 100% !important;
        }
        div[data-testid="stDataFrame"] > div {
            width: 100% !important;
            max-width: 100% !important;
        }
        /* Reduce padding around the dataframe container */
        section[data-testid="stVerticalBlock"] > div:has(div[data-testid="stDataFrame"]) {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        /* Make the block container wider for this section */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Check if there are any highlighted rows and show explanation
    has_shortfall = (df['Monthly Shortfall'] > 0).any() if 'Monthly Shortfall' in df.columns else False
    has_4pct_violation = False
    has_both = False
    
    if 'Withdrawal vs 4% Rule' in df.columns:
        retirement_rows = df[df['Age'] >= retirement_age]
        has_4pct_violation = (retirement_rows['Withdrawal vs 4% Rule'] > 0).any()
        
        # Check if any rows have both conditions
        if has_shortfall and has_4pct_violation:
            for _, row in retirement_rows.iterrows():
                if row['Monthly Shortfall'] > 0 and row['Withdrawal vs 4% Rule'] > 0:
                    has_both = True
                    break
    
    # Show highlighting explanation only if there are highlighted rows
    if has_shortfall or has_4pct_violation:
        highlight_messages = []
        if has_both:
            highlight_messages.append("🟠 **Orange rows** = Both shortfall AND over 4% rule (critical)")
        if has_shortfall:
            highlight_messages.append("🔴 **Red rows** = Monthly shortfall exists")
        if has_4pct_violation:
            highlight_messages.append("🟡 **Yellow rows** = Withdrawing more than 4% rule")
        
        st.caption(" | ".join(highlight_messages))
    
    # Add explanation of 4% rule columns
    with st.expander("ℹ️ Understanding the 4% Rule Comparison & Today's Dollars"):
        st.markdown("""
        **What is the 4% Rule?**
        
        The 4% rule is a retirement planning guideline that suggests withdrawing 4% of your portfolio 
        in the first year of retirement, then adjusting that dollar amount for inflation each year. 
        This approach has historically provided a 95% success rate over 30-year retirements.
        
        **Your Comparison Columns:**
        
        - **Total Monthly Income**: Your actual monthly income in future dollars (includes inflation)
        - **Income (Today's $)**: What that income is worth in today's purchasing power
        - **4% Rule Amount**: What you should withdraw per month following the 4% rule
        - **Withdrawal vs 4% Rule**: How much more (positive) or less (negative) you're withdrawing
        - **% Over 4% Rule**: Percentage difference from the safe 4% guideline
        
        **Why "Today's Dollars" Matters:**
        
        Due to inflation, $10,000 in 20 years won't buy as much as $10,000 today. The "Income (Today's $)" 
        column shows your real purchasing power, making it easier to understand if you can maintain your 
        current lifestyle. For example:
        - Age 62: $9,000/month might be $7,000 in today's dollars
        - Age 82: $15,000/month might still be only $7,000 in today's dollars
        
        This helps you see if your retirement income keeps pace with your current standard of living.
        
        **Color Coding:**
        - 🟠 Orange background = Both shortfall AND over 4% rule (most critical - multiple issues)
        - 🔴 Red background = Monthly shortfall exists (you don't have enough income)
        - 🟡 Yellow background = You're withdrawing MORE than the 4% rule (higher risk)
        - White background = You're at or below the 4% rule with no shortfall (safer)
        
        **Why This Matters:**
        
        Withdrawing significantly more than the 4% rule increases your risk of running out of money, 
        especially if markets perform poorly early in retirement. If you see many red rows, consider:
        - Reducing retirement expenses
        - Delaying retirement
        - Working part-time longer
        - Increasing pre-retirement savings
        """)
    
    # Interactive Charts Section
    st.header("📊 Interactive Visualizations")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Balance Projection",
        "💰 Income Sources", 
        "⚖️ 4% Rule Comparison",
        "💵 Purchasing Power",
        "🎯 Dashboard"
    ])
    
    with tab1:
        st.plotly_chart(
            create_balance_projection_chart(df, retirement_age),
            use_container_width=True
        )
        st.caption("Hover over the chart to see detailed values. Zoom and pan to explore different time periods.")
    
    with tab2:
        st.plotly_chart(
            create_income_sources_chart(df, retirement_age),
            use_container_width=True
        )
        st.caption("Shows how your income sources change throughout retirement. Click legend items to show/hide sources.")
    
    with tab3:
        st.plotly_chart(
            create_withdrawal_vs_4pct_chart(df, retirement_age),
            use_container_width=True
        )
        st.caption("Red shaded area shows where you're withdrawing more than the safe 4% rule.")
    
    with tab4:
        st.plotly_chart(
            create_purchasing_power_chart(df, retirement_age),
            use_container_width=True
        )
        st.caption("Compare nominal income (future dollars) vs real income (today's purchasing power).")
    
    with tab5:
        st.plotly_chart(
            create_dashboard_summary(df, inputs, results),
            use_container_width=True
        )
        st.caption("All key metrics in one view. Perfect for presentations or quick reviews.")
    
    # Export options
    st.subheader("Export Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = export_to_csv(df)
        st.download_button(
            "📄 Download CSV",
            csv_data,
            "retirement_plan.csv",
            "text/csv"
        )
    
    with col2:
        excel_data = export_to_excel(df, inputs)
        st.download_button(
            "📊 Download Excel",
            excel_data,
            "retirement_plan.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col3:
        pdf_data = export_to_pdf(df, inputs, results)
        st.download_button(
            "📑 Download PDF",
            pdf_data,
            "retirement_plan.pdf",
            "application/pdf"
        )
    
    # Investment advice
    if results.get('advice'):
        st.header("💡 Comprehensive Investment Advice")
        
        # Add Monte Carlo context if available
        if 'mc_results' in st.session_state and st.session_state.mc_results:
            mc_results = st.session_state.mc_results
            advice_with_mc = results['advice'] + "\n\n" + generate_monte_carlo_advice(mc_results, inputs, results)
            st.markdown(advice_with_mc)
        else:
            st.markdown(results['advice'])
            st.info("💡 **Tip:** Run the Monte Carlo simulation below for additional risk-based recommendations.")
    
    # Monte Carlo Simulation Section
    st.header("🎲 Monte Carlo Stress Test")
    st.markdown("""
    **Important:** Your baseline projection above assumes constant returns every year. 
    Real markets are volatile - use Monte Carlo to test your plan against realistic market conditions.
    
    Monte Carlo tests 10,000 scenarios with variable returns (averaging your expected return) to assess:
    - **Market volatility** (variable returns each year)
    - **Sequence of returns risk** (market crashes early in retirement)
    - **Historical market patterns** (18% standard deviation)
    
    💡 Your baseline might show $2.5M at age 100, but Monte Carlo might show only 35% success - this is normal!
    The baseline assumes perfect constant returns (unrealistic), while Monte Carlo uses realistic variable returns.
    """)
    
    if st.button("Run Monte Carlo Simulation (10,000 scenarios)", type="secondary"):
        with st.spinner("Running 10,000 simulations... This may take a moment."):
            simulator = MonteCarloSimulator(inputs, num_simulations=10000)
            mc_results = simulator.run_simulation()
            st.session_state.mc_results = mc_results
            st.rerun()
    
    # Display Monte Carlo results if they exist
    if 'mc_results' in st.session_state and st.session_state.mc_results:
        mc_results = st.session_state.mc_results
        simulator = MonteCarloSimulator(inputs, num_simulations=10000)
        
        # Display Monte Carlo results
        success_rate = mc_results['success_rate']
        rating, interpretation = simulator.get_interpretation(success_rate)
        
        # Success rate display
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col2:
            st.metric("Rating", rating)
        with col3:
            st.metric("Successful Scenarios", f"{mc_results['successes']:,} / 10,000")
        
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
            st.plotly_chart(
                create_failure_age_histogram(mc_results),
                use_container_width=True
            )
        
        # Balance percentiles chart
        st.subheader("Balance Projections Across Scenarios")
        st.markdown("Shows how your balance might evolve across different market conditions:")
        
        st.plotly_chart(
            create_monte_carlo_percentile_chart(mc_results, retirement_age),
            use_container_width=True
        )
        
        # Key insights
        st.subheader("Key Insights")
        st.markdown(f"""
        - **Median final balance:** ${mc_results['median_final_balance']:,.0f}
        - **Best case scenario:** ${mc_results['best_case_balance']:,.0f}
        - **Worst case scenario:** ${mc_results['worst_case_balance']:,.0f}
        - **Sequence of returns risk:** {'High' if success_rate < 80 else 'Moderate' if success_rate < 90 else 'Low'}
        
        💡 **Recommendation:** A success rate of 80% or higher is considered robust for retirement planning.
        """)
