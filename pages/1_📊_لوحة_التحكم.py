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

    # (أ) "عرض" (Display) "المؤشرات" (KPIs) "الرئيسية" (Main)
    label_1 = "System Reliability (%)"
    value_1 = f"{kpis['reliability_percent']:.2f} %" # (تم "إصلاح" (Fixed) "الخطأ" (Error) `%%` "في" (In) V10.33)
    st.sidebar.metric(label=label_1, value=value_1)

    label_2 = "Total Shortage (Baghdad BCM)"
    value_2 = f"{kpis['shortage_bag']:.2f} BCM"
    st.sidebar.metric(label=label_2, value=value_2)

    label_3 = "Total Shortage (Euphrates BCM)"
    value_3 = f"{kpis['shortage_euph']:.2f} BCM"
    st.sidebar.metric(label=label_3, value=value_3)

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

    # --- "الإضافة" (ADDITION) V10.34 ---
    # "إضافة" (Add) "شريط" (Slider) "الزمن" (Time) "لتصفية" (Filter) "البيانات" (Data)
    st.subheader("1. اختر النطاق الزمني (الأشهر)")

    # "الشريط" (Slider) "سيعمل" (Will work) "من" (From) "الشهر" (Month) 1 "إلى" (To) 600
    selected_range = st.slider(
        "اختر نطاق الأشهر (من 1 إلى 600):",
        min_value=1,
        max_value=600,
        value=(1, 600) # "الافتراضي" (Default) "هو" (Is) "عرض" (Display) "كل" (All) "الـ" (the) 600 "شهر" (Months)
    )
    start_month, end_month = selected_range

    # "تحويل" (Convert) "قيم" (Values) "الشريط" (Slider) (1-600) "إلى" (To) "فهرس" (Index) "الجدول" (DataFrame) (0-599)
    start_index = start_month - 1
    end_index = end_month - 1 # "لا" (No) "نحتاج" (Need) "+1" "هنا" (Here) "لأن" (Because) "الفهرس" (Index) "يبدأ" (Starts) "من" (From) 0

    # "تصفية" (Filter) "الجدول" (DataFrame) "الرئيسي" (Main)
    df_filtered = df.iloc[start_index:end_index] # "استخدام" (Use) "الجدول" (DataFrame) "المصفى" (Filtered) "للأسفل" (Below)
    # --- "نهاية" (End) "الإضافة" (Addition) ---

    if not all_selected_vars:
        st.info("يرجى اختيار متغير واحد على الأقل من الشريط الجانبي لعرضه.")
    else:
        # (أ) "الرسم" (Plot) "البياني" (Chart) "الزمني" (Time-series)
        st.subheader(f"2. النتائج الشهرية (من شهر {start_month} إلى {end_month})")
        # "استخدام" (Use) "الجدول" (DataFrame) "المصفى" (Filtered) "هنا" (Here)
        st.line_chart(df_filtered[all_selected_vars])

        # (ب) "عرض" (Display) "البيانات" (Data) "الخام" (Raw)
        st.subheader(f"3. البيانات الخام للنطاق المختار")
        # "استخدام" (Use) "الجدول" (DataFrame) "المصفى" (Filtered) "هنا" (Here) "أيضاً" (Also)
        st.dataframe(df_filtered[all_selected_vars].describe(), width='stretch') 
        st.dataframe(df_filtered[all_selected_vars], width='stretch')

    try:
        st.image("../logo.jpg", width=200) 
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
