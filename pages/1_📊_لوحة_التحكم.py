import streamlit as st
from password_check import check_password 
from model_logic import run_iron_model
import pandas as pd

# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():

    # --- (1) "تشغيل" (Run) "النموذج" (Model) ---
    try:
        df, kpis = run_iron_model()
    except Exception as e:
        st.error(f"حدث خطأ أثناء تشغيل النموذج (run_iron_model): {e}")
        st.stop()

    # --- (2) "الشريط الجانبي" (Sidebar) "للخيارات" (Options) ---
    st.sidebar.header("خيارات العرض (V10)")
    st.sidebar.subheader("📊 مؤشرات الأداء (KPIs)")

    # --- "الإصلاح" (FIX) V10.32 (The "%%" Fix) ---
    label_1 = "System Reliability (%)"
    # "أضفنا" (We added) "%%" "في" (In) "النهاية" (End) "لإصلاح" (To fix) "الخطأ" (Error)
    value_1 = f"{kpis['Reliability (% Months without Shortage)]:.2f} %%" 
    st.sidebar.metric(label=label_1, value=value_1)

    label_2 = "Total Shortage (Baghdad BCM)"
    value_2 = f"{kpis['Total Shortage Baghdad (BCM)]:.2f} BCM"
    st.sidebar.metric(label=label_2, value=value_2)

    label_3 = "Total Shortage (Euphrates BCM)"
    value_3 = f"{kpis['Total Shortage Euphrates (BCM)]:.2f} BCM"
    st.sidebar.metric(label=label_3, value=value_3)
    # --- "نهاية" (End) "الإصلاح" (Fix) ---

    # (ب) "اختيار" (Select) "المتغيرات" (Variables) "للرسم" (Plotting)
    st.sidebar.subheader("📈 اختر المتغيرات للرسم")

    storage_vars = [col for col in df.columns if col.startswith('S_')]
    release_vars = [col for col in df.columns if col.startswith('X')]
    inflow_vars = [col for col in df.columns if col.startswith('I_')]
    shortage_vars = [col for col in df.columns if col.startswith('Shortage_')]

    selected_storage = st.sidebar.multiselect("اختر الخزن (Storage)", storage_vars)
    selected_releases = st.sidebar.multiselect("اختر الإطلاقات (Releases)", release_vars)
    selected_inflows = st.sidebar.multiselect("اختر الواردات (Inflows)", inflow_vars)
    selected_shortage = st.sidebar.multiselect("اختر العجز (Shortage)", shortage_vars, default=shortage_vars)

    all_selected_vars = selected_storage + selected_releases + selected_inflows + selected_shortage

    # --- (3) "لوحة التحكم" (Dashboard) "الرئيسية" (Main) ---
    st.title("📊 لوحة تحكم النتائج (I.R.O.N)")

    if not all_selected_vars:
        st.info("يرجى اختيار متغير واحد على الأقل من الشريط الجانبي لعرضه.")
    else:
        st.subheader("النتائج الشهرية (600 شهر)")
        st.line_chart(df[all_selected_vars])

        st.subheader("البيانات الخام (Raw Data)")
        st.dataframe(df[all_selected_vars].describe(), width='stretch') 
        st.dataframe(df[all_selected_vars], width='stretch')

    try:
        st.image("../logo.jpg", width=200) 
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
