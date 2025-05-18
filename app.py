import streamlit as st

# --- DEFAULT PARAMETERS (can be overridden by scenarios) ---
DEFAULT_PARAMS = {
    "machine_cost": 1000000,
    "machine_lifespan_years": 4,
    "annual_maintenance_cost_pct": 0.10, # 10% of machine cost
    "engineer_monthly_salary": 7000,
    "operating_days_per_year": 250,
    "lessor_target_profit_margin": 0.40,
    "machine_utilization_leasing_days": 200, # For leasing model annual profit calc
    "powder_cost_per_ton": 700,
    "powder_tons_per_villa": 100,
    "steel_cables_cost_per_villa": 25000,
    "villa_printing_days": 30,
    "unoptimised_villa_cost_baseline": 1300000,
    "labor_savings_absolute": 120000,
    "formwork_savings_absolute": 60000,
    "waste_reduction_savings_absolute": 25000,
    "time_related_overhead_savings_absolute": 50000,
    "market_selling_price_per_villa": 2200000,
    "villas_built_per_year_contracting": 7, # For contracting model annual profit calc
}

def calculate_leasing_model(params):
    results = {}
    annual_capital_recovery = params["machine_cost"] / params["machine_lifespan_years"]
    annual_maintenance = params["machine_cost"] * params["annual_maintenance_cost_pct"]
    annual_engineer_cost = params["engineer_monthly_salary"] * 12
    
    total_annual_lessor_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost
    results["total_annual_lessor_cost"] = total_annual_lessor_cost
    
    daily_lessor_cost = total_annual_lessor_cost / params["operating_days_per_year"]
    results["daily_lessor_cost"] = daily_lessor_cost
    
    # Ensure profit margin is less than 1 to avoid division by zero or negative
    profit_margin_divisor = 1 - params["lessor_target_profit_margin"]
    if profit_margin_divisor <= 0:
        profit_margin_divisor = 0.001 # Avoid division by zero/negative

    recommended_daily_lease_price = daily_lessor_cost / profit_margin_divisor
    results["recommended_daily_lease_price"] = recommended_daily_lease_price
    
    daily_profit_lessor = recommended_daily_lease_price - daily_lessor_cost
    annual_profit_lessor = daily_profit_lessor * params["machine_utilization_leasing_days"]
    results["annual_profit_lessor_at_utilization"] = annual_profit_lessor
    
    lease_cost_for_villa = recommended_daily_lease_price * params["villa_printing_days"]
    powder_cost_for_villa_lease = params["powder_cost_per_ton"] * params["powder_tons_per_villa"]
    results["contractor_3dcp_elements_cost_per_villa"] = lease_cost_for_villa + powder_cost_for_villa_lease + params["steel_cables_cost_per_villa"]
    
    return results

def calculate_contracting_model(params):
    results = {}
    annual_capital_recovery = params["machine_cost"] / params["machine_lifespan_years"]
    annual_maintenance = params["machine_cost"] * params["annual_maintenance_cost_pct"]
    annual_engineer_cost = params["engineer_monthly_salary"] * 12
    total_annual_machine_op_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost
    
    machine_op_cost_per_day = total_annual_machine_op_cost / params["operating_days_per_year"]
    machine_op_cost_for_project = machine_op_cost_per_day * params["villa_printing_days"]
    results["machine_op_cost_for_project"] = machine_op_cost_for_project
    
    powder_cost_for_villa_contract = params["powder_cost_per_ton"] * params["powder_tons_per_villa"]
    results["powder_cost_for_villa"] = powder_cost_for_villa_contract
    
    total_identified_savings = (params["labor_savings_absolute"] +
                                params["formwork_savings_absolute"] +
                                params["waste_reduction_savings_absolute"] +
                                params["time_related_overhead_savings_absolute"])
    results["total_identified_savings_per_villa"] = total_identified_savings
    
    adjusted_base_cost = params["unoptimised_villa_cost_baseline"] - total_identified_savings
    
    optimized_total_cost_per_villa = (adjusted_base_cost +
                                      powder_cost_for_villa_contract +
                                      params["steel_cables_cost_per_villa"] +
                                      machine_op_cost_for_project)
    results["optimized_total_cost_per_villa"] = optimized_total_cost_per_villa
    
    profit_per_villa = params["market_selling_price_per_villa"] - optimized_total_cost_per_villa
    results["profit_per_villa"] = profit_per_villa
    
    annual_profit_contracting = profit_per_villa * params["villas_built_per_year_contracting"]
    results["annual_profit_contracting"] = annual_profit_contracting
    
    return results

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("3D Concrete Printing Business Case Simulator")

st.sidebar.header("Input Parameters for Simulation")

# --- INPUTS ---
current_params = {} # To store user inputs

st.sidebar.subheader("Machine & General Operations")
current_params["machine_cost"] = st.sidebar.number_input("Machine Cost (AED)", min_value=100000, value=DEFAULT_PARAMS["machine_cost"], step=50000)
current_params["machine_lifespan_years"] = st.sidebar.number_input("Machine Lifespan (Years)", min_value=1, value=DEFAULT_PARAMS["machine_lifespan_years"], step=1)
current_params["annual_maintenance_cost_pct"] = st.sidebar.slider("Annual Maintenance (% of Machine Cost)", min_value=0.01, max_value=0.30, value=DEFAULT_PARAMS["annual_maintenance_cost_pct"], step=0.01, format="%.2f")
current_params["engineer_monthly_salary"] = st.sidebar.number_input("Engineer Monthly Salary (AED)", min_value=0, value=DEFAULT_PARAMS["engineer_monthly_salary"], step=500)
current_params["operating_days_per_year"] = st.sidebar.number_input("Operating Days per Year (Machine)", min_value=100, max_value=365, value=DEFAULT_PARAMS["operating_days_per_year"], step=5)

