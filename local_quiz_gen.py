from llm import gpt4o, claude35Sonnet200k
from supabase_client import supabase
from asyncio import run
import json
import time

import streamlit as st


async def gen(book_name="창세기", how_many=10, progress_text=None, progress_bar=None):
    header_query= f"Generate {how_many} of Bible quiz questions for book name: {book_name} in Korean. "
    query_to_llm = header_query + 'Include question, options, answer, and reference(where the quiz from). Provide a certain format in JSON : "{ "data": [{ "question":"", "difficulty": (number 1-10), options: [...], answer: "", reference: "", type: "bible"]} Do not put any other message besides the JSON format. (even without ```json or ```)'
    print(f"query_to_llm : {query_to_llm}")

    response = await gpt4o(query_to_llm)
    from_llm = response.get("message", "Error")
    print("=====")
    print(from_llm)
    if(from_llm == "Error"):
        st.text_area("오류 발생!", value=from_llm)
        return

    json_data= json.loads(from_llm)
    print("=====")
    print(json_data)
    print("=====")

    for index, quiz in enumerate(json_data['data']):
        print(f"{index}: {quiz}")
        time.sleep(1)
        progress_text.text(f"{index+1}개 진행중...")
        progress_bar.progress((index + 1) / how_many)

        result_rpc = supabase.rpc('insert_quiz', {
                        'p_question': str(quiz['question']),
                        'p_difficulty': quiz['difficulty'],
                        'p_options': quiz['options'],
                        'p_answer': str(quiz['answer']),
                        'p_type': str(quiz['type']),
                        'p_reference': str(quiz['reference'])
                    }).execute()
        print("result_rpc ====> " + str(result_rpc.data))
        st.text_area("생성된 퀴즈", value=str(result_rpc.data) + "\n\n" + str(quiz), height=110)



st.header("BQ gen")
st.subheader("현재 퀴즈DB 조회")
button2_clicked = st.button("DB 조회")
if button2_clicked:
    result = supabase.table('quiz').select('id,question,options,answer,reference,type,difficulty').execute()
    st.dataframe(result.data, selection_mode="single-row")

button3_redundant_clicked = st.button("중복의심되는 퀴즈 찾기")
if button3_redundant_clicked:
    with st.spinner("중복 퀴즈를 검색중입니다..."):
        result = supabase.table('quiz').select('id,question,options').execute()
        query_to_llm = f'{result} \n\n 여기에서 유사한 제목의 퀴즈를 찾고, id를 set로 출력해줘. 예시: 중복의심제목: [13,194,222...], 중복의심제목: [3,4...]'
        print(f"query_to_llm : {query_to_llm}")

        async def check_redundant():
            from_llm = await claude35Sonnet200k(query_to_llm)
            print("=====")
            print(from_llm)
            st.text_area("중복검출된 퀴즈들", value=from_llm, height=350)

        run(check_redundant())

st.subheader("퀴즈 생성하고 자동업로드")

book_name = st.text_input("Book name", placeholder="예: Genesis, Exodus, Leviticus, Numbers, Deuteronomy")
count = st.text_input("개수", value="2", max_chars=2)
button1_clicked = st.button(f"{count}개의 퀴즈 만들기")
if button1_clicked:
    progress_text = st.empty()
    progress_bar = st.progress(0)
    #total = int(count)
    #for i in range(total):
    
    time.sleep(1)
    run(gen(book_name, int(count), progress_text, progress_bar))

    progress_text.text("완료!")
    progress_bar.empty()
