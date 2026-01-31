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
        
        /* Unbold all checkbox labels */
        .stCheckbox label {
            font-weight: normal !important;
        }
        .stCheckbox label p {
            font-weight: normal !important;
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
if 'bridged_enabled_p1' not in st.session_state:
    st.session_state['bridged_enabled_p1'] = False
if 'bridged_enabled_p2' not in st.session_state:
    st.session_state['bridged_enabled_p2'] = False

st.title("🇨🇦 Canadian Retirement Planning Calculator")
st.markdown("Plan your retirement with pension, and investment projections")

# Sidebar for scenario management
with st.sidebar:
    # Compact styling
    st.markdown("""
        <style>
        .sidebar .element-container {
            margin-bottom: 0.2rem;
        }
        .sidebar h3 {
            font-size: 0.75rem;
            margin-bottom: 0.3rem;
            margin-top: 0.3rem;
        }
        .sidebar .stButton button {
            padding: 0.15rem 0.3rem;
            font-size: 0.65rem;
            background-color: rgb(255, 255, 255);
            border: 1px solid rgba(49, 51, 63, 0.2);
        }
        .sidebar .stButton button:hover {
            border-color: rgb(255, 75, 75);
            color: rgb(255, 75, 75);
        }
        .sidebar .stCaption {
            font-size: 0.6rem;
        }
        /* Style file uploader */
        .sidebar [data-testid="stFileUploader"] {
            font-size: 0.65rem;
        }
        .sidebar [data-testid="stFileUploader"] section {
            padding: 0.3rem;
            border: 1px dashed rgba(49, 51, 63, 0.2);
            border-radius: 0.25rem;
        }
        .sidebar [data-testid="stFileUploader"] button {
            padding: 0.15rem 0.3rem;
            font-size: 0.65rem;
            background-color: rgb(255, 255, 255);
            border: 1px solid rgba(49, 51, 63, 0.2);
        }
        .sidebar [data-testid="stFileUploader"] button:hover {
            border-color: rgb(255, 75, 75);
            color: rgb(255, 75, 75);
        }
        /* Custom text for drag-drop area */
        .sidebar [data-testid="stFileUploader"] section > div:first-child {
            font-size: 0.6rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Scenario Management")
    
    # Initialize scenarios in session state
    if 'saved_scenarios' not in st.session_state:
        st.session_state.saved_scenarios = {}
    if 'active_scenario_name' not in st.session_state:
        st.session_state.active_scenario_name = None
    
    # Loaded Scenarios Section - moved to top
    scenario_list = list(st.session_state.saved_scenarios.keys())
    
    if scenario_list:
        st.subheader("Loaded Scenarios")
        
        # Dropdown to switch between loaded scenarios
        current_index = scenario_list.index(st.session_state.active_scenario_name) if st.session_state.active_scenario_name in scenario_list else 0
        active_scenario = st.selectbox(
            "Active:",
            options=scenario_list,
            index=current_index,
            key="active_scenario_selector",
            label_visibility="collapsed"
        )
        
        # If selection changed, load that scenario
        if active_scenario != st.session_state.active_scenario_name:
            loaded_scenario = st.session_state.saved_scenarios[active_scenario]
            
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
            st.session_state.active_scenario_name = active_scenario
            st.session_state.current_scenario_name = active_scenario
            
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
        
        st.caption(f"{len(scenario_list)} loaded")
    
    st.markdown("---")
    
    # Quick Actions - vertical buttons
    if st.button("🗑️ Clear", use_container_width=True, help="Clear all"):
        st.session_state.show_clear_dialog = True
    
    if st.button("💾 Save", use_container_width=True, help="Save scenario"):
        st.session_state.show_new_dialog = True
    
    # Load button with file uploader (styled to look like button)
    uploaded = st.file_uploader(
        "Load Scenario",
        type=['json'],
        accept_multiple_files=True,
        key="load_uploader"
    )
    
    if uploaded:
        count = 0
        for file in uploaded:
            try:
                data = json.load(file)
                name = data.get('scenario_name', file.name.replace('.json', ''))
                
                # Set defaults
                data.setdefault('reduction_1_enabled', True)
                data.setdefault('reduction_2_enabled', True)
                data.setdefault('lump_sums', [])
                data.setdefault('lump_sum_withdrawals', [])
                
                st.session_state.saved_scenarios[name] = data
                count += 1
            except Exception as e:
                st.error(f"Error: {file.name}")
        
        if count > 0:
            st.success(f"✅ Loaded {count}")
            st.rerun()
    
    # New Scenario Dialog - one-click save & download
    if st.session_state.get('show_new_dialog', False):
        st.markdown("---")
        new_name = st.text_input("Name:", placeholder="My Scenario", key="new_name_input")
        
        if new_name and new_name not in st.session_state.saved_scenarios:
            from datetime import datetime
            
            # Prepare data
            if 'inputs' in st.session_state:
                data = st.session_state.inputs.copy()
            else:
                data = {
                    'current_age': 30, 'retirement_age': 65, 'tfsa': 0, 'rrsp': 0,
                    'non_registered': 0, 'lira': 0, 'total_investments': 0,
                    'monthly_investments': 0, 'investment_return': 6.0,
                    'yearly_inflation': 2.1, 'retirement_year_one_income': 0,
                    'couple_mode': False, 'oas_start_age': 65, 'monthly_oas': 0,
                    'cpp_start_age': 70, 'monthly_cpp': 0,
                    'private_pension_start_age': 500, 'monthly_private_pension': 0,
                    'part_time_income': 0, 'lump_sums': [], 'lump_sum_withdrawals': []
                }
            
            data['scenario_name'] = new_name
            data['last_saved'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare download
            safe_name = new_name.replace(' ', '_').replace('/', '-').replace('\\', '-')
            json_str = json.dumps(data, indent=2)
            
            col1, col2 = st.columns(2)
            with col1:
                # Download button that also saves to session
                if st.download_button(
                    "💾 Save",
                    data=json_str,
                    file_name=f"{safe_name}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"save_dl_{new_name}"
                ):
                    # Save to session after download initiated
                    st.session_state.saved_scenarios[new_name] = data
                    st.session_state.active_scenario_name = new_name
                    st.session_state.loaded_scenario = data
                    st.session_state.show_new_dialog = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_new_dialog = False
                    st.rerun()
        elif new_name in st.session_state.saved_scenarios:
            st.error("Name exists!")
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_new_dialog = False
                st.rerun()
        else:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_new_dialog = False
                st.rerun()
    

    # Clear All Dialog
    if st.session_state.get('show_clear_dialog', False):
        st.markdown("---")
        st.warning("Clear all scenarios?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", use_container_width=True):
                st.session_state.saved_scenarios = {}
                st.session_state.active_scenario_name = None
                st.session_state.loaded_scenario = None
                st.session_state.show_clear_dialog = False
                st.rerun()
        with col2:
            if st.button("No", use_container_width=True):
                st.session_state.show_clear_dialog = False
                st.rerun()
    
    # Loaded Scenarios List - compact
    if scenario_list:
        st.markdown("---")
        for name in scenario_list:
            col1, col2 = st.columns([6, 1])
            with col1:
                prefix = "🎯" if name == st.session_state.active_scenario_name else "📄"
                st.caption(f"{prefix} {name}")
            with col2:
                if st.button("❌", key=f"del_{name}", help="Delete"):
                    del st.session_state.saved_scenarios[name]
                    if st.session_state.active_scenario_name == name:
                        st.session_state.active_scenario_name = None
                    st.rerun()
        
        # Export All as ZIP
        if len(scenario_list) > 1:
            st.markdown("---")
            if st.button("📦 Export All", use_container_width=True):
                import io
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for name, data in st.session_state.saved_scenarios.items():
                        safe_name = name.replace(' ', '_').replace('/', '-').replace('\\', '-')
                        zf.writestr(f"{safe_name}.json", json.dumps(data, indent=2))
                
                zip_buffer.seek(0)
                st.download_button(
                    "⬇️ Download ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="scenarios.zip",
                    mime="application/zip",
                    use_container_width=True
                )

# Main content continues with input parameters
st.title("🏖️ Retirement Planner")

# Get current scenario name for display
scenario_name = st.session_state.get('active_scenario_name', 'Unsaved Scenario')

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. 👤 Personal & Basic", "2. 💰 Investments", "3. 🏛️ Pensions", "4. 💼 Extra Income & Lump Sums", "5. 📉 Spending Adjustments"])

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
        ignore_oas_clawback = st.checkbox("Income Splitting (Ignore OAS Clawback)", get_default('ignore_oas_clawback', False), help="Enable if using income splitting to avoid OAS clawback")
    
    st.markdown("### Financial Assumptions")
    col1, col2 = st.columns(2)
    
    with col1:
        yearly_inflation = st.number_input("Annual Inflation Rate (%)", 0.0, 10.0, get_default('yearly_inflation', 2.1), step=0.1)
    
    with col2:
        investment_return = st.number_input("Expected Investment Return (%)", 0.0, 20.0, get_default('investment_return', 6.0), step=0.1)
    
    # Calculate button
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col2:
        calculate_button_tab1 = st.button("📊 Calculate", type="primary", use_container_width=True, key="calc_tab1")

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
        # Clamp default value to be within valid range
        default_stop_age = get_default('stop_investments_age', retirement_age)
        # Ensure default is within the valid range [current_age, retirement_age]
        if current_age <= retirement_age:
            default_stop_age = max(current_age, min(default_stop_age, retirement_age))
        else:
            # If current_age > retirement_age, use retirement_age as both min and max
            default_stop_age = retirement_age
        stop_investments_age = st.number_input("Stop Contributions at Age", 
                                              min(current_age, retirement_age), 
                                              max(current_age, retirement_age), 
                                              default_stop_age, 
                                              help="Age when you'll stop making monthly contributions")
    
    # Calculate button
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col2:
        calculate_button_tab2 = st.button("📊 Calculate", type="primary", use_container_width=True, key="calc_tab2")

with tab3:
    # Couple mode toggle at the top
    st.markdown("### Planning Mode")
    couple_mode = st.checkbox("👫 Couple Mode (Separate Pensions)", 
                              value=get_default('couple_mode', False),
                              help="Enable to enter separate pension amounts for each person")
    
    st.markdown("---")
    
    st.markdown("### Old Age Security (OAS)")
    
    if couple_mode:
        # Person 1 OAS
        st.markdown("#### Person 1")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            oas_start_age = st.number_input("Start Age", 65, 70, key="oas_start_p1", 
                                           value=get_default('oas_start_age', 65), 
                                           help="Age when OAS starts (typically 65)")
        
        with col2:
            monthly_oas = st.number_input("Monthly Amount (Today's $)", 0, 5000, step=50, key="oas_amt_p1", 
                                         value=get_default('monthly_oas', 0), 
                                         help="Monthly OAS amount in today's dollars")
        
        with col3:
            oas_inflation_adjusted = st.checkbox("Indexed to Inflation", key="oas_idx_p1", 
                                                value=get_default('oas_inflation_adjusted', True))
        
        # Person 2 OAS
        st.markdown("#### Person 2")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            oas_start_age_p2 = st.number_input("Start Age", 65, 70, key="oas_start_p2", 
                                              value=min(get_default('oas_start_age_p2', 65), 70), 
                                              help="Age when OAS starts (typically 65)")
        
        with col2:
            monthly_oas_p2 = st.number_input("Monthly Amount (Today's $)", 0, 5000, step=50, key="oas_amt_p2", 
                                            value=get_default('monthly_oas_p2', 0), 
                                            help="Monthly OAS amount in today's dollars")
        
        with col3:
            oas_inflation_adjusted_p2 = st.checkbox("Indexed to Inflation", key="oas_idx_p2", 
                                                   value=get_default('oas_inflation_adjusted_p2', True))
    else:
        # Single person OAS
        col1, col2, col3 = st.columns(3)
        
        with col1:
            oas_start_age = st.number_input("Start Age", 65, 70, key="oas_start", 
                                           value=get_default('oas_start_age', 65), 
                                           help="Age when OAS starts (typically 65)")
        
        with col2:
            monthly_oas = st.number_input("Monthly Amount (Today's $)", 0, 5000, step=50, key="oas_amt", 
                                         value=get_default('monthly_oas', 0), 
                                         help="Monthly OAS amount in today's dollars")
        
        with col3:
            oas_inflation_adjusted = st.checkbox("Indexed to Inflation", key="oas_idx", 
                                                value=get_default('oas_inflation_adjusted', True))
        
        # Set Person 2 values to 0 for single mode
        oas_start_age_p2 = 999
        monthly_oas_p2 = 0
        oas_inflation_adjusted_p2 = True
    
    st.markdown("### Canada Pension Plan (CPP)")
    
    if couple_mode:
        # Person 1 CPP
        st.markdown("#### Person 1")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpp_start_age = st.number_input("Start Age", 60, 70, key="cpp_start_p1", 
                                           value=get_default('cpp_start_age', 70), 
                                           help="Age when CPP starts (60-70)")
        
        with col2:
            monthly_cpp = st.number_input("Monthly Amount (Today's $)", 0, 10000, step=50, key="cpp_amt_p1", 
                                         value=get_default('monthly_cpp', 0), 
                                         help="Monthly CPP amount in today's dollars")
        
        with col3:
            cpp_inflation_adjusted = st.checkbox("Indexed to Inflation", key="cpp_idx_p1", 
                                                value=get_default('cpp_inflation_adjusted', True))
        
        # Person 2 CPP
        st.markdown("#### Person 2")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpp_start_age_p2 = st.number_input("Start Age", 60, 70, key="cpp_start_p2", 
                                              value=min(get_default('cpp_start_age_p2', 70), 70), 
                                              help="Age when CPP starts (60-70)")
        
        with col2:
            monthly_cpp_p2 = st.number_input("Monthly Amount (Today's $)", 0, 10000, step=50, key="cpp_amt_p2", 
                                            value=get_default('monthly_cpp_p2', 0), 
                                            help="Monthly CPP amount in today's dollars")
        
        with col3:
            cpp_inflation_adjusted_p2 = st.checkbox("Indexed to Inflation", key="cpp_idx_p2", 
                                                   value=get_default('cpp_inflation_adjusted_p2', True))
    else:
        # Single person CPP
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpp_start_age = st.number_input("Start Age", 60, 70, key="cpp_start", 
                                           value=get_default('cpp_start_age', 70), 
                                           help="Age when CPP starts (60-70)")
        
        with col2:
            monthly_cpp = st.number_input("Monthly Amount (Today's $)", 0, 10000, step=50, key="cpp_amt", 
                                         value=get_default('monthly_cpp', 0), 
                                         help="Monthly CPP amount in today's dollars")
        
        with col3:
            cpp_inflation_adjusted = st.checkbox("Indexed to Inflation", key="cpp_idx", 
                                                value=get_default('cpp_inflation_adjusted', True))
        
        # Set Person 2 values to 0 for single mode
        cpp_start_age_p2 = 999
        monthly_cpp_p2 = 0
        cpp_inflation_adjusted_p2 = True
    
    st.markdown("### Employer/Private Pension")
    
    if couple_mode:
        # Person 1 Employer Pension
        col_title, col_checkbox = st.columns([3, 1])
        with col_title:
            st.markdown("#### Person 1")
        with col_checkbox:
            bridged_enabled_p1 = st.checkbox("Add Bridge", key="bridged_p1", 
                                            value=get_default('bridged_enabled_p1', False),
                                            help="Enable if pension has a bridged amount until CPP/OAS starts")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            private_pension_start_age = st.number_input("Start Age", 50, 100, key="priv_start_p1", 
                                                       value=min(get_default('private_pension_start_age', 500), 100),
                                                       help="Age when employer pension starts")
        
        with col2:
            monthly_private_pension = st.number_input("Monthly Amount (Today's $)", 0, 50000, step=100, key="priv_amt_p1", 
                                                     value=get_default('monthly_private_pension', 0),
                                                     help="Monthly pension amount in today's dollars")
        
        with col3:
            private_pension_inflation_adjusted = st.checkbox("Indexed to Inflation", key="priv_idx_p1", 
                                                            value=get_default('private_pension_inflation_adjusted', True))
        
        # Bridged amount fields on same row for Person 1
        if bridged_enabled_p1:
            col1, col2, col3 = st.columns(3)
            with col1:
                bridged_start_age_p1 = st.number_input("Bridge Start Age", 50, 100, key="bridged_start_p1",
                                                       value=get_default('bridged_start_age_p1', private_pension_start_age),
                                                       help="Age when bridged amount starts")
            with col2:
                # Fix: Ensure default value is within valid range
                default_end_age = get_default('bridged_end_age_p1', 65)
                default_end_age = max(bridged_start_age_p1, min(default_end_age, 100))
                bridged_end_age_p1 = st.number_input("Bridge End Age", bridged_start_age_p1, 100, key="bridged_end_p1",
                                                     value=default_end_age,
                                                     help="Age when bridged amount ends (typically when CPP/OAS starts)")
            with col3:
                bridged_amount_p1 = st.number_input("Bridge Monthly Amount (Today's $)", 0, 50000, step=100, key="bridged_amt_p1",
                                                    value=get_default('bridged_amount_p1', 0),
                                                    help="Additional monthly amount during bridge period")
        else:
            bridged_start_age_p1 = 999
            bridged_end_age_p1 = 999
            bridged_amount_p1 = 0
        
        # Person 2 Employer Pension
        col_title, col_checkbox = st.columns([3, 1])
        with col_title:
            st.markdown("#### Person 2")
        with col_checkbox:
            bridged_enabled_p2 = st.checkbox("Add Bridge", key="bridged_p2", 
                                            value=get_default('bridged_enabled_p2', False),
                                            help="Enable if pension has a bridged amount until CPP/OAS starts")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            private_pension_start_age_p2 = st.number_input("Start Age", 50, 100, key="priv_start_p2", 
                                                          value=min(get_default('private_pension_start_age_p2', 500), 100),
                                                          help="Age when employer pension starts")
        
        with col2:
            monthly_private_pension_p2 = st.number_input("Monthly Amount (Today's $)", 0, 50000, step=100, key="priv_amt_p2", 
                                                        value=get_default('monthly_private_pension_p2', 0),
                                                        help="Monthly pension amount in today's dollars")
        
        with col3:
            private_pension_inflation_adjusted_p2 = st.checkbox("Indexed to Inflation", key="priv_idx_p2", 
                                                               value=get_default('private_pension_inflation_adjusted_p2', True))
        
        # Bridged amount fields on same row for Person 2
        if bridged_enabled_p2:
            col1, col2, col3 = st.columns(3)
            with col1:
                bridged_start_age_p2 = st.number_input("Bridge Start Age", 50, 100, key="bridged_start_p2",
                                                       value=get_default('bridged_start_age_p2', private_pension_start_age_p2),
                                                       help="Age when bridged amount starts")
            with col2:
                # Fix: Ensure default value is within valid range
                default_end_age = get_default('bridged_end_age_p2', 65)
                default_end_age = max(bridged_start_age_p2, min(default_end_age, 100))
                bridged_end_age_p2 = st.number_input("Bridge End Age", bridged_start_age_p2, 100, key="bridged_end_p2",
                                                     value=default_end_age,
                                                     help="Age when bridged amount ends (typically when CPP/OAS starts)")
            with col3:
                bridged_amount_p2 = st.number_input("Bridge Monthly Amount (Today's $)", 0, 50000, step=100, key="bridged_amt_p2",
                                                    value=get_default('bridged_amount_p2', 0),
                                                    help="Additional monthly amount during bridge period")
        else:
            bridged_start_age_p2 = 999
            bridged_end_age_p2 = 999
            bridged_amount_p2 = 0
    else:
        # Single person Employer Pension
        col_title, col_checkbox = st.columns([3, 1])
        with col_title:
            st.markdown("### Employer/Private Pension")
        with col_checkbox:
            bridged_enabled_p1 = st.checkbox("Add Bridge", key="bridged_single", 
                                            value=get_default('bridged_enabled_p1', False),
                                            help="Enable if pension has a bridged amount until CPP/OAS starts")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            private_pension_start_age = st.number_input("Start Age", 50, 100, key="priv_start", 
                                                       value=min(get_default('private_pension_start_age', 500), 100),
                                                       help="Age when employer pension starts")
        
        with col2:
            monthly_private_pension = st.number_input("Monthly Amount (Today's $)", 0, 50000, step=100, key="priv_amt", 
                                                     value=get_default('monthly_private_pension', 0),
                                                     help="Monthly pension amount in today's dollars")
        
        with col3:
            private_pension_inflation_adjusted = st.checkbox("Indexed to Inflation", key="priv_idx", 
                                                            value=get_default('private_pension_inflation_adjusted', True))
        
        # Bridged amount fields on same row for single person
        if bridged_enabled_p1:
            col1, col2, col3 = st.columns(3)
            with col1:
                bridged_start_age_p1 = st.number_input("Bridge Start Age", 50, 100, key="bridged_start_single",
                                                       value=get_default('bridged_start_age_p1', private_pension_start_age),
                                                       help="Age when bridged amount starts")
            with col2:
                # Fix: Ensure default value is within valid range
                default_end_age = get_default('bridged_end_age_p1', 65)
                default_end_age = max(bridged_start_age_p1, min(default_end_age, 100))
                bridged_end_age_p1 = st.number_input("Bridge End Age", bridged_start_age_p1, 100, key="bridged_end_single",
                                                     value=default_end_age,
                                                     help="Age when bridged amount ends (typically when CPP/OAS starts)")
            with col3:
                bridged_amount_p1 = st.number_input("Bridge Monthly Amount (Today's $)", 0, 50000, step=100, key="bridged_amt_single",
                                                    value=get_default('bridged_amount_p1', 0),
                                                    help="Additional monthly amount during bridge period")
        else:
            bridged_start_age_p1 = 999
            bridged_end_age_p1 = 999
            bridged_amount_p1 = 0
        
        # Set Person 2 values to 0 for single mode
        private_pension_start_age_p2 = 999
        monthly_private_pension_p2 = 0
        private_pension_inflation_adjusted_p2 = True
        bridged_enabled_p2 = False
        bridged_start_age_p2 = 999
        bridged_end_age_p2 = 999
        bridged_amount_p2 = 0
    
    # Calculate button
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col2:
        calculate_button_tab3 = st.button("📊 Calculate", type="primary", use_container_width=True, key="calc_tab3")

with tab4:
    st.markdown("### Part-Time Work")
    
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
            default_part_time_end = get_default('part_time_end_age', retirement_age - 1)
            part_time_end_age = st.number_input("End Age", part_time_start_age, 100, default_part_time_end if default_part_time_end >= part_time_start_age else retirement_age)
        with c3:
            part_time_income = st.number_input("$/Mo", 0, 20000, step=100, key="pt_income", help="Monthly part-time income in today's dollars")
    
    st.markdown("### Lump Sums")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**💵 Deposits**")
            
            # Initialize lump_sums from loaded_scenario if available
            if 'lump_sums' not in st.session_state:
                st.session_state.lump_sums = get_default('lump_sums', [])
            
            num_lump_sums = st.number_input("Number of Deposits", 0, 10, len(st.session_state.lump_sums), key="num_deposits")
            
            while len(st.session_state.lump_sums) < num_lump_sums:
                st.session_state.lump_sums.append({'age': current_age, 'amount': 0})
            while len(st.session_state.lump_sums) > num_lump_sums:
                st.session_state.lump_sums.pop()
            
            lump_sums = []
            if num_lump_sums > 0:
                for i in range(num_lump_sums):
                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        age = st.number_input(f"Age #{i+1}", current_age, 100, 
                            st.session_state.lump_sums[i].get('age', current_age),
                            key=f"lump_age_{i}")
                    with c_b:
                        amount = st.number_input(f"Amount #{i+1}", 0, 10000000,
                            st.session_state.lump_sums[i].get('amount', 0),
                            step=1000, key=f"lump_amount_{i}")
                    lump_sums.append({'age': age, 'amount': amount})
                    st.session_state.lump_sums[i] = {'age': age, 'amount': amount}
    
    with col2:
        with st.container(border=True):
            st.markdown("**💸 Withdrawals**")
            
            # Initialize lump_sum_withdrawals from loaded_scenario if available
            if 'lump_sum_withdrawals' not in st.session_state:
                st.session_state.lump_sum_withdrawals = get_default('lump_sum_withdrawals', [])
            
            num_lump_withdrawals = st.number_input("Number of Withdrawals", 0, 10, len(st.session_state.lump_sum_withdrawals), key="num_withdrawals")
            
            while len(st.session_state.lump_sum_withdrawals) < num_lump_withdrawals:
                st.session_state.lump_sum_withdrawals.append({'age': current_age, 'amount': 0})
            while len(st.session_state.lump_sum_withdrawals) > num_lump_withdrawals:
                st.session_state.lump_sum_withdrawals.pop()
            
            lump_withdrawals = []
            if num_lump_withdrawals > 0:
                for i in range(num_lump_withdrawals):
                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        age = st.number_input(f"Age #{i+1}", current_age, 100, 
                            st.session_state.lump_sum_withdrawals[i].get('age', current_age),
                            key=f"lump_withdrawal_age_{i}")
                    with c_b:
                        amount = st.number_input(f"Amount #{i+1}", 0, 10000000,
                            st.session_state.lump_sum_withdrawals[i].get('amount', 0),
                            step=1000, key=f"lump_withdrawal_amount_{i}")
                    lump_withdrawals.append({'age': age, 'amount': amount})
                    st.session_state.lump_sum_withdrawals[i] = {'age': age, 'amount': amount}
    
    # Calculate button
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col2:
        calculate_button_tab4 = st.button("📊 Calculate", type="primary", use_container_width=True, key="calc_tab4")

with tab5:
    st.markdown("### Age-Based Spending Reductions")
    st.caption("Reduce your required income at specific ages to reflect lower spending in later retirement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### First Reduction")
        reduction_1_enabled = st.checkbox("Enable First Reduction", key="reduction_1_enabled", value=get_default('reduction_1_enabled', True))
        
        c1, c2 = st.columns(2)
        with c1:
            # Clamp default value to be within valid range
            default_age_77 = get_default('age_77_threshold', 77)
            default_age_77 = max(retirement_age, min(default_age_77, 100))
            age_77_threshold = st.number_input("At Age", retirement_age, 100, key="age_reduction_1_age", disabled=not reduction_1_enabled, value=default_age_77)
        with c2:
            age_77_reduction = st.number_input("Reduce By (%)", 0, 100, key="age_reduction_1_pct", disabled=not reduction_1_enabled, value=get_default('age_77_reduction', 10))
    
    with col2:
        st.markdown("#### Second Reduction")
        reduction_2_enabled = st.checkbox("Enable Second Reduction", key="reduction_2_enabled", value=get_default('reduction_2_enabled', True))
        
        c1, c2 = st.columns(2)
        with c1:
            # Clamp default value to be within valid range
            default_age_83 = get_default('age_83_threshold', 83)
            default_age_83 = max(retirement_age, min(default_age_83, 100))
            age_83_threshold = st.number_input("At Age", retirement_age, 100, key="age_reduction_2_age", disabled=not reduction_2_enabled, value=default_age_83)
        with c2:
            age_83_reduction = st.number_input("Reduce By (%)", 0, 100, key="age_reduction_2_pct", disabled=not reduction_2_enabled, value=get_default('age_83_reduction', 10))
    
    # Calculate button
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col2:
        calculate_button_tab5 = st.button("📊 Calculate", type="primary", use_container_width=True, key="calc_tab5")

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
    'couple_mode': couple_mode,
    'oas_start_age': oas_start_age,
    'monthly_oas': monthly_oas,
    'oas_inflation_adjusted': oas_inflation_adjusted,
    'oas_start_age_p2': oas_start_age_p2,
    'monthly_oas_p2': monthly_oas_p2,
    'oas_inflation_adjusted_p2': oas_inflation_adjusted_p2,
    'cpp_start_age': cpp_start_age,
    'monthly_cpp': monthly_cpp,
    'cpp_inflation_adjusted': cpp_inflation_adjusted,
    'cpp_start_age_p2': cpp_start_age_p2,
    'monthly_cpp_p2': monthly_cpp_p2,
    'cpp_inflation_adjusted_p2': cpp_inflation_adjusted_p2,
    'private_pension_start_age': private_pension_start_age,
    'monthly_private_pension': monthly_private_pension,
    'private_pension_inflation_adjusted': private_pension_inflation_adjusted,
    'private_pension_start_age_p2': private_pension_start_age_p2,
    'monthly_private_pension_p2': monthly_private_pension_p2,
    'private_pension_inflation_adjusted_p2': private_pension_inflation_adjusted_p2,
    'bridged_enabled_p1': bridged_enabled_p1,
    'bridged_start_age_p1': bridged_start_age_p1,
    'bridged_end_age_p1': bridged_end_age_p1,
    'bridged_amount_p1': bridged_amount_p1,
    'bridged_enabled_p2': bridged_enabled_p2,
    'bridged_start_age_p2': bridged_start_age_p2,
    'bridged_end_age_p2': bridged_end_age_p2,
    'bridged_amount_p2': bridged_amount_p2,
    'part_time_income': part_time_income,
    'part_time_start_age': part_time_start_age,
    'part_time_end_age': part_time_end_age,
    'part_time_inflation_adjusted': part_time_inflation_adjusted,
    'stop_investments_age': stop_investments_age,
    'inflation_adjustment_enabled': inflation_adjustment_enabled,
    'ignore_oas_clawback': ignore_oas_clawback,
    'lump_sums': st.session_state.get('lump_sums', []),
    'lump_sum_withdrawals': st.session_state.get('lump_sum_withdrawals', [])
}
st.session_state.inputs = inputs

# Check if any calculate button was pressed
calculate_button = (calculate_button_tab1 or calculate_button_tab2 or calculate_button_tab3 or 
                   calculate_button_tab4 or calculate_button_tab5)

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
    
    # Check if there are any OAS clawbacks
    has_oas_clawback = (df['OAS Clawback'] > 0).any() if 'OAS Clawback' in df.columns else False
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
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
    with col7:
        st.metric("OAS Clawback?", "Yes" if has_oas_clawback else "No")
    
    # Projection table
    st.subheader("Year-by-Year Projection")
    
    # Add legend for row highlighting
    legend_parts = []
    if has_shortfall:
        legend_parts.append("🔴 Red = Monthly shortfall")
    legend_parts.append("🟡 Yellow = Withdrawal exceeds 4% rule")
    if has_oas_clawback:
        legend_parts.append("🔴 Red text in OAS Clawback column = Income above $86,912 threshold")
    
    if legend_parts:
        st.caption(" | ".join(legend_parts))
    
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
        'Monthly Surplus',
        'Surplus Reinvested',
        'OAS',
        'OAS P1',
        'OAS P2',
        'CPP',
        'CPP P1',
        'CPP P2',
        'Employer Pension',
        'Employer Pension P1',
        'Employer Pension P2',
        'Monthly Pension',
        'Investment Withdrawal',
        'Part-Time Income',
        'Monthly Investment',
        'Yearly Investment Return',
        'Yearly Pension Amount',
        'Lump Sum',
        'Lump Sum Withdrawal',
        'OAS Clawback',
        '4% Rule Amount',
        'Withdrawal vs 4% Rule',
        '% Over 4% Rule'
    ]
    
    # Reorder columns to match desired order
    df = df[[col for col in column_order if col in df.columns]]
    
    # Format currency columns
    currency_cols = ['Investment Balance Start', 'Monthly Investment', 'Investment Withdrawal', 
                     'OAS', 'OAS P1', 'OAS P2', 'CPP', 'CPP P1', 'CPP P2', 
                     'Employer Pension', 'Employer Pension P1', 'Employer Pension P2',
                     'Monthly Pension', 'Part-Time Income', 
                     'Lump Sum', 'Lump Sum Withdrawal', 
                     'Required Income', 'Total Monthly Income', 'Monthly Shortfall', 'Monthly Surplus',
                     'Surplus Reinvested', 'Income (Today\'s $)',
                     'Yearly Investment Return', 'Yearly Pension Amount', 'Investment Balance End',
                     'OAS Clawback', '4% Rule Amount', 'Withdrawal vs 4% Rule']
    
    df_display = df.copy()
    for col in currency_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")
    
    # Format percentage column
    if '% Over 4% Rule' in df_display.columns:
        df_display['% Over 4% Rule'] = df_display['% Over 4% Rule'].apply(
            lambda x: f"{x:,.1f}%" if x != 0 else "-"
        )
    
    # Add styling to highlight rows where withdrawal exceeds 4% rule or has shortfall, and red text for OAS clawback
    def highlight_issues(row):
        styles = [''] * len(row)
        
        has_shortfall = False
        has_4pct_violation = False
        
        # Check for shortfall (darker red - most critical)
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
        
        # Apply row background colors based on conditions
        if has_shortfall and has_4pct_violation:
            styles = ['background-color: #ffcc99'] * len(row)  # Orange for both critical issues
        elif has_shortfall:
            styles = ['background-color: #ffcccc'] * len(row)  # Red for shortfall only
        elif has_4pct_violation:
            styles = ['background-color: #ffffcc'] * len(row)  # Yellow for 4% rule only
        
        # Apply red text color to OAS Clawback column if clawback exists
        if 'OAS Clawback' in row.index:
            try:
                clawback_str = str(row['OAS Clawback']).replace('$', '').replace(',', '')
                clawback_val = float(clawback_str)
                if clawback_val > 0:
                    oas_idx = row.index.get_loc('OAS Clawback')
                    styles[oas_idx] = styles[oas_idx] + '; color: red; font-weight: bold'
            except (ValueError, AttributeError):
                pass
        
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
