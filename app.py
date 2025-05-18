import streamlit as st
import pandas as pd
import plotly.express as px
import json # For saving/loading scenarios
import numpy_financial as npf # For IRR/NPV (pip install numpy-financial)

# --- DEFAULT PARAMETERS ---
DEFAULT_SINGLE_MACHINE_PARAMS = {
    "id": 1,
    "machine_cost": 1000000,
    "machine_lifespan_years": 4,
    "annual_maintenance_cost_pct": 0.10,
    "engineer_monthly_salary": 7000,
}

DEFAULT_GLOBAL_PARAMS = {
    "operating_days_per_year": 250,
    "discount_rate_for_npv": 0.10, # 10% discount rate
    # Leasing
    "lessor_target_profit_margin": 0.40,
    "machine_utilization_leasing_days_per_machine": 200,
    # Villa & Material (3DCP)
    "powder_cost_per_ton": 700,
    "powder_tons_per_villa": 100,
    "steel_cables_cost_per_villa": 25000,
    "villa_printing_days_3dcp": 30,
    "villa_additional_prep_finish_days_3dcp": 15,
    "market_selling_price_per_villa": 2200000,
    # Detailed 3DCP Villa Costs (Excluding 3DCP Shell Process itself)
    "cost_foundation_per_villa_3dcp": 80000,
    "cost_roofing_per_villa_3dcp": 100000,
    "cost_mep_per_villa_3dcp": 120000,
    "cost_finishes_per_villa_3dcp": 150000,
    "cost_site_prep_approvals_design_3dcp": 50000,
    # Traditional Model
    "traditional_villa_build_months": 9,
    "traditional_villa_cost": 1300000, # This is the all-in cost for comparison
}

# --- CALCULATION FUNCTIONS ---
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
    # 3DCP Shell Process Costs (Machine part + materials for shell)
    machine_op_cost_for_project_per_villa = machine_daily_op_cost * global_params["villa_printing_days_3dcp"]
    results["machine_op_cost_for_project_per_villa"] = machine_op_cost_for_project_per_villa 

    powder_cost_for_villa = global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"]
    steel_cables_cost = global_params["steel_cables_cost_per_villa"]
    total_3dcp_shell_process_cost = machine_op_cost_for_project_per_villa + powder_cost_for_villa + steel_cables_cost
    results["total_3dcp_shell_process_cost_per_villa"] = total_3dcp_shell_process_cost

    # Other Direct Villa Costs (3DCP) - Foundation, Roofing, MEP, Finishes, Site Prep/Design
    other_direct_costs_3dcp = (
        global_params["cost_foundation_per_villa_3dcp"] +
        global_params["cost_roofing_per_villa_3dcp"] +
        global_params["cost_mep_per_villa_3dcp"] +
        global_params["cost_finishes_per_villa_3dcp"] +
        global_params["cost_site_prep_approvals_design_3dcp"]
    )
    results["other_direct_costs_per_villa_3dcp"] = other_direct_costs_3dcp
    
    optimized_total_cost_per_3dcp_villa = total_3dcp_shell_process_cost + other_direct_costs_3dcp
    results["optimized_total_cost_per_3dcp_villa"] = optimized_total_cost_per_3dcp_villa
    
    profit_per_3dcp_villa = global_params["market_selling_price_per_villa"] - optimized_total_cost_per_3dcp_villa
    results["profit_per_3dcp_villa"] = profit_per_3dcp_villa
    return results

