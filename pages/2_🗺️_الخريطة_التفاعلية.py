import streamlit as st
from password_check import check_password # "استيراد" (Import) "الحماية" (Security)
from model_logic import run_iron_model, dam_locations, dam_variable_mapping # "استيراد" (Import) "العقل" (Brain) + "المواقع" (Locations)
import pandas as pd
import folium # (مكتبة الخرائط)
from streamlit_folium import st_folium # (أداة ربط الخريطة)

# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():

    # --- (1) "تشغيل" (Run) "النموذج" (Model) (أو "الحصول" (Get) عليه من "الذاكرة" (Cache)) ---
    try:
        # "تشغيل" (Run) "الدالة" (Function) "المشتركة" (Shared) من `model_logic.py`
        df, kpis = run_iron_model()
    except Exception as e:
        st.error(f"حدث خطأ أثناء تشغيل النموذج (run_iron_model): {e}")
        st.stop()

    # --- (2) "إعداد" (Setup) "الخريطة" (Map) ---
    st.title("🗺️ الخريطة التفاعلية لأداء السدود")
    st.write("انقر (Click) على أيقونة السد لرؤية النتائج الإحصائية للخزن والإطلاق.")

    # (أ) "حساب" (Calculate) "الإحصائيات" (Stats) "المتوسطة" (Average) (للنوافذ "المنبثقة" (Popup))
    avg_stats = {}
    for dam_name, (storage_var, release_var, inflow_var) in dam_variable_mapping.items():
        avg_storage = df[storage_var].mean()
        avg_release = df[release_var].mean()

        # (التعامل "بأمان" (Safely) مع "الواردات" (Inflows) (التي قد تكون `None`))
        avg_inflow = 0
        if inflow_var and inflow_var in df.columns:
            avg_inflow = df[inflow_var].mean()

        avg_stats[dam_name] = {
            "storage_var": storage_var,
            "avg_storage": avg_storage,
            "release_var": release_var,
            "avg_release": avg_release,
            "inflow_var": inflow_var,
            "avg_inflow": avg_inflow
        }

    # (ب) "إنشاء" (Create) "الخريطة" (Map) (متمركزة على العراق)
    m = folium.Map(location=[33.2232, 43.6793], zoom_start=6)

    # (ج) "إضافة" (Add) "العلامات" (Markers)
    for dam_name, (lat, lon) in dam_locations.items():

        # "الحصول" (Get) على "الإحصائيات" (Stats)
        stats = avg_stats.get(dam_name)
        if not stats:
            continue

        # "إنشاء" (Create) "النص" (Text) "المنبثق" (Popup) (HTML)
        popup_html = f"""
        <b>{dam_name}</b><br>
        <hr>
        <b>متوسط الخزن ({stats['storage_var']}):</b> {stats['avg_storage']:.2f} BCM<br>
        <b>متوسط الإطلاق ({stats['release_var']}):</b> {stats['avg_release']:.2f} BCM<br>
        """
        if stats['inflow_var']:
             popup_html += f"<b>متوسط الوارد ({stats['inflow_var']}):</b> {stats['avg_inflow']:.2f} BCM"

        # "إضافة" (Add) "العلامة" (Marker) (بالأيقونة "الافتراضية" (Default) "الحالية" (Current))
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=dam_name,
            icon=folium.Icon(color='blue', icon='info-sign') # (هذه "الأيقونة" (Icon) "التي" (That) "سنغيرها" (Change) "لاحقاً" (Later))
        ).add_to(m)

    # (د) "عرض" (Render) "الخريطة" (Map) في "ستريملت" (Streamlit)
    st_folium(m, width='100%', height=600)

    # (هـ) "الشعار" (Logo) (في "الأسفل" (Bottom))
    try:
        st.image("../logo.jpg", width=200) # (ملاحظة: المسار `../` "ضروري" (Necessary))
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