st.sidebar.subheader("Leasing Model Specifics")
current_params["lessor_target_profit_margin"] = st.sidebar.slider("Lessor Target Profit Margin (%)", min_value=0.01, max_value=0.90, value=DEFAULT_PARAMS["lessor_target_profit_margin"], step=0.01, format="%.2f")
current_params["machine_utilization_leasing_days"] = st.sidebar.number_input("Machine Utilization Days (Leasing)", min_value=1, max_value=current_params["operating_days_per_year"], value=DEFAULT_PARAMS["machine_utilization_leasing_days"], step=5)


st.sidebar.subheader("Contracting Model & Villa Specifics")
current_params["powder_cost_per_ton"] = st.sidebar.number_input("Powder Cost per Ton (AED)", min_value=100, value=DEFAULT_PARAMS["powder_cost_per_ton"], step=10)
current_params["powder_tons_per_villa"] = st.sidebar.number_input("Powder Tons per Villa", min_value=10, value=DEFAULT_PARAMS["powder_tons_per_villa"], step=5)
current_params["steel_cables_cost_per_villa"] = st.sidebar.number_input("Steel & Cables Cost per Villa (AED)", min_value=0, value=DEFAULT_PARAMS["steel_cables_cost_per_villa"], step=1000)
current_params["villa_printing_days"] = st.sidebar.number_input("Villa Printing Days", min_value=5, value=DEFAULT_PARAMS["villa_printing_days"], step=1)
current_params["unoptimised_villa_cost_baseline"] = st.sidebar.number_input("Unoptimised Villa Cost Baseline (AED)", min_value=500000, value=DEFAULT_PARAMS["unoptimised_villa_cost_baseline"], step=50000)
current_params["labor_savings_absolute"] = st.sidebar.number_input("Labor Savings (Absolute AED)", min_value=0, value=DEFAULT_PARAMS["labor_savings_absolute"], step=10000)
current_params["formwork_savings_absolute"] = st.sidebar.number_input("Formwork Savings (Absolute AED)", min_value=0, value=DEFAULT_PARAMS["formwork_savings_absolute"], step=5000)
current_params["waste_reduction_savings_absolute"] = st.sidebar.number_input("Waste Reduction Savings (Absolute AED)", min_value=0, value=DEFAULT_PARAMS["waste_reduction_savings_absolute"], step=5000)
current_params["time_related_overhead_savings_absolute"] = st.sidebar.number_input("Time-Related Overhead Savings (Absolute AED)", min_value=0, value=DEFAULT_PARAMS["time_related_overhead_savings_absolute"], step=5000)
current_params["market_selling_price_per_villa"] = st.sidebar.number_input("Market Selling Price per Villa (AED)", min_value=500000, value=DEFAULT_PARAMS["market_selling_price_per_villa"], step=50000)
current_params["villas_built_per_year_contracting"] = st.sidebar.number_input("Villas Built per Year (Contracting)", min_value=1, value=DEFAULT_PARAMS["villas_built_per_year_contracting"], step=1)


if st.sidebar.button("Run Simulation"):
    leasing_output = calculate_leasing_model(current_params)
    contracting_output = calculate_contracting_model(current_params)

    st.header("Simulation Results")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leasing Model")
        st.markdown(f"**Total Annual Lessor Cost:** AED {leasing_output['total_annual_lessor_cost']:,.2f}")
        st.markdown(f"**Daily Lessor Cost (Basis):** AED {leasing_output['daily_lessor_cost']:,.2f}")
        st.markdown(f"**Recommended Daily Lease Price:** AED {leasing_output['recommended_daily_lease_price']:,.2f}")
        st.markdown(f"**Annual Profit for Lessor (at {current_params['machine_utilization_leasing_days']} days util.):** <span style='color:green; font-weight:bold;'>AED {leasing_output['annual_profit_lessor_at_utilization']:,.2f}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**Contractor's 3DCP Elements Cost per Villa (Lease + Powder + Steel/Cables):** AED {leasing_output['contractor_3dcp_elements_cost_per_villa']:,.2f}")

    with col2:
        st.subheader("Direct Contracting Model")
        st.markdown(f"**Machine Operating Cost for Villa Project:** AED {contracting_output['machine_op_cost_for_project']:,.2f}")
        st.markdown(f"**Powder Cost for Villa:** AED {contracting_output['powder_cost_for_villa']:,.2f}")
        st.markdown(f"**Total Identified Savings per Villa:** AED {contracting_output['total_identified_savings_per_villa']:,.2f}")
        st.markdown(f"**Optimized Total Cost per Villa:** AED {contracting_output['optimized_total_cost_per_villa']:,.2f}")
        st.markdown(f"**Net Profit per Villa:** <span style='color:green; font-weight:bold;'>AED {contracting_output['profit_per_villa']:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"**Annual Net Profit (at {current_params['villas_built_per_year_contracting']} villas/year):** <span style='color:blue; font-weight:bold; font-size:1.1em;'>AED {contracting_output['annual_profit_contracting']:,.2f}</span>", unsafe_allow_html=True)
else:
    st.info("Adjust parameters in the sidebar and click 'Run Simulation'.")

st.markdown("---")
st.markdown("Note: Calculations are based on the input parameters. Review assumptions carefully.")
