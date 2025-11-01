import streamlit as st

# --- (1) "دالة" (Function) فحص كلمة المرور ---
def check_password():
    # (أ) التحقق مما إذا كنا قد سجلنا الدخول بالفعل
    if st.session_state.get("password_correct", False):
        return True

    # (ب) إذا لم نسجل الدخول، اعرض "شاشة" (Screen) كلمة المرور
    st.set_page_config(page_title="I.R.O.N Login", page_icon="🔒")
    st.title("🔒 المصادقة مطلوبة")
    st.write("يرجى إدخال كلمة المرور للوصول إلى لوحة التحكم.")

    # (ج) قراءة "كلمة المرور السرية" (Secret) من (الخطوة 2)
    try:
        correct_password = st.secrets["PASSWORD"]
    except FileNotFoundError:
        st.error("ملف الأسرار (Secrets) غير موجود. يرجى الاتصال بالمسؤول.")
        return False

    # (د) حقل إدخال كلمة المرور
    password = st.text_input("كلمة المرور:", type="password")

    if st.button("تسجيل الدخول"):
        if password == correct_password:
            # (هـ) كلمة المرور صحيحة!
            st.session_state.password_correct = True
            st.rerun() # (أعد تشغيل الصفحة)
        else:
            st.error("كلمة المرور التي أدخلتها غير صحيحة.")

    return False # (لا تستمر إذا كانت كلمة المرور خاطئة)

# --- (2) "التطبيق" (App) الرئيسي ---
if check_password():
    # --- "الآن" (Now) نحن آمنون، اعرض "التطبيق" (App) ---

    # (أ) تهيئة الصفحة (يجب أن يكون أول أمر بعد تسجيل الدخول)
    st.set_page_config(
        page_title="I.R.O.N Dashboard",
        page_icon="🌊",
        layout="wide" 
    )

    # (ب) عرض الشعار والمعلومات
    # المسار "logo.jpg" صحيح لأن Home.py في المجلد الرئيسي
    st.image("logo.jpg", width=400) 

    st.title("أهلاً بك في لوحة تحكم مشروع I.R.O.N")
    st.write("لقد قمت بتسجيل الدخول بنجاح.")
    st.write("يرجى اختيار التطبيق المطلوب من الشريط الجانبي على اليسار.")
    st.write("---")
    st.header("مكونات المشروع:")

    st.subheader("1. 🌊 لوحة تحكم I.R.O.N")
    st.write("النموذج الرئيسي للمحاكاة والأمثلية للنظام المائي العراقي.")

    st.subheader("2. (تطبيقات مستقبلية)")
    st.write("هنا ستظهر التطبيقات المستقبلية (مثل تطبيق الطقس).")