def calculate_fleet_contracting_financials(num_machines, list_of_machine_params, global_params, contracting_villa_details):
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

    total_annual_fleet_machine_op_costs = sum(calculate_machine_operational_costs(mp, global_params)[0] for mp in list_of_machine_params)
    
    variable_shell_material_cost_per_villa = (global_params["powder_cost_per_ton"] * global_params["powder_tons_per_villa"] +
                                             global_params["steel_cables_cost_per_villa"])
    total_annual_variable_shell_material_costs_fleet = variable_shell_material_cost_per_villa * total_villas_per_year_3dcp_fleet

    variable_other_direct_costs_per_villa = contracting_villa_details["other_direct_costs_per_villa_3dcp"]
    total_annual_other_direct_costs_fleet = variable_other_direct_costs_per_villa * total_villas_per_year_3dcp_fleet
    
    total_annual_cost_3dcp_fleet_contracting = (total_annual_fleet_machine_op_costs + 
                                                total_annual_variable_shell_material_costs_fleet + 
                                                total_annual_other_direct_costs_fleet)
    results["total_annual_cost_3dcp_fleet_contracting"] = total_annual_cost_3dcp_fleet_contracting
    
    annual_profit_3dcp_fleet_contracting = annual_revenue_3dcp_fleet - total_annual_cost_3dcp_fleet_contracting
    results["annual_profit_3dcp_fleet_contracting"] = annual_profit_3dcp_fleet_contracting
    results["profit_per_3dcp_villa_fleet_avg"] = contracting_villa_details.get("profit_per_3dcp_villa", 0) 
    
    if total_capital_invested_fleet > 0:
        results["roi_3dcp_fleet_contracting"] = (annual_profit_3dcp_fleet_contracting / total_capital_invested_fleet) * 100
    else:
        results["roi_3dcp_fleet_contracting"] = 0

    cash_flows = [-total_capital_invested_fleet] 
    machine_lifespan_for_npv = int(max(mp["machine_lifespan_years"] for mp in list_of_machine_params) if list_of_machine_params else 1)

    for _ in range(machine_lifespan_for_npv): 
        cash_flows.append(annual_profit_3dcp_fleet_contracting)
    
    try:
        results["npv_3dcp_fleet"] = npf.npv(global_params["discount_rate_for_npv"], cash_flows)
        results["irr_3dcp_fleet"] = npf.irr(cash_flows) * 100 if len(cash_flows) > 1 and not (len(set(cash_flows[1:])) <= 1 and cash_flows[1] <= 0) else "N/A (Check Cash Flows)"
    except Exception as e: 
        results["npv_3dcp_fleet"] = "N/A"
        results["irr_3dcp_fleet"] = "N/A (Error)"

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

    fixed_costs_fleet = total_annual_fleet_machine_op_costs 
    total_variable_costs_per_villa = variable_shell_material_cost_per_villa + variable_other_direct_costs_per_villa
    contribution_margin_per_villa = (global_params["market_selling_price_per_villa"] - total_variable_costs_per_villa)
                                     
    if contribution_margin_per_villa > 0:
        results["break_even_villas_fleet"] = fixed_costs_fleet / contribution_margin_per_villa
    else:
        results["break_even_villas_fleet"] = "N/A (CM <= 0)" 
        
    return results

def get_all_inputs_as_dict(global_inputs_from_ss, machine_list_from_ss):
    # Global inputs are already in the correct format if taken from session_state
    # Machine list is also in the correct format
    return {
        "global_params": global_inputs_from_ss,
        "machine_params_list": machine_list_from_ss,
        "num_machines": len(machine_list_from_ss) 
    }

