import streamlit as st
from pyomo.environ import *
import random
import pandas as pd

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

    # (أ) إنشاء "جدول" (DataFrame) فارغ لـ 600 شهر
    months = pd.date_range(start='2025-01-01', periods=600, freq='MS')
    df = pd.DataFrame(index=months)

    # (ب) توليد "واردات" (Inflows) عشوائية (محاكاة)
    # (هذه هي "الواردات الشهرية" (Monthly Inflows) بالـ BCM)
    df['I_Mosul'] = [random.uniform(1.0, 3.5) for _ in range(600)]
    df['I_Dokan'] = [random.uniform(0.5, 2.0) for _ in range(600)]
    df['I_Darban'] = [random.uniform(0.4, 1.8) for _ in range(600)]
    df['I_Adhaim'] = [random.uniform(0.1, 0.6) for _ in range(600)]
    df['I_Haditha'] = [random.uniform(1.5, 4.0) for _ in range(600)]
    # (ملاحظة: حمرين والثرثار ليس لهما "واردات" (Inflows) "طبيعية" (Natural) خاصة بهما في هذا النموذج)

    # --- (2) إعداد "نموذج" (Model) "بيومو" (Pyomo) ---
    model = ConcreteModel()

    # --- (3) "المجموعات" (Sets) ---
    # (أ) "مجموعة" (Set) "الشهور" (Months) (من 0 إلى 599)
    model.Months = RangeSet(0, 599)

    # --- (4) "المتغيرات" (Variables) ---
    # (يجب أن تكون "غير سالبة" (Non-negative))

    # (أ) "الخزن" (Storage) (في "نهاية" (End) كل "شهر" (Month))
    model.S_Mosul_End = Var(model.Months, bounds=(0, 11.0))
    model.S_Dokan_End = Var(model.Months, bounds=(0, 6.8))
    model.S_Darban_End = Var(model.Months, bounds=(0, 3.2))
    model.S_Adhaim_End = Var(model.Months, bounds=(0, 1.5))
    model.S_Haditha_End = Var(model.Months, bounds=(0, 8.2))
    model.S_Hamrin_End = Var(model.Months, bounds=(0, 2.0))
    model.S_Thar_End = Var(model.Months, bounds=(0, 40.0)) # (السعة "الحية" (Live) للثرثار)

    # (ب) "الإطلاقات" (Releases) (خلال "الشهر" (Month))
    model.X1_R_Mosul = Var(model.Months, bounds=(0, None))
    model.X2_R_Dokan = Var(model.Months, bounds=(0, None))
    model.X3_R_Darban = Var(model.Months, bounds=(0, None))
    model.X4_R_Adhaim = Var(model.Months, bounds=(0, None))
    model.X5_R_Haditha = Var(model.Months, bounds=(0, None))
    model.X6_R_Hamrin = Var(model.Months, bounds=(0, None))
    model.X7_R_Thar_Euph = Var(model.Months, bounds=(0, None)) # (الثرثار -> الفرات)
    model.X8_R_Tigris_Baghdad = Var(model.Months, bounds=(0, Baghdad_River_Capacity)) # (دجلة -> بغداد)
    model.X9_R_Thar_Tigris = Var(model.Months, bounds=(0, None)) # (الثرثار -> دجلة)
    model.X10_R_Tigris_Thar = Var(model.Months, bounds=(0, None)) # (دجلة -> الثرثار)

    # (ج) "العجز" (Shortage) (متغيرات "العقوبة" (Penalty))
    model.Shortage_Baghdad = Var(model.Months, bounds=(0, None))
    model.Shortage_Euphrates = Var(model.Months, bounds=(0, None))

    # --- (5) "الهدف" (Objective Function) ---
    # (الهدف: "تقليل" (Minimize) "العجز" (Shortage) "الإجمالي" (Total))
    def objective_rule(m):
        # (نحن "نعاقب" (Penalize) "العجز" (Shortage) في بغداد "أكثر" (More) لأنه "أهم" (More critical))
        return sum(m.Shortage_Baghdad[i] * 1000 + m.Shortage_Euphrates[i] * 500 for i in m.Months)
    model.Objective = Objective(rule=objective_rule, sense=minimize)

    # --- (6) "القيود" (Constraints) ---
    model.Constraints = ConstraintList()

    # (أ) "تعريف" (Define) "الخزن" (Storage) "الأولي" (Initial)
    # (نفترض أن جميع "الخزانات" (Reservoirs) "نصف ممتلئة" (Half-full) في "الشهر" (Month) 0)
    initial_storage = {
        'Mosul': 5.5, 'Dokan': 3.4, 'Darban': 1.6, 'Adhaim': 0.75,
        'Haditha': 4.1, 'Hamrin': 1.0, 'Thar': 20.0
    }

    # (ب) "حلقة" (Loop) "القيود" (Constraints) (لكل 600 شهر)
    for i in model.Months:

        # (I) "الحصول" (Get) على "الخزن" (Storage) "السابق" (Previous)
        if i == 0:
            S_Mosul_Start = initial_storage['Mosul']
            S_Dokan_Start = initial_storage['Dokan']
            S_Darban_Start = initial_storage['Darban']
            S_Adhaim_Start = initial_storage['Adhaim']
            S_Haditha_Start = initial_storage['Haditha']
            S_Hamrin_Start = initial_storage['Hamrin']
            S_Thar_Start = initial_storage['Thar']
        else:
            S_Mosul_Start = model.S_Mosul_End[i-1]
            S_Dokan_Start = model.S_Dokan_End[i-1]
            S_Darban_Start = model.S_Darban_End[i-1]
            S_Adhaim_Start = model.S_Adhaim_End[i-1]
            S_Haditha_Start = model.S_Haditha_End[i-1]
            S_Hamrin_Start = model.S_Hamrin_End[i-1]
            S_Thar_Start = model.S_Thar_End[i-1]

        # (II) "الحصول" (Get) على "الواردات" (Inflows) "الحالية" (Current) من "الجدول" (DataFrame)
        I_Mosul = df.loc[df.index[i], 'I_Mosul']
        I_Dokan = df.loc[df.index[i], 'I_Dokan']
        I_Darban = df.loc[df.index[i], 'I_Darban']
        I_Adhaim = df.loc[df.index[i], 'I_Adhaim']
        I_Haditha = df.loc[df.index[i], 'I_Haditha']

        # (III) "قيود" (Constraints) "توازن الكتلة" (Mass Balance)

        # (1) دجلة (Tigris)
        model.Constraints.add(model.S_Mosul_End[i] == S_Mosul_Start + I_Mosul - model.X1_R_Mosul[i])
        model.Constraints.add(model.S_Dokan_End[i] == S_Dokan_Start + I_Dokan - model.X2_R_Dokan[i])

        # (نقطة "التقاء" (Junction) دجلة)
        Tigris_Junction = model.X1_R_Mosul[i] + model.X2_R_Dokan[i]

        # (2) ديالى (Diyala)
        model.Constraints.add(model.S_Darban_End[i] == S_Darban_Start + I_Darban - model.X3_R_Darban[i])
        model.Constraints.add(model.S_Hamrin_End[i] == S_Hamrin_Start + model.X3_R_Darban[i] - model.X6_R_Hamrin[i])

        # (3) العظيم (Adhaim)
        model.Constraints.add(model.S_Adhaim_End[i] == S_Adhaim_Start + I_Adhaim - model.X4_R_Adhaim[i])

        # (4) الفرات (Euphrates)
        model.Constraints.add(model.S_Haditha_End[i] == S_Haditha_Start + I_Haditha - model.X5_R_Haditha[i])

        # (5) الثرثار (Tharthar)
        # (الثرثار "يدخل" (In) من دجلة "ويخرج" (Out) إلى دجلة والفرات)
        model.Constraints.add(model.S_Thar_End[i] == S_Thar_Start + model.X10_R_Tigris_Thar[i] - model.X7_R_Thar_Euph[i] - model.X9_R_Thar_Tigris[i])

        # (IV) "قيود" (Constraints) "الطلب" (Demand) (النقطة "الحرجة" (Critical))

        # (الطلب "الأدنى" (Minimum) في بغداد: 3.0 BCM)
        # (دجلة "يحصل" (Gets) على "مياه" (Water) من "الالتقاء" (Junction) + حمرين + العظيم + "دعم" (Support) الثرثار)
        # (دجلة "يفقد" (Loses) "مياه" (Water) "للتحويل" (Diversion) إلى الثرثار)
        Demand_Baghdad = 3.0
        Supply_Baghdad = (Tigris_Junction + model.X6_R_Hamrin[i] + model.X4_R_Adhaim[i] + model.X9_R_Thar_Tigris[i] 
                          - model.X10_R_Tigris_Thar[i])

        model.Constraints.add(model.X8_R_Tigris_Baghdad[i] == Supply_Baghdad - model.Shortage_Baghdad[i])
        model.Constraints.add(model.X8_R_Tigris_Baghdad[i] >= Demand_Baghdad) # (حاول "تلبية" (Meet) "الطلب" (Demand))

        # (الطلب "الأدنى" (Minimum) في الفرات: 2.5 BCM)
        # (الفرات "يحصل" (Gets) على "مياه" (Water) من حديثة + "دعم" (Support) الثرثار)
        Demand_Euphrates = 2.5
        Supply_Euphrates = model.X5_R_Haditha[i] + model.X7_R_Thar_Euph[i]
        model.Constraints.add(Supply_Euphrates >= Demand_Euphrates - model.Shortage_Euphrates[i])

    # --- (7) "حل" (Solve) "النموذج" (Model) ---
    print("--- جارٍ " + "حل" + " نموذج الـ 600 شهر... ---")
    solver = SolverFactory('glpk')
    results = solver.solve(model, tee=False)
    print("--- " + "اكتمل الحل" + "! ---")

    # --- (8) "استخراج" (Extract) "النتائج" (Results) ---

    # (أ) "تفريغ" (Dump) "النتائج" (Results) "مرة أخرى" (Back) إلى "الجدول" (DataFrame)
    for i in model.Months:
        month_date = df.index[i]

        # (تخزين "الخزن" (Storage) و "الإطلاقات" (Releases))
        df.loc[month_date, 'S_Mosul_End'] = value(model.S_Mosul_End[i])
        df.loc[month_date, 'S_Dokan_End'] = value(model.S_Dokan_End[i])
        df.loc[month_date, 'S_Darban_End'] = value(model.S_Darban_End[i])
        df.loc[month_date, 'S_Adhaim_End'] = value(model.S_Adhaim_End[i])
        df.loc[month_date, 'S_Haditha_End'] = value(model.S_Haditha_End[i])
        df.loc[month_date, 'S_Hamrin_End'] = value(model.S_Hamrin_End[i])
        df.loc[month_date, 'S_Thar_End'] = value(model.S_Thar_End[i])

        df.loc[month_date, 'X1_R_Mosul'] = value(model.X1_R_Mosul[i])
        df.loc[month_date, 'X2_R_Dokan'] = value(model.X2_R_Dokan[i])
        df.loc[month_date, 'X3_R_Darban'] = value(model.X3_R_Darban[i])
        df.loc[month_date, 'X4_R_Adhaim'] = value(model.X4_R_Adhaim[i])
        df.loc[month_date, 'X5_R_Haditha'] = value(model.X5_R_Haditha[i])
        df.loc[month_date, 'X6_R_Hamrin'] = value(model.X6_R_Hamrin[i])

        df.loc[month_date, 'X7_R_Thar_Euph'] = value(model.X7_R_Thar_Euph[i])
        df.loc[month_date, 'X9_R_Thar_Tigris'] = value(model.X9_R_Thar_Tigris[i])
        df.loc[month_date, 'X10_R_Tigris_Thar'] = value(model.X10_R_Tigris_Thar[i])

        df.loc[month_date, 'Shortage_Baghdad'] = value(model.Shortage_Baghdad[i])
        df.loc[month_date, 'Shortage_Euphrates'] = value(model.Shortage_Euphrates[i])

    # (ب) "حساب" (Calculate) "المؤشرات" (KPIs) "النهائية" (Final)
    total_shortage_baghdad = df['Shortage_Baghdad'].sum()
    total_shortage_euphrates = df['Shortage_Euphrates'].sum()
    total_months_with_shortage = len(df[(df['Shortage_Baghdad'] > 0.01) | (df['Shortage_Euphrates'] > 0.01)])

    kpis = {
        "Total Shortage Baghdad (BCM)": total_shortage_baghdad,
        "Total Shortage Euphrates (BCM)": total_shortage_euphrates,
        "Reliability (% Months without Shortage)": (1 - (total_months_with_shortage / 600.0)) * 100
    }

    # (ج) "إرجاع" (Return) "النتائج" (Results)
    return df, kpis
