import streamlit as st
from password_check import check_password # <-- "استيراد" (Import) "الدالة" (Function)

# --- (1) "التطبيق" (App) الرئيسي ---
# "تحقق" (Check) من "كلمة المرور" (Password) "أولاً" (First)
if check_password():
    # --- "الآن" (Now) نحن آمنون، اعرض "التطبيق" (App) ---

    # (أ) تهيئة الصفحة (يجب أن يكون أول أمر بعد تسجيل الدخول)
    st.set_page_config(
        page_title="I.R.O.N Dashboard",
        page_icon="🌊",
        layout="wide" 
    )

    # (ب) عرض الشعار والمعلومات
    # (ملاحظة: قمتُ "بإصلاح" (Fixed) "خطأ الشعار" (Logo error) الذي رأيته في "صورتك" (Screenshot) `image_d3a720.jpg`)
    try:
        st.image("logo.jpg", width=400) 
    except Exception as e:
        st.error(f"لم يتم العثور على ملف الشعار 'logo.jpg'. الخطأ: {e}")

    st.title("أهلاً بك في لوحة تحكم مشروع I.R.O.N")
    st.write("لقد قمت بتسجيل الدخول بنجاح.")
    st.write("يرجى اختيار التطبيق المطلوب من الشريط الجانبي على اليسار.")
    st.write("---")
    st.header("مكونات المشروع:")

    st.subheader("1. 🌊 لوحة تحكم I.R.O.N")
    st.write("النموذج الرئيسي للمحاكاة والأمثلية للنظام المائي العراقي.")

    st.subheader("2. (تطبيقات مستقبلية)")
    st.write("هنا ستظهر التطبيقات المستقبلية (مثل تطبيق الطقس).")