def load_scenario_into_session_state(scenario_data):
    loaded_global = scenario_data.get("global_params", {})
    loaded_machines_list = scenario_data.get("machine_params_list", [])
    loaded_num_machines = scenario_data.get("num_machines", 1)

    for key, value in loaded_global.items():
        session_key = f"global_{key}" 
        if session_key in st.session_state: 
             st.session_state[session_key] = value

    st.session_state.num_machines_widget = loaded_num_machines 
    
    new_machine_params_list_for_ss = []
    for i in range(loaded_num_machines):
        machine_data = loaded_machines_list[i] if i < len(loaded_machines_list) else DEFAULT_SINGLE_MACHINE_PARAMS.copy()
        
        machine_id = machine_data.get("id", i + 1)
        cost = machine_data.get("machine_cost", DEFAULT_SINGLE_MACHINE_PARAMS["machine_cost"])
        lifespan = machine_data.get("machine_lifespan_years", DEFAULT_SINGLE_MACHINE_PARAMS["machine_lifespan_years"])
        maintenance_pct = machine_data.get("annual_maintenance_cost_pct", DEFAULT_SINGLE_MACHINE_PARAMS["annual_maintenance_cost_pct"])
        engineer_salary = machine_data.get("engineer_monthly_salary", DEFAULT_SINGLE_MACHINE_PARAMS["engineer_monthly_salary"])

        new_machine_params_list_for_ss.append({
            "id": machine_id, "machine_cost": cost, "machine_lifespan_years": lifespan,
            "annual_maintenance_cost_pct": maintenance_pct, "engineer_monthly_salary": engineer_salary
        })
        
        st.session_state[f"m_cost_{i}"] = cost
        st.session_state[f"m_life_{i}"] = lifespan
        st.session_state[f"m_maint_{i}"] = maintenance_pct
        st.session_state[f"m_eng_{i}"] = engineer_salary
    
    st.session_state.machine_params_list = new_machine_params_list_for_ss
    # Call the on_change handler for num_machines_widget to ensure consistency
    # This will trigger the resizing of machine_params_list if num_machines changed
    update_num_machines_internal()


st.set_page_config(layout="wide", page_title="Advanced 3DCP Business Simulator")
st.title("🏗️ Advanced 3DCP Business Case & Financial Simulator")

# Initialize session state for global parameters based on DEFAULT_GLOBAL_PARAMS
for key, value in DEFAULT_GLOBAL_PARAMS.items():
    session_key_global = f"global_{key}"
    if session_key_global not in st.session_state:
        st.session_state[session_key_global] = value

if 'num_machines_widget' not in st.session_state: 
    st.session_state.num_machines_widget = 1
# Initialize machine_params_list based on num_machines_widget if it's not set or size mismatch
if 'machine_params_list' not in st.session_state or len(st.session_state.machine_params_list) != st.session_state.num_machines_widget:
    st.session_state.machine_params_list = []
    for i in range(st.session_state.num_machines_widget):
        new_m = DEFAULT_SINGLE_MACHINE_PARAMS.copy()
        new_m["id"] = i + 1
        st.session_state.machine_params_list.append(new_m)
        # Also initialize individual machine widget session states
        st.session_state[f"m_cost_{i}"] = new_m["machine_cost"]
        st.session_state[f"m_life_{i}"] = new_m["machine_lifespan_years"]
        st.session_state[f"m_maint_{i}"] = new_m["annual_maintenance_cost_pct"]
        st.session_state[f"m_eng_{i}"] = new_m["engineer_monthly_salary"]


