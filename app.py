import streamlit as st
import pandas as pd
import plotly.express as px # For interactive charts

# --- DEFAULT PARAMETERS FOR A SINGLE MACHINE ---
DEFAULT_SINGLE_MACHINE_PARAMS = {
    "id": 1,
    "machine_cost": 1000000,
    "machine_lifespan_years": 4,
    "annual_maintenance_cost_pct": 0.10,
    "engineer_monthly_salary": 7000,
}

# --- GLOBAL DEFAULT PARAMETERS ---
DEFAULT_GLOBAL_PARAMS = {
    "operating_days_per_year": 250,
    "lessor_target_profit_margin": 0.40,
    "machine_utilization_leasing_days_per_machine": 200,
    "powder_cost_per_ton": 700,
    "powder_tons_per_villa": 100,
    "steel_cables_cost_per_villa": 25000,
    "villa_printing_days_3dcp": 30,
    "villa_additional_prep_finish_days_3dcp": 15,
    "unoptimised_villa_cost_baseline_traditional": 1300000,
    "labor_savings_absolute_3dcp": 120000,
    "formwork_savings_absolute_3dcp": 60000,
    "waste_reduction_savings_absolute_3dcp": 25000,
    "time_related_overhead_savings_absolute_3dcp": 50000,
    "market_selling_price_per_villa": 2200000,
    "traditional_villa_build_months": 9,
    "traditional_villa_cost": 1300000,
}

# --- CALCULATION FUNCTIONS (largely unchanged, added ROI) ---

def calculate_machine_operational_costs(machine_params, global_params):
    annual_capital_recovery = machine_params["machine_cost"] / machine_params["machine_lifespan_years"]
    annual_maintenance = machine_params["machine_cost"] * machine_params["annual_maintenance_cost_pct"]
    annual_engineer_cost = machine_params["engineer_monthly_salary"] * 12
    total_annual_op_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost
    daily_op_cost = total_annual_op_cost / global_params["operating_days_per_year"]
    return total_annual_op_cost, daily_op_cost

def calculate_leasing_model_for_machine(machine_params, global_params):
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
    villa_total_cycle_days_3dcp = global_params["villa_printing_days_3dcp"] + global_params["villa_additional_prep_finish_days_3dcp"]
    if villa_total_cycle_days_3dcp == 0: villa_total_cycle_days_3dcp = 1
    villas_per_year_per_active_3dcp_machine = global_params["operating_days_per_year"] / villa_total_cycle_days_3dcp
    total_villas_per_year_3dcp_fleet = villas_per_year_per_active_3dcp_machine * num_machines
    results["villa_total_cycle_days_3dcp"] = villa_total_cycle_days_3dcp
    results["villas_per_year_per_active_3dcp_machine"] = villas_per_year_per_active_3dcp_machine
    results["total_villas_per_year_3dcp_fleet"] = total_villas_per_year_3dcp_fleet
    annual_revenue_3dcp_fleet = total_villas_per_year_3dcp_fleet * global_params["market_selling_price_per_villa"]
    results["annual_revenue_3dcp_fleet"] = annual_revenue_3dcp_fleet
    
    total_capital_invested_fleet = sum(mp["machine_cost"] for mp in list_of_machine_params)
    results["total_capital_invested_fleet"] = total_capital_invested_fleet

    total_annual_fleet_operational_cost = sum(calculate_machine_operational_costs(mp, global_params)[0] for mp in list_of_machine_params)
    total_annual_material_cost_3dcp_fleet = (global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"] +
                                            global_params["steel_cables_cost_per_villa"]) * total_villas_per_year_3dcp_fleet
    total_identified_savings_vs_traditional_shell_per_villa = (
        global_params["labor_savings_absolute_3dcp"] +
        global_params["formwork_savings_absolute_3dcp"] +
        global_params["waste_reduction_savings_absolute_3dcp"] +
        global_params["time_related_overhead_savings_absolute_3dcp"]
    )
    non_shell_cost_per_villa = global_params["unoptimised_villa_cost_baseline_traditional"] - total_identified_savings_vs_traditional_shell_per_villa
    total_annual_other_costs_3dcp_fleet = non_shell_cost_per_villa * total_villas_per_year_3dcp_fleet
    total_annual_cost_3dcp_fleet_contracting = (total_annual_fleet_operational_cost +
                                                total_annual_material_cost_3dcp_fleet +
                                                total_annual_other_costs_3dcp_fleet)
    results["total_annual_cost_3dcp_fleet_contracting"] = total_annual_cost_3dcp_fleet_contracting
    annual_profit_3dcp_fleet_contracting = annual_revenue_3dcp_fleet - total_annual_cost_3dcp_fleet_contracting
    results["annual_profit_3dcp_fleet_contracting"] = annual_profit_3dcp_fleet_contracting
    results["profit_per_3dcp_villa_fleet_avg"] = contracting_villa_details.get("profit_per_3dcp_villa", 0)
    
    if total_capital_invested_fleet > 0:
        results["roi_3dcp_fleet_contracting"] = (annual_profit_3dcp_fleet_contracting / total_capital_invested_fleet) * 100
    else:
        results["roi_3dcp_fleet_contracting"] = 0

    traditional_villa_build_days = global_params["traditional_villa_build_months"] * 30
    if traditional_villa_build_days == 0: traditional_villa_build_days = 1
    villas_per_year_traditional_setup = global_params["operating_days_per_year"] / traditional_villa_build_days
    total_villas_per_year_traditional_equivalent_effort = villas_per_year_traditional_setup * num_machines
    results["traditional_villa_build_days"] = traditional_villa_build_days
    results["villas_per_year_per_traditional_setup"] = villas_per_year_traditional_setup
    results["total_villas_per_year_traditional_equivalent_effort"] = total_villas_per_year_traditional_equivalent_effort
    annual_revenue_traditional_equivalent = total_villas_per_year_traditional_equivalent_effort * global_params["market_selling_price_per_villa"]
    results["annual_revenue_traditional_equivalent"] = annual_revenue_traditional_equivalent
    total_cost_traditional_equivalent = total_villas_per_year_traditional_equivalent_effort * global_params["traditional_villa_cost"]
    annual_profit_traditional_equivalent = annual_revenue_traditional_equivalent - total_cost_traditional_equivalent
    results["annual_profit_traditional_equivalent_effort"] = annual_profit_traditional_equivalent
    cost_saving_per_villa_3dcp = global_params["traditional_villa_cost"] - contracting_villa_details.get("optimized_total_cost_per_3dcp_villa", global_params["traditional_villa_cost"])
    time_saving_per_villa_3dcp_days = traditional_villa_build_days - villa_total_cycle_days_3dcp
    results["cost_saving_per_villa_3dcp_vs_traditional"] = cost_saving_per_villa_3dcp
    results["time_saving_per_villa_3dcp_vs_traditional_days"] = time_saving_per_villa_3dcp_days
    return results

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="3DCP Business Simulator")
st.title("🏗️ 3D Concrete Printing Business Case & ROI Simulator")

