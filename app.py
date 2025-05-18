import streamlit as st
import pandas as pd # For displaying machine parameters neatly

# --- DEFAULT PARAMETERS FOR A SINGLE MACHINE ---
DEFAULT_SINGLE_MACHINE_PARAMS = {
    "id": 1, # For identification
    "machine_cost": 1000000,
    "machine_lifespan_years": 4,
    "annual_maintenance_cost_pct": 0.10,
    "engineer_monthly_salary": 7000,
    # Note: operating_days_per_year is now a global setting
}

# --- GLOBAL DEFAULT PARAMETERS ---
DEFAULT_GLOBAL_PARAMS = {
    "operating_days_per_year": 250,
    "lessor_target_profit_margin": 0.40,
    "machine_utilization_leasing_days_per_machine": 200, # For leasing model annual profit calc
    "powder_cost_per_ton": 700,
    "powder_tons_per_villa": 100,
    "steel_cables_cost_per_villa": 25000,
    "villa_printing_days_3dcp": 30,
    "villa_additional_prep_finish_days_3dcp": 15, # For total cycle time
    "unoptimised_villa_cost_baseline_traditional": 1300000, # Used for savings calculation
    "labor_savings_absolute_3dcp": 120000,
    "formwork_savings_absolute_3dcp": 60000,
    "waste_reduction_savings_absolute_3dcp": 25000,
    "time_related_overhead_savings_absolute_3dcp": 50000,
    "market_selling_price_per_villa": 2200000,
    "villas_built_per_year_per_3dcp_machine_contracting": 7, # If manually set, otherwise calculated
    # Traditional Model Parameters
    "traditional_villa_build_months": 9,
    "traditional_villa_cost": 1300000, # For direct comparison
}

def calculate_machine_operational_costs(machine_params, global_params):
    """Calculates annual and daily operational costs for a single machine."""
    annual_capital_recovery = machine_params["machine_cost"] / machine_params["machine_lifespan_years"]
    annual_maintenance = machine_params["machine_cost"] * machine_params["annual_maintenance_cost_pct"]
    annual_engineer_cost = machine_params["engineer_monthly_salary"] * 12
    
    total_annual_op_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost
    daily_op_cost = total_annual_op_cost / global_params["operating_days_per_year"]
    return total_annual_op_cost, daily_op_cost

def calculate_leasing_model_for_machine(machine_params, global_params):
    """Calculates leasing metrics for a single machine type."""
    results = {}
    total_annual_op_cost, daily_op_cost = calculate_machine_operational_costs(machine_params, global_params)
    results["total_annual_lessor_cost_per_machine"] = total_annual_op_cost
    results["daily_lessor_cost_basis_per_machine"] = daily_op_cost
    
    profit_margin_divisor = 1 - global_params["lessor_target_profit_margin"]
    if profit_margin_divisor <= 0: profit_margin_divisor = 0.001

    recommended_daily_lease_price = daily_op_cost / profit_margin_divisor
    results["recommended_daily_lease_price_per_machine"] = recommended_daily_lease_price
    
    daily_profit_lessor = recommended_daily_lease_price - daily_op_cost
    annual_profit_lessor = daily_profit_lessor * global_params["machine_utilization_leasing_days_per_machine"]
    results["annual_profit_lessor_per_machine_at_utilization"] = annual_profit_lessor
    
    lease_cost_for_villa = recommended_daily_lease_price * global_params["villa_printing_days_3dcp"]
    powder_cost_for_villa_lease = global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"]
    results["contractor_3dcp_elements_cost_per_villa_via_leasing"] = (
        lease_cost_for_villa + powder_cost_for_villa_lease + global_params["steel_cables_cost_per_villa"]
    )
    return results


