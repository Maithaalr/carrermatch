import json
import base64
import os
import re

import pandas as pd
import streamlit as st
from openai import OpenAI

# =========================
# حطي API KEY هني مباشرة
# =========================
client = OpenAI(api_key="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")

MODEL = "gpt-4.1-mini"

st.set_page_config(
    page_title="بوصلة الشباب المهنية",
    page_icon="Wlogo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Helpers
# =========================
def load_image_as_base64(image_file):
    if not os.path.exists(image_file):
        return None
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def parse_json_response(content):
    content = content.strip()
    content = re.sub(r"^```json\s*", "", content)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


logo_base64 = load_image_as_base64("logo.png")

# =========================
# Same Welcome Page Style
# =========================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">

<style>
[data-testid="stSidebar"] {
    display: none;
}

header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

footer {
    visibility: hidden;
}

html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
}

.stApp {
    background: linear-gradient(135deg, #f7f2ed 0%, #f0e7df 100%);
}

.block-container {
    padding-top: 25px !important;
    padding-left: 55px !important;
    padding-right: 55px !important;
    max-width: 1200px !important;
}

.top-header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 25px;
}

.top-header img {
    height: 62px;
}

.hero-card {
    background: rgba(255, 255, 255, 0.38);
    border: 1px solid rgba(107, 62, 9, 0.18);
    border-radius: 28px;
    padding: 32px 38px;
    margin-bottom: 26px;
}

.divider-title {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-direction: row-reverse;
    gap: 10px;
    margin-bottom: 12px;
}

.divider-title::before {
    content: "";
    width: 70px;
    height: 2px;
    background-color: #6b3e09;
    opacity: 0.8;
}

.divider-title::after {
    content: "";
    width: 30px;
    height: 2px;
    background-color: #6b3e09;
    opacity: 0.8;
}

.divider-title span {
    color: #7a7a7a;
    font-size: 18px;
    font-weight: 400;
}

.main-title {
    color: #6b3e09;
    font-weight: 500;
    font-size: 42px;
    margin: 0 0 10px 0;
}

.sub-title {
    color: #4a4a4a;
    font-size: 20px;
    line-height: 1.8;
    margin: 0;
}

.section-card {
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(107, 62, 9, 0.14);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    border-radius: 18px !important;
    font-family: 'Tajawal', sans-serif !important;
}

.stFileUploader section {
    border: 1.5px dashed #a67c52 !important;
    background: rgba(255,255,255,0.35) !important;
    border-radius: 22px !important;
}

.stButton button {
    background: transparent !important;
    color: #6b3e09 !important;
    border: 1.8px solid #6b3e09 !important;
    padding: 8px 34px !important;
    border-radius: 25px !important;
    font-size: 17px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    font-family: 'Tajawal', sans-serif !important;
}

.stButton button:hover {
    background-color: #6b3e09 !important;
    color: #fff !important;
    border-color: #6b3e09 !important;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.58);
    border: 1px solid rgba(107, 62, 9, 0.14);
    border-radius: 22px;
    padding: 18px;
}

h1, h2, h3, h4, p, label, span, div {
    font-family: 'Tajawal', sans-serif !important;
}

h2, h3 {
    color: #6b3e09 !important;
}
</style>
""", unsafe_allow_html=True)

if logo_base64:
    st.markdown(
        f"""
        <div class="top-header">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<div class="hero-card">
    <div class="divider-title"><span>ابدأ رحلتك</span></div>
    <h1 class="main-title">بوصلة الشباب المهنية</h1>
        
</div>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """
أنت مستشار مهني ذكي في معرض توظيف.

لديك قائمة وظائف تحتوي فقط على:
- اسم الجهة
- المسمى الوظيفي

مهمتك:
تحليل بيانات الباحث عن العمل ومقارنتها مع الوظائف المتاحة اعتماداً على:
- المستوى الدراسي
- التخصص
- المهارات
- الخبرة
- بيئة العمل المفضلة

حتى لو لم تتوفر متطلبات الوظيفة، استنتج المهارات وطبيعة العمل من المسمى الوظيفي واسم الجهة بشكل منطقي.

قواعد مهمة:
- اختر فقط من قائمة الوظائف المتاحة.
- لا تخترع وظائف أو جهات غير موجودة.
- النسبة تقديرية وليست قبولاً وظيفياً.
- لا تطلب معلومات إضافية.
- أخرج النتيجة JSON فقط بدون أي شرح خارجي.


آلية احتساب نسبة التقارب:

1. التخصص المناسب للوظيفة = 35%
2. المهارات المناسبة للوظيفة = 35%
3. المستوى الدراسي = 15%
4. الخبرة = 10%
5. بيئة العمل المفضلة = 5%

احسب النسبة النهائية من 100 بناءً على هذه الأوزان.

صيغة JSON المطلوبة:
{
  "matches": [
    {
      "rank": 1,
      "entity": "اسم الجهة",
      "job_title": "المسمى الوظيفي",
      "match_percentage": 90,
      "reason": "سبب مختصر",
      "skill_to_develop": "مهارة مقترحة"
    }
  ],
  "general_note": "ملاحظة قصيرة"
}
"""


