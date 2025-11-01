import streamlit as st
from password_check import check_password # "استيراد" (Import) "الدالة" (Function)

# --- (1) "التطبيق" (App) الرئيسي ---
# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():
    # --- "الآن" (Now) نحن آمنون، اعرض "التطبيق" (App) ---

    # (أ) تهيئة الصفحة (يجب أن يكون أول أمر بعد تسجيل الدخول)
    st.set_page_config(
        page_title="مقدمة I.R.O.N", # (تم تغيير "العنوان" (Title))
        page_icon="📜", # (تم تغيير "الأيقونة" (Icon))
        layout="wide" 
    )

    # (ب) عرض الشعار والمعلومات
    try:
        st.image("logo.jpg", width=400) 
    except Exception as e:
        st.warning(f"لم يتم العثور على ملف الشعار 'logo.jpg'.")

    st.title("📜 مقدمة: نظام دعم القرار (I.R.O.N)")
    st.subheader("محاكاة وأمثلية النظام المائي العراقي")
    st.write("---")

    st.header("الملخص التنفيذي")
    st.write("""
    يمثل نظام (I.R.O.N) - (Iraq's Reservoirs Operation Network) أداة دعم قرار استراتيجية
    تم تصميمها لمحاكاة وإيجاد "السياسة التشغيلية المثلى" (Optimal operation policy) لشبكة الخزانات الرئيسية في العراق.
    في مواجهة تحديات "التغير المناخي" (Climate change) و "ندرة المياه" (Water scarcity)، يصبح
    من الضروري الانتقال من "التشغيل التقليدي" (Traditional operation) إلى "التشغيل الذكي" (Smart operation)
    القائم على "البيانات" (Data) و "نماذج الأمثلية" (Optimization models).
    """)

    st.header("الهدف من المشروع")
    st.write("""
    الهدف الأساسي لهذا المشروع هو "تقليل العجز المائي" (Minimize water shortage)
    في "نقاط الطلب الحرجة" (Critical demand points) (مثل بغداد والفرات السفلي)،
    مع "الحفاظ" (Maintaining) على "الخزين المائي" (Reservoir storage) ضمن "الحدود الآمنة" (Safe levels).

    يستخدم هذا "التطبيق" (App) "نموذج برمجة خطية" (Linear Programming model)
    تم بناؤه "بلغة" (Language) `Pyomo` "لحل" (Solve) "مسألة" (Problem) "توزيع" (Allocation) "المياه" (Water)
    عبر 600 "شهر" (Months) (محاكاة 50 عاماً) في "خطوة واحدة" (Single step).
    """)

    st.header("كيفية استخدام هذا التطبيق")
    st.write("""
    يرجى استخدام "الشريط الجانبي" (Sidebar) على "اليسار" (Left) "للتنقل" (Navigate) بين "أجزاء" (Components) "المشروع" (Project):

    * **📜 المقدمة (Home):** (هذه الصفحة) نظرة عامة على المشروع.
    * **📊 لوحة التحكم (Dashboard):** "الواجهة التفاعلية" (Interactive interface) "الرئيسية" (Main) "لتحليل" (Analyze) "نتائج" (Results) "المحاكاة" (Simulation) (مثل "الخزن" (Storage) و "الإطلاقات" (Releases)).
    * **🗺️ الخريطة التفاعلية (Map):** "عرض جغرافي" (Geospatial view) "لأداء" (Performance) "السدود" (Dams) "الرئيسية" (Main).
    """)

    st.info("تم " + "تطوير" + " هذا " + "النموذج" + " (V10.24) " + "بواسطة" + " الذكاء الاصطناعي (Gemini) " + "وإشرافك.")
