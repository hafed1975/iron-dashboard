# ----------------------------------------------------------------------
# "العقل" (I.R.O.N) - الإصدار 10.0 (بايثون)
# "لوحة التحكم التفاعلية الاحترافية" (The Professional Decision Tool)
# ----------------------------------------------------------------------

# الخطوة 1: استيراد المكتبات
import streamlit as st 
from pyomo.environ import *
import random 
import pandas as pd 
import folium # (مكتبة الخرائط)
from streamlit_folium import st_folium # (أداة ربط الخريطة)

# ----------------------------------------------------------------------
# "المدخلات الثابتة" (Global Constants)
# ----------------------------------------------------------------------

Baghdad_River_Capacity = 4.0

# (إحداثيات السدود لرسم الخريطة)
dam_locations = {
    'سد الموصل (Mosul)': (36.630, 42.823),
    'سد دوكان (Dokan)': (35.954, 44.953),
    'سد دربندخان (Darban)': (35.116, 45.686),
    'سد العظيم (Adhaim)': (34.566, 44.513),
    'سد حديثة (Haditha)': (34.197, 42.356),
    'سد حمرين (Hamrin)': (34.125, 45.033),
    'منخفض الثرثار (Tharthar)': (33.984, 43.253)
}

# (قاموس "ربط" الأسماء بالمتغيرات لتحليل الخريطة)
dam_variable_mapping = {
    'سد الموصل (Mosul)': ('S_Mosul_End', 'X1_R_Mosul', 'I_Mosul'),
    'سد دوكان (Dokan)': ('S_Dokan_End', 'X2_R_Dokan', 'I_Dokan'),
    'سد دربندخان (Darban)': ('S_Darban_End', 'X3_R_Darban', 'I_Darban'),
    'سد العظيم (Adhaim)': ('S_Adhaim_End', 'X4_R_Adhaim', 'I_Adhaim'),
    'سد حديثة (Haditha)': ('S_Haditha_End', 'X5_R_Haditha', 'I_Haditha'),
    'سد حمرين (Hamrin)': ('S_Hamrin_End', 'X6_R_Hamrin', None), # (حمرين ليس له وارد خاص)
    'منخفض الثرثار (Tharthar)': ('S_Thar_End', 'X9_R_Thar_Tigris', None) # (الثرثار ليس له وارد طبيعي)
}

# ----------------------------------------------------------------------
# "الخطوة 2: "العقل" (I.R.O.N)
# (الدالة المخبأة - تم تعديلها لتصدير "الواردات" أيضاً)
# ----------------------------------------------------------------------
@st.cache_data # (يتم تشغيل هذا مرة واحدة فقط)
def run_iron_model():
    print("--- [IRON_V10] بدء " + "تشغيل المحرك" + " (يحدث مرة واحدة فقط)... ---")
    
    # --- (1) توليد البيانات (Data Generation) ---
    inflow_pattern_flood = {
        'I_Mosul':   [1.2, 1.5, 2.0, 6.0, 2.0, 1.0, 0.6, 0.4, 0.4, 0.5, 0.7, 0.9],
        'I_Dokan':   [0.8, 1.0, 1.5, 4.0, 1.5, 0.8, 0.5, 0.3, 0.3, 0.4, 0.5, 0.6],
        'I_Darban':  [0.3, 0.4, 0.5, 0.6, 0.4, 0.2, 0.1, 0.1, 0.1, 0.15, 0.2, 0.25],
        'I_Adhaim':  [0.1, 0.15, 0.2, 0.25, 0.1, 0.05, 0.01, 0.01, 0.01, 0.05, 0.05, 0.05],
        'I_Haditha': [1.5, 1.8, 2.0, 2.2, 1.9, 1.6, 1.4, 1.3, 1.2, 1.2, 1.3, 1.4]
    }
    inflow_pattern_normal = {k: [round(v * 0.6, 2) for v in vals] for k, vals in inflow_pattern_flood.items()}
    inflow_pattern_drought = {k: [round(v * 0.3, 2) for v in vals] for k, vals in inflow_pattern_flood.items()}
    demand_pattern_12_months = {
        'D_Mosul':   [0.08, 0.08, 0.09, 0.1, 0.12, 0.15, 0.2, 0.2, 0.15, 0.1, 0.09, 0.08],
        'D_Tikrit':  [0.08, 0.08, 0.09, 0.1, 0.12, 0.15, 0.2, 0.2, 0.15, 0.1, 0.09, 0.08],
        'D_Erbil':   [0.04, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1, 0.1, 0.08, 0.06, 0.05, 0.04],
        'D_Kirkuk':  [0.18, 0.18, 0.2, 0.22, 0.25, 0.3, 0.35, 0.35, 0.3, 0.22, 0.2, 0.18],
        'D_Ishaqi':  [0.18, 0.18, 0.2, 0.22, 0.25, 0.3, 0.35, 0.35, 0.3, 0.22, 0.2, 0.18],
        'D_Ramadi':  [0.1, 0.1, 0.12, 0.15, 0.18, 0.2, 0.25, 0.25, 0.2, 0.15, 0.12, 0.1],
        'D_Karbala': [0.35, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.6, 0.55, 0.45, 0.4, 0.35],
        'D_Hindiya': [0.45, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.7, 0.65, 0.55, 0.5, 0.45],
        'D_Baghdad': [0.8, 0.8, 0.85, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1, 0.9, 0.85, 0.8],
        'D_Kut':     [0.7, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0, 1.0, 0.9, 0.8, 0.75, 0.7]
    }
    Inflows = {k: {} for k in inflow_pattern_flood.keys()}
    Demands = {k: {} for k in demand_pattern_12_months.keys()}
    total_months = 600
    current_month = 1
    for year in range(50): 
        rand_num = random.random() 
        if rand_num < 0.1: 
            chosen_inflow_pattern = inflow_pattern_flood
        elif rand_num < 0.3: 
            chosen_inflow_pattern = inflow_pattern_drought
        else: 
            chosen_inflow_pattern = inflow_pattern_normal
        for month_of_year in range(12):
            for key in Inflows.keys():
                Inflows[key][current_month] = chosen_inflow_pattern[key][month_of_year]
            for key in Demands.keys():
                Demands[key][current_month] = demand_pattern_12_months[key][month_of_year]
            current_month += 1

    # --- (2) المدخلات (Inputs) ---
    S_Max = {'Mosul': 11.11, 'Dokan': 6.9, 'Haditha': 8.3, 'Darban': 3.0, 'Hamrin': 2.0, 'Adhaim': 1.5, 'Tharthar': 35.0}
    S_Min = {'Mosul': 2.95, 'Dokan': 0.8, 'Haditha': 1.0, 'Darban': 0.5, 'Hamrin': 0.2, 'Adhaim': 0.1, 'Tharthar': 5.0}
    S_Initial = {'Mosul': 6.0, 'Dokan': 4.0, 'Darban': 2.0, 'Adhaim': 0.5, 'Haditha': 5.0, 'Hamrin': 1.0, 'Tharthar': 10.0}
    E_Coeff = {'Mosul': 0.002, 'Dokan': 0.002, 'Haditha': 0.003, 'Darban': 0.002, 'Hamrin': 0.008, 'Adhaim': 0.01, 'Tharthar': 0.012}

    # --- (3) بناء النموذج (Build Model) ---
    model = ConcreteModel(name="IRON_v10_Dashboard_Model")
    model.T = RangeSet(1, total_months)
    model.X1_R_Mosul = Var(model.T, within=NonNegativeReals)
    model.X2_R_Dokan = Var(model.T, within=NonNegativeReals)
    model.X3_R_Darban = Var(model.T, within=NonNegativeReals)
    model.X4_R_Adhaim = Var(model.T, within=NonNegativeReals)
    model.X5_R_Haditha = Var(model.T, within=NonNegativeReals)
    model.X6_R_Hamrin = Var(model.T, within=NonNegativeReals)
    model.X7_D_Thar = Var(model.T, within=NonNegativeReals)
    model.X8_R_Thar_Euph = Var(model.T, within=NonNegativeReals)
    model.X9_R_Thar_Tigris = Var(model.T, within=NonNegativeReals)
    model.X10_Deficit_Mosul_Tikrit = Var(model.T, within=NonNegativeReals)
    model.X11_Deficit_Zab = Var(model.T, within=NonNegativeReals)
    model.X12_Deficit_Ishaqi = Var(model.T, within=NonNegativeReals)
    model.X13_Deficit_Ramadi = Var(model.T, within=NonNegativeReals)
    model.X14_Deficit_Hindiya = Var(model.T, within=NonNegativeReals)
    model.X15_Deficit_Baghdad = Var(model.T, within=NonNegativeReals)
    model.X16_Deficit_Kut = Var(model.T, within=NonNegativeReals)
    model.S_Mosul_Start = Var(model.T); model.S_Mosul_End = Var(model.T); model.E_Mosul = Var(model.T)
    model.S_Dokan_Start = Var(model.T); model.S_Dokan_End = Var(model.T); model.E_Dokan = Var(model.T)
    model.S_Darban_Start = Var(model.T); model.S_Darban_End = Var(model.T); model.E_Darban = Var(model.T)
    model.S_Adhaim_Start = Var(model.T); model.S_Adhaim_End = Var(model.T); model.E_Adhaim = Var(model.T)
    model.S_Haditha_Start = Var(model.T); model.S_Haditha_End = Var(model.T); model.E_Haditha = Var(model.T)
    model.S_Hamrin_Start = Var(model.T); model.S_Hamrin_End = Var(model.T); model.E_Hamrin = Var(model.T)
    model.S_Thar_Start = Var(model.T); model.S_Thar_End = Var(model.T); model.E_Thar = Var(model.T)
    model.Flow_Mosul_to_Sam = Var(model.T)
    model.Flow_Zab_to_Tigris = Var(model.T)
    model.I_Samarra = Var(model.T)
    model.R_Samarra_to_Bag = Var(model.T)
    model.Flow_pre_Hindiya = Var(model.T)
    model.Check_Hindiya = Var(model.T)
    model.Flow_Baghdad = Var(model.T)
    model.Check_Baghdad = Var(model.T)
    model.Flow_pre_Kut = Var(model.T)
    model.Check_Kut = Var(model.T)

    # --- (4) المعادلات الحاكمة (Logic) ---
    def objective_rule(m):
        total_evap = 0
        total_deficit = 0
        deficit_penalty = 1000 
        for t in m.T:
            total_evap += (m.S_Mosul_Start[t] + m.S_Mosul_End[t]) / 2 * E_Coeff['Mosul']
            total_evap += (m.S_Dokan_Start[t] + m.S_Dokan_End[t]) / 2 * E_Coeff['Dokan']
            total_evap += (m.S_Darban_Start[t] + m.S_Darban_End[t]) / 2 * E_Coeff['Darban']
            total_evap += (m.S_Adhaim_Start[t] + m.S_Adhaim_End[t]) / 2 * E_Coeff['Adhaim']
            total_evap += (m.S_Haditha_Start[t] + m.S_Haditha_End[t]) / 2 * E_Coeff['Haditha']
            total_evap += (m.S_Hamrin_Start[t] + m.S_Hamrin_End[t]) / 2 * E_Coeff['Hamrin']
            total_evap += (m.S_Thar_Start[t] + m.S_Thar_End[t]) / 2 * E_Coeff['Tharthar']
            total_deficit += m.X10_Deficit_Mosul_Tikrit[t]
            total_deficit += m.X11_Deficit_Zab[t]
            total_deficit += m.X12_Deficit_Ishaqi[t]
            total_deficit += m.X13_Deficit_Ramadi[t]
            total_deficit += m.X14_Deficit_Hindiya[t]
            total_deficit += m.X15_Deficit_Baghdad[t]
            total_deficit += m.X16_Deficit_Kut[t]
        return total_evap + (total_deficit * deficit_penalty)
    model.Objective = Objective(rule=objective_rule, sense=minimize)

    model.Constraints = ConstraintList()
    for t in model.T:
        if t == 1: 
            model.Constraints.add(model.S_Mosul_Start[t] == S_Initial['Mosul'])
            model.Constraints.add(model.S_Dokan_Start[t] == S_Initial['Dokan'])
            model.Constraints.add(model.S_Darban_Start[t] == S_Initial['Darban'])
            model.Constraints.add(model.S_Adhaim_Start[t] == S_Initial['Adhaim'])
            model.Constraints.add(model.S_Haditha_Start[t] == S_Initial['Haditha'])
            model.Constraints.add(model.S_Hamrin_Start[t] == S_Initial['Hamrin'])
            model.Constraints.add(model.S_Thar_Start[t] == S_Initial['Tharthar'])
        else: 
            model.Constraints.add(model.S_Mosul_Start[t] == model.S_Mosul_End[t-1])
            model.Constraints.add(model.S_Dokan_Start[t] == model.S_Dokan_End[t-1])
            model.Constraints.add(model.S_Darban_Start[t] == model.S_Darban_End[t-1])
            model.Constraints.add(model.S_Adhaim_Start[t] == model.S_Adhaim_End[t-1])
            model.Constraints.add(model.S_Haditha_Start[t] == model.S_Haditha_End[t-1])
            model.Constraints.add(model.S_Hamrin_Start[t] == model.S_Hamrin_End[t-1])
            model.Constraints.add(model.S_Thar_Start[t] == model.S_Thar_End[t-1])
        model.Constraints.add(model.E_Mosul[t] == (model.S_Mosul_Start[t] + model.S_Mosul_End[t]) / 2 * E_Coeff['Mosul'])
        model.Constraints.add(model.E_Dokan[t] == (model.S_Dokan_Start[t] + model.S_Dokan_End[t]) / 2 * E_Coeff['Dokan'])
        model.Constraints.add(model.E_Darban[t] == (model.S_Darban_Start[t] + model.S_Darban_End[t]) / 2 * E_Coeff['Darban'])
        model.Constraints.add(model.E_Adhaim[t] == (model.S_Adhaim_Start[t] + model.S_Adhaim_End[t]) / 2 * E_Coeff['Adhaim'])
        model.Constraints.add(model.E_Haditha[t] == (model.S_Haditha_Start[t] + model.S_Haditha_End[t]) / 2 * E_Coeff['Haditha'])
        model.Constraints.add(model.E_Hamrin[t] == (model.S_Hamrin_Start[t] + model.S_Hamrin_End[t]) / 2 * E_Coeff['Hamrin'])
        model.Constraints.add(model.E_Thar[t] == (model.S_Thar_Start[t] + model.S_Thar_End[t]) / 2 * E_Coeff['Tharthar'])
        model.Constraints.add(model.S_Mosul_End[t] == model.S_Mosul_Start[t] + Inflows['I_Mosul'][t] - model.X1_R_Mosul[t] - model.E_Mosul[t])
        model.Constraints.add(model.S_Dokan_End[t] == model.S_Dokan_Start[t] + Inflows['I_Dokan'][t] - model.X2_R_Dokan[t] - model.E_Dokan[t])
        model.Constraints.add(model.S_Darban_End[t] == model.S_Darban_Start[t] + Inflows['I_Darban'][t] - model.X3_R_Darban[t] - model.E_Darban[t])
        model.Constraints.add(model.S_Adhaim_End[t] == model.S_Adhaim_Start[t] + Inflows['I_Adhaim'][t] - model.X4_R_Adhaim[t] - model.E_Adhaim[t])
        model.Constraints.add(model.S_Haditha_End[t] == model.S_Haditha_Start[t] + Inflows['I_Haditha'][t] - model.X5_R_Haditha[t] - model.E_Haditha[t])
        model.Constraints.add(model.S_Hamrin_End[t] == model.S_Hamrin_Start[t] + model.X3_R_Darban[t] - model.X6_R_Hamrin[t] - model.E_Hamrin[t])
        model.Constraints.add(model.S_Thar_End[t] == model.S_Thar_Start[t] + model.X7_D_Thar[t] - model.X8_R_Thar_Euph[t] - model.X9_R_Thar_Tigris[t] - model.E_Thar[t])
        model.Constraints.add(model.Flow_Mosul_to_Sam[t] == model.X1_R_Mosul[t] - Demands['D_Mosul'][t] - Demands['D_Tikrit'][t])
        model.Constraints.add(model.Flow_Zab_to_Tigris[t] == model.X2_R_Dokan[t] - Demands['D_Erbil'][t] - Demands['D_Kirkuk'][t])
        model.Constraints.add(model.I_Samarra[t] == model.Flow_Mosul_to_Sam[t] + model.Flow_Zab_to_Tigris[t])
        model.Constraints.add(model.R_Samarra_to_Bag[t] == model.I_Samarra[t] - model.X7_D_Thar[t] - Demands['D_Ishaqi'][t])
        model.Constraints.add(model.Flow_pre_Hindiya[t] == model.X5_R_Haditha[t] - Demands['D_Ramadi'][t])
        model.Constraints.add(model.Check_Hindiya[t] == model.Flow_pre_Hindiya[t] + model.X8_R_Thar_Euph[t] - Demands['D_Hindiya'][t] - Demands['D_Karbala'][t])
        model.Constraints.add(model.Flow_Baghdad[t] == model.R_Samarra_to_Bag[t] + model.X4_R_Adhaim[t] + model.X9_R_Thar_Tigris[t])
        model.Constraints.add(model.Check_Baghdad[t] == model.Flow_Baghdad[t] - Demands['D_Baghdad'][t])
        model.Constraints.add(model.Flow_pre_Kut[t] == model.Check_Baghdad[t] + model.X6_R_Hamrin[t])
        model.Constraints.add(model.Check_Kut[t] == model.Flow_pre_Kut[t] - Demands['D_Kut'][t])
        model.Constraints.add(model.Flow_Mosul_to_Sam[t] + model.X10_Deficit_Mosul_Tikrit[t] >= 0)
        model.Constraints.add(model.Flow_Zab_to_Tigris[t] + model.X11_Deficit_Zab[t] >= 0)
        model.Constraints.add(model.R_Samarra_to_Bag[t] + model.X12_Deficit_Ishaqi[t] >= 0)
        model.Constraints.add(model.Flow_pre_Hindiya[t] + model.X13_Deficit_Ramadi[t] >= 0)
        model.Constraints.add(model.Check_Hindiya[t] + model.X14_Deficit_Hindiya[t] >= 0)
        model.Constraints.add(model.Check_Baghdad[t] + model.X15_Deficit_Baghdad[t] >= 0)
        model.Constraints.add(model.Check_Kut[t] + model.X16_Deficit_Kut[t] >= 0)
        model.Constraints.add(model.S_Mosul_End[t] <= S_Max['Mosul'])
        model.Constraints.add(model.S_Dokan_End[t] <= S_Max['Dokan'])
        model.Constraints.add(model.S_Darban_End[t] <= S_Max['Darban'])
        model.Constraints.add(model.S_Adhaim_End[t] <= S_Max['Adhaim'])
        model.Constraints.add(model.S_Haditha_End[t] <= S_Max['Haditha'])
        model.Constraints.add(model.S_Hamrin_End[t] <= S_Max['Hamrin']) 
        model.Constraints.add(model.S_Thar_End[t] <= S_Max['Tharthar'])
        model.Constraints.add(model.S_Mosul_End[t] >= S_Min['Mosul'])
        model.Constraints.add(model.S_Dokan_End[t] >= S_Min['Dokan'])
        model.Constraints.add(model.S_Darban_End[t] >= S_Min['Darban'])
        model.Constraints.add(model.S_Adhaim_End[t] >= S_Min['Adhaim'])
        model.Constraints.add(model.S_Haditha_End[t] >= S_Min['Haditha'])
        model.Constraints.add(model.S_Hamrin_End[t] >= S_Min['Hamrin'])
        model.Constraints.add(model.S_Thar_End[t] >= S_Min['Tharthar'])
        model.Constraints.add(model.Flow_Baghdad[t] <= Baghdad_River_Capacity)

    # --- (5) تشغيل الحل (Solve) ---
    print("--- جارٍ حل نموذج الـ 600 شهر... ---")
    # !! "الإصلاح الجراحي" (V10.1) - تحديد مسار المحرك يدوياً للسحابة !!
    # !! "الإصلاح السحابي" (V10.5) - استخدام "cyipopt" المدمج !!
