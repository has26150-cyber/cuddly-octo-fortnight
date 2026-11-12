import time
import uuid
from datetime import date, datetime

import streamlit as st

st.set_page_config(page_title="학생 공부 관리", page_icon="📚", layout="centered")

# 세션 데이터 초기화
DEFAULTS = {
    "subjects": ["국어", "영어", "수학", "과학", "사회"],
    "selected_subject": "국어",
    "elapsed": 0.0,
    "started_at": None,
    "is_running": False,
    "records": {},
    "history": [],
    "todo_list": [],
    "reflections": [],
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def elapsed_now():
    value = st.session_state.elapsed
    if st.session_state.is_running and st.session_state.started_at is not None:
        value += time.time() - st.session_state.started_at
    return max(0.0, value)


def format_time(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def pause_timer():
    if st.session_state.is_running:
        st.session_state.elapsed = elapsed_now()
        st.session_state.started_at = None
        st.session_state.is_running = False


st.sidebar.title("📚 공부 관리")
page = st.sidebar.radio("메뉴 선택", ["공부 타이머", "오늘 할 일", "공부 회고"])

# 1. 공부 타이머
if page == "공부 타이머":
    st.title("⏱️ 공부 타이머")
    st.caption("과목을 선택하고 공부 시간을 측정해 보세요.")

    col_subject, col_add = st.columns([2, 1])
    with col_subject:
        st.session_state.selected_subject = st.selectbox(
            "공부할 과목",
            st.session_state.subjects,
            index=st.session_state.subjects.index(st.session_state.selected_subject),
            disabled=st.session_state.is_running,
        )
    with col_add:
        with st.popover("＋ 과목 추가", use_container_width=True):
            new_subject = st.text_input("새 과목 이름", key="new_subject")
            if st.button("과목 등록", use_container_width=True):
                name = new_subject.strip()
                if not name:
                    st.warning("과목 이름을 입력해 주세요.")
                elif name in st.session_state.subjects:
                    st.info("이미 등록된 과목입니다.")
                else:
                    st.session_state.subjects.append(name)
                    st.session_state.selected_subject = name
                    st.rerun()

    st.divider()
    st.subheader("학습 타이머")

    @st.fragment(run_every="1s")
    def timer_panel():
        current = elapsed_now()
        status = "공부 중" if st.session_state.is_running else "일시정지"
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#172554,#1d4ed8);
            color:white;padding:28px 12px;border-radius:18px;text-align:center;">
              <div style="font-size:15px;">{st.session_state.selected_subject}</div>
              <div style="font-size:clamp(42px,9vw,64px);font-weight:700;
              font-variant-numeric:tabular-nums;">{format_time(current)}</div>
              <div style="font-size:13px;">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        a, b, c = st.columns(3)
        with a:
            if st.button("▶ 시작", type="primary", use_container_width=True,
                         disabled=st.session_state.is_running):
                st.session_state.started_at = time.time()
                st.session_state.is_running = True
                st.rerun()
        with b:
            if st.button("⏸ 일시정지", use_container_width=True,
                         disabled=not st.session_state.is_running):
                pause_timer()
                st.rerun()
        with c:
            if st.button("↺ 초기화", use_container_width=True):
                st.session_state.elapsed = 0.0
                st.session_state.started_at = time.time() if st.session_state.is_running else None
                st.rerun()

    timer_panel()
    st.caption("과목을 바꾸려면 타이머를 먼저 일시정지하세요.")

    st.divider()
    st.subheader("학습 기록 저장")
    st.write(f"선택 과목: **{st.session_state.selected_subject}**")
    st.write(f"현재 시간: **{format_time(elapsed_now())}**")
    save_col, clear_col = st.columns([2, 1])
    with save_col:
        if st.button("기록 저장", type="primary", use_container_width=True):
            pause_timer()
            seconds = st.session_state.elapsed
            if seconds <= 0:
                st.warning("저장할 시간이 없습니다. 타이머를 먼저 시작해 주세요.")
            else:
                subject = st.session_state.selected_subject
                st.session_state.records[subject] = st.session_state.records.get(subject, 0) + seconds
                st.session_state.history.append({
                    "과목": subject,
                    "학습 시간": format_time(seconds),
                    "저장 일시": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.session_state.elapsed = 0.0
                st.session_state.started_at = None
                st.session_state.is_running = False
                st.success("학습 기록을 저장했습니다.")
                st.rerun()
    with clear_col:
        if st.button("기록 전체 삭제", use_container_width=True):
            st.session_state.records = {}
            st.session_state.history = []
            st.rerun()

    st.divider()
    st.subheader("과목별 누적 학습 시간")
    if st.session_state.records:
        total = sum(st.session_state.records.values())
        st.metric("전체 학습 시간", format_time(total))
        for subject, seconds in sorted(st.session_state.records.items(),
                                       key=lambda pair: pair[1], reverse=True):
            st.write(f"**{subject}** — {format_time(seconds)}")
            st.progress(seconds / total if total else 0.0)
    else:
        st.info("아직 저장된 학습 기록이 없습니다.")
    if st.session_state.history:
        with st.expander("저장 기록 자세히 보기"):
            st.dataframe(list(reversed(st.session_state.history)),
                         use_container_width=True, hide_index=True)

# 2. 오늘 할 일
elif page == "오늘 할 일":
    st.title("📝 오늘 할 일")
    st.caption("오늘 공부할 과목과 할 일을 기록해 보세요.")
    subject = st.text_input("과목", placeholder="예: 수학", key="todo_subject")
    task = st.text_input("할 일", placeholder="예: 교과서 20~30쪽 풀기", key="todo_task")

    if st.button("➕ 추가하기", use_container_width=True):
        if not subject.strip() or not task.strip():
            st.warning("과목과 할 일을 모두 입력해 주세요.")
        else:
            st.session_state.todo_list.append({
                "id": str(uuid.uuid4()), "subject": subject.strip(),
                "task": task.strip(), "done": False,
            })
            st.success("할 일이 추가되었습니다.")
            st.rerun()

    st.divider()
    st.subheader("📋 오늘의 할 일 목록")
    if st.session_state.todo_list:
        for item in st.session_state.todo_list:
            left, right = st.columns([5, 1])
            with left:
                item["done"] = st.checkbox(
                    f"**[{item['subject']}]** {item['task']}",
                    value=item["done"], key=f"todo_check_{item['id']}"
                )
            with right:
                if st.button("🗑️", key=f"todo_delete_{item['id']}"):
                    st.session_state.todo_list = [
                        x for x in st.session_state.todo_list if x["id"] != item["id"]
                    ]
                    st.rerun()
        total = len(st.session_state.todo_list)
        done = sum(1 for item in st.session_state.todo_list if item["done"])
        st.divider()
        st.metric("완료한 할 일", f"{done} / {total}")
        st.progress(done / total)
    else:
        st.info("아직 등록된 할 일이 없습니다.")

# 3. 공부 회고
elif page == "공부 회고":
    st.title("📖 공부 회고")
    st.caption("오늘의 공부를 돌아보고 내일의 목표를 세워 보세요.")

    reflection_date = st.date_input("회고 날짜", value=date.today())
    st.divider()
    learned = st.text_area("1. 오늘 배운 내용",
                           placeholder="오늘 공부한 내용이나 새롭게 알게 된 점을 적어 보세요.",
                           height=100)
    good = st.text_area("2. 오늘 잘한 점",
                        placeholder="오늘 스스로 칭찬하고 싶은 점은 무엇인가요?",
                        height=90)
    difficult = st.text_area("3. 아쉬웠던 점",
                             placeholder="어려웠던 점이나 개선하고 싶은 점을 적어 보세요.",
                             height=90)
    satisfaction = st.slider("4. 오늘의 공부 만족도", 1, 5, 3)
    st.write("⭐" * satisfaction + "☆" * (5 - satisfaction))
    tomorrow = st.text_area("5. 내일의 목표",
                            placeholder="내일 꼭 끝내고 싶은 공부 목표를 적어 보세요.",
                            height=90)

    if st.button("💾 회고 저장하기", type="primary", use_container_width=True):
        if not any([learned.strip(), good.strip(), difficult.strip(), tomorrow.strip()]):
            st.warning("회고 내용을 한 가지 이상 작성해 주세요.")
        else:
            st.session_state.reflections.append({
                "id": str(uuid.uuid4()),
                "date": reflection_date.strftime("%Y-%m-%d"),
                "learned": learned.strip(),
                "good": good.strip(),
                "difficult": difficult.strip(),
                "satisfaction": satisfaction,
                "tomorrow": tomorrow.strip(),
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.success("공부 회고가 저장되었습니다.")
            st.rerun()

    st.divider()
    st.subheader("📚 이전 공부 회고")
    if st.session_state.reflections:
        previous = sorted(st.session_state.reflections,
                          key=lambda x: (x["date"], x["saved_at"]), reverse=True)
        for item in previous:
            with st.expander(f"{item['date']} · {'⭐' * item['satisfaction']}"):
                st.markdown("**오늘 배운 내용**")
                st.write(item["learned"] or "작성하지 않음")
                st.markdown("**오늘 잘한 점**")
                st.write(item["good"] or "작성하지 않음")
                st.markdown("**아쉬웠던 점**")
                st.write(item["difficult"] or "작성하지 않음")
                st.markdown("**내일의 목표**")
                st.write(item["tomorrow"] or "작성하지 않음")
                st.caption(f"저장 일시: {item['saved_at']}")
                if st.button("이 회고 삭제", key=f"reflection_delete_{item['id']}"):
                    st.session_state.reflections = [
                        x for x in st.session_state.reflections if x["id"] != item["id"]
                    ]
                    st.rerun()
    else:
        st.info("저장된 공부 회고가 없습니다. 첫 회고를 작성해 보세요.")

st.sidebar.caption("※ 현재 데이터는 세션에 저장되며 세션 종료 시 사라질 수 있습니다.")
