import streamlit as st
from password_check import check_password # "استيراد" (Import) "الحماية" (Security)
from model_logic import run_iron_model # "استيراد" (Import) "العقل" (The Brain)
import pandas as pd

# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():

    # --- (1) "تشغيل" (Run) "النموذج" (Model) (أو "الحصول" (Get) عليه من "الذاكرة" (Cache)) ---
    try:
        # "تشغيل" (Run) "الدالة" (Function) "المشتركة" (Shared) من `model_logic.py`
        df, kpis = run_iron_model()
    except Exception as e:
        st.error(f"حدث خطأ أثناء تشغيل النموذج (run_iron_model): {e}")
        st.stop()

    # --- (2) "الشريط الجانبي" (Sidebar) "للخيارات" (Options) ---
    st.sidebar.header("خيارات العرض (V10)")

    # (أ) "عرض" (Display) "المؤشرات" (KPIs) "الرئيسية" (Main)
    st.sidebar.subheader("📊 مؤشرات الأداء (KPIs)")

    # --- "الإصلاح" (FIX) V10.30 ---
    # "استخدام" (Use) "عناوين" (Labels) "إنجليزية" (English) "لتجنب" (Avoid) "الخطأ" (Error) `SyntaxError`
    st.sidebar.metric(
        label="System Reliability (%)",
        value=f"{kpis['Reliability (% Months without Shortage)]:.2f} %"
    )
    st.sidebar.metric(
        label="Total Shortage (Baghdad BCM)",
        value=f"{kpis['Total Shortage Baghdad (BCM)]:.2f} BCM"
    )
    st.sidebar.metric(
        label="Total Shortage (Euphrates BCM)",
        value=f"{kpis['Total Shortage Euphrates (BCM)]:.2f} BCM"
    )
    # --- "نهاية" (End) "الإصلاح" (Fix) ---

    # (ب) "اختيار" (Select) "المتغيرات" (Variables) "للرسم" (Plotting)
    st.sidebar.subheader("📈 اختر المتغيرات للرسم")

    # (تجميع "المتغيرات" (Variables) حسب "النوع" (Type))
    storage_vars = [col for col in df.columns if col.startswith('S_')]
    release_vars = [col for col in df.columns if col.startswith('X')]
    inflow_vars = [col for col in df.columns if col.startswith('I_')]
    shortage_vars = [col for col in df.columns if col.startswith('Shortage_')]

    # "القوائم" (Lists) "المنسدلة" (Dropdown)
    selected_storage = st.sidebar.multiselect("اختر الخزن (Storage)", storage_vars)
    selected_releases = st.sidebar.multiselect("اختر الإطلاقات (Releases)", release_vars)
    selected_inflows = st.sidebar.multiselect("اختر الواردات (Inflows)", inflow_vars)
    selected_shortage = st.sidebar.multiselect("اختر العجز (Shortage)", shortage_vars, default=shortage_vars)

    # "دمج" (Combine) "الاختيارات" (Selections)
    all_selected_vars = selected_storage + selected_releases + selected_inflows + selected_shortage

    # --- (3) "لوحة التحكم" (Dashboard) "الرئيسية" (Main) ---
    st.title("📊 لوحة تحكم النتائج (I.R.O.N)")

    if not all_selected_vars:
        st.info("يرجى اختيار متغير واحد على الأقل من الشريط الجانبي لعرضه.")
    else:
        # (أ) "الرسم" (Plot) "البياني" (Chart) "الزمني" (Time-series)
        st.subheader("النتائج الشهرية (600 شهر)")
        st.line_chart(df[all_selected_vars])

        # (ب) "عرض" (Display) "البيانات" (Data) "الخام" (Raw)
        st.subheader("البيانات الخام (Raw Data)")
        # "إصلاح" (Fix) "التحذير" (Warning) "الخاص" (Special) "بـ" (by) `use_container_width`
        st.dataframe(df[all_selected_vars].describe(), width='stretch') # (عرض "الإحصائي" (Stats))
        st.dataframe(df[all_selected_vars], width='stretch') # (عرض "الجدول" (Table) "بالكامل" (Full))

    # (ج) "الشعار" (Logo) (في "الأسفل" (Bottom))
    try:
        st.image("../logo.jpg", width=200) # (ملاحظة: المسار `../` "ضروري" (Necessary))
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