solver = SolverFactory('ipopt')
    solver = SolverFactory('ipopt', executable=solver_executable_path)
    results = solver.solve(model, tee=False) 
    print("--- اكتمل الحل! ---")

    # --- (6) استخراج النتائج (Extract Results) ---
    if (results.solver.status != SolverStatus.ok) or (results.solver.termination_condition != TerminationCondition.optimal):
        print("فشل " + "Solver" + " في إيجاد حل أمثل!")
        return None, None 

    print("--- جارٍ استخراج 600 شهر من النتائج... ---")
    
    data_to_export = {'Month': list(range(1, total_months + 1))}
    
    # (أ) إضافة "الواردات" (المدخلات) إلى قاموس التصدير
    for dam_key, inflow_dict in Inflows.items():
        data_to_export[dam_key] = [inflow_dict[t] for t in model.T]

    # (ب) إضافة "المخرجات" (المتغيرات) إلى قاموس التصدير
    all_vars_to_export = [
        'X1_R_Mosul', 'X2_R_Dokan', 'X3_R_Darban', 'X4_R_Adhaim', 'X5_R_Haditha', 'X6_R_Hamrin',
        'X7_D_Thar', 'X8_R_Thar_Euph', 'X9_R_Thar_Tigris',
        'X10_Deficit_Mosul_Tikrit', 'X11_Deficit_Zab', 'X12_Deficit_Ishaqi',
        'X13_Deficit_Ramadi', 'X14_Deficit_Hindiya', 'X15_Deficit_Baghdad', 'X16_Deficit_Kut',
        'S_Mosul_End', 'S_Dokan_End', 'S_Darban_End', 'S_Adhaim_End', 
        'S_Haditha_End', 'S_Hamrin_End', 'S_Thar_End',
        'Flow_Baghdad', 'Check_Baghdad', 'Check_Kut', 'Check_Hindiya',
        'E_Mosul', 'E_Dokan', 'E_Darban', 'E_Adhaim', 'E_Haditha', 'E_Hamrin', 'E_Thar'
    ]
    for var_name in all_vars_to_export:
        var_object = getattr(model, var_name)
        data_to_export[var_name] = [round(var_object[t].value, 3) for t in model.T]
    
    # (ج) تحويل البيانات إلى "DataFrame"
    df = pd.DataFrame(data_to_export)
    
    # (د) حساب "الملخص" (KPIs)
    total_evap = sum(df['E_Mosul'] + df['E_Dokan'] + df['E_Darban'] + df['E_Adhaim'] + 
                     df['E_Haditha'] + df['E_Hamrin'] + df['E_Thar'])
    total_deficit = sum(df['X10_Deficit_Mosul_Tikrit'] + df['X11_Deficit_Zab'] + df['X12_Deficit_Ishaqi'] +
                        df['X13_Deficit_Ramadi'] + df['X14_Deficit_Hindiya'] + df['X15_Deficit_Baghdad'] +
                        df['X16_Deficit_Kut'])
    flood_months = 0
    for t in model.T:
        if model.Flow_Baghdad[t].value >= (Baghdad_River_Capacity * 0.99):
            flood_months += 1
            
    kpis = {
        "total_deficit": round(total_deficit, 2),
        "total_evap": round(total_evap, 2),
        "flood_months": flood_months
    }
    
    print("--- اكتمل تشغيل المحرك (V10). ---")
    return df, kpis