def calculate_contracting_model_per_villa(machine_daily_op_cost, global_params):
    """Calculates cost and profit for one 3DCP villa, given machine op cost."""
    results = {}
    machine_op_cost_for_project = machine_daily_op_cost * global_params["villa_printing_days_3dcp"]
    results["machine_op_cost_for_project_per_villa"] = machine_op_cost_for_project
    
    powder_cost_for_villa = global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"]
    results["powder_cost_for_villa"] = powder_cost_for_villa
    
    total_identified_savings_vs_traditional_shell = (
        global_params["labor_savings_absolute_3dcp"] +
        global_params["formwork_savings_absolute_3dcp"] +
        global_params["waste_reduction_savings_absolute_3dcp"] +
        global_params["time_related_overhead_savings_absolute_3dcp"]
    )
    results["total_identified_savings_vs_traditional_shell_per_villa"] = total_identified_savings_vs_traditional_shell
    
    # Cost of 3DCP villa is baseline traditional MINUS identified savings, PLUS new 3DCP specific costs
    # This assumes the 'unoptimised_villa_cost_baseline_traditional' included costs now being saved.
    base_cost_after_shell_savings = global_params["unoptimised_villa_cost_baseline_traditional"] - total_identified_savings_vs_traditional_shell
    
    optimized_total_cost_per_3dcp_villa = (
        base_cost_after_shell_savings +
        powder_cost_for_villa +
        global_params["steel_cables_cost_per_villa"] +
        machine_op_cost_for_project
    )
    results["optimized_total_cost_per_3dcp_villa"] = optimized_total_cost_per_3dcp_villa
    
    profit_per_3dcp_villa = global_params["market_selling_price_per_villa"] - optimized_total_cost_per_3dcp_villa
    results["profit_per_3dcp_villa"] = profit_per_3dcp_villa
    return results

