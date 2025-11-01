import streamlit as st
from password_check import check_password 
from model_logic import run_iron_model, dam_locations, dam_variable_mapping
import pandas as pd
import folium 
from streamlit_folium import st_folium 

# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():

    # --- (1) "تشغيل" (Run) "النموذج" (Model) ---
    try:
        df, kpis = run_iron_model()
    except Exception as e:
        st.error(f"حدث خطأ أثناء تشغيل النموذج (run_iron_model): {e}")
        st.stop()

    # --- (2) "إعداد" (Setup) "الخريطة" (Map) ---
    st.title("🗺️ الخريطة التفاعلية لأداء السدود")
    st.write("انقر على أيقونة السد لرؤية النتائج الإحصائية للخزن والإطلاق.")

    # (أ) "حساب" (Calculate) "الإحصائي" (Stats) "المتوسط" (Average)
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
            "avg_inflow": avg_inflow # "الاسم" (Name) "الصحيح" (Correct)
        }

    # (ب) "إنشاء" (Create) "الخريطة" (Map) (متمركزة على العراق)
    m = folium.Map(location=[33.2232, 43.6793], zoom_start=6)

    # (ج) "إضافة" (Add) "حدود" (Borders) "العراق" (Iraq)
    try:
        borders_url = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IRQ/ADM1/geoBoundaries-IRQ-ADM1.geojson"
        folium.GeoJson(
            borders_url,
            name="Iraq Borders",
            style_function=lambda x: {'color': '#000000', 'weight': 2, 'fillOpacity': 0.0}
        ).add_to(m)
    except Exception as e:
        st.warning(f"لم نتمكن من تحميل طبقة الحدود. الخطأ: {e}")

    # (د) "إضافة" (Add) "الأنهار" (Rivers) (من "رابط" (Link) "جديد" (New) "نظيف" (Clean))
    try:
        rivers_url = "https://gist.githubusercontent.com/Gemini-Helper-Account/f83713076b10d321151614f1074a8f9a/raw/iraq_rivers_cleaned.geojson"
        folium.GeoJson(
            rivers_url,
            name="Rivers",
            style_function=lambda x: {'color': '#007BFF', 'weight': 2.0} 
        ).add_to(m)
    except Exception as e:
        st.warning(f"لم نتمكن من تحميل طبقة الأنهار. الخطأ: {e}")

    # --- "التعديل" (EDIT) V10.50 (استخدام "الأيقونة" (Icon) "المحلية" (Local) "الخاصة" (Special) "بك" (your)) ---

    # (هـ) "إضافة" (Add) "العلامات" (Markers)
    try:
        # "هنا" (Here) "نحن" (we) "نستدعي" (call) "الملف" (the file) "الذي" (that) "قمت" (you did) "برفعه" (uploading it)
        icon_path = 'images.png' 
        icon = folium.CustomIcon(
            icon_path,
            icon_size=(30, 30) # "الحجم" (Size) 30x30 "بيكسل" (Pixels)
        )
    except Exception as e:
        st.warning(f"لم نتمكن من تحميل 'images.png'. هل قمت برفعه إلى GitHub؟ سنستخدم الدائرة الافتراضية. الخطأ: {e}")
        icon = None 
    # --- "نهاية" (End) "التعديل" (Edit) ---

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

        if icon:
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=dam_name,
                icon=icon # "تطبيق" (Apply) "الأيقونة" (the icon) "الخاصة" (special) "بك" (your)
            ).add_to(m)
        else:
            # "الخطة" (Plan) "الاحتياطية" (Backup) "إذا" (if) "فشل" (failed) "الرفع" (upload)
            folium.CircleMarker(
                location=[lat, lon],
                radius=8, 
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=dam_name,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.7
            ).add_to(m)

    # (و) "عرض" (Render) "الخريطة" (Map) في "ستريملت" (Streamlit)
    st_folium(m, width='100%', height=600)

    # (ز) "الشعار" (Logo) (في "أسفل" (Bottom))
    try:
        st.image("../logo.jpg", width=200) 
    except Exception as e:
        st.warning("لم يتم العثور على الشعار (logo.jpg)")
