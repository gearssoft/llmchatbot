import os

from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain.embeddings import CacheBackedEmbeddings

from langchain_community.vectorstores import Chroma,FAISS

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough,RunnableLambda
from langchain.schema import HumanMessage
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.document_loaders.csv_loader import CSVLoader

from langchain.storage import LocalFileStore

import streamlit as st

    
base_path = "../srcData/"

if 'check_list' not in st.session_state:
    st.session_state.check_list = []
if 'files' not in st.session_state:
    st.session_state.files = []
if 'needClearUploadedFiles' not in st.session_state:
    st.session_state.needClearUploadedFiles = False

check_list = st.session_state.check_list


def renderFileList() :
    st.session_state.check_list = []
    files = os.listdir(base_path)
    for file in files:
        st.session_state.check_list.append( (st.checkbox(f"{file}"), file))
    

def renderFileListForm() :
    renderFileList()
    
    if(len(check_list) > 0):
        if st.button("Delete"):
            for i in range(len(check_list) - 1, -1, -1):
                check = check_list[i]
                print(f"delete check : {check}")
                # delete check
                if check[0]:
                    os.remove(os.path.join(base_path, check[1]))
                    del check_list[i]
                    
            st.session_state.check_list = []
            
            st.rerun()
            
uploaded_files = None

if st.session_state.needClearUploadedFiles :
    st.session_state.needClearUploadedFiles  = False
    renderFileList()
    st.button("upload ok click to rerun")
    
else :
    uploaded_files = st.file_uploader("Choose a CSV file to upload", accept_multiple_files=True)

if uploaded_files is not None:
    # st.session_state.files = uploaded_files
    total_files = len(uploaded_files)  # 총 파일 수
    
    if total_files > 0:
        my_bar = st.progress(0)  # 진행바 초기화

        for index, uploaded_file in enumerate(uploaded_files):
            file_content = uploaded_file.read()  # 파일 내용 읽기
            file_path = os.path.join(base_path, uploaded_file.name)  # 파일 경로 조합

            # 파일 쓰기
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 진행 상태 업데이트
            percent_complete = (index + 1) / total_files  # 진행률 계산
            my_bar.progress(percent_complete)  # 진행바 업데이트
            # progress_text = f"{percent_complete:.2f}% Complete"  # 진행률 텍스트
            # st.write(progress_text)  # 텍스트 출력
        
        st.session_state.needClearUploadedFiles = True
        st.rerun()
        
        # st.button("upload ok click to rerun")
    else :
        renderFileListForm()
            
            
        