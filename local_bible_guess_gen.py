from llm import gpt4o, claude35Sonnet200k
from supabase_client import supabase
from asyncio import run
import json
import time

import requests
import re

import streamlit as st


def find_match(text):
    # Use a regular expression to extract JSON content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    json_content = ""
    if match:
        json_content = match.group(0)
        #print("=====")
        #print(json_content)
    return json_content

async def gen():

    url = "https://beta.ourmanna.com/api/v1/get?format=json&order=random"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    print(response.text)

    query_to_llm = f'```{response.text}``` \n\n해당 json을 한글로 보여줘 (value 값만 한글로 변경), details.text 는 KRV 성경으로 가져와줘.'
    print(f"query_to_llm : {query_to_llm}")

    response = await gpt4o(query_to_llm)
    from_llm = response.get("message", "Error")
    json_data = ""

    # Check if the response is not an error
    # Check if the response is not an error
    if from_llm != "Error":
        json_string = find_match(from_llm)
        try:
            json_data = json.loads(json_string)
        except json.JSONDecodeError:
            print("Failed to parse JSON.")
            return
    else:
        return

    print("=====")
    print(json_data)
    print("=====")

    if json_data:
        if json_data['verse']['details']:
            details = json_data['verse']['details']
            
            # Extract details
            text = details.get('text', '')
            reference = details.get('reference', '')
            version = details.get('version', '')
            verseurl = details.get('verseurl', '')
            
            # Extract notice
            notice = json_data['verse'].get('notice', '')
            
            # Use the extracted information
            print(f"Text: {text}")
            print(f"Reference: {reference}")
            print(f"Version: {version}")
            print(f"Verse URL: {verseurl}")
            #print(f"Notice: {notice}")

            result_rpc = supabase.rpc('insert_quiz', {
                        'p_question': str(text),
                        'p_difficulty': 3,
                        'p_options': [],
                        'p_answer': str(reference),
                        'p_type': str('bible_verse'),
                        'p_reference': str(reference)
                    }).execute()
            print("result_rpc ====> " + str(result_rpc.data))


st.header("BQ gen")
st.subheader("1. get a random verse and gen")

count = st.text_input("개수", value="0", max_chars=2)
button1_clicked = st.button(f"{count}개의 퀴즈 만들기")
if button1_clicked:
    progress_text = st.empty()
    progress_bar = st.progress(0)
    total = int(count)
    for i in range(total):
        progress_text.text(f"{i+1}개 진행중...")
        progress_bar.progress((i + 1) / total)
        time.sleep(1)
        run(gen())
    progress_text.text("완료!")
    progress_bar.empty()