def calculate_productivity_and_turnover(num_machines, list_of_machine_params, global_params, contracting_villa_details):
    results = {}
    # 3DCP Productivity & Turnover
    villa_total_cycle_days_3dcp = global_params["villa_printing_days_3dcp"] + global_params["villa_additional_prep_finish_days_3dcp"]
    if villa_total_cycle_days_3dcp == 0: villa_total_cycle_days_3dcp = 1 # Avoid division by zero
    
    villas_per_year_per_active_3dcp_machine = global_params["operating_days_per_year"] / villa_total_cycle_days_3dcp
    total_villas_per_year_3dcp_fleet = villas_per_year_per_active_3dcp_machine * num_machines
    
    results["villa_total_cycle_days_3dcp"] = villa_total_cycle_days_3dcp
    results["villas_per_year_per_active_3dcp_machine"] = villas_per_year_per_active_3dcp_machine
    results["total_villas_per_year_3dcp_fleet"] = total_villas_per_year_3dcp_fleet
    
    annual_revenue_3dcp_fleet = total_villas_per_year_3dcp_fleet * global_params["market_selling_price_per_villa"]
    results["annual_revenue_3dcp_fleet"] = annual_revenue_3dcp_fleet
    
    # Calculate total annual profit for the 3DCP contracting fleet
    # This requires knowing the average machine op cost if machines are different
    # For simplicity, if machines are different, we might need to average or use a representative machine for per-villa profit.
    # Or, calculate total fleet cost and total fleet revenue.
    total_annual_fleet_operational_cost = 0
    for m_params in list_of_machine_params:
        annual_op_cost, _ = calculate_machine_operational_costs(m_params, global_params)
        total_annual_fleet_operational_cost += annual_op_cost
    
    total_annual_material_cost_3dcp_fleet = (global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"] +
                                            global_params["steel_cables_cost_per_villa"]) * total_villas_per_year_3dcp_fleet
    
    # Savings relative to traditional for the SHELL part of the villa
    total_identified_savings_vs_traditional_shell_per_villa = (
        global_params["labor_savings_absolute_3dcp"] +
        global_params["formwork_savings_absolute_3dcp"] +
        global_params["waste_reduction_savings_absolute_3dcp"] +
        global_params["time_related_overhead_savings_absolute_3dcp"]
    )
    # Cost of non-shell parts (assuming it's the traditional baseline minus the shell savings)
    non_shell_cost_per_villa = global_params["unoptimised_villa_cost_baseline_traditional"] - total_identified_savings_vs_traditional_shell_per_villa

    total_annual_other_costs_3dcp_fleet = non_shell_cost_per_villa * total_villas_per_year_3dcp_fleet

    total_annual_cost_3dcp_fleet_contracting = (total_annual_fleet_operational_cost +
                                                total_annual_material_cost_3dcp_fleet +
                                                total_annual_other_costs_3dcp_fleet)
    results["total_annual_cost_3dcp_fleet_contracting"] = total_annual_cost_3dcp_fleet_contracting
    
    annual_profit_3dcp_fleet_contracting = annual_revenue_3dcp_fleet - total_annual_cost_3dcp_fleet_contracting
    results["annual_profit_3dcp_fleet_contracting"] = annual_profit_3dcp_fleet_contracting
    results["profit_per_3dcp_villa_fleet_avg"] = contracting_villa_details.get("profit_per_3dcp_villa", 0) # From single villa calc

    # Traditional Model Productivity & Turnover
    traditional_villa_build_days = global_params["traditional_villa_build_months"] * 30 # Approx days
    if traditional_villa_build_days == 0: traditional_villa_build_days = 1
    
    # To compare apples-to-apples for turnover, let's assume same number of "projects" or "capacity"
    # Or, how many villas can one "traditional team/setup" produce in a year
    villas_per_year_traditional_setup = global_params["operating_days_per_year"] / traditional_villa_build_days
    # If we want to match the number of 3DCP machines with "traditional teams":
    total_villas_per_year_traditional_equivalent_effort = villas_per_year_traditional_setup * num_machines # Assuming num_machines represents "teams"
    
    results["traditional_villa_build_days"] = traditional_villa_build_days
    results["villas_per_year_per_traditional_setup"] = villas_per_year_traditional_setup
    results["total_villas_per_year_traditional_equivalent_effort"] = total_villas_per_year_traditional_equivalent_effort
    
    annual_revenue_traditional_equivalent = total_villas_per_year_traditional_equivalent_effort * global_params["market_selling_price_per_villa"]
    results["annual_revenue_traditional_equivalent"] = annual_revenue_traditional_equivalent

    total_cost_traditional_equivalent = total_villas_per_year_traditional_equivalent_effort * global_params["traditional_villa_cost"]
    annual_profit_traditional_equivalent = annual_revenue_traditional_equivalent - total_cost_traditional_equivalent
    results["annual_profit_traditional_equivalent_effort"] = annual_profit_traditional_equivalent

    # Savings
    cost_saving_per_villa_3dcp = global_params["traditional_villa_cost"] - contracting_villa_details.get("optimized_total_cost_per_3dcp_villa", global_params["traditional_villa_cost"])
    time_saving_per_villa_3dcp_days = traditional_villa_build_days - villa_total_cycle_days_3dcp
    results["cost_saving_per_villa_3dcp_vs_traditional"] = cost_saving_per_villa_3dcp
    results["time_saving_per_villa_3dcp_vs_traditional_days"] = time_saving_per_villa_3dcp_days

    return results

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Enhanced 3D Concrete Printing Business Case Simulator")

# --- Global Parameters Sidebar ---
st.sidebar.header("Global Simulation Parameters")
global_params_input = {}
global_params_input["operating_days_per_year"] = st.sidebar.number_input("Operating Days per Year (All Machines)", min_value=100, max_value=365, value=DEFAULT_GLOBAL_PARAMS["operating_days_per_year"], step=5, key="global_op_days")

st.sidebar.subheader("Leasing Model Globals")
global_params_input["lessor_target_profit_margin"] = st.sidebar.slider("Lessor Target Profit Margin (%)", min_value=0.01, max_value=0.90, value=DEFAULT_GLOBAL_PARAMS["lessor_target_profit_margin"], step=0.01, format="%.2f", key="global_profit_margin")
global_params_input["machine_utilization_leasing_days_per_machine"] = st.sidebar.number_input("Machine Utilization Days (Leasing, Per Machine)", min_value=1, max_value=global_params_input["operating_days_per_year"], value=DEFAULT_GLOBAL_PARAMS["machine_utilization_leasing_days_per_machine"], step=5, key="global_util_days")

