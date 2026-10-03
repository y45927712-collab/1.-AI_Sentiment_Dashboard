import streamlit as st
from textblob import TextBlob
import pandas as pd
from deep_translator import GoogleTranslator

# 1. إعدادات وتصميم الصفحة
st.set_page_config(page_title="AI Business Advisor", page_icon="📈", layout="wide")
st.title("🤖 AI Business Advisor & Sentiment Dashboard")
st.write("Upload your Products CSV file to analyze customer feedback and get AI recommendations!")

# 2. صندوق رفع الملفات
uploaded_file = st.file_uploader("Choose your products_report.csv file:", type=["csv"])

if uploaded_file is not None:
    # قراءة ملف الـ CSV بنجاح باستخدام الفاصلة المنقوطة
    df = pd.read_csv(uploaded_file, sep=";")
    
    # تحويل أسماء الأعمدة إلى أحرف كبيرة لتوحيد الفحص
    df.columns = [col.upper() for col in df.columns]
    
    # التأكد من وجود عمود التقييمات الحقيقي، وإذا لم يجد، يضع قيمة افتراضية فارغة لمنع الخطأ
    if "REVIEW" not in df.columns:
        df["REVIEW"] = "no review"

    decisions = []
    scores = []
    recommendations = []

    # 3. محرك الـ AI يمر على كل منتج حقيقي في الجدول ويحلله بدقة
    for index, row in df.iterrows():
        review_text = str(row["REVIEW"]).strip()
        
        # إذا كان الحقل فارغاً أو يحتوي على no review، نعتبره محايداً تلقائياً
        if review_text.lower() == "no review" or review_text == "" or review_text.lower() == "nan":
            decisions.append("细 Neutral")
            scores.append(0.0)
            recommendations.append("No customer review available yet.")
            continue
            
        # خطوة الترجمة التلقائية الآمنة
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(review_text)
        except Exception:
            translated = review_text

        analysis = TextBlob(translated)
        score = analysis.sentiment.polarity
        scores.append(score)

        # تحديد القرار بناءً على منطقة الأمان 0.1 التي برمجتها أنت
        if score > 0.1:
            decisions.append("🟢 Positive")
            recommendations.append("Keep it up! Customer loves the quality.")
        elif score < -0.1:
            decisions.append("🔴 Negative")
            product_title = row.get("TITLE", "This product")
            recommendations.append(f"Action Required: Check price or features for '{product_title}' to reduce complaints.")
        else:
            decisions.append("🟡 Neutral")
            recommendations.append("Consider adding discounts to attract more positive reviews.")

    # إضافة نتائج الـ AI كأعمدة جديدة في الجدول
    df["AI Decision"] = decisions
    df["AI Score"] = scores
    df["AI Recommendation"] = recommendations

    # 4. عرض الإحصائيات الإجمالية
    total_reviews = len(df)
    pos_count = decisions.count("🟢 Positive")
    neg_count = decisions.count("🔴 Negative")
    neu_count = decisions.count("🟡 Neutral")

    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products Analyzed", total_reviews)
    col2.metric("Positive Feedback 🟢", pos_count)
    col3.metric("Neutral Feedback 🟡", neu_count)
    col4.metric("Negative Feedback 🔴", neg_count)

    # 5. خطة العمل والتنبيهات الحمراء الذكية لحماية المتجر
    st.write("### 🧠 AI Business Action Plan:")
    has_negatives = False
    for index, row in df.iterrows():
        if "Negative" in row["AI Decision"]:
            has_negatives = True
            st.error(f"⚠️ **Product: {row.get('TITLE', 'Unknown')}** -> {row['AI Recommendation']} (Reason: {row['REVIEW']})")
            
    if not has_negatives:
        st.success("🎉 Excellent! No negative reviews found in this file.")

    # 6. الرسم البياني وعرض جدول البيانات المطور بالكامل
    st.write("### 📊 Sentiment Chart:")
    st.bar_chart({"Positive": pos_count, "Neutral": neu_count, "Negative": neg_count})

    st.write("### 📋 Full AI Analysis Data Table:")
    st.dataframe(df)
