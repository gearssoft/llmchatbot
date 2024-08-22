import os

from langchain_openai.chat_models import ChatOpenAI

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough,RunnableLambda

import streamlit as st

# .env 파일 로드 및 환경 변수 설정
from dotenv import load_dotenv
load_dotenv()

def log_chain(x):
    print("log : ", x) # 이전 단계에서 넘어온 데이터를 확인할 수 있다.
    st.write(x)
    return x

rbLogChain = RunnableLambda(log_chain)

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

st.set_page_config(
    page_title="instruction Chat",
    page_icon="📃",
)

# _inst.txt 파일 로드
with open('instruction.txt', 'r') as f:
    _instruction = f.read()

    with st.sidebar:
        instruction = st.text_area("Instructions",
        _instruction, height=200)
        
        if st.button("Save"):
            with open('temp_inst.txt', 'w') as f:
                f.write(instruction)
            st.write("Saved")

llm = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'), 
    # max_new_tokens=32, 
    temperature=0.1,
    timeout=10
    )

def create_chain(instruction):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
다음 "명령"에 따라 답변하세요.
"명령" : {instruction}\n\n
=====================================
""",
            ),
            ("human", "질문 : {question}"),
        ]
    )
    

    chain = (
        {
            
            "question": RunnablePassthrough(),
        }
        | prompt | rbLogChain
        | llm
    )
    
    return chain

question = st.chat_input("ask anything...")

if question :
    st.write(f"instruction : {instruction}")
    st.write(f"you : {question}")
    
    chain = create_chain(instruction)
    
    _answer = chain.invoke(question)
    st.write(_answer.content)
    
