{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fmodern\fcharset0 Courier;}
{\colortbl;\red255\green255\blue255;\red238\green88\blue85;\red27\green28\blue31;\red219\green219\blue223;
\red99\green112\blue125;\red134\green196\blue255;\red91\green165\blue255;\red211\green171\blue250;\red242\green139\blue64;
\red157\green172\blue187;}
{\*\expandedcolortbl;;\cssrgb\c95686\c43922\c40392;\cssrgb\c14118\c14902\c16078;\cssrgb\c88627\c88627\c89804;
\cssrgb\c46275\c51373\c56471;\cssrgb\c58824\c81569\c100000;\cssrgb\c42353\c71373\c100000;\cssrgb\c86275\c74118\c98431;\cssrgb\c96471\c61569\c31373;
\cssrgb\c67843\c72941\c78039;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11220\viewh8100\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs26 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import\cf4 \strokec4  streamlit \cf2 \strokec2 as\cf4 \strokec4  st\
\
\pard\pardeftab720\partightenfactor0
\cf5 \strokec5 # --- DEFAULT PARAMETERS (can be overridden by scenarios) ---\cf4 \strokec4 \
DEFAULT_PARAMS = \{\
    \cf6 \strokec6 "machine_cost"\cf4 \strokec4 : \cf7 \strokec7 1000000\cf4 \strokec4 ,\
    \cf6 \strokec6 "machine_lifespan_years"\cf4 \strokec4 : \cf7 \strokec7 4\cf4 \strokec4 ,\
    \cf6 \strokec6 "annual_maintenance_cost_pct"\cf4 \strokec4 : \cf7 \strokec7 0.10\cf4 \strokec4 , \cf5 \strokec5 # 10% of machine cost\cf4 \strokec4 \
    \cf6 \strokec6 "engineer_monthly_salary"\cf4 \strokec4 : \cf7 \strokec7 7000\cf4 \strokec4 ,\
    \cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 : \cf7 \strokec7 250\cf4 \strokec4 ,\
    \cf6 \strokec6 "lessor_target_profit_margin"\cf4 \strokec4 : \cf7 \strokec7 0.40\cf4 \strokec4 ,\
    \cf6 \strokec6 "machine_utilization_leasing_days"\cf4 \strokec4 : \cf7 \strokec7 200\cf4 \strokec4 , \cf5 \strokec5 # For leasing model annual profit calc\cf4 \strokec4 \
    \cf6 \strokec6 "powder_cost_per_ton"\cf4 \strokec4 : \cf7 \strokec7 700\cf4 \strokec4 ,\
    \cf6 \strokec6 "powder_tons_per_villa"\cf4 \strokec4 : \cf7 \strokec7 100\cf4 \strokec4 ,\
    \cf6 \strokec6 "steel_cables_cost_per_villa"\cf4 \strokec4 : \cf7 \strokec7 25000\cf4 \strokec4 ,\
    \cf6 \strokec6 "villa_printing_days"\cf4 \strokec4 : \cf7 \strokec7 30\cf4 \strokec4 ,\
    \cf6 \strokec6 "unoptimised_villa_cost_baseline"\cf4 \strokec4 : \cf7 \strokec7 1300000\cf4 \strokec4 ,\
    \cf6 \strokec6 "labor_savings_absolute"\cf4 \strokec4 : \cf7 \strokec7 120000\cf4 \strokec4 ,\
    \cf6 \strokec6 "formwork_savings_absolute"\cf4 \strokec4 : \cf7 \strokec7 60000\cf4 \strokec4 ,\
    \cf6 \strokec6 "waste_reduction_savings_absolute"\cf4 \strokec4 : \cf7 \strokec7 25000\cf4 \strokec4 ,\
    \cf6 \strokec6 "time_related_overhead_savings_absolute"\cf4 \strokec4 : \cf7 \strokec7 50000\cf4 \strokec4 ,\
    \cf6 \strokec6 "market_selling_price_per_villa"\cf4 \strokec4 : \cf7 \strokec7 2200000\cf4 \strokec4 ,\
    \cf6 \strokec6 "villas_built_per_year_contracting"\cf4 \strokec4 : \cf7 \strokec7 7\cf4 \strokec4 , \cf5 \strokec5 # For contracting model annual profit calc\cf4 \strokec4 \
\}\
\
\pard\pardeftab720\partightenfactor0
\cf2 \strokec2 def\cf4 \strokec4  \cf8 \strokec8 calculate_leasing_model\cf4 \strokec4 (params):\
    results = \{\}\
    annual_capital_recovery = params[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ] / params[\cf6 \strokec6 "machine_lifespan_years"\cf4 \strokec4 ]\
    annual_maintenance = params[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ] * params[\cf6 \strokec6 "annual_maintenance_cost_pct"\cf4 \strokec4 ]\
    annual_engineer_cost = params[\cf6 \strokec6 "engineer_monthly_salary"\cf4 \strokec4 ] * \cf7 \strokec7 12\cf4 \strokec4 \
    \
    total_annual_lessor_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost\
    results[\cf6 \strokec6 "total_annual_lessor_cost"\cf4 \strokec4 ] = total_annual_lessor_cost\
    \
    daily_lessor_cost = total_annual_lessor_cost / params[\cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "daily_lessor_cost"\cf4 \strokec4 ] = daily_lessor_cost\
    \
    \cf5 \strokec5 # Ensure profit margin is less than 1 to avoid division by zero or negative\cf4 \strokec4 \
    profit_margin_divisor = \cf7 \strokec7 1\cf4 \strokec4  - params[\cf6 \strokec6 "lessor_target_profit_margin"\cf4 \strokec4 ]\
    \cf2 \strokec2 if\cf4 \strokec4  profit_margin_divisor <= \cf7 \strokec7 0\cf4 \strokec4 :\
        profit_margin_divisor = \cf7 \strokec7 0.001\cf4 \strokec4  \cf5 \strokec5 # Avoid division by zero/negative\cf4 \strokec4 \
\
    recommended_daily_lease_price = daily_lessor_cost / profit_margin_divisor\
    results[\cf6 \strokec6 "recommended_daily_lease_price"\cf4 \strokec4 ] = recommended_daily_lease_price\
    \
    daily_profit_lessor = recommended_daily_lease_price - daily_lessor_cost\
    annual_profit_lessor = daily_profit_lessor * params[\cf6 \strokec6 "machine_utilization_leasing_days"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "annual_profit_lessor_at_utilization"\cf4 \strokec4 ] = annual_profit_lessor\
    \
    lease_cost_for_villa = recommended_daily_lease_price * params[\cf6 \strokec6 "villa_printing_days"\cf4 \strokec4 ]\
    powder_cost_for_villa_lease = params[\cf6 \strokec6 "powder_cost_per_ton"\cf4 \strokec4 ] * params[\cf6 \strokec6 "powder_tons_per_villa"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "contractor_3dcp_elements_cost_per_villa"\cf4 \strokec4 ] = lease_cost_for_villa + powder_cost_for_villa_lease + params[\cf6 \strokec6 "steel_cables_cost_per_villa"\cf4 \strokec4 ]\
    \
    \cf2 \strokec2 return\cf4 \strokec4  results\
\
\cf2 \strokec2 def\cf4 \strokec4  \cf8 \strokec8 calculate_contracting_model\cf4 \strokec4 (params):\
    results = \{\}\
    annual_capital_recovery = params[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ] / params[\cf6 \strokec6 "machine_lifespan_years"\cf4 \strokec4 ]\
    annual_maintenance = params[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ] * params[\cf6 \strokec6 "annual_maintenance_cost_pct"\cf4 \strokec4 ]\
    annual_engineer_cost = params[\cf6 \strokec6 "engineer_monthly_salary"\cf4 \strokec4 ] * \cf7 \strokec7 12\cf4 \strokec4 \
    total_annual_machine_op_cost = annual_capital_recovery + annual_maintenance + annual_engineer_cost\
    \
    machine_op_cost_per_day = total_annual_machine_op_cost / params[\cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 ]\
    machine_op_cost_for_project = machine_op_cost_per_day * params[\cf6 \strokec6 "villa_printing_days"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "machine_op_cost_for_project"\cf4 \strokec4 ] = machine_op_cost_for_project\
    \
    powder_cost_for_villa_contract = params[\cf6 \strokec6 "powder_cost_per_ton"\cf4 \strokec4 ] * params[\cf6 \strokec6 "powder_tons_per_villa"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "powder_cost_for_villa"\cf4 \strokec4 ] = powder_cost_for_villa_contract\
    \
    total_identified_savings = (params[\cf6 \strokec6 "labor_savings_absolute"\cf4 \strokec4 ] +\
                                params[\cf6 \strokec6 "formwork_savings_absolute"\cf4 \strokec4 ] +\
                                params[\cf6 \strokec6 "waste_reduction_savings_absolute"\cf4 \strokec4 ] +\
                                params[\cf6 \strokec6 "time_related_overhead_savings_absolute"\cf4 \strokec4 ])\
    results[\cf6 \strokec6 "total_identified_savings_per_villa"\cf4 \strokec4 ] = total_identified_savings\
    \
    adjusted_base_cost = params[\cf6 \strokec6 "unoptimised_villa_cost_baseline"\cf4 \strokec4 ] - total_identified_savings\
    \
    optimized_total_cost_per_villa = (adjusted_base_cost +\
                                      powder_cost_for_villa_contract +\
                                      params[\cf6 \strokec6 "steel_cables_cost_per_villa"\cf4 \strokec4 ] +\
                                      machine_op_cost_for_project)\
    results[\cf6 \strokec6 "optimized_total_cost_per_villa"\cf4 \strokec4 ] = optimized_total_cost_per_villa\
    \
    profit_per_villa = params[\cf6 \strokec6 "market_selling_price_per_villa"\cf4 \strokec4 ] - optimized_total_cost_per_villa\
    results[\cf6 \strokec6 "profit_per_villa"\cf4 \strokec4 ] = profit_per_villa\
    \
    annual_profit_contracting = profit_per_villa * params[\cf6 \strokec6 "villas_built_per_year_contracting"\cf4 \strokec4 ]\
    results[\cf6 \strokec6 "annual_profit_contracting"\cf4 \strokec4 ] = annual_profit_contracting\
    \
    \cf2 \strokec2 return\cf4 \strokec4  results\
\
\pard\pardeftab720\partightenfactor0
\cf5 \strokec5 # --- Streamlit UI ---\cf4 \strokec4 \
st.set_page_config(layout=\cf6 \strokec6 "wide"\cf4 \strokec4 )\
st.title(\cf6 \strokec6 "3D Concrete Printing Business Case Simulator"\cf4 \strokec4 )\
\
st.sidebar.header(\cf6 \strokec6 "Input Parameters for Simulation"\cf4 \strokec4 )\
\
\cf5 \strokec5 # --- INPUTS ---\cf4 \strokec4 \
current_params = \{\} \cf5 \strokec5 # To store user inputs\cf4 \strokec4 \
\
st.sidebar.subheader(\cf6 \strokec6 "Machine & General Operations"\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Machine Cost (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 100000\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "machine_cost"\cf4 \strokec4 ], step=\cf7 \strokec7 50000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "machine_lifespan_years"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Machine Lifespan (Years)"\cf4 \strokec4 , min_value=\cf7 \strokec7 1\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "machine_lifespan_years"\cf4 \strokec4 ], step=\cf7 \strokec7 1\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "annual_maintenance_cost_pct"\cf4 \strokec4 ] = st.sidebar.slider(\cf6 \strokec6 "Annual Maintenance (% of Machine Cost)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0.01\cf4 \strokec4 , max_value=\cf7 \strokec7 0.30\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "annual_maintenance_cost_pct"\cf4 \strokec4 ], step=\cf7 \strokec7 0.01\cf4 \strokec4 , \cf9 \strokec9 format\cf4 \strokec4 =\cf6 \strokec6 "%.2f"\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "engineer_monthly_salary"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Engineer Monthly Salary (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "engineer_monthly_salary"\cf4 \strokec4 ], step=\cf7 \strokec7 500\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Operating Days per Year (Machine)"\cf4 \strokec4 , min_value=\cf7 \strokec7 100\cf4 \strokec4 , max_value=\cf7 \strokec7 365\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 ], step=\cf7 \strokec7 5\cf4 \strokec4 )\
\
st.sidebar.subheader(\cf6 \strokec6 "Leasing Model Specifics"\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "lessor_target_profit_margin"\cf4 \strokec4 ] = st.sidebar.slider(\cf6 \strokec6 "Lessor Target Profit Margin (%)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0.01\cf4 \strokec4 , max_value=\cf7 \strokec7 0.90\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "lessor_target_profit_margin"\cf4 \strokec4 ], step=\cf7 \strokec7 0.01\cf4 \strokec4 , \cf9 \strokec9 format\cf4 \strokec4 =\cf6 \strokec6 "%.2f"\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "machine_utilization_leasing_days"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Machine Utilization Days (Leasing)"\cf4 \strokec4 , min_value=\cf7 \strokec7 1\cf4 \strokec4 , max_value=current_params[\cf6 \strokec6 "operating_days_per_year"\cf4 \strokec4 ], value=DEFAULT_PARAMS[\cf6 \strokec6 "machine_utilization_leasing_days"\cf4 \strokec4 ], step=\cf7 \strokec7 5\cf4 \strokec4 )\
\
\
st.sidebar.subheader(\cf6 \strokec6 "Contracting Model & Villa Specifics"\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "powder_cost_per_ton"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Powder Cost per Ton (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 100\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "powder_cost_per_ton"\cf4 \strokec4 ], step=\cf7 \strokec7 10\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "powder_tons_per_villa"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Powder Tons per Villa"\cf4 \strokec4 , min_value=\cf7 \strokec7 10\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "powder_tons_per_villa"\cf4 \strokec4 ], step=\cf7 \strokec7 5\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "steel_cables_cost_per_villa"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Steel & Cables Cost per Villa (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "steel_cables_cost_per_villa"\cf4 \strokec4 ], step=\cf7 \strokec7 1000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "villa_printing_days"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Villa Printing Days"\cf4 \strokec4 , min_value=\cf7 \strokec7 5\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "villa_printing_days"\cf4 \strokec4 ], step=\cf7 \strokec7 1\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "unoptimised_villa_cost_baseline"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Unoptimised Villa Cost Baseline (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 500000\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "unoptimised_villa_cost_baseline"\cf4 \strokec4 ], step=\cf7 \strokec7 50000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "labor_savings_absolute"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Labor Savings (Absolute AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "labor_savings_absolute"\cf4 \strokec4 ], step=\cf7 \strokec7 10000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "formwork_savings_absolute"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Formwork Savings (Absolute AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "formwork_savings_absolute"\cf4 \strokec4 ], step=\cf7 \strokec7 5000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "waste_reduction_savings_absolute"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Waste Reduction Savings (Absolute AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "waste_reduction_savings_absolute"\cf4 \strokec4 ], step=\cf7 \strokec7 5000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "time_related_overhead_savings_absolute"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Time-Related Overhead Savings (Absolute AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 0\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "time_related_overhead_savings_absolute"\cf4 \strokec4 ], step=\cf7 \strokec7 5000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "market_selling_price_per_villa"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Market Selling Price per Villa (AED)"\cf4 \strokec4 , min_value=\cf7 \strokec7 500000\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "market_selling_price_per_villa"\cf4 \strokec4 ], step=\cf7 \strokec7 50000\cf4 \strokec4 )\
current_params[\cf6 \strokec6 "villas_built_per_year_contracting"\cf4 \strokec4 ] = st.sidebar.number_input(\cf6 \strokec6 "Villas Built per Year (Contracting)"\cf4 \strokec4 , min_value=\cf7 \strokec7 1\cf4 \strokec4 , value=DEFAULT_PARAMS[\cf6 \strokec6 "villas_built_per_year_contracting"\cf4 \strokec4 ], step=\cf7 \strokec7 1\cf4 \strokec4 )\
\
\
\pard\pardeftab720\partightenfactor0
\cf2 \strokec2 if\cf4 \strokec4  st.sidebar.button(\cf6 \strokec6 "Run Simulation"\cf4 \strokec4 ):\
    leasing_output = calculate_leasing_model(current_params)\
    contracting_output = calculate_contracting_model(current_params)\
