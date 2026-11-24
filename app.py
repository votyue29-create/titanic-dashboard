import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 (와이드 레이아웃)
st.set_page_config(
    page_title="타이타닉, 누가 살아남았나?",
    layout="wide"
)

# 2. 데이터 로드 (캐싱 적용)
# 2. 데이터 로드 (CSV 파일 직접 읽기)
@st.cache_data
def load_data():
    df = pd.read_csv('titanic.csv')
    return df

df = load_data()

# 3. 사이드바 필터 구성
with st.sidebar:
    # 성별 필터 (multiselect)
    sex_options = df['sex'].unique().tolist()
    selected_sex = st.multiselect(
        "성별",
        options=sex_options,
        default=sex_options
    )
    
    # 객실 등급 필터 (multiselect)
    pclass_options = sorted(df['pclass'].unique().tolist())
    selected_pclass = st.multiselect(
        "객실 등급",
        options=pclass_options,
        default=pclass_options
    )
    
    # 나이 슬라이더 (0 ~ 80)
    min_age = int(df['age'].min())
    max_age = int(df['age'].max())
    selected_age = st.slider(
        "나이",
        min_value=0,
        max_value=80,
        value=(0, 80)
    )

# 4. 필터링 적용
# 주의: 전체(0~80세) 선택 시 나이 결측치(NaN) 데이터까지 포함해야 891명이 나옵니다.
condition = (
    (df['sex'].isin(selected_sex)) &
    (df['pclass'].isin(selected_pclass))
)

if selected_age == (0, 80):
    filtered_df = df[condition & ((df['age'].between(selected_age[0], selected_age[1])) | (df['age'].isna()))]
else:
    filtered_df = df[condition & (df['age'].between(selected_age[0], selected_age[1]))]

# 5. 메인 화면 타이틀
st.title("타이타닉, 누가 살아남았나?")

# 6. 상단 핵심 지표 (KPI Metric 3개)
col1, col2, col3 = st.columns(3)

total_passengers = len(filtered_df)
survival_rate = (filtered_df['survived'].mean() * 100) if total_passengers > 0 else 0
mean_age = filtered_df['age'].mean() if total_passengers > 0 else 0

with col1:
    st.metric(label="승객 수", value=f"{total_passengers}명")
with col2:
    st.metric(label="생존율", value=f"{survival_rate:.1f}%")
with col3:
    st.metric(label="평균 나이", value=f"{mean_age:.1f}세" if pd.notna(mean_age) else "0.0세")

st.write("") # 여백

# 7. 중단 차트 영역 (2단 분할)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("객실 등급별 생존율(%)")
    if total_passengers > 0:
        # 등급별 생존율 계산
        pclass_surv = filtered_df.groupby('pclass')['survived'].mean().reset_index()
        pclass_surv['survived'] = (pclass_surv['survived'] * 100).round(1)
        pclass_surv['pclass'] = pclass_surv['pclass'].astype(str) + "등급"
        
        fig_bar = px.bar(
            pclass_surv,
            x='pclass',
            y='survived',
            text='survived'
        )
        # 막대 내부 텍스트 및 스타일 설정
        fig_bar.update_traces(
            textposition='inside',
            marker_color='#0068c9'
        )
        fig_bar.update_layout(
            xaxis_title="pclass",
            yaxis_title="survived",
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("생존 여부별 나이 분포")
    if total_passengers > 0:
        # 나이 결측치 제거 후 히스토그램 생성
        age_df = filtered_df.dropna(subset=['age']).copy()
        age_df['survived'] = age_df['survived'].astype(str)
        
        fig_hist = px.histogram(
            age_df,
            x='age',
            color='survived',
            nbins=40,
            barmode='overlay',
            color_discrete_map={'0': '#0068c9', '1': '#83c9ff'}
        )
        fig_hist.update_layout(
            xaxis_title="age",
            yaxis_title="count",
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# 8. 하단 데이터 표 보기 (Expander)
with st.expander("데이터 보기"):
    st.dataframe(filtered_df, use_container_width=True)