# ----------------------------------------------------------------------
# "الخطوة 3: "واجهة المستخدم" (The User Interface)
# ----------------------------------------------------------------------

# (أ) إعدادات الصفحة (يجب أن يكون أول أمر Streamlit)
st.set_page_config(layout="wide", page_title="نظام I.R.O.N الذكي")

# (ب) "الشريط الجانبي" (Sidebar)
with st.sidebar:
    st.title("لوحة تحكم I.R.O.N")
    
    # (إصلاح تحذير الشعار)
    try:
        st.image("logo.jpg", width='stretch') 
    except:
        st.error("لم يتم العثور على ملف الشعار 'logo.jpg'")
        
    st.header("إعداد:")
    st.subheader("(اكتب اسمك هنا)") # !! "عدل هذا السطر" !!
    
    st.subheader("التشكيل:")
    st.text("(اكتب اسم الدائرة/الوزارة هنا)") # !! "عدل هذا السطر" !!
    
    st.divider()
    st.info("تم بناء هذا النموذج كأداة تحسين (Optimization) لإيجاد السياسة المثلى لـ 50 عاماً.")

# (ج) تشغيل النموذج (يحدث مرة واحدة فقط ويتم تخزينه)
with st.spinner("...جارٍ تشغيل " + "العقل" + " (I.R.O.N) لمحاكاة 50 عاماً..."):
    df, kpis = run_iron_model()
    
    if df is None:
        st.error("فشل " + "العقل" + " (I.R.O.N) في إيجاد حل.")
        st.stop() 