def load_jobs():
    file_path = "jobs_template.xlsx"  # اسم ملف الإكسل

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    required_cols = ["اسم الجهة", "المسمى الوظيفي"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"ملف الإكسل لازم يحتوي على عمود: {col}")
            st.stop()

    df = df.dropna(subset=["اسم الجهة", "المسمى الوظيفي"])
    return df



def get_ai_matches(visitor_data, jobs_df):
    jobs = jobs_df[["اسم الجهة", "المسمى الوظيفي"]].to_dict(orient="records")

    user_payload = {
        "visitor": visitor_data,
        "available_jobs": jobs
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False)
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    return parse_json_response(content)


with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    def load_jobs():
        file_path = "jobs_template.xlsx"  # اسم ملف الإكسل

        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        required_cols = ["اسم الجهة", "المسمى الوظيفي"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"ملف الإكسل لازم يحتوي على عمود: {col}")
                st.stop()

        df = df.dropna(subset=["اسم الجهة", "المسمى الوظيفي"])
        return df

    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        major = st.text_input("التخصص", placeholder="     ")
        skills = st.text_area("المهارات", placeholder="          ")
        experience = st.text_input("الخبرة", placeholder="        ")

    with col2:
        education_level = st.selectbox(
            "المستوى الدراسي",
            [
                "ثانوية عامة",
                "دبلوم",
                "دبلوم عالي",
                "بكالوريوس",
                "ماجستير",
                "دكتوراه"
            ]
        )
        preferred_environment = st.selectbox(
            "بيئة العمل المفضلة",
            ["مكتبي", "ميداني", "تقني", "إداري", "خدمة متعاملين"]
        )

    submit = st.button("اعرض النتيجة", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


if submit:

    if (not major.strip() or not skills.strip() or not experience.strip()
            or education_level == "       "
            or preferred_environment == "   "):
        st.warning("يرجى تعبئة جميع الحقول")
        st.stop()

    jobs_df = load_jobs()


    visitor_data = {
        "education_level": education_level,
        "major": major,
        "skills": skills,
        "experience": experience,
        "preferred_environment": preferred_environment
    }

    with st.spinner("جاري تحليل الوظائف المناسبة..."):
        result = get_ai_matches(visitor_data, jobs_df)

    matches = result.get("matches", [])

    if not matches:
        st.error("لم يتم العثور على نتائج مناسبة.")
        st.stop()

    top = matches[0]

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown('<div class="divider-title"><span>نتيجتك</span></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">نتيجتك المهنية الذكية</h1>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("أفضل وظيفة مناسبة", top["job_title"])

    with c2:
        st.metric("الجهة", top["entity"])

    with c3:
        st.metric("نسبة التقارب", f'{top["match_percentage"]}%')

    st.progress(top["match_percentage"] / 100)

    st.subheader("لماذا هذه الوظيفة؟")
    st.info(top["reason"])

    st.subheader("مهارة مقترحة للتطوير")
    st.success(top["skill_to_develop"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("أفضل 3 وظائف مناسبة لك")

    for match in matches[:3]:
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([1, 3, 2])

            with col_a:
                st.markdown(f"### #{match['rank']}")

            with col_b:
                st.markdown(f"**{match['job_title']}**")
                st.write(match["entity"])
                st.caption(match["reason"])

            with col_c:
                st.metric("نسبة التقارب", f"{match['match_percentage']}%")
                st.progress(match["match_percentage"] / 100)

    st.caption(result.get("general_note", "النسبة تقديرية ولا تعني القبول أو الترشيح الرسمي."))
    st.markdown('</div>', unsafe_allow_html=True)
