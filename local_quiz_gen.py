from llm import gpt4o, claude35Sonnet200k
from supabase_client import supabase
from asyncio import run
import json
import time
from PIL import Image
import io

import streamlit as st



# gen quiz related to paintings Bible books
async def gen_paintings(painting_name="unknown", how_many=10, progress_text=None, progress_bar=None):
    header_query= f"Generate {how_many} of quiz questions for a painting. The name of the painting is {painting_name}"
    query_to_llm = header_query + 'Include question, options, answer, and reference(what year the painting related of). Provide a certain format in JSON : "{ "data": [{ "question":"", "difficulty": (number 1-10), options: [...], answer: "", reference: "", type: "painting"]} Do not put any other message besides the JSON format. (even without ```json or ```)'
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

        result_rpc = supabase.rpc('insert_quiz_painting', {
                        'p_question': str(quiz['question']),
                        'p_difficulty': quiz['difficulty'],
                        'p_options': quiz['options'],
                        'p_answer': str(quiz['answer']),
                        'p_type': str(quiz['type']),
                        'p_reference': str(quiz['reference'])
                    }).execute()
        print("result_rpc ====> " + str(result_rpc.data))
        st.text_area("생성된 퀴즈", value=str(result_rpc.data) + "\n\n" + str(quiz), height=110)


# gen quiz only related to classic Bible books
async def gen_bq(book_name="창세기", how_many=10, progress_text=None, progress_bar=None):
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