# (د) العنوان الرئيسي والملخص (KPIs)
st.title("نظام I.R.O.N الذكي لإدارة الموارد المائية العراقية")
st.markdown("لوحة تحكم تفاعلية لنتائج محاكاة 50 عاماً (600 شهر)")

st.header("الملخص التنفيذي لـ 50 عاماً (السياسة المثلى)")
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي العجز (BCM) ⬇️", kpis["total_deficit"])
col2.metric("إجمالي التبخر (BCM) ⬇️", kpis["total_evap"])
col3.metric("أشهر الفيضان في بغداد 🛡️", kpis["flood_months"])
st.divider() 

# (هـ) "الفلتر الزمني العام" (Global Time Filter)
# (تم نقله هنا ليتحكم في "كل" الألسنة)
st.header("التحليل التفاعلي (600 شهر)")
selected_months = st.slider(
    "اختر النطاق الزمني (الأشهر) لعرضه:",
    min_value=1, 
    max_value=600, 
    value=(1, 600) # (الافتراضي: اعرض كل شيء)
)
# (فلترة البيانات بناءً على "الفلتر")
filtered_df = df[(df['Month'] >= selected_months[0]) & (df['Month'] <= selected_months[1])]
filtered_df_indexed = filtered_df.set_index('Month') # (نسخة مفهرسة للرسوم)

