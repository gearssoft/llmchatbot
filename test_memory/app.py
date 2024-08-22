#%%
from langchain.memory import ConversationSummaryBufferMemory

from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import StreamingStdOutCallbackHandler

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.messages.system import SystemMessage

import streamlit as st



import time
import os
from dotenv import load_dotenv
load_dotenv('../.env')

#%%
llm = ChatOpenAI(temperature=0.8)

if 'memory' not in st.session_state:
        st.session_state.memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=120,
            return_messages=True,
        )
        
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 사람들과 도움이되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

def load_memory(args):
    
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    
    return {
        'question': args['question'], 
        'history': history
    }
    
def log_chain(x):
    print("log : ", x) # 이전 단계에서 넘어온 데이터를 확인할 수 있다.
    st.write(x)
    return x

rbLogChain = RunnableLambda(log_chain)
rbLoadMemory = RunnableLambda(load_memory)

#chain = rbLoadMemory | rbLogChain | prompt |  rbLogChain | llm 
chain = rbLoadMemory | prompt | llm

st.title("Test Chatbot proto_model1")

with st.sidebar:
    st.header("Chat History")
    

def _update_chat_history_text():
    history = st.session_state.memory.load_memory_variables({}).get("history", [])
    with st.sidebar:
        st.write(history)

# _update_chat_history_text()
prompt = st.chat_input("Say something")
if prompt:
    with st.spinner("Thinking..."):
        result = chain.invoke({"question": prompt})
        st.write(result.content)
        
    with st.spinner("Summary Conversation History Saving..."):
        st.session_state.memory.save_context(
            {"input": prompt},
            {"output": result.content},
        )
        _update_chat_history_text()
        