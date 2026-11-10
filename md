오늘의 대화

날짜: 2026년 11월 10일

1. 학생용 학습 타이머 개발 요청
개발 목표

Streamlit Cloud에서 실행할 수 있는 학생용 학습 타이머 웹 애플리케이션 제작.

요청 기능
시작 버튼
일시정지 버튼
초기화 버튼
과목별 학습 시간 기록
과목별 누적 학습 시간 확인
학습 기록 CSV 다운로드
2. 프로젝트 파일 구성
text
study-timer/
├── main.py
└── requirements.txt

3. requirements.txt

버전 숫자 없이 라이브러리 이름만 사용.

text
streamlit
streamlit-autorefresh
pandas

4. main.py
python
import streamlit as st
import streamlit_autorefresh
import time
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="학생용 학습 타이머",
    page_icon="📚",
    layout="centered"
)

if "running" not in st.session_state:
    st.session_state.running = False

if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "records" not in st.session_state:
    st.session_state.records = []

if "subject" not in st.session_state:
    st.session_state.subject = "수학"

st.title("📚 나의 학습 타이머")
st.caption("오늘도 목표를 향해 한 걸음씩!")

st.divider()

subject = st.selectbox(
    "공부할 과목을 선택하세요.",
    ["국어", "영어", "수학", "과학", "사회", "기타"],
    key="subject"
)

if st.session_state.running:
    elapsed = (
        st.session_state.elapsed
        + time.time() - st.session_state.start_time
    )
else:
    elapsed = st.session_state.elapsed

hours = int(elapsed // 3600)
minutes = int((elapsed % 3600) // 60)
seconds = int(elapsed % 60)

st.subheader("⏱️ 공부 시간")

st.markdown(
    f"""
    <div style="
        background-color: #172554;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <div style="color: #93C5FD; font-size: 18px;">
            {subject} 학습 시간
        </div>
        <div style="
            color: white;
            font-size: 55px;
            font-weight: bold;
            font-family: monospace;
        ">
            {hours:02d}:{minutes:02d}:{seconds:02d}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "▶ 시작",
        use_container_width=True,
        disabled=st.session_state.running
    ):
        st.session_state.start_time = time.time()
        st.session_state.running = True
        st.rerun()

with col2:
    if st.button(
        "⏸ 일시정지",
        use_container_width=True,
        disabled=not st.session_state.running
    ):
        st.session_state.elapsed += (
            time.time() - st.session_state.start_time
        )
        st.session_state.running = False
        st.session_state.start_time = None
        st.rerun()

with col3:
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed = 0.0
        st.session_state.start_time = None
        st.rerun()

st.divider()
st.subheader("📝 학습 기록 저장")

if st.button(
    "💾 현재 공부 시간 기록하기",
    use_container_width=True
):
    current_elapsed = st.session_state.elapsed

    if st.session_state.running:
        current_elapsed += (
            time.time() - st.session_state.start_time
        )

    if current_elapsed > 0:
        st.session_state.records.append({
            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "과목": subject,
            "학습 시간": (
                f"{int(current_elapsed // 3600):02d}:"
                f"{int((current_elapsed % 3600) // 60):02d}:"
                f"{int(current_elapsed % 60):02d}"
            ),
            "초": int(current_elapsed)
        })

        st.session_state.elapsed = 0.0

        if st.session_state.running:
            st.session_state.start_time = time.time()

        st.success("학습 기록이 저장되었습니다!")
        st.rerun()
    else:
        st.warning("먼저 학습 타이머를 시작하세요.")

if st.session_state.running:
    streamlit_autorefresh.st_autorefresh(
        interval=1000,
        key="timer_refresh"
    )

st.divider()
st.subheader("📊 과목별 학습 기록")

if st.session_state.records:

    df = pd.DataFrame(st.session_state.records)

    summary = df.groupby("과목")["초"].sum()

    st.markdown("### 과목별 누적 학습 시간")

    for name, total in summary.items():
        h = int(total // 3600)
        m = int((total % 3600) // 60)
        s = int(total % 60)

        st.write(
            f"📘 **{name}** : "
            f"{h}시간 {m}분 {s}초"
        )

    st.divider()
    st.markdown("### 전체 학습 기록")

    display_df = df.drop(columns=["초"])

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="📥 학습 기록 CSV 다운로드",
        data=csv,
        file_name="study_records.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("🗑️ 전체 기록 삭제"):
        st.session_state.records = []
        st.rerun()

else:
    st.info("아직 저장된 학습 기록이 없습니다.")

st.divider()
st.caption("📚 매일 조금씩 공부하는 습관을 만들어 보세요!")

5. Streamlit Cloud 배포 방법
GitHub에 새 Repository 생성
main.py 업로드
requirements.txt 업로드
https://share.streamlit.io/ 접속
GitHub Repository 선택
Main file path에 main.py 입력
Deploy 클릭
6. 향후 개선 사항
SQLite 데이터베이스 연동
학습 기록 영구 저장
날짜별 학습 통계
과목별 학습 목표 설정
주간 및 월간 학습 그래프
학생별 학습 기록 관리

프로젝트명: 학생용 학습 타이머
개발 환경: Python / Streamlit
배포 환경: Streamlit Community Cloud
필요 파일: main.py, requirements.txt
