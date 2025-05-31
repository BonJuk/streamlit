import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# -----------------------------
# 1. Setup
st.set_page_config(page_title="부산 관광지 혼잡도 시각화", layout="wide")
st.title("🗺️ 부산 관광지 혼잡도 및 유동인구 분석 WebApp")

# -----------------------------
# 2. Sample Data (실제 공공데이터로 교체 가능)
data = {
    '관광지': ['해운대', '광안리', '자갈치시장', '태종대', '용두산공원'],
    '위도': [35.1587, 35.1533, 35.0971, 35.0512, 35.1038],
    '경도': [129.1604, 129.1186, 129.0305, 129.0849, 129.0327]
}
locations_df = pd.DataFrame(data)

dates = pd.date_range("2024-05-01", "2024-05-31", freq='D')
time_slots = list(range(0, 24))

@st.cache_data
def generate_traffic_data():
    rows = []
    for _, row in locations_df.iterrows():
        for date in dates:
            for hour in time_slots:
                traffic = np.random.randint(50, 1000)  # 임의 유동인구 수
                rows.append({
                    '관광지': row['관광지'],
                    '날짜': date.date(),
                    '시간': hour,
                    '유동인구': traffic
                })
    return pd.DataFrame(rows)

traffic_df = generate_traffic_data()

# -----------------------------
# 3. Sidebar Input
st.sidebar.header("설정")
selected_date = st.sidebar.date_input("날짜 선택", value=pd.to_datetime("2024-05-15"))
selected_place = st.sidebar.selectbox("관광지 선택", locations_df['관광지'].tolist())

# -----------------------------
# 4. Filtered Data
filtered = traffic_df[
    (traffic_df['관광지'] == selected_place) &
    (traffic_df['날짜'] == selected_date)
]

# -----------------------------
# 5. Line Chart
st.subheader(f"'{selected_place}'의 시간대별 유동인구")
st.line_chart(filtered.set_index('시간')['유동인구'])

# -----------------------------
# 6. Map Visualization with congestion level
st.subheader("부산 주요 관광지 혼잡도 지도")

# 혼잡도 등급 (평균 기준): 여유 (<300), 보통 (300~700), 혼잡 (>700)
congestion_today = traffic_df[traffic_df['날짜'] == selected_date].groupby('관광지')['유동인구'].mean().reset_index()
congestion_today = congestion_today.merge(locations_df, on='관광지')
congestion_today['혼잡도'] = pd.cut(
    congestion_today['유동인구'],
    bins=[0, 300, 700, 1500],
    labels=['여유', '보통', '혼잡']
)

color_map = {'여유': [0, 255, 0], '보통': [255, 165, 0], '혼잡': [255, 0, 0]}
congestion_today['color'] = congestion_today['혼잡도'].astype(str).map(color_map)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=congestion_today,
    get_position='[경도, 위도]',
    get_color='color',
    get_radius=300,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=35.15,
    longitude=129.06,
    zoom=11,
    pitch=0
)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "{관광지}\n혼잡도: {혼잡도}"}
))

# -----------------------------
# 7. Footer
st.caption("데이터는 예시이며, 실제 부산시 공공데이터포털의 유동인구 데이터를 사용할 수 있습니다.")