# --- Sidebar for Global Parameters ---
with st.sidebar:
    st.header("⚙️ Global Simulation Parameters")
    global_params_input = {}
    # ... (Keep all global parameter inputs as before) ...
    global_params_input["operating_days_per_year"] = st.number_input("Operating Days per Year (All Machines)", min_value=100, max_value=365, value=DEFAULT_GLOBAL_PARAMS["operating_days_per_year"], step=5, key="global_op_days")

    st.subheader("Leasing Model Globals")
    global_params_input["lessor_target_profit_margin"] = st.slider("Lessor Target Profit Margin (%)", 0.01, 0.90, DEFAULT_GLOBAL_PARAMS["lessor_target_profit_margin"], 0.01, format="%.2f", key="global_profit_margin")
    global_params_input["machine_utilization_leasing_days_per_machine"] = st.number_input("Machine Utilization Days (Leasing, Per Machine)", 1, global_params_input["operating_days_per_year"], DEFAULT_GLOBAL_PARAMS["machine_utilization_leasing_days_per_machine"], 5, key="global_util_days")

    st.subheader("Villa & Material Globals (3DCP)")
    global_params_input["powder_cost_per_ton"] = st.number_input("Powder Cost per Ton (AED)", 100, value=DEFAULT_GLOBAL_PARAMS["powder_cost_per_ton"], step=10, key="global_powder_cost")
    global_params_input["powder_tons_per_villa"] = st.number_input("Powder Tons per Villa", 10, value=DEFAULT_GLOBAL_PARAMS["powder_tons_per_villa"], step=5, key="global_powder_tons")
    global_params_input["steel_cables_cost_per_villa"] = st.number_input("Steel & Cables Cost per Villa (AED)", 0, value=DEFAULT_GLOBAL_PARAMS["steel_cables_cost_per_villa"], step=1000, key="global_steel_cost")
    global_params_input["villa_printing_days_3dcp"] = st.number_input("Villa Printing Days (3DCP)", 5, value=DEFAULT_GLOBAL_PARAMS["villa_printing_days_3dcp"], step=1, key="global_print_days")
    global_params_input["villa_additional_prep_finish_days_3dcp"] = st.number_input("Villa Additional Prep/Finish Days (3DCP)", 0, value=DEFAULT_GLOBAL_PARAMS["villa_additional_prep_finish_days_3dcp"], step=1, key="global_prep_days")
    global_params_input["market_selling_price_per_villa"] = st.number_input("Market Selling Price per Villa (AED)", 500000, value=DEFAULT_GLOBAL_PARAMS["market_selling_price_per_villa"], step=50000, key="global_sell_price")

    st.subheader("Savings & Cost Basis (vs. Traditional)")
    global_params_input["unoptimised_villa_cost_baseline_traditional"] = st.number_input("Traditional Villa Cost Baseline (AED - for savings calc)", 500000, value=DEFAULT_GLOBAL_PARAMS["unoptimised_villa_cost_baseline_traditional"], step=50000, key="global_trad_baseline")
    global_params_input["labor_savings_absolute_3dcp"] = st.number_input("3DCP Labor Savings (Absolute AED)", 0, value=DEFAULT_GLOBAL_PARAMS["labor_savings_absolute_3dcp"], step=10000, key="global_labor_save")
    global_params_input["formwork_savings_absolute_3dcp"] = st.number_input("3DCP Formwork Savings (Absolute AED)", 0, value=DEFAULT_GLOBAL_PARAMS["formwork_savings_absolute_3dcp"], step=5000, key="global_form_save")
    global_params_input["waste_reduction_savings_absolute_3dcp"] = st.number_input("3DCP Waste Reduction Savings (Absolute AED)", 0, value=DEFAULT_GLOBAL_PARAMS["waste_reduction_savings_absolute_3dcp"], step=5000, key="global_waste_save")
    global_params_input["time_related_overhead_savings_absolute_3dcp"] = st.number_input("3DCP Time-Overhead Savings (Absolute AED)", 0, value=DEFAULT_GLOBAL_PARAMS["time_related_overhead_savings_absolute_3dcp"], step=5000, key="global_time_save")

    st.subheader("Traditional Model Parameters (for Comparison)")
    global_params_input["traditional_villa_build_months"] = st.number_input("Traditional Villa Build Time (Months)", 1, value=DEFAULT_GLOBAL_PARAMS["traditional_villa_build_months"], step=1, key="global_trad_months")
    global_params_input["traditional_villa_cost"] = st.number_input("Traditional Villa Cost (AED - for comparison)", 500000, value=DEFAULT_GLOBAL_PARAMS["traditional_villa_cost"], step=50000, key="global_trad_cost")


# --- Machine Configuration Area ---
st.subheader("🛠️ Machine Fleet Configuration")
num_machines = st.number_input("Number of 3DCP Machines in Fleet", min_value=1, value=1, step=1, key="num_machines")

if 'machine_params_list' not in st.session_state or len(st.session_state.machine_params_list) != num_machines:
    st.session_state.machine_params_list_backup = st.session_state.get('machine_params_list', []) # Backup before overwrite
    st.session_state.machine_params_list = []
    for i in range(num_machines):
        new_machine = DEFAULT_SINGLE_MACHINE_PARAMS.copy()
        new_machine["id"] = i + 1
        if i < len(st.session_state.machine_params_list_backup):
             new_machine.update(st.session_state.machine_params_list_backup[i]) # Restore if possible
        st.session_state.machine_params_list.append(new_machine)

active_machine_params_list = []
# Display machine configs in expanders or columns
for i in range(num_machines):
    with st.expander(f"Machine {st.session_state.machine_params_list[i]['id']} Parameters", expanded=(i==0)): # Expand first by default
        current_machine_input = st.session_state.machine_params_list[i]
        # ... (Keep machine parameter inputs as before, ensuring unique keys) ...
        current_machine_input["machine_cost"] = st.number_input(f"Cost (AED)##{i}", 100000, value=current_machine_input["machine_cost"], step=50000, key=f"m_cost_{i}")
        current_machine_input["machine_lifespan_years"] = st.number_input(f"Lifespan (Years)##{i}", 1, value=current_machine_input["machine_lifespan_years"], step=1, key=f"m_life_{i}")
        current_machine_input["annual_maintenance_cost_pct"] = st.slider(f"Maintenance (% Cost)##{i}", 0.01, 0.30, current_machine_input["annual_maintenance_cost_pct"], 0.01, format="%.2f", key=f"m_maint_{i}")
        current_machine_input["engineer_monthly_salary"] = st.number_input(f"Engineer Salary (AED/month)##{i}", 0, value=current_machine_input["engineer_monthly_salary"], step=500, key=f"m_eng_{i}")
        active_machine_params_list.append(current_machine_input)