st.sidebar.subheader("Villa & Material Globals (3DCP)")
global_params_input["powder_cost_per_ton"] = st.sidebar.number_input("Powder Cost per Ton (AED)", min_value=100, value=DEFAULT_GLOBAL_PARAMS["powder_cost_per_ton"], step=10, key="global_powder_cost")
global_params_input["powder_tons_per_villa"] = st.sidebar.number_input("Powder Tons per Villa", min_value=10, value=DEFAULT_GLOBAL_PARAMS["powder_tons_per_villa"], step=5, key="global_powder_tons")
global_params_input["steel_cables_cost_per_villa"] = st.sidebar.number_input("Steel & Cables Cost per Villa (AED)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["steel_cables_cost_per_villa"], step=1000, key="global_steel_cost")
global_params_input["villa_printing_days_3dcp"] = st.sidebar.number_input("Villa Printing Days (3DCP)", min_value=5, value=DEFAULT_GLOBAL_PARAMS["villa_printing_days_3dcp"], step=1, key="global_print_days")
global_params_input["villa_additional_prep_finish_days_3dcp"] = st.sidebar.number_input("Villa Additional Prep/Finish Days (3DCP)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["villa_additional_prep_finish_days_3dcp"], step=1, key="global_prep_days")
global_params_input["market_selling_price_per_villa"] = st.sidebar.number_input("Market Selling Price per Villa (AED)", min_value=500000, value=DEFAULT_GLOBAL_PARAMS["market_selling_price_per_villa"], step=50000, key="global_sell_price")

st.sidebar.subheader("Savings & Cost Basis (vs. Traditional)")
global_params_input["unoptimised_villa_cost_baseline_traditional"] = st.sidebar.number_input("Traditional Villa Cost Baseline (AED - for savings calc)", min_value=500000, value=DEFAULT_GLOBAL_PARAMS["unoptimised_villa_cost_baseline_traditional"], step=50000, key="global_trad_baseline")
global_params_input["labor_savings_absolute_3dcp"] = st.sidebar.number_input("3DCP Labor Savings (Absolute AED)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["labor_savings_absolute_3dcp"], step=10000, key="global_labor_save")
# ... (add other savings inputs similarly: formwork, waste, time_related_overhead)
global_params_input["formwork_savings_absolute_3dcp"] = st.sidebar.number_input("3DCP Formwork Savings (Absolute AED)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["formwork_savings_absolute_3dcp"], step=5000, key="global_form_save")
global_params_input["waste_reduction_savings_absolute_3dcp"] = st.sidebar.number_input("3DCP Waste Reduction Savings (Absolute AED)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["waste_reduction_savings_absolute_3dcp"], step=5000, key="global_waste_save")
global_params_input["time_related_overhead_savings_absolute_3dcp"] = st.sidebar.number_input("3DCP Time-Overhead Savings (Absolute AED)", min_value=0, value=DEFAULT_GLOBAL_PARAMS["time_related_overhead_savings_absolute_3dcp"], step=5000, key="global_time_save")


st.sidebar.subheader("Traditional Model Parameters (for Comparison)")
global_params_input["traditional_villa_build_months"] = st.sidebar.number_input("Traditional Villa Build Time (Months)", min_value=1, value=DEFAULT_GLOBAL_PARAMS["traditional_villa_build_months"], step=1, key="global_trad_months")
global_params_input["traditional_villa_cost"] = st.sidebar.number_input("Traditional Villa Cost (AED - for comparison)", min_value=500000, value=DEFAULT_GLOBAL_PARAMS["traditional_villa_cost"], step=50000, key="global_trad_cost")

# --- Machine Configuration Area ---
st.header("Machine Fleet Configuration")
num_machines = st.number_input("Number of 3DCP Machines in Fleet", min_value=1, value=1, step=1, key="num_machines")

# Initialize session state for machine_params_list if it doesn't exist
if 'machine_params_list' not in st.session_state or len(st.session_state.machine_params_list) != num_machines:
    st.session_state.machine_params_list = []
    for i in range(num_machines):
        new_machine = DEFAULT_SINGLE_MACHINE_PARAMS.copy()
        new_machine["id"] = i + 1
        # If there was a previous machine with this ID, try to load its params
        if i < len(st.session_state.get('machine_params_list_backup', [])):
             new_machine.update(st.session_state.machine_params_list_backup[i])
        st.session_state.machine_params_list.append(new_machine)

# Backup current params before changing num_machines potentially wipes them
st.session_state.machine_params_list_backup = [mp.copy() for mp in st.session_state.machine_params_list]


active_machine_params_list = []
cols = st.columns(num_machines if num_machines <= 3 else 3) # Max 3 columns for readability
for i in range(num_machines):
    col = cols[i % len(cols)]
    with col:
        st.subheader(f"Machine {st.session_state.machine_params_list[i]['id']} Parameters")
        current_machine_input = st.session_state.machine_params_list[i] # Get current machine's dict
        
        current_machine_input["machine_cost"] = st.number_input(f"Cost (AED)##{i}", min_value=100000, value=current_machine_input["machine_cost"], step=50000, key=f"m_cost_{i}")
        current_machine_input["machine_lifespan_years"] = st.number_input(f"Lifespan (Years)##{i}", min_value=1, value=current_machine_input["machine_lifespan_years"], step=1, key=f"m_life_{i}")
        current_machine_input["annual_maintenance_cost_pct"] = st.slider(f"Maintenance (% Cost)##{i}", 0.01, 0.30, current_machine_input["annual_maintenance_cost_pct"], 0.01, format="%.2f", key=f"m_maint_{i}")
        current_machine_input["engineer_monthly_salary"] = st.number_input(f"Engineer Salary (AED/month)##{i}", min_value=0, value=current_machine_input["engineer_monthly_salary"], step=500, key=f"m_eng_{i}")
        active_machine_params_list.append(current_machine_input)


# --- Simulation Execution and Display ---
if st.button("Run Full Simulation", key="run_sim_button"):
    st.header("Simulation Results")

    # --- LEASING MODEL RESULTS (Per Machine Type if different, or average) ---
    st.subheader("Leasing Model Insights (Representative Machine)")
    # For simplicity, showing results for the *first* machine as representative for leasing
    # A more complex app could show a table for each machine type
    if active_machine_params_list:
        rep_machine_params_leasing = active_machine_params_list[0]
        leasing_output_rep = calculate_leasing_model_for_machine(rep_machine_params_leasing, global_params_input)
        st.markdown(f"**For Machine {rep_machine_params_leasing['id']} (Representative for Leasing):**")
        st.markdown(f"  - Recommended Daily Lease Price: AED {leasing_output_rep['recommended_daily_lease_price_per_machine']:,.2f}")
        st.markdown(f"  - Annual Profit (Leasing this machine at {global_params_input['machine_utilization_leasing_days_per_machine']} days util.): <span style='color:green; font-weight:bold;'>AED {leasing_output_rep['annual_profit_lessor_per_machine_at_utilization']:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"  - Contractor's Cost for 3DCP Elements (via leasing this machine): AED {leasing_output_rep['contractor_3dcp_elements_cost_per_villa_via_leasing']:,.2f}")
        
        if len(active_machine_params_list) > 1:
            st.caption("Note: Leasing insights shown for the first machine configured. For a fleet with varied machines, leasing would be per machine type.")
    else:
        st.warning("No machines configured for leasing model insights.")


    # --- CONTRACTING MODEL RESULTS (Fleet Aggregated) ---
    st.subheader("Direct Contracting Model Insights (Full Fleet)")
    if active_machine_params_list:
        # Calculate average daily op cost if machines are different, for per-villa profit estimation
        # Or, better: calculate total fleet costs and profits.
        avg_daily_op_cost_fleet = sum(calculate_machine_operational_costs(mp, global_params_input)[1] for mp in active_machine_params_list) / len(active_machine_params_list)
        
        contracting_villa_details = calculate_contracting_model_per_villa(avg_daily_op_cost_fleet, global_params_input)
        
        st.markdown(f"**Per 3DCP Villa (based on average machine operational cost):**")
        st.markdown(f"  - Optimized Total Cost: AED {contracting_villa_details['optimized_total_cost_per_3dcp_villa']:,.2f}")
        st.markdown(f"  - Net Profit per Villa: <span style='color:green; font-weight:bold;'>AED {contracting_villa_details['profit_per_3dcp_villa']:,.2f}</span>", unsafe_allow_html=True)

        # --- Productivity & Turnover Comparison ---
        st.subheader("Productivity, Turnover & Savings Comparison")
        productivity_turnover_results = calculate_productivity_and_turnover(num_machines, active_machine_params_list, global_params_input, contracting_villa_details)

        col_prod1, col_prod2 = st.columns(2)
        with col_prod1:
            st.markdown("**3DCP Fleet Performance:**")
            st.markdown(f"- Villas per Year (per active machine): {productivity_turnover_results['villas_per_year_per_active_3dcp_machine']:.2f}")
            st.markdown(f"- Total Villas per Year (Fleet of {num_machines}): {productivity_turnover_results['total_villas_per_year_3dcp_fleet']:.2f}")
            st.markdown(f"- Annual Revenue (Fleet): AED {productivity_turnover_results['annual_revenue_3dcp_fleet']:,.2f}")
            st.markdown(f"- Total Annual Cost (Fleet Contracting): AED {productivity_turnover_results['total_annual_cost_3dcp_fleet_contracting']:,.2f}")
            st.markdown(f"- **Annual Net Profit (Fleet Contracting):** <span style='color:blue; font-weight:bold; font-size:1.1em;'>AED {productivity_turnover_results['annual_profit_3dcp_fleet_contracting']:,.2f}</span>", unsafe_allow_html=True)
        
        with col_prod2:
            st.markdown("**Traditional Model Performance (Equivalent Effort):**")
            st.markdown(f"- Villas per Year (per traditional setup): {productivity_turnover_results['villas_per_year_per_traditional_setup']:.2f}")
            st.markdown(f"- Total Villas per Year (equivalent to {num_machines} setups): {productivity_turnover_results['total_villas_per_year_traditional_equivalent_effort']:.2f}")
            st.markdown(f"- Annual Revenue (Traditional Equivalent): AED {productivity_turnover_results['annual_revenue_traditional_equivalent']:,.2f}")
            st.markdown(f"- **Annual Net Profit (Traditional Equivalent):** AED {productivity_turnover_results['annual_profit_traditional_equivalent_effort']:,.2f}")

        st.markdown("---")
        st.markdown("**Savings per Villa (3DCP vs. Traditional):**")
        st.markdown(f"- Cost Saving: <span style='color:darkorange; font-weight:bold;'>AED {productivity_turnover_results['cost_saving_per_villa_3dcp_vs_traditional']:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"- Time Saving (Days): <span style='color:darkorange; font-weight:bold;'>{productivity_turnover_results['time_saving_per_villa_3dcp_vs_traditional_days']:.0f} days</span>", unsafe_allow_html=True)
        st.markdown(f"  (Based on traditional build time of {global_params_input['traditional_villa_build_months']} months vs. 3DCP cycle of {productivity_turnover_results['villa_total_cycle_days_3dcp']:.0f} days)")

    else:
        st.warning("Configure at least one machine to run the contracting model simulation.")

else:
    st.info("Adjust global parameters and machine configurations, then click 'Run Full Simulation'.")

st.markdown("---")
st.caption("Note: Calculations are based on the input parameters. Review assumptions carefully. For fleets with diverse machines, 'per villa' contracting metrics are based on average operational costs.")
