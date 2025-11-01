import streamlit as st

# (1) تهيئة الصفحة (يجب أن يكون أول أمر)
# هذا الأمر سيعمل "لكل" الصفحات
st.set_page_config(
    page_title="I.R.O.N Dashboard",
    page_icon="🌊",
    layout="wide" 
)

# (2) عرض الشعار والمعلومات
# المسار "logo.jpg" صحيح لأن Home.py في المجلد الرئيسي
st.image("logo.jpg", width=400) 

st.title("أهلاً بك في لوحة تحكم مشروع I.R.O.N")
st.write("يرجى اختيار التطبيق المطلوب من الشريط الجانبي على اليسار.")
st.write("---")
st.header("مكونات المشروع:")

st.subheader("1. 🌊 لوحة تحكم I.R.O.N")
st.write("النموذج الرئيسي للمحاكاة والأمثلية للنظام المائي العراقي.")

st.subheader("2. (تطبيقات مستقبلية)")
st.write("هنا ستظهر التطبيقات المستقبلية (مثل تطبيق الطقس).")