with st.sidebar:
    st.header("⚙️ Global Simulation Parameters")
    st.session_state.global_operating_days_per_year = st.number_input("Operating Days/Year", 100, 365, st.session_state.global_operating_days_per_year, 5, key="widget_global_operating_days_per_year", help="Total productive days available for machines annually.")
    st.session_state.global_discount_rate_for_npv = st.slider("Discount Rate for NPV/IRR (%)", 0.01, 0.25, st.session_state.global_discount_rate_for_npv, 0.01, format="%.2f", key="widget_global_discount_rate_for_npv", help="Rate used to discount future cash flows for NPV calculation.")

    st.subheader("Leasing Model Globals")
    st.session_state.global_lessor_target_profit_margin = st.slider("Lessor Target Profit Margin (%)", 0.01, 0.90, st.session_state.global_lessor_target_profit_margin, 0.01, format="%.2f", key="widget_global_lessor_target_profit_margin", help="Desired profit margin for the lessor on leasing operations.")
    st.session_state.global_machine_utilization_leasing_days_per_machine = st.number_input("Machine Util. Days (Leasing)", 1, st.session_state.global_operating_days_per_year, st.session_state.global_machine_utilization_leasing_days_per_machine, 5, key="widget_global_machine_utilization_leasing_days_per_machine", help="Expected number of days each machine will be leased out per year.")

    st.subheader("Villa Construction & Material Globals (3DCP)")
    st.session_state.global_powder_cost_per_ton = st.number_input("Powder Cost/Ton (AED)", 100, value=st.session_state.global_powder_cost_per_ton, step=10, key="widget_global_powder_cost_per_ton", help="Cost of 1 ton of 3D printing powder.")
    st.session_state.global_powder_tons_per_villa = st.number_input("Powder Tons/Villa", 10, value=st.session_state.global_powder_tons_per_villa, step=5, key="widget_global_powder_tons_per_villa", help="Amount of powder required for one villa.")
    st.session_state.global_steel_cables_cost_per_villa = st.number_input("Steel/Cables Cost/Villa (AED)", 0, value=st.session_state.global_steel_cables_cost_per_villa, step=1000, key="widget_global_steel_cables_cost_per_villa", help="Cost of steel reinforcement and cables per villa.")
    st.session_state.global_villa_printing_days_3dcp = st.number_input("Villa Printing Days (3DCP)", 5, value=st.session_state.global_villa_printing_days_3dcp, step=1, key="widget_global_villa_printing_days_3dcp", help="Number of days the 3D printer is actively printing for one villa.")
    st.session_state.global_villa_additional_prep_finish_days_3dcp = st.number_input("Villa Additional Prep/Finish Days (3DCP)", 0, value=st.session_state.global_villa_additional_prep_finish_days_3dcp, step=1, key="widget_global_villa_additional_prep_finish_days_3dcp", help="Additional days for site prep, machine setup, and post-printing finishing related to one villa cycle.")
    st.session_state.global_market_selling_price_per_villa = st.number_input("Market Selling Price/Villa (AED)", 500000, value=st.session_state.global_market_selling_price_per_villa, step=50000, key="widget_global_market_selling_price_per_villa", help="Expected selling price for a completed villa.")

    st.subheader("Detailed 3DCP Villa Costs (Excl. 3DCP Shell Process)")
    st.session_state.global_cost_foundation_per_villa_3dcp = st.number_input("Foundation Cost/Villa (AED)", 0, value=st.session_state.global_cost_foundation_per_villa_3dcp, step=5000, key="widget_global_cost_foundation_per_villa_3dcp")
    st.session_state.global_cost_roofing_per_villa_3dcp = st.number_input("Roofing Cost/Villa (AED)", 0, value=st.session_state.global_cost_roofing_per_villa_3dcp, step=5000, key="widget_global_cost_roofing_per_villa_3dcp")
    st.session_state.global_cost_mep_per_villa_3dcp = st.number_input("MEP Cost/Villa (AED)", 0, value=st.session_state.global_cost_mep_per_villa_3dcp, step=5000, key="widget_global_cost_mep_per_villa_3dcp")
    st.session_state.global_cost_finishes_per_villa_3dcp = st.number_input("Finishes Cost/Villa (AED)", 0, value=st.session_state.global_cost_finishes_per_villa_3dcp, step=5000, key="widget_global_cost_finishes_per_villa_3dcp")
    st.session_state.global_cost_site_prep_approvals_design_3dcp = st.number_input("Site Prep/Approvals/Design Cost/Villa (AED)", 0, value=st.session_state.global_cost_site_prep_approvals_design_3dcp, step=5000, key="widget_global_cost_site_prep_approvals_design_3dcp")

    st.subheader("Traditional Model Parameters (for Comparison)")
    st.session_state.global_traditional_villa_build_months = st.number_input("Traditional Villa Build Time (Months)", 1, value=st.session_state.global_traditional_villa_build_months, step=1, key="widget_global_traditional_villa_build_months", help="Typical time to build a villa using traditional methods.")
    st.session_state.global_traditional_villa_cost = st.number_input("Traditional Villa All-in Cost (AED)", 500000, value=st.session_state.global_traditional_villa_cost, step=50000, key="widget_global_traditional_villa_cost", help="Total cost to build a villa using traditional methods, for direct comparison.")
    
    current_global_inputs_for_saving = {k: st.session_state[f"global_{k}"] for k in DEFAULT_GLOBAL_PARAMS.keys()}
    
    st.subheader("Scenario Management")
    current_scenario_data_to_save = get_all_inputs_as_dict(current_global_inputs_for_saving, st.session_state.machine_params_list)
    st.download_button(
        label="📥 Save Current Scenario",
        data=json.dumps(current_scenario_data_to_save, indent=2),
        file_name="3dcp_scenario.json",
        mime="application/json"
    )
    uploaded_file = st.file_uploader("📤 Load Scenario from JSON", type="json", key="scenario_uploader")
    if uploaded_file is not None:
        try:
            loaded_scenario_data = json.load(uploaded_file)
            load_scenario_into_session_state(loaded_scenario_data)
            st.success("Scenario loaded! Input fields updated.")
            st.session_state.scenario_uploader = None 
            st.experimental_rerun() 
        except json.JSONDecodeError: st.error("Invalid JSON file.")
        except Exception as e: st.error(f"Error loading scenario: {e}")


