import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="منظومة تحليل العقود الخاصة",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# DESIGN
# =========================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;600;700&display=swap" rel="stylesheet">

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
    background:
        radial-gradient(circle at top right, rgba(255,255,255,0.8), transparent 35%),
        linear-gradient(135deg, #f8f4f0 0%, #efe5dc 100%);
}

.block-container {
    padding-top: 35px !important;
    padding-left: 55px !important;
    padding-right: 55px !important;
    max-width: 1450px !important;
}

/* HERO */
.hero-card {
    background: rgba(255,255,255,0.48);
    border: 1px solid rgba(107,62,9,0.15);
    border-radius: 30px;
    padding: 42px 46px;
    margin-bottom: 25px;
    box-shadow: 0 8px 30px rgba(107,62,9,0.04);
}

.eyebrow {
    color: #8a725b;
    font-size: 16px;
    margin-bottom: 8px;
}

.main-title {
    color: #6b3e09;
    font-size: 46px;
    font-weight: 500;
    margin: 0;
}

.hero-text {
    color: #555;
    font-size: 19px;
    line-height: 1.9;
    margin-top: 12px;
    max-width: 850px;
}

/* SECTION */
.section-title {
    color: #6b3e09;
    font-size: 29px;
    font-weight: 500;
    margin-top: 35px;
    margin-bottom: 6px;
}

.section-subtitle {
    color: #777;
    font-size: 15px;
    margin-bottom: 20px;
}

/* KPI */
.kpi-card {
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(107,62,9,0.12);
    border-radius: 24px;
    padding: 22px;
    min-height: 125px;
    box-shadow: 0 6px 22px rgba(80,50,20,0.035);
}

.kpi-label {
    color: #85776b;
    font-size: 14px;
    margin-bottom: 9px;
}

.kpi-value {
    color: #6b3e09;
    font-size: 30px;
    font-weight: 600;
}

.kpi-note {
    color: #999;
    font-size: 12px;
    margin-top: 5px;
}

/* CHART CARD */
.chart-card {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(107,62,9,0.11);
    border-radius: 25px;
    padding: 15px 20px 5px 20px;
    margin-bottom: 18px;
}

/* INSIGHT */
.insight-card {
    background: rgba(107,62,9,0.06);
    border-right: 4px solid #6b3e09;
    border-radius: 20px;
    padding: 22px 25px;
    margin: 18px 0 25px 0;
}

.insight-label {
    color: #6b3e09;
    font-size: 13px;
    font-weight: 600;
}

.insight-text {
    color: #444;
    font-size: 17px;
    line-height: 1.8;
    margin-top: 5px;
}

/* UPLOADER */
.stFileUploader section {
    border: 1.5px dashed #a67c52 !important;
    background: rgba(255,255,255,0.4) !important;
    border-radius: 22px !important;
}

/* FILTERS */
div[data-baseweb="select"] {
    border-radius: 16px !important;
}

h1,h2,h3,h4,p,label,span,div {
    font-family: 'Tajawal', sans-serif !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def clean_columns(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\xa0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


def find_column(df, possibilities):
    for col in possibilities:
        if col in df.columns:
            return col
    return None


def numeric_series(df, col):
    if col is None:
        return pd.Series(0, index=df.index)

    return pd.to_numeric(
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("AED", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)


def safe_mean(df, col):
    if col is None:
        return 0

    values = pd.to_numeric(df[col], errors="coerce")
    return values.mean() if values.notna().any() else 0


def style_fig(fig, height=420):

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Tajawal",
            color="#555"
        ),
        margin=dict(l=25, r=25, t=55, b=25),
        legend_title_text=""
    )

    return fig


def kpi_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero-card">

    <div class="eyebrow">
        ذكاء القوى العاملة
    </div>

    <h1 class="main-title">
        منظومة تحليل العقود الخاصة
    </h1>

    <div class="hero-text">
        تحليل متكامل للعقود الخاصة بهدف فهم توزيعها،
        خصائص القوى العاملة، الكفاءات، التكلفة،
        والاستثناءات التي تستحق المراجعة الإدارية.
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "ارفع ملف بيانات الموظفين",
    type=["xlsx", "xls"]
)

