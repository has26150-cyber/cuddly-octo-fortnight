import time
from datetime import datetime

import streamlit as st


st.set_page_config(
    page_title="학생 학습 관리",
    page_icon="📚",
    layout="centered",
)

# -----------------------------
# 세션 상태 초기화
# -----------------------------
defaults = {
    "subjects": ["국어", "영어", "수학", "과학", "사회"],
    "selected_subject": "국어",
    "elapsed": 0.0,
    "started_at": None,
    "is_running": False,
    "records": {},
    "history": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def elapsed_now():
    """현재 타이머의 누적 경과 시간(초)을 계산합니다."""
    elapsed = st.session_state.elapsed
    if st.session_state.is_running and st.session_state.started_at is not None:
        elapsed += time.time() - st.session_state.started_at
    return max(0.0, elapsed)


def format_time(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def pause_timer():
    if st.session_state.is_running:
        st.session_state.elapsed = elapsed_now()
        st.session_state.started_at = None
        st.session_state.is_running = False


# -----------------------------
# 사이드바 메뉴
# -----------------------------
st.sidebar.title("📚 공부 관리")
page = st.sidebar.radio(
    "메뉴 선택",
    ["공부 타이머", "오늘 할 일", "공부 회고"],
)

# -----------------------------
# 공부 타이머 페이지
# -----------------------------
if page == "공부 타이머":
    st.title("⏱️ 공부 타이머")
    st.caption("과목을 선택하고 공부 시간을 측정해 보세요.")

    st.subheader("📚 과목")
    subject_col, add_col = st.columns([2, 1])

    with subject_col:
        selected = st.selectbox(
            "공부할 과목",
            st.session_state.subjects,
            index=st.session_state.subjects.index(st.session_state.selected_subject),
            disabled=st.session_state.is_running,
            label_visibility="collapsed",
        )
        st.session_state.selected_subject = selected

    with add_col:
        with st.popover("＋ 과목 추가", use_container_width=True):
            new_subject = st.text_input("과목 이름", key="new_subject_input")
            if st.button("추가하기", use_container_width=True):
                cleaned = new_subject.strip()
                if not cleaned:
                    st.warning("과목 이름을 입력해 주세요.")
                elif cleaned in st.session_state.subjects:
                    st.info("이미 등록된 과목입니다.")
                else:
                    st.session_state.subjects.append(cleaned)
                    st.session_state.selected_subject = cleaned
                    st.rerun()

    st.divider()
    st.subheader("⏱️ 학습 타이머")

    @st.fragment(run_every="1s")
    def timer_panel():
        current = elapsed_now()
        status = "공부 중" if st.session_state.is_running else "일시정지"
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #172554, #1e40af);
                border-radius: 18px;
                padding: 30px 16px;
                text-align: center;
                color: white;
                margin: 8px 0 18px 0;
            ">
                <div style="font-size: 14px; opacity: .85;">
                    {st.session_state.selected_subject}
                </div>
                <div style="font-size: clamp(42px, 9vw, 64px);
                            font-weight: 700;
                            font-variant-numeric: tabular-nums;
                            letter-spacing: 2px;">
                    {format_time(current)}
                </div>
                <div style="font-size: 13px; opacity: .8;">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        start_col, pause_col, reset_col = st.columns(3)

        with start_col:
            if st.button(
                "▶ 시작",
                use_container_width=True,
                type="primary",
                disabled=st.session_state.is_running,
            ):
                st.session_state.started_at = time.time()
                st.session_state.is_running = True
                st.rerun()

        with pause_col:
            if st.button(
                "⏸ 일시정지",
                use_container_width=True,
                disabled=not st.session_state.is_running,
            ):
                pause_timer()
                st.rerun()

        with reset_col:
            if st.button("↺ 초기화", use_container_width=True):
                st.session_state.elapsed = 0.0
                st.session_state.started_at = (
                    time.time() if st.session_state.is_running else None
                )
                st.rerun()

        st.caption("과목 변경은 타이머를 일시정지한 뒤 할 수 있습니다.")

    timer_panel()

    st.divider()
    st.subheader("📝 학습 기록 저장")
    st.write(f"현재 선택 과목: **{st.session_state.selected_subject}**")
    st.write(f"저장할 시간: **{format_time(elapsed_now())}**")

    save_col, clear_col = st.columns([2, 1])

    with save_col:
        if st.button("기록 저장", use_container_width=True, type="primary"):
            pause_timer()
            seconds = st.session_state.elapsed

            if seconds <= 0:
                st.warning("저장할 학습 시간이 없습니다. 타이머를 먼저 시작해 주세요.")
            else:
                subject = st.session_state.selected_subject
                st.session_state.records[subject] = (
                    st.session_state.records.get(subject, 0.0) + seconds
                )
                st.session_state.history.append(
                    {
                        "과목": subject,
                        "학습 시간": format_time(seconds),
                        "저장 일시": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
                st.session_state.elapsed = 0.0
                st.session_state.started_at = None
                st.session_state.is_running = False
                st.success(f"{subject} 학습 기록을 저장했습니다.")
                st.rerun()

    with clear_col:
        if st.button("기록 전체 삭제", use_container_width=True):
            st.session_state.records = {}
            st.session_state.history = []
            st.success("과목별 누적 기록을 삭제했습니다.")
            st.rerun()

    st.divider()
    st.subheader("📊 과목별 누적 학습 시간")

    if st.session_state.records:
        total_seconds = sum(st.session_state.records.values())
        st.metric("전체 학습 시간", format_time(total_seconds))

        for subject, seconds in sorted(
            st.session_state.records.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            st.write(f"**{subject}** — {format_time(seconds)}")
            st.progress(seconds / total_seconds if total_seconds else 0.0)
    else:
        st.info("아직 저장된 학습 기록이 없습니다.")

    if st.session_state.history:
        with st.expander("저장한 기록 자세히 보기"):
            st.dataframe(
                list(reversed(st.session_state.history)),
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        "※ 기록은 현재 브라우저 세션에 저장됩니다. "
        "페이지를 새로 시작하거나 세션이 종료되면 사라질 수 있습니다."
    )

# -----------------------------
# 오늘 할 일 페이지
# -----------------------------
elif page == "오늘 할 일":
    st.title("📝 오늘 할 일")

# -----------------------------
# 공부 회고 페이지
# -----------------------------
elif page == "공부 회고":
    st.title("📖 공부 회고")