\
    st.header(\cf6 \strokec6 "Simulation Results"\cf4 \strokec4 )\
\
    col1, col2 = st.columns(\cf7 \strokec7 2\cf4 \strokec4 )\
\
    \cf2 \strokec2 with\cf4 \strokec4  col1:\
        st.subheader(\cf6 \strokec6 "Leasing Model"\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Total Annual Lessor Cost:** AED \cf10 \strokec10 \{leasing_output[\cf6 \strokec6 'total_annual_lessor_cost'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Daily Lessor Cost (Basis):** AED \cf10 \strokec10 \{leasing_output[\cf6 \strokec6 'daily_lessor_cost'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Recommended Daily Lease Price:** AED \cf10 \strokec10 \{leasing_output[\cf6 \strokec6 'recommended_daily_lease_price'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Annual Profit for Lessor (at \cf10 \strokec10 \{current_params[\cf6 \strokec6 'machine_utilization_leasing_days'\cf10 \strokec10 ]\}\cf6 \strokec6  days util.):** <span style='color:green; font-weight:bold;'>AED \cf10 \strokec10 \{leasing_output[\cf6 \strokec6 'annual_profit_lessor_at_utilization'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 </span>"\cf4 \strokec4 , unsafe_allow_html=\cf7 \strokec7 True\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 "---"\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Contractor's 3DCP Elements Cost per Villa (Lease + Powder + Steel/Cables):** AED \cf10 \strokec10 \{leasing_output[\cf6 \strokec6 'contractor_3dcp_elements_cost_per_villa'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
\
    \cf2 \strokec2 with\cf4 \strokec4  col2:\
        st.subheader(\cf6 \strokec6 "Direct Contracting Model"\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Machine Operating Cost for Villa Project:** AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'machine_op_cost_for_project'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Powder Cost for Villa:** AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'powder_cost_for_villa'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Total Identified Savings per Villa:** AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'total_identified_savings_per_villa'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Optimized Total Cost per Villa:** AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'optimized_total_cost_per_villa'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 "\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Net Profit per Villa:** <span style='color:green; font-weight:bold;'>AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'profit_per_villa'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 </span>"\cf4 \strokec4 , unsafe_allow_html=\cf7 \strokec7 True\cf4 \strokec4 )\
        st.markdown(\cf6 \strokec6 f"**Annual Net Profit (at \cf10 \strokec10 \{current_params[\cf6 \strokec6 'villas_built_per_year_contracting'\cf10 \strokec10 ]\}\cf6 \strokec6  villas/year):** <span style='color:blue; font-weight:bold; font-size:1.1em;'>AED \cf10 \strokec10 \{contracting_output[\cf6 \strokec6 'annual_profit_contracting'\cf10 \strokec10 ]:,\cf7 \strokec7 .2\cf10 \strokec10 f\}\cf6 \strokec6 </span>"\cf4 \strokec4 , unsafe_allow_html=\cf7 \strokec7 True\cf4 \strokec4 )\
\cf2 \strokec2 else\cf4 \strokec4 :\
    st.info(\cf6 \strokec6 "Adjust parameters in the sidebar and click 'Run Simulation'."\cf4 \strokec4 )\
\
st.markdown(\cf6 \strokec6 "---"\cf4 \strokec4 )\
st.markdown(\cf6 \strokec6 "Note: Calculations are based on the input parameters. Review assumptions carefully."\cf4 \strokec4 )}