if uploaded_file is None:

    st.markdown("""
    <div class="insight-card">
        <div class="insight-label">ابدأ التحليل</div>
        <div class="insight-text">
        ارفع ملف Excel وسيتم تحديد العقود الخاصة وتحليلها تلقائياً.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# READ DATA
# =========================================================

try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"تعذر قراءة الملف: {e}")
    st.stop()

df = clean_columns(df)


# =========================================================
# COLUMN MAPPING
# =========================================================

contract_col = find_column(
    df,
    ["نوع العقد"]
)

department_col = find_column(
    df,
    ["الدائرة"]
)

entity_col = find_column(
    df,
    ["اسم الجهة التابعة"]
)

employee_col = find_column(
    df,
    ["اسم الموظف"]
)

employee_id_col = find_column(
    df,
    ["الرقم الوظيفي"]
)

unit_col = find_column(
    df,
    ["الوحدة التنظيمية"]
)

job_title_col = find_column(
    df,
    ["المسمى الوظيفي"]
)

job_col = find_column(
    df,
    ["الوظيفة"]
)

grade_col = find_column(
    df,
    ["الدرجة الوظيفية"]
)

nationality_col = find_column(
    df,
    ["الجنسية"]
)

gender_col = find_column(
    df,
    ["الجنس"]
)

age_col = find_column(
    df,
    ["العمر"]
)

service_col = find_column(
    df,
    ["مدة الخدمة"]
)

education_col = find_column(
    df,
    ["المستوى التعليمي"]
)

major_col = find_column(
    df,
    ["التخصص"]
)

qualification_match_col = find_column(
    df,
    ["هل المؤهل متوافق للوظيفة"]
)

experience_col = find_column(
    df,
    ["عدد سنوات الخبرة السابقة"]
)


# =========================================================
# CONTRACT FILTER
# =========================================================

if contract_col is None:
    st.error("لم يتم العثور على حقل 'نوع العقد'.")
    st.stop()


contracts_available = (
    df[contract_col]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

special_mask = (
    df[contract_col]
    .astype(str)
    .str.strip()
    .str.contains("خاص", na=False)
)

special_df = df[special_mask].copy()


if special_df.empty:

    st.warning(
        "لم يتم العثور على سجلات تحتوي على كلمة 'خاص' في نوع العقد."
    )

    st.write("أنواع العقود الموجودة:")
    st.write(contracts_available)

    st.stop()


# =========================================================
# FINANCIAL CALCULATION
# =========================================================

financial_columns = [
    "الراتب الاساسي",
    "الراتب الأساسي",
    "التكميلي",
    "بدل هاتف",
    "مساهمة الدائرة في التأمينات الاجتماعية",
    "المكافأة الشهرية",
    "علاوة ابناء",
    "علاوة أبناء",
    "بدل مؤهل",
    "بدل طبيعة عمل"
]

existing_financial_cols = [
    col for col in financial_columns
    if col in special_df.columns
]

special_df["التكلفة الشهرية التقديرية"] = 0.0

for col in existing_financial_cols:
    special_df["التكلفة الشهرية التقديرية"] += numeric_series(
        special_df,
        col
    )


# =========================================================
# FILTERS
# =========================================================

st.markdown(
    '<div class="section-title">تصفية البيانات</div>',
    unsafe_allow_html=True
)

filter_cols = st.columns(4)

filtered_df = special_df.copy()


with filter_cols[0]:

    if department_col:

        departments = sorted(
            special_df[department_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_dept = st.multiselect(
            "الدائرة",
            departments
        )

        if selected_dept:
            filtered_df = filtered_df[
                filtered_df[department_col]
                .astype(str)
                .isin(selected_dept)
            ]


with filter_cols[1]:

    if unit_col:

        units = sorted(
            filtered_df[unit_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_units = st.multiselect(
            "الوحدة التنظيمية",
            units
        )

        if selected_units:
            filtered_df = filtered_df[
                filtered_df[unit_col]
                .astype(str)
                .isin(selected_units)
            ]


with filter_cols[2]:

    if grade_col:

        grades = sorted(
            filtered_df[grade_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_grades = st.multiselect(
            "الدرجة الوظيفية",
            grades
        )

        if selected_grades:
            filtered_df = filtered_df[
                filtered_df[grade_col]
                .astype(str)
                .isin(selected_grades)
            ]


with filter_cols[3]:

    if nationality_col:

        nationalities = sorted(
            filtered_df[nationality_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_nat = st.multiselect(
            "الجنسية",
            nationalities
        )

        if selected_nat:
            filtered_df = filtered_df[
                filtered_df[nationality_col]
                .astype(str)
                .isin(selected_nat)
            ]


# =========================================================
# KPIs
# =========================================================

total_employees = len(df)
special_count = len(filtered_df)

special_percentage = (
    len(special_df) / total_employees * 100
    if total_employees > 0
    else 0
)

monthly_cost = filtered_df[
    "التكلفة الشهرية التقديرية"
].sum()

avg_cost = filtered_df[
    "التكلفة الشهرية التقديرية"
].mean()

avg_age = safe_mean(
    filtered_df,
    age_col
)

avg_experience = safe_mean(
    filtered_df,
    experience_col
)


st.markdown(
    '<div class="section-title">العقود الخاصة في لمحة</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'نظرة تنفيذية على حجم العقود الخاصة وخصائصها الرئيسية.'
    '</div>',
    unsafe_allow_html=True
)


k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    kpi_card(
        "عدد العقود الخاصة",
        f"{special_count:,}",
        "موظف"
    )

with k2:
    kpi_card(
        "نسبة العقود الخاصة",
        f"{special_percentage:.1f}%",
        "من إجمالي القوى العاملة"
    )

with k3:
    kpi_card(
        "التكلفة الشهرية",
        f"{monthly_cost:,.0f}",
        "درهم تقديرياً"
    )

with k4:
    kpi_card(
        "متوسط العمر",
        f"{avg_age:.1f}",
        "سنة"
    )

with k5:
    kpi_card(
        "متوسط الخبرة السابقة",
        f"{avg_experience:.1f}",
        "سنة"
    )


# =========================================================
# AUTOMATIC FIRST INSIGHT
# =========================================================

if department_col and not filtered_df.empty:

    dept_counts = (
        filtered_df[department_col]
        .fillna("غير محدد")
        .value_counts()
    )

    top_department = dept_counts.index[0]
    top_count = dept_counts.iloc[0]

    top_percentage = (
        top_count / len(filtered_df) * 100
    )

    st.markdown(
        f"""
        <div class="insight-card">

            <div class="insight-label">
                أبرز ملاحظة
            </div>

            <div class="insight-text">
                تتركز أعلى نسبة من العقود الخاصة في
                <b>{top_department}</b>،
                بعدد <b>{top_count:,}</b> موظف،
                بما يمثل تقريباً
                <b>{top_percentage:.1f}%</b>
                من العقود الخاصة ضمن البيانات المعروضة.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SECTION 1
# WHERE ARE SPECIAL CONTRACTS?
# =========================================================

st.markdown(
    '<div class="section-title">'
    'أين تتركز العقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'تحليل التوزيع المؤسسي للعقود الخاصة عبر الدوائر والوحدات التنظيمية.'
    '</div>',
    unsafe_allow_html=True
)


c1, c2 = st.columns([1.15, 1])


# DEPARTMENT BAR
with c1:

    if department_col:

        dept_data = (
            filtered_df[department_col]
            .fillna("غير محدد")
            .value_counts()
            .reset_index()
        )

        dept_data.columns = [
            "الدائرة",
            "عدد العقود"
        ]

        fig = px.bar(
            dept_data.head(12),
            x="عدد العقود",
            y="الدائرة",
            orientation="h",
            title="العقود الخاصة حسب الدائرة"
        )

        fig.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# UNIT TREEMAP
with c2:

    if unit_col:

        tree_df = (
            filtered_df
            .groupby(
                [department_col, unit_col],
                dropna=False
            )
            .size()
            .reset_index(name="عدد العقود")
        )

        tree_df[department_col] = (
            tree_df[department_col]
            .fillna("غير محدد")
        )

        tree_df[unit_col] = (
            tree_df[unit_col]
            .fillna("غير محدد")
        )

        fig = px.treemap(
            tree_df,
            path=[
                department_col,
                unit_col
            ],
            values="عدد العقود",
            title="الانتشار داخل الوحدات التنظيمية"
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# CONTRACT DEPENDENCY
# =========================================================

if department_col:

    total_by_dept = (
        df.groupby(department_col)
        .size()
        .reset_index(name="إجمالي الموظفين")
    )

    special_by_dept = (
        special_df.groupby(department_col)
        .size()
        .reset_index(name="العقود الخاصة")
    )

    dependency = pd.merge(
        total_by_dept,
        special_by_dept,
        on=department_col,
        how="left"
    )

    dependency["العقود الخاصة"] = (
        dependency["العقود الخاصة"]
        .fillna(0)
    )

    dependency["نسبة الاعتماد"] = (
        dependency["العقود الخاصة"]
        / dependency["إجمالي الموظفين"]
        * 100
    )

    dependency = dependency.sort_values(
        "نسبة الاعتماد",
        ascending=False
    )

    fig = px.bar(
        dependency.head(15),
        x="نسبة الاعتماد",
        y=department_col,
        orientation="h",
        title="نسبة اعتماد كل دائرة على العقود الخاصة",
        text_auto=".1f"
    )

    fig.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    style_fig(fig, 480)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SECTION 2
# WHO ARE THEY?
# =========================================================

st.markdown(
    '<div class="section-title">'
    'من هم موظفو العقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'قراءة ديموغرافية ووظيفية للقوى العاملة بعقود خاصة.'
    '</div>',
    unsafe_allow_html=True
)


c1, c2 = st.columns(2)


# NATIONALITY
with c1:

    if nationality_col:

        nat_data = (
            filtered_df[nationality_col]
            .fillna("غير محدد")
            .value_counts()
            .head(10)
            .reset_index()
        )

        nat_data.columns = [
            "الجنسية",
            "العدد"
        ]

        fig = px.bar(
            nat_data,
            x="العدد",
            y="الجنسية",
            orientation="h",
            title="أبرز الجنسيات"
        )

        fig.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# GENDER
with c2:

    if gender_col:

        gender_data = (
            filtered_df[gender_col]
            .fillna("غير محدد")
            .value_counts()
            .reset_index()
        )

        gender_data.columns = [
            "الجنس",
            "العدد"
        ]

        fig = px.pie(
            gender_data,
            names="الجنس",
            values="العدد",
            hole=0.62,
            title="التوزيع حسب الجنس"
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# AGE
if age_col:

    ages = pd.to_numeric(
        filtered_df[age_col],
        errors="coerce"
    )

    age_df = pd.DataFrame({
        "العمر": ages
    }).dropna()

    fig = px.histogram(
        age_df,
        x="العمر",
        nbins=12,
        title="التوزيع العمري لموظفي العقود الخاصة"
    )

    style_fig(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# JOB STRUCTURE
# =========================================================

st.markdown(
    '<div class="section-title">'
    'في أي وظائف تتركز العقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

j1, j2 = st.columns(2)


with j1:

    if job_title_col:

        jobs_data = (
            filtered_df[job_title_col]
            .fillna("غير محدد")
            .value_counts()
            .head(15)
            .reset_index()
        )

        jobs_data.columns = [
            "المسمى الوظيفي",
            "العدد"
        ]

        fig = px.bar(
            jobs_data,
            x="العدد",
            y="المسمى الوظيفي",
            orientation="h",
            title="أكثر المسميات الوظيفية"
        )

        fig.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        style_fig(fig, 500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with j2:

    if grade_col:

        grade_data = (
            filtered_df[grade_col]
            .fillna("غير محدد")
            .value_counts()
            .reset_index()
        )

        grade_data.columns = [
            "الدرجة الوظيفية",
            "العدد"
        ]

        fig = px.bar(
            grade_data,
            x="الدرجة الوظيفية",
            y="العدد",
            title="التوزيع حسب الدرجة الوظيفية"
        )

        style_fig(fig, 500)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# SECTION 3
# QUALIFICATIONS
# =========================================================

st.markdown(
    '<div class="section-title">'
    'ما مستوى الكفاءات التي تستقطبها العقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'تحليل المؤهلات والتخصصات والخبرات ومدى مواءمتها للوظائف الحالية.'
    '</div>',
    unsafe_allow_html=True
)


q1, q2 = st.columns(2)


with q1:

    if education_col:

        edu_data = (
            filtered_df[education_col]
            .fillna("غير محدد")
            .value_counts()
            .reset_index()
        )

        edu_data.columns = [
            "المستوى التعليمي",
            "العدد"
        ]

        fig = px.bar(
            edu_data,
            x="العدد",
            y="المستوى التعليمي",
            orientation="h",
            title="المستوى التعليمي"
        )

        fig.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with q2:

    if qualification_match_col:

        match_data = (
            filtered_df[qualification_match_col]
            .fillna("غير محدد")
            .value_counts()
            .reset_index()
        )

        match_data.columns = [
            "حالة التوافق",
            "العدد"
        ]

        fig = px.pie(
            match_data,
            names="حالة التوافق",
            values="العدد",
            hole=0.65,
            title="مدى توافق المؤهل مع الوظيفة"
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


if major_col:

    major_data = (
        filtered_df[major_col]
        .fillna("غير محدد")
        .value_counts()
        .head(15)
        .reset_index()
    )

    major_data.columns = [
        "التخصص",
        "العدد"
    ]

    fig = px.treemap(
        major_data,
        path=["التخصص"],
        values="العدد",
        title="أبرز التخصصات"
    )

    style_fig(fig, 450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SECTION 4
# EXPERIENCE VS COST
# =========================================================

if experience_col:

    filtered_df["_experience"] = pd.to_numeric(
        filtered_df[experience_col],
        errors="coerce"
    )

    scatter_df = filtered_df[
        filtered_df["_experience"].notna()
    ].copy()

    if not scatter_df.empty:

        st.markdown(
            '<div class="section-title">'
            'هل ترتبط التكلفة بمستوى الخبرة؟'
            '</div>',
            unsafe_allow_html=True
        )

        hover_fields = []

        if employee_col:
            hover_fields.append(employee_col)

        if job_title_col:
            hover_fields.append(job_title_col)

        if department_col:
            hover_fields.append(department_col)

        fig = px.scatter(
            scatter_df,
            x="_experience",
            y="التكلفة الشهرية التقديرية",
            hover_data=hover_fields,
            title="الخبرة السابقة مقابل التكلفة الشهرية"
        )

        fig.update_xaxes(
            title="سنوات الخبرة السابقة"
        )

        fig.update_yaxes(
            title="التكلفة الشهرية التقديرية"
        )

        style_fig(fig, 520)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# SECTION 5
# FINANCIAL INTELLIGENCE
# =========================================================

st.markdown(
    '<div class="section-title">'
    'ما التكلفة الفعلية للعقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'تحليل توزيع التكلفة والتفاوتات بين الجهات والوظائف.'
    '</div>',
    unsafe_allow_html=True
)


f1, f2, f3 = st.columns(3)

with f1:
    kpi_card(
        "إجمالي التكلفة الشهرية",
        f"{monthly_cost:,.0f}",
        "درهم"
    )

with f2:
    kpi_card(
        "التكلفة السنوية التقديرية",
        f"{monthly_cost * 12:,.0f}",
        "درهم"
    )

with f3:
    kpi_card(
        "متوسط تكلفة الموظف",
        f"{avg_cost:,.0f}",
        "درهم شهرياً"
    )


if department_col:

    cost_dept = (
        filtered_df
        .groupby(department_col)[
            "التكلفة الشهرية التقديرية"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )

    fig = px.bar(
        cost_dept,
        x="التكلفة الشهرية التقديرية",
        y=department_col,
        orientation="h",
        title="التكلفة الشهرية للعقود الخاصة حسب الدائرة"
    )

    fig.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    style_fig(fig, 500)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# COST COMPONENTS
# =========================================================

if existing_financial_cols:

    component_values = []

    for col in existing_financial_cols:

        component_values.append({
            "المكون": col,
            "القيمة": numeric_series(
                filtered_df,
                col
            ).sum()
        })

    component_df = pd.DataFrame(
        component_values
    )

    component_df = component_df[
        component_df["القيمة"] > 0
    ]

    if not component_df.empty:

        fig = px.bar(
            component_df,
            x="المكون",
            y="القيمة",
            title="مكونات التكلفة الشهرية"
        )

        style_fig(fig, 460)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# SECTION 6
# LONG TENURE
# =========================================================

if service_col:

    service_numeric = pd.to_numeric(
        filtered_df[service_col],
        errors="coerce"
    )

    if service_numeric.notna().any():

        filtered_df["_service_years"] = service_numeric

        bins = [
            -1,
            1,
            3,
            5,
            10,
            15,
            np.inf
        ]

        labels = [
            "أقل من سنة",
            "1 - 3 سنوات",
            "3 - 5 سنوات",
            "5 - 10 سنوات",
            "10 - 15 سنة",
            "15 سنة فأكثر"
        ]

        filtered_df["_service_group"] = pd.cut(
            filtered_df["_service_years"],
            bins=bins,
            labels=labels
        )

        service_data = (
            filtered_df["_service_group"]
            .value_counts(sort=False)
            .reset_index()
        )

        service_data.columns = [
            "مدة الخدمة",
            "العدد"
        ]

        st.markdown(
            '<div class="section-title">'
            'منذ متى تستمر العقود الخاصة؟'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.bar(
            service_data,
            x="مدة الخدمة",
            y="العدد",
            title="توزيع العقود الخاصة حسب مدة الخدمة"
        )

        style_fig(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        long_tenure = (
            filtered_df["_service_years"] >= 10
        ).sum()

        long_pct = (
            long_tenure
            / len(filtered_df)
            * 100
            if len(filtered_df)
            else 0
        )

        st.markdown(
            f"""
            <div class="insight-card">

                <div class="insight-label">
                    استمرارية العقود
                </div>

                <div class="insight-text">
                    يوجد <b>{long_tenure:,}</b> موظفاً
                    بعقد خاص تجاوزت مدة خدمتهم
                    <b>10 سنوات</b>،
                    بما يمثل
                    <b>{long_pct:.1f}%</b>
                    من العقود الخاصة المعروضة.
                    قد تمثل هذه الفئة مجالاً مناسباً للمراجعة
                    لفهم طبيعة الاحتياج طويل الأمد.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# SECTION 7
# COST OUTLIERS
# =========================================================

st.markdown(
    '<div class="section-title">'
    'أين توجد الحالات المالية غير الاعتيادية؟'
    '</div>',
    unsafe_allow_html=True
)


cost_series = filtered_df[
    "التكلفة الشهرية التقديرية"
]

if len(cost_series) >= 4 and cost_series.max() > 0:

    q1 = cost_series.quantile(0.25)
    q3 = cost_series.quantile(0.75)

    iqr = q3 - q1

    upper_limit = q3 + (1.5 * iqr)

    filtered_df["_cost_outlier"] = (
        cost_series > upper_limit
    )

    outlier_count = (
        filtered_df["_cost_outlier"]
        .sum()
    )

    fig = px.box(
        filtered_df,
        y="التكلفة الشهرية التقديرية",
        points="outliers",
        title="توزيع التكلفة وتحديد القيم غير الاعتيادية"
    )

    style_fig(fig, 470)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        f"""
        <div class="insight-card">

            <div class="insight-label">
                Cost Intelligence
            </div>

            <div class="insight-text">
                حدد التحليل الإحصائي
                <b>{outlier_count:,}</b>
                حالة ذات تكلفة أعلى من النطاق المعتاد
                وفقاً لتوزيع البيانات.
                لا تعني هذه الحالات وجود خطأ،
                وإنما تمثل حالات مناسبة للمراجعة والمقارنة.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SECTION 8
# DATA QUALITY
# =========================================================

st.markdown(
    '<div class="section-title">'
    'ما مدى اكتمال بيانات العقود الخاصة؟'
    '</div>',
    unsafe_allow_html=True
)

quality_fields = [
    department_col,
    employee_id_col,
    employee_col,
    unit_col,
    job_title_col,
    grade_col,
    nationality_col,
    age_col,
    education_col,
    qualification_match_col
]

quality_fields = [
    col for col in quality_fields
    if col is not None
]

if quality_fields:

    missing_stats = []

    for col in quality_fields:

        missing_count = (
            filtered_df[col]
            .isna()
            .sum()
        )

        missing_stats.append({
            "الحقل": col,
            "البيانات الناقصة": missing_count
        })

    missing_df = pd.DataFrame(
        missing_stats
    ).sort_values(
        "البيانات الناقصة",
        ascending=False
    )

    total_cells = (
        len(filtered_df)
        * len(quality_fields)
    )

    missing_cells = (
        filtered_df[quality_fields]
        .isna()
        .sum()
        .sum()
    )

    completeness = (
        (1 - missing_cells / total_cells) * 100
        if total_cells
        else 0
    )

    d1, d2 = st.columns(
        [0.7, 1.3]
    )

    with d1:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=completeness,
                number={
                    "suffix": "%"
                },
                title={
                    "text": "اكتمال البيانات"
                },
                gauge={
                    "axis": {
                        "range": [0, 100]
                    }
                }
            )
        )

        style_fig(fig, 400)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with d2:

        fig = px.bar(
            missing_df,
            x="البيانات الناقصة",
            y="الحقل",
            orientation="h",
            title="الحقول الأكثر نقصاً"
        )

        fig.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        style_fig(fig, 400)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# FINAL EXECUTIVE VIEW
# =========================================================
# =========================================================
# FINAL EXECUTIVE VIEW
# =========================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="eyebrow">Executive Intelligence</div>

        <h1 class="main-title" style="font-size:34px;">
            ماذا تخبرنا البيانات؟
        </h1>

        <div class="hero-text">
            تجمع المنظومة بين تحليل الانتشار المؤسسي،
            وخصائص القوى العاملة، والكفاءات،
            والتكلفة، والاستثناءات؛ بهدف توجيه
            المراجعة الإدارية إلى الحالات والأنماط
            الأكثر أهمية.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA PREVIEW
# =========================================================

with st.expander(
    "عرض بيانات العقود الخاصة"
):

    preview_cols = [
        col for col in [
            employee_id_col,
            employee_col,
            department_col,
            unit_col,
            job_title_col,
            grade_col,
            nationality_col,
            age_col,
            experience_col
        ]
        if col is not None
    ]

    preview_cols.append(
        "التكلفة الشهرية التقديرية"
    )

    st.dataframe(
        filtered_df[preview_cols],
        use_container_width=True,
        hide_index=True
    )