# (و) الألسنة (Tabs)
tab1, tab2 = st.tabs(["📊 لوحة التحكم (Dashboard)", "🗺️ الخريطة التفاعلية (Interactive Map)"])

# (ز) "محتوى اللسان الأول" (لوحة التحكم)
with tab1:
    # (الرسم البياني 1: حماية بغداد)
    st.subheader("الرسم 1: سياسة حماية بغداد (التدفق)")
    baghdad_plot_df = filtered_df_indexed[['Flow_Baghdad']]
    baghdad_plot_df['Max_Capacity (4.0 BCM)'] = Baghdad_River_Capacity
    st.line_chart(baghdad_plot_df, color=["#0000FF", "#FF0000"]) 

    # (الرسم البياني 2: سياسة الخزن)
    st.subheader("الرسم 2: سياسة الخزن (اختر السدود لتحليلها)")
    storage_cols_to_plot = [
        'S_Mosul_End', 'S_Dokan_End', 'S_Darban_End', 'S_Adhaim_End', 
        'S_Haditha_End', 'S_Hamrin_End', 'S_Thar_End'
    ]
    selected_storages = st.multiselect(
        "اختر الخزانات لعرضها:",
        options=storage_cols_to_plot,
        default=['S_Mosul_End', 'S_Thar_End'] 
    )
    if selected_storages:
        st.line_chart(filtered_df_indexed[selected_storages])

    # (الرسم البياني 3: سياسة العجز)
    st.subheader("الرسم 3: سياسة إدارة الجفاف (العجز)")
    deficit_cols_to_plot = [
        'X10_Deficit_Mosul_Tikrit', 'X11_Deficit_Zab', 'X12_Deficit_Ishaqi',
        'X13_Deficit_Ramadi', 'X14_Deficit_Hindiya', 'X15_Deficit_Baghdad', 'X16_Deficit_Kut'
    ]
    selected_deficits = st.multiselect(
        "اختر نقاط الطلب لعرض " + "العجز" + " فيها:",
        options=deficit_cols_to_plot,
        default=['X15_Deficit_Baghdad', 'X16_Deficit_Kut'] 
    )
    if selected_deficits:
        st.bar_chart(filtered_df_indexed[selected_deficits])

    # (إصلاح مكان "أيقونة البيانات")
    st.divider()
    if st.checkbox("إظهار البيانات الأولية (الـ 600 شهر)"):
        st.dataframe(df) # (عرض "كل" البيانات، وليس المفلترة)