st.subheader("🛠️ Machine Fleet Configuration")

def update_num_machines_internal():
    # Target number of machines based on the widget
    target_num_machines = st.session_state.num_machines_widget
    current_num_machines = len(st.session_state.machine_params_list)

    if target_num_machines > current_num_machines: # Add machines
        for i in range(current_num_machines, target_num_machines):
            new_m = DEFAULT_SINGLE_MACHINE_PARAMS.copy()
            new_m["id"] = i + 1
            st.session_state.machine_params_list.append(new_m)
            # Initialize session state for new widget keys
            st.session_state[f"m_cost_{i}"] = new_m["machine_cost"]
            st.session_state[f"m_life_{i}"] = new_m["machine_lifespan_years"]
            st.session_state[f"m_maint_{i}"] = new_m["annual_maintenance_cost_pct"]
            st.session_state[f"m_eng_{i}"] = new_m["engineer_monthly_salary"]
    elif target_num_machines < current_num_machines: # Remove machines
        st.session_state.machine_params_list = st.session_state.machine_params_list[:target_num_machines]
        # Optionally, clean up unused session state keys for removed machines (more complex)

st.number_input(
    "Number of 3DCP Machines", 1, 10, 
    key="num_machines_widget", 
    on_change=update_num_machines_internal 
)
# Ensure consistency after potential load scenario
if st.session_state.num_machines_widget != len(st.session_state.machine_params_list):
    update_num_machines_internal()


active_machine_params_list_for_calc = [] 
for i in range(st.session_state.num_machines_widget): 
    if i >= len(st.session_state.machine_params_list): # Should not happen if update_num_machines_internal works
        continue 

    machine_obj_for_display = st.session_state.machine_params_list[i] 

    with st.expander(f"Machine {machine_obj_for_display.get('id', i+1)} Parameters", expanded=(i==0)):
        cost_key = f"m_cost_{i}"
        life_key = f"m_life_{i}"
        maint_key = f"m_maint_{i}"
        eng_key = f"m_eng_{i}"

        # Ensure session state keys exist, using values from machine_params_list as default
        if cost_key not in st.session_state: st.session_state[cost_key] = machine_obj_for_display["machine_cost"]
        if life_key not in st.session_state: st.session_state[life_key] = machine_obj_for_display["machine_lifespan_years"]
        if maint_key not in st.session_state: st.session_state[maint_key] = machine_obj_for_display["annual_maintenance_cost_pct"]
        if eng_key not in st.session_state: st.session_state[eng_key] = machine_obj_for_display["engineer_monthly_salary"]
        
        st.number_input(f"Cost (AED)", 100000, value=st.session_state[cost_key], step=50000, key=cost_key)
        st.number_input(f"Lifespan (Years)", 1, value=st.session_state[life_key], step=1, key=life_key)
        st.slider(f"Maintenance (% Cost)", 0.01, 0.30, st.session_state[maint_key], 0.01, format="%.2f", key=maint_key)
        st.number_input(f"Engineer Salary (AED/month)", 0, value=st.session_state[eng_key], step=500, key=eng_key)

        st.session_state.machine_params_list[i]["machine_cost"] = st.session_state[cost_key]
        st.session_state.machine_params_list[i]["machine_lifespan_years"] = st.session_state[life_key]
        st.session_state.machine_params_list[i]["annual_maintenance_cost_pct"] = st.session_state[maint_key]
        st.session_state.machine_params_list[i]["engineer_monthly_salary"] = st.session_state[eng_key]
        st.session_state.machine_params_list[i]["id"] = machine_obj_for_display.get('id', i+1)

        active_machine_params_list_for_calc.append(st.session_state.machine_params_list[i])


