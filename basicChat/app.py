# 필요한 라이브러리 임포트
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI  # 최신 패키지에서 ChatOpenAI 임포트
from langchain.schema import SystemMessage
from langchain.schema.runnable import RunnablePassthrough

import streamlit as st
import os
from dotenv import load_dotenv

import tiktoken

# .env 파일 로드
load_dotenv('.env')

print(f"model name : {os.getenv('OPENAI_MODEL_NAME')}")

# 토큰 수 계산 함수 정의
def count_tokens(text, model_name=os.getenv('OPENAI_MODEL_NAME') ):
    tokenizer = tiktoken.encoding_for_model(model_name)
    tokens = tokenizer.encode(text)
    return len(tokens)

# ChatOpenAI 초기화
llm = ChatOpenAI(temperature=0.8)



# 세션 상태에 memory가 없으면 초기화
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1024,
        return_messages=True,
    )

# load_memory 함수 정의
def load_memory(args):
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    return {
        'question': args['question'],
        'history': history
    }

# log_chain 함수 정의
def log_chain(x):
    print("log : ", x)  # 로그 데이터 출력
    
    if isinstance(x, dict) and 'question' in x:
        question_tokens = count_tokens(x['question'])
        print(f"Question token count: {question_tokens}")
    # History의 각 메시지의 토큰 수 계산
    if 'history' in x:
        for i, message in enumerate(x['history']):
            # 메시지에서 실제 내용을 추출
            content = message.content
            message_tokens = count_tokens(content)
            print(f"History message {i} token count: {message_tokens}")
    
    st.write(x)
    return x

# RunnablePassthrough 사용
rbLogChain = RunnablePassthrough(log_chain)
rbLoadMemory = RunnablePassthrough(load_memory)

# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="당신은 사람들과 도움이 되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

# 체인 정의
chain = rbLoadMemory | log_chain | prompt | llm 

# Streamlit 앱 제목
st.title("Chatbot App Basic Sample")

# 사이드바에 채팅 기록 표시
with st.sidebar:
    st.header("Chat History")

# 사이드바에 채팅 기록 텍스트 업데이트 함수
def _update_chat_history_text():
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    with st.sidebar:
        st.write(history)
        
# 사용자 입력 프롬프트
chatMsg = st.chat_input("Say something")
if chatMsg:
    with st.spinner("Thinking..."):
        input_data = load_memory({'question': chatMsg})
        result = chain.invoke(input_data)
        st.write(result.content)

    with st.spinner("Summary Conversation History Saving..."):
        st.session_state.memory.save_context(
            {"input": chatMsg},
            {"output": result.content},
        )
        _update_chat_history_text()