# (ح) "محتوى اللسان الثاني" (الخريطة التفاعلية)
with tab2:
    st.header("خريطة مواقع السدود والتحليل التفصيلي")
    
    # (1) تقسيم الشاشة: 70% للخريطة، 30% للبيانات الجانبية
    map_col, data_col = st.columns([0.6, 0.4]) # (أعطيت 40% للبيانات)
    
    with map_col:
        # (1.أ) إنشاء الخريطة
        m = folium.Map(location=[34.0, 43.5], zoom_start=6) 
        for dam_name, coords in dam_locations.items():
            folium.Marker(
                location=coords,
                popup=folium.Popup(dam_name, max_width=300),
                tooltip=dam_name,
                icon=folium.Icon(color='blue', icon='water') 
            ).add_to(m)
        st_folium(m, width=700, height=500)
    
    with data_col:
        # (2.أ) "القسم الجديد": التحليل التفاعلي للخريطة
        st.subheader("تحليل بيانات الموقع")
        
        selected_dam_name = st.selectbox(
            "اختر موقعاً لعرض بياناته التفصيلية (للفترة المحددة):",
            options=list(dam_locations.keys())
        )
        
        # (2.ب) جلب أسماء المتغيرات الصحيحة
        storage_var, release_var, inflow_var = dam_variable_mapping[selected_dam_name]

        # (2.ج) عرض البيانات الملخصة للموقع المختار (للفترة المفلترة)
        st.markdown(f"**ملخص بيانات: {selected_dam_name}**")
        avg_storage = filtered_df[storage_var].mean()
        avg_release = filtered_df[release_var].mean()
        st.metric(f"متوسط الخزن (BCM)", f"{avg_storage:.2f}")
        st.metric(f"متوسط الإطلاق (BCM)", f"{avg_release:.2f}")

        # (2.د) عرض الرسوم البيانية للموقع المختار (للفترة المفلترة)
        
        # (الخزن)
        st.markdown(f"**الخزن الشهري (BCM)**")
        st.line_chart(filtered_df_indexed[storage_var])
        
        # (الإطلاق)
        st.markdown(f"**الإطلاق الشهري (BCM)**")
        st.line_chart(filtered_df_indexed[release_var])
        
        # (الوارد)
        if inflow_var:
            st.markdown(f"**الوارد الشهري (BCM)**")
            st.line_chart(filtered_df_indexed[inflow_var])
        else:

            st.info(f"ملاحظة: {selected_dam_name} ليس له وارد طبيعي مباشر في النموذج (يتم تغذيته من سد آخر أو بالتحويل).")