# --- Simulation Execution and Dashboard Display ---
if st.button("🚀 Run Simulation & Generate Dashboard", key="run_sim_button", type="primary"):
    if not active_machine_params_list:
        st.error("Please configure at least one machine.")
    else:
        # Calculate average daily op cost for per-villa metrics if machines are different
        avg_daily_op_cost_fleet = sum(calculate_machine_operational_costs(mp, global_params_input)[1] for mp in active_machine_params_list) / len(active_machine_params_list)
        contracting_villa_details_output = calculate_contracting_model_per_villa(avg_daily_op_cost_fleet, global_params_input)
        prod_turnover_output = calculate_productivity_and_turnover(num_machines, active_machine_params_list, global_params_input, contracting_villa_details_output)

        st.header("📊 Simulation Dashboard")

        # --- Key Performance Indicators (KPIs) ---
        st.subheader("📈 Key Performance Indicators (3DCP Fleet Contracting)")
        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Annual Net Profit (Fleet)", f"AED {prod_turnover_output['annual_profit_3dcp_fleet_contracting']:,.0f}")
        kpi_cols[1].metric("Annual ROI (Fleet)", f"{prod_turnover_output['roi_3dcp_fleet_contracting']:.2f}%")
        kpi_cols[2].metric("Profit per Villa (Avg)", f"AED {prod_turnover_output['profit_per_3dcp_villa_fleet_avg']:,.0f}")
        kpi_cols[3].metric("Total Villas/Year (Fleet)", f"{prod_turnover_output['total_villas_per_year_3dcp_fleet']:.1f}")

        # --- Financial Performance Charts ---
        st.subheader("💰 Financial Performance Comparison")
        fin_cols = st.columns(2)
        # Chart 1: Profit Comparison
        profit_data = pd.DataFrame({
            'Model': ['3DCP Fleet Contracting', 'Traditional Equivalent Effort'],
            'Annual Net Profit (AED)': [
                prod_turnover_output['annual_profit_3dcp_fleet_contracting'],
                prod_turnover_output['annual_profit_traditional_equivalent_effort']
            ]
        })
        fig_profit = px.bar(profit_data, x='Model', y='Annual Net Profit (AED)', title='Annual Profit Comparison',
                            color='Model', labels={'Annual Net Profit (AED)': 'Annual Profit (AED)'},
                            text_auto=True)
        fig_profit.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
        fin_cols[0].plotly_chart(fig_profit, use_container_width=True)

        # Chart 2: ROI vs Capital
        roi_data = pd.DataFrame({
            'Metric': ['Total Capital Invested (3DCP)', 'Annual ROI (3DCP)'],
            'Value': [prod_turnover_output['total_capital_invested_fleet'], prod_turnover_output['roi_3dcp_fleet_contracting']],
            'Type': ['Capital (AED)', 'ROI (%)']
        })
        # For ROI, it's better as a metric or text. A bar chart needs careful scaling.
        # Using a simple display here.
        fin_cols[1].markdown(f"**Total Capital Invested (3DCP Fleet):** AED {prod_turnover_output['total_capital_invested_fleet']:,.0f}")
        fin_cols[1].markdown(f"**Achieved Annual ROI (3DCP Fleet):** {prod_turnover_output['roi_3dcp_fleet_contracting']:.2f}%")
        
        # Chart 3: Cost Breakdown per Villa (3DCP vs Traditional)
        cost_breakdown_data = [
            {'Component': 'Machine Ops', 'Cost': contracting_villa_details_output['machine_op_cost_for_project_per_villa'], 'Type': '3DCP Villa'},
            {'Component': 'Powder', 'Cost': contracting_villa_details_output['powder_cost_for_villa'], 'Type': '3DCP Villa'},
            {'Component': 'Steel/Cables', 'Cost': global_params_input['steel_cables_cost_per_villa'], 'Type': '3DCP Villa'},
            {'Component': 'Other (Non-Shell)', 'Cost': global_params_input['unoptimised_villa_cost_baseline_traditional'] - contracting_villa_details_output['total_identified_savings_vs_traditional_shell_per_villa'], 'Type': '3DCP Villa'},
            {'Component': 'Full Traditional Cost', 'Cost': global_params_input['traditional_villa_cost'], 'Type': 'Traditional Villa'}
        ]
        df_cost_breakdown = pd.DataFrame(cost_breakdown_data)
        
        # Sum 3DCP costs for comparison
        total_3dcp_cost_villa = contracting_villa_details_output['optimized_total_cost_per_3dcp_villa']
        
        cost_comparison_data = pd.DataFrame({
            'Villa Type': ['3DCP Villa', 'Traditional Villa'],
            'Total Cost per Villa (AED)': [total_3dcp_cost_villa, global_params_input['traditional_villa_cost']]
        })
        fig_cost_comp = px.bar(cost_comparison_data, x='Villa Type', y='Total Cost per Villa (AED)',
                                 title='Total Cost per Villa Comparison', color='Villa Type', text_auto=True)
        fig_cost_comp.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
        fin_cols[1].plotly_chart(fig_cost_comp, use_container_width=True)


        # --- Productivity & Efficiency Charts ---
        st.subheader("⏱️ Productivity & Efficiency")
        prod_cols = st.columns(2)
        # Chart 4: Villas Built Per Year
        villas_data = pd.DataFrame({
            'Production Method': [
                f"3DCP Fleet ({num_machines} machines)",
                f"Traditional Equivalent ({num_machines} teams)"
            ],
            'Villas per Year': [
                prod_turnover_output['total_villas_per_year_3dcp_fleet'],
                prod_turnover_output['total_villas_per_year_traditional_equivalent_effort']
            ]
        })
        fig_villas = px.bar(villas_data, x='Production Method', y='Villas per Year', title='Annual Villa Production Capacity',
                             color='Production Method', text_auto=True)
        fig_villas.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        prod_cols[0].plotly_chart(fig_villas, use_container_width=True)

        # Chart 5: Project Timeline Comparison
        timeline_data = pd.DataFrame({
            'Method': ['3DCP Villa Cycle', 'Traditional Villa Build'],
            'Duration (Days)': [
                prod_turnover_output['villa_total_cycle_days_3dcp'],
                prod_turnover_output['traditional_villa_build_days']
            ]
        })
        fig_timeline = px.bar(timeline_data, y='Method', x='Duration (Days)', title='Project Duration per Villa',
                                orientation='h', color='Method', text_auto=True)
        fig_timeline.update_traces(texttemplate='%{x:.0f} days', textposition='outside')
        prod_cols[1].plotly_chart(fig_timeline, use_container_width=True)
        
        # --- Savings ---
        st.subheader("💸 Savings per Villa (3DCP vs. Traditional)")
        sav_cols = st.columns(2)
        sav_cols[0].metric("Cost Saving per Villa", f"AED {prod_turnover_output['cost_saving_per_villa_3dcp_vs_traditional']:,.0f}")
        sav_cols[1].metric("Time Saving per Villa", f"{prod_turnover_output['time_saving_per_villa_3dcp_vs_traditional_days']:.0f} Days")


        # --- Leasing Model Insights (Representative) ---
        st.subheader("🔑 Leasing Model Insights (Representative - First Machine)")
        if active_machine_params_list:
            rep_machine_params_leasing = active_machine_params_list[0] # First machine as representative
            leasing_output_rep = calculate_leasing_model_for_machine(rep_machine_params_leasing, global_params_input)
            st.markdown(f"**For Machine {rep_machine_params_leasing['id']}:**")
            lease_cols = st.columns(3)
            lease_cols[0].metric("Recommended Daily Lease Price", f"AED {leasing_output_rep['recommended_daily_lease_price_per_machine']:,.0f}")
            lease_cols[1].metric(f"Annual Profit (Leasing this machine, {global_params_input['machine_utilization_leasing_days_per_machine']} days util.)", f"AED {leasing_output_rep['annual_profit_lessor_per_machine_at_utilization']:,.0f}")
            lease_cols[2].metric("Contractor's 3DCP Cost/Villa (via leasing)", f"AED {leasing_output_rep['contractor_3dcp_elements_cost_per_villa_via_leasing']:,.0f}")
            if len(active_machine_params_list) > 1:
                st.caption("Note: Leasing insights above are for the first configured machine. For a fleet with varied machines, leasing profitability would be assessed per machine type.")
        else:
            st.warning("No machines configured for leasing model insights.")

else:
    st.info("Adjust global parameters and machine configurations, then click 'Run Simulation & Generate Dashboard'.")

st.markdown("---")
st.caption("Simulator v2.1: Includes ROI and graphical dashboard. All calculations are based on input parameters; review assumptions carefully.")
