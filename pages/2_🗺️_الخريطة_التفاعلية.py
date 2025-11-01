import streamlit as st
from password_check import check_password 
from model_logic import run_iron_model, dam_locations, dam_variable_mapping
import pandas as pd
import folium 
from streamlit_folium import st_folium 

# --- "إضافة" (ADDITION) V10.36 (إصلاح "الأيقونات" (Icons)) ---
# "هذا" (This) "يضمن" (Ensures) "تحميل" (Loading) "مكتبة" (Library) Font Awesome "بشكل صحيح" (Correctly)
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)
# --- "نهاية" (End) "الإضافة" (Addition) ---


# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():

    # --- (1) "تشغيل" (Run) "النموذج" (Model) (أو "الحصول" (Get) عليه من "الذاكرة" (Cache)) ---
    try:
        df, kpis = run_iron_model()
    except Exception as e:
        st.error(f"حدث خطأ أثناء تشغيل النموذج (run_iron_model): {e}")
        st.stop()

    # --- (2) "إعداد" (Setup) "الخريطة" (Map) ---
    st.title("🗺️ الخريطة التفاعلية لأداء السدود")
    st.write("انقر على أيقونة السد لرؤية النتائج الإحصائية للخزن والإطلاق.")

    # (أ) "حساب" (Calculate) "الإحصائيات" (Stats) "المتوسطة" (Average) (للنوافذ "المنبثقة" (Popup))
    avg_stats = {}
    for dam_name, (storage_var, release_var, inflow_var) in dam_variable_mapping.items():
        avg_storage = df[storage_var].mean()
        avg_release = df[release_var].mean()

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

    # (ج) "إضافة" (Add) "حدود" (Borders) "العراق" (Iraq) (المحافظات) "باللون" (In color) "الأسود" (Black)
    try:
        borders_url = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IRQ/ADM1/geoBoundaries-IRQ-ADM1.geojson"
        folium.GeoJson(
            borders_url,
            name="Iraq Borders",
            style_function=lambda x: {'color': '#000000', 'weight': 2, 'fillOpacity': 0.0}
        ).add_to(m)
    except Exception as e:
        st.warning(f"لم نتمكن من تحميل طبقة الحدود. الخطأ: {e}")

    # (د) "إضافة" (Add) "العلامات" (Markers) (مع "الأيقونات" (Icons) "الجديدة" (New))
    for dam_name, (lat, lon) in dam_locations.items():

        stats = avg_stats.get(dam_name)
        if not stats:
            continue

        popup_html = f"""
        <b>{dam_name}</b><br>
        <hr>
        <b>متوسط الخزن ({stats['storage_var']}):</b> {stats['avg_storage']:.2f} BCM<br>
        <b>متوسط الإطلاق ({stats['release_var']}):</b> {stats['avg_release']:.2f} BCM<br>
        """
        if stats['inflow_var']:
             popup_html += f"<b>متوسط الوارد ({stats['inflow_var']}):</b> {stats['avg_inflow']:.2f} BCM"

        icon_name = 'tint' 
        icon_color = 'blue'

        if dam_name == 'منخفض الثرثار (Tharthar)':
            icon_name = 'database' 
            icon_color = 'green'

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=dam_name,
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa') 
        ).add_to(m)

    # (هـ) "عرض" (Render) "الخريطة" (Map) في "ستريملت" (Streamlit)
    st_folium(m, width='100%', height=600)

    # (و) "الشعار" (Logo) (في "الأسفل" (Bottom))
    try:
        st.image("../logo.jpg", width=200) 
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
