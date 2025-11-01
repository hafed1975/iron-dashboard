import streamlit as st

# "الدالة" (Function) "العالمية" (Global) لفحص كلمة المرور
def check_password():
    # (أ) التحقق مما إذا كنا قد سجلنا الدخول بالفعل
    if st.session_state.get("password_correct", False):
        return True

    # (ب) إذا لم نسجل الدخول، اعرض "شاشة" (Screen) كلمة المرور
    # (ملاحظة: "تهيئة الصفحة" (Page config) هنا "للصفحة" (Page) "السرية" (Secret) فقط)
    st.set_page_config(page_title="I.R.O.N Login", page_icon="🔒")
    st.title("🔒 المصادقة مطلوبة")
    st.write("يرجى إدخال كلمة المرور للوصول إلى لوحة التحكم.")

    # (ج) قراءة "كلمة المرور السرية" (Secret) (التي خزنتها في Streamlit)
    try:
        correct_password = st.secrets["PASSWORD"]
    except KeyError: # (هذا هو "الخطأ" (Error) "الصحيح" (Correct) إذا لم يتم العثور على "السر" (Secret))
        st.error("ملف الأسرار (Secrets) غير موجود أو أن كلمة المرور غير معرفة. يرجى الاتصال بالمسؤول.")
        return False

    # (د) حقل إدخال كلمة المرور
    password = st.text_input("كلمة المرور:", type="password")

    if st.button("تسجيل الدخول"):
        if password == correct_password:
            # (هـ) كلمة المرور صحيحة!
            st.session_state.password_correct = True
            st.rerun() # (أعد تشغيل الصفحة "لإظهار" (Show) "المحتوى" (Content))
        else:
            st.error("كلمة المرور التي أدخلتها غير صحيحة.")

    return False # (لا تستمر إذا كانت كلمة المرور خاطئة)