st.set_page_config(
    page_title="AI연동 퀴즈DB 관리 프로그램",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://tangibleidea.net',
        'Report a bug': "mailto:mark.choi@tangibleidea.net",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.header("AI 명화퀴즈 생성기.")

tab1, tab2, tab3, tab4 = st.tabs(["1.DB 관리", "2.퀴즈 생성", "3.이미지 업로드", "4.만든 퀴즈 풀어보기"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        button2_clicked = st.button("DB 조회")
    with col2:
        button3_redundant_clicked = st.button("중복의심되는 퀴즈 찾기")

        target_deletion= st.text_input("삭제할 DB id array:", placeholder="[12,36].. 와 같이 적어주세요")
        execute_deletion_clicked = st.button("퀴즈 DB에서 삭제하기")

    if button2_clicked:
        result = supabase.table('quiz_painting').select('id,question,options,answer,reference,type,difficulty').execute()
        st.dataframe(result.data, selection_mode="single-row")

    if execute_deletion_clicked:
        target_deletion= target_deletion.replace("[", "{")
        target_deletion= target_deletion.replace("]", "}")
        result_rpc = supabase.rpc('delete_quizzes_by_ids', {
                        'id_array': target_deletion
                    }).execute()
        print("result_rpc ====> " + str(result_rpc.data))
        st.text_area("삭제된 퀴즈", value=str(result_rpc.data))


    if button3_redundant_clicked:
        with st.spinner("중복 퀴즈를 검색중입니다..."):
            result = supabase.table('quiz_painting').select('id,question,options').execute()
            query_to_llm = str(result) + '\n\n 여기에서 유사한 제목의 퀴즈를 찾고, id를 set로 출력해줘. 예시: 중복의심제목: [13,194,222...], 중복의심제목: [3,4...]'
            print(f"query_to_llm : {query_to_llm}")

            async def check_redundant():
                from_llm = await claude35Sonnet200k(query_to_llm)
                
                print("=====")
                print(from_llm)

                st.text_area("중복검출된 퀴즈들", value=from_llm, height=350)

            run(check_redundant())

with tab2:
    #book_name = st.text_input("Book name", placeholder="예: Genesis, Exodus, 창세기, 출애굽기 등...")
    painting_name = st.text_input("명화 이름/설명", placeholder="예: 레오나르도 다빈치의 최후의 만찬, 카라바조의 도마뱀에 물린 소년 등...")
    count = st.text_input("개수", value="2", max_chars=2)
    button1_clicked = st.button(f"{count}개의 퀴즈 만들기")
    if button1_clicked:
        progress_text = st.empty()
        progress_bar = st.progress(0)

        progress_text.text("퀴즈를 생성중입니다...")
        progress_bar.progress(50)

        run(gen_paintings(book_name, painting_name, int(count), progress_text, progress_bar))

        progress_text.text("완료!")
        progress_bar.empty()

with tab3:
    bible_chapters = {
        "창세기": "Genesis", "출애굽기": "Exodus", "레위기": "Leviticus", "민수기": "Numbers", "신명기": "Deuteronomy",
        "여호수아": "Joshua", "사사기": "Judges", "룻기": "Ruth", "사무엘상": "1_Samuel", "사무엘하": "2_Samuel",
        "열왕기상": "1_Kings", "열왕기하": "2_Kings", "역대상": "1_Chronicles", "역대하": "2_Chronicles", "에스라": "Ezra",
        "느헤미야": "Nehemiah", "에스더": "Esther", "욥기": "Job", "시편": "Psalms", "잠언": "Proverbs",
        "전도서": "Ecclesiastes", "아가": "Song_of_Solomon", "이사야": "Isaiah", "예레미야": "Jeremiah", "예레미야애가": "Lamentations",
        "에스겔": "Ezekiel", "다니엘": "Daniel", "호세아": "Hosea", "요엘": "Joel", "아모스": "Amos",
        "오바댜": "Obadiah", "요나": "Jonah", "미가": "Micah", "나훔": "Nahum", "하박국": "Habakkuk",
        "스바냐": "Zephaniah", "학개": "Haggai", "스가랴": "Zechariah", "말라기": "Malachi",
        "마태복음": "Matthew", "마가복음": "Mark", "누가복음": "Luke", "요한복음": "John",
        "사도행전": "Acts", "로마서": "Romans", "고린도전서": "1_Corinthians", "고린도후서": "2_Corinthians",
        "갈라디아서": "Galatians", "에베소서": "Ephesians", "빌립보서": "Philippians", "골로새서": "Colossians",
        "데살로니가전서": "1_Thessalonians", "데살로니가후서": "2_Thessalonians", "디모데전서": "1_Timothy", "디모데후서": "2_Timothy",
        "디도서": "Titus", "빌레몬서": "Philemon", "히브리서": "Hebrews", "야고보서": "James",
        "베드로전서": "1_Peter", "베드로후서": "2_Peter", "요한일서": "1_John", "요한이서": "2_John",
        "요한삼서": "3_John", "유다서": "Jude", "요한계시록": "Revelation"
    }
    
    col1, col2 = st.columns(2)
    with col1:
        selected_korean_chapter = st.selectbox("성경 책을 선택하세요", list(bible_chapters.keys()))
        selected_english_chapter = bible_chapters[selected_korean_chapter]
    with col2:
        chapter_number = st.number_input("장 번호", min_value=1, value=1, step=1)
    
    uploaded_file = st.file_uploader("이미지 파일을 선택하세요", type=['jpg'])
    if uploaded_file is not None:
        with st.spinner("이미지를 업로드 중입니다..."):
            # Open the uploaded image
            image = Image.open(uploaded_file)
            
            # Resize or compress the image to be under 2MB
            max_size = (1024, 1024)  # Example max size, adjust as needed
            image.thumbnail(max_size)
            
            # Save the image to a bytes buffer
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)  # Adjust quality for compression
            img_byte_arr.seek(0)
            file_bytes = img_byte_arr.read()
            
            # Display the resized image
            st.image(image, caption="업로드된 이미지 (압축됨)")
            
            # Create filename with English chapter name and verse
            file_extension = uploaded_file.name.split('.')[-1].lower()
            filename = f"{selected_english_chapter}_{chapter_number}.{file_extension}"
            
            try:
                # Upload to Supabase storage with overwrite
                res = supabase.storage.from_('bq').upload(
                    path=filename,
                    file=file_bytes,
                    file_options={
                        "content-type": "image/jpeg",
                        "upsert": "true"
                    }
                )
                
                # Get the public URL
                public_url = supabase.storage.from_('bq').get_public_url(filename)
                st.success(f"이미지가 성공적으로 업로드되었습니다!")
                st.code(public_url, language="text")
                
            except Exception as e:
                st.error(f"업로드 중 오류가 발생했습니다: {str(e)}")

with tab4:
    book_name = st.text_input("풀어볼 내용", placeholder="예: Genesis 2, Exodus 17")
    button4_clicked = st.button("퀴즈 풀기")
    if button4_clicked:
        st.text("준비중...")