if st.button("🚀 Run Simulation & Generate Dashboard", key="run_sim_button", type="primary"):
    if not active_machine_params_list_for_calc: 
        st.error("Please configure at least one machine.")
    else:
        current_global_params_for_calc = {k: st.session_state[f"global_{k}"] for k in DEFAULT_GLOBAL_PARAMS.keys()}

        avg_daily_op_cost_fleet = sum(calculate_machine_operational_costs(mp, current_global_params_for_calc)[1] for mp in active_machine_params_list_for_calc) / len(active_machine_params_list_for_calc)
        contracting_villa_details_output = calculate_contracting_model_per_villa(avg_daily_op_cost_fleet, current_global_params_for_calc)
        fleet_financials_output = calculate_fleet_contracting_financials(st.session_state.num_machines_widget, active_machine_params_list_for_calc, current_global_params_for_calc, contracting_villa_details_output)

        st.header("📊 Simulation Dashboard")
        st.subheader("📈 Key Financial Indicators (3DCP Fleet Contracting)")
        kpi_cols = st.columns(5)
        kpi_cols[0].metric("Annual Net Profit", f"AED {fleet_financials_output['annual_profit_3dcp_fleet_contracting']:,.0f}", help="Total revenue minus total costs for the fleet's contracting operations annually.")
        kpi_cols[1].metric("Annual ROI", f"{fleet_financials_output['roi_3dcp_fleet_contracting']:.2f}%" if isinstance(fleet_financials_output['roi_3dcp_fleet_contracting'], (int,float)) else "N/A", help="Return on Investment: (Annual Profit / Total Capital Invested) * 100.")
        kpi_cols[2].metric("NPV (Net Present Value)", f"AED {fleet_financials_output['npv_3dcp_fleet']:,.0f}" if isinstance(fleet_financials_output['npv_3dcp_fleet'], (int, float)) else fleet_financials_output['npv_3dcp_fleet'], help=f"Present value of future cash flows minus initial investment, discounted at {current_global_params_for_calc['discount_rate_for_npv']*100:.0f}%.")
        kpi_cols[3].metric("IRR (Internal Rate of Return)", f"{fleet_financials_output['irr_3dcp_fleet']:.2f}%" if isinstance(fleet_financials_output['irr_3dcp_fleet'], (int, float)) else fleet_financials_output['irr_3dcp_fleet'], help="Discount rate at which the NPV of all cash flows equals zero. Higher is better.")
        kpi_cols[4].metric("Break-Even Villas/Year", f"{fleet_financials_output['break_even_villas_fleet']:.1f}" if isinstance(fleet_financials_output['break_even_villas_fleet'], (int, float)) else fleet_financials_output['break_even_villas_fleet'], help="Number of villas the fleet needs to build and sell annually to cover all fixed operational costs.")

        st.subheader("💰 Financial Performance Comparison")
        fin_cols = st.columns(2)
        profit_data = pd.DataFrame({
            'Model': ['3DCP Fleet Contracting', 'Traditional Equivalent Effort'],
            'Annual Net Profit (AED)': [
                fleet_financials_output['annual_profit_3dcp_fleet_contracting'],
                fleet_financials_output['annual_profit_traditional_equivalent_effort']
            ]})
        fig_profit = px.bar(profit_data, x='Model', y='Annual Net Profit (AED)', title='Annual Profit Comparison', color='Model', text_auto=True)
        fig_profit.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
        fin_cols[0].plotly_chart(fig_profit, use_container_width=True)

        cost_comparison_data = pd.DataFrame({
            'Villa Type': ['3DCP Villa (Avg.)', 'Traditional Villa'],
            'Total Cost per Villa (AED)': [contracting_villa_details_output['optimized_total_cost_per_3dcp_villa'], current_global_params_for_calc['traditional_villa_cost']]
        })
        fig_cost_comp = px.bar(cost_comparison_data, x='Villa Type', y='Total Cost per Villa (AED)', title='Total Cost per Villa Comparison', color='Villa Type', text_auto=True)
        fig_cost_comp.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
        fin_cols[1].plotly_chart(fig_cost_comp, use_container_width=True)

        st.subheader("⏱️ Productivity & Efficiency")
        prod_cols = st.columns(2)
        villas_data = pd.DataFrame({
            'Production Method': [f"3DCP Fleet ({st.session_state.num_machines_widget} machines)", f"Traditional Equivalent ({st.session_state.num_machines_widget} teams)"],
            'Villas per Year': [fleet_financials_output['total_villas_per_year_3dcp_fleet'], fleet_financials_output['total_villas_per_year_traditional_equivalent_effort']]
        })
        fig_villas = px.bar(villas_data, x='Production Method', y='Villas per Year', title='Annual Villa Production Capacity', color='Production Method', text_auto=True)
        fig_villas.update_traces(texttemplate='%{y:.1f}', textposition='outside')
        prod_cols[0].plotly_chart(fig_villas, use_container_width=True)

        timeline_data = pd.DataFrame({
            'Method': ['3DCP Villa Cycle', 'Traditional Villa Build'],
            'Duration (Days)': [fleet_financials_output['villa_total_cycle_days_3dcp'], fleet_financials_output['traditional_villa_build_days']]
        })
        fig_timeline = px.bar(timeline_data, y='Method', x='Duration (Days)', title='Project Duration per Villa', orientation='h', color='Method', text_auto=True)
        fig_timeline.update_traces(texttemplate='%{x:.0f} days', textposition='outside')
        prod_cols[1].plotly_chart(fig_timeline, use_container_width=True)
        
        st.subheader("💸 Savings per Villa (3DCP vs. Traditional)")
        sav_cols = st.columns(2)
        sav_cols[0].metric("Cost Saving per Villa", f"AED {fleet_financials_output['cost_saving_per_villa_3dcp_vs_traditional']:,.0f}")
        sav_cols[1].metric("Time Saving per Villa", f"{fleet_financials_output['time_saving_per_villa_3dcp_vs_traditional_days']:.0f} Days")

        st.subheader("🔑 Leasing Model Insights (Representative - First Machine)")
        if active_machine_params_list_for_calc: 
            rep_machine_params_leasing = active_machine_params_list_for_calc[0]
            leasing_output_rep = calculate_leasing_model_for_machine(rep_machine_params_leasing, current_global_params_for_calc)
            st.markdown(f"**For Machine {rep_machine_params_leasing.get('id', 1)}:**") # Use .get for safety
            lease_cols = st.columns(3)
            lease_cols[0].metric("Rec. Daily Lease Price", f"AED {leasing_output_rep['recommended_daily_lease_price_per_machine']:,.0f}")
            lease_cols[1].metric(f"Annual Profit (Leasing, {current_global_params_for_calc['machine_utilization_leasing_days_per_machine']} days util.)", f"AED {leasing_output_rep['annual_profit_lessor_per_machine_at_utilization']:,.0f}")
            lease_cols[2].metric("Contractor's 3DCP Cost/Villa (via leasing)", f"AED {leasing_output_rep['contractor_3dcp_elements_cost_per_villa_via_leasing']:,.0f}")

else:
    st.info("Adjust parameters and click 'Run Simulation & Generate Dashboard'.")

st.markdown("---")
st.caption(f"Simulator v3.2: Session State Fixes. Review assumptions carefully.")
