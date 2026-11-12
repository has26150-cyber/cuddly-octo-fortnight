
elif page == "오늘 할 일":
    st.title("📝 오늘 할 일")
    st.caption("오늘 공부할 과목과 할 일을 기록해 보세요.")

    # 할 일 목록 초기화
    if "todo_list" not in st.session_state:
        st.session_state.todo_list = []

    st.subheader("할 일 추가")

    # 과목 입력
    subject = st.text_input(
        "과목",
        placeholder="예: 수학"
    )

    # 할 일 입력
    task = st.text_input(
        "할 일",
        placeholder="예: 교과서 20~30쪽 풀기"
    )

    # 추가 버튼
    if st.button("➕ 추가하기", use_container_width=True):
        if subject.strip() == "" or task.strip() == "":
            st.warning("과목과 할 일을 모두 입력해 주세요.")
        else:
            st.session_state.todo_list.append({
                "과목": subject.strip(),
                "할 일": task.strip(),
                "완료": False
            })
            st.success("할 일이 추가되었습니다!")
            st.rerun()

    st.divider()

    st.subheader("📋 오늘의 할 일 목록")

    if st.session_state.todo_list:

        for i, item in enumerate(st.session_state.todo_list):
            col1, col2 = st.columns([5, 1])

            with col1:
                done = st.checkbox(
                    f"**[{item['과목']}]** {item['할 일']}",
                    value=item["완료"],
                    key=f"todo_check_{i}"
                )
                st.session_state.todo_list[i]["완료"] = done

            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.todo_list.pop(i)
                    st.rerun()

        # 완료 현황
        total = len(st.session_state.todo_list)
        completed = sum(
            1 for item in st.session_state.todo_list
            if item["완료"]
        )

        st.divider()
        st.subheader("📊 오늘의 달성 현황")
        st.metric("완료한 할 일", f"{completed} / {total}")

        st.progress(completed / total)

    else:
        st.info("아직 등록된 할 일이 없습니다.")
