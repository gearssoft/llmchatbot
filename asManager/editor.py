import os

from langchain_openai.chat_models import ChatOpenAI

from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough,RunnableLambda
from langchain.memory import ConversationSummaryBufferMemory

import streamlit as st

# .env 파일 로드 및 환경 변수 설정
from dotenv import load_dotenv
load_dotenv()


def log_chain(x):
    print("log : ", x) # 이전 단계에서 넘어온 데이터를 확인할 수 있다.
    st.write(x)
    return x

rbLogChain = RunnableLambda(log_chain)


st.set_page_config(
    page_title="instruction Chat",
    page_icon="📃",
)

instruction__file_path = './temp/inst.txt'
#/temp/inst.txt d이없으면 만들기
if not os.path.exists(instruction__file_path):
    with open(instruction__file_path, 'w') as f:
        f.write("당신은 AS 접수관리자입니다. 고객의 문의에 대한 답변을 하세요.")

# _inst.txt 파일 로드
with open(instruction__file_path, 'r') as f:
    _instruction = f.read()

    with st.sidebar:
        instruction = st.text_area("Instructions",
        _instruction, height=200)
        
        if st.button("Save"):
            with open(instruction__file_path, 'w') as f:
                f.write(instruction)
            st.write("Saved")

llm = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'), 
    # max_new_tokens=32, 
    temperature=0.1,
    timeout=10
    )

if 'memory' not in st.session_state:
        st.session_state.memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=120,
            return_messages=True,
        )
def load_memory(args):
    
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    
    return {
        'question': args['question'], 
        'history': history
    }

        
def create_chain(instruction):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
다음 "명령"에 따라 답변하세요.
"명령" : {instruction}\n\n
=====================================\n
이전 대화 내용을 참고하여 답변하세요.
{st.session_state.memory.load_memory_variables({}).get("history", [])}\n\n
=====================================\n
""",
            ),
            # MessagesPlaceholder(variable_name="history"),
            ("human", "질문 : {question}"),
        ]
    )
    

    chain = (
        RunnableLambda(load_memory)        
        | prompt | rbLogChain
        | llm
    )
    
    return chain

question = st.chat_input("ask anything...")

def _update_chat_history_text():
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    with st.sidebar:
        st.write(history)

if question :
    st.write(f"instruction : {instruction}")
    st.write(f"you : {question}")
    
    chain = create_chain(instruction)
    
    _answer = chain.invoke({"question": question})
    st.write(_answer.content)
    
    with st.spinner("대화 내용 요약중..."):
        st.session_state.memory.save_context(
            {"input": question},
            {"output": _answer.content},
        )
        _update_chat_history_text()
    
    
    
