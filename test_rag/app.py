import os
import streamlit as st

# from langchain.prompts import ChatPromptTemplate
# # from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
# from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
# from langchain.text_splitter import CharacterTextSplitter

# from langchain_community.llms import OpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import UnstructuredFileLoader,CSVLoader

from langchain_community.vectorstores import Chroma,FAISS
from langchain.embeddings import CacheBackedEmbeddings

# .env 파일 로드 및 환경 변수 설정
from dotenv import load_dotenv
load_dotenv()

embedding_model = OpenAIEmbeddings()

base_path = './.cache/files/'

st.title("Document Example")

if 'all_data' not in st.session_state:
    st.session_state.all_data = []
if 'check_list' not in st.session_state:
    st.session_state.check_list = []

def upload_file():
    st.header("Upload Example")

    # 파일리스트 보여주기 항목은 체크박스 있고 삭제 버튼 있음

    # 폴더가 없으면 생성
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    if 'check_list' not in st.session_state:
        st.session_state.check_list = []
    if 'files' not in st.session_state:
        st.session_state.files = []

    check_list = st.session_state.check_list

    #파일저장 
    if st.button("save file") : 
        for uploaded_file in st.session_state.files:
            file_content = uploaded_file.read()
            file_path = os.path.join(base_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(file_content)
                
        if st.button("Delete"):
            for i in range(len(check_list) - 1, -1, -1):
                check = check_list[i]
                print(check)
                # delete check
                if check[0]:
                    os.remove(os.path.join(base_path, check[1]))
                    del check_list[i]
                    # st.write(f"Delete {check[1]}")
            files = os.listdir(base_path)
            for file in files:
                check_list.append( (st.checkbox(f"{file}"), file))
        else :
            st.session_state.check_list = []
            files = os.listdir(base_path)
            for file in files:
                st.session_state.check_list.append( (st.checkbox(f"{file}"), file))
        
        
    else :
        #업로드 할 파일 준비 
        uploaded_files = st.file_uploader("Choose a CSV file to upload", accept_multiple_files=True)

        if uploaded_files is not None:
            st.session_state.files = uploaded_files
                    
            if st.button("Delete"):
                for i in range(len(check_list) - 1, -1, -1):
                    check = check_list[i]
                    print(check)
                    # delete check
                    if check[0]:
                        os.remove(os.path.join(base_path, check[1]))
                        del check_list[i]
                        # st.write(f"Delete {check[1]}")
                        
                st.session_state.check_list = []
                files = os.listdir(base_path)
                for file in files:
                    st.session_state.check_list.append( (st.checkbox(f"{file}"), file))
            else :
                st.session_state.check_list = []
                files = os.listdir(base_path)
                for file in files:
                    st.session_state.check_list.append( (st.checkbox(f"{file}"), file))

def rag_document():
    st.header("Document Retrieval Example")
    if st.button("load document"):
        
        check_list = st.session_state.check_list
        all_data = []
        
        with st.spinner("reading file..."):
            for i in range(len(check_list)):
                check = check_list[i]
                if check[0]:
                    st.write(f"Retrieve {check[1]}")
                    file_path = os.path.join(base_path, check[1])
                    # 파일 내용을 읽습니다
                    try:
                        # file_content = loader.load(file_path)
                        loader = CSVLoader(file_path=file_path)
                        file_content = loader.load()
                        all_data.extend(file_content)
                        st.write(f"path : {file_path} , size : {len(file_content)}")
                        # st.write(file_content)
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
            st.session_state.all_data = all_data
            
    if st.button("embedding loaded document"):
        all_data = st.session_state.all_data
        
        if len(all_data) == 0:
            st.error("No data to embed")
            return
        
        with st.spinner("embedding document..."):
            cache_dir = LocalFileStore("./.cache/")
            cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embedding_model, cache_dir)
            vectorstore = FAISS.from_documents(all_data, cached_embeddings)
            st.session_state.vectorstore = vectorstore
            # st.write(vectorstore)
            st.write(f"document size : {vectorstore.index.ntotal}")
    
    if st.button("save vectorstore"):
        vectorstore = st.session_state.vectorstore
        vectorstore.save_local("./.db/vectorstore.db")
        
    if st.button("load vectorstore"):
        vectorstore = FAISS.load_local("./.db/vectorstore.db",embedding_model)
        st.session_state.vectorstore = vectorstore
        st.write(f"document size : {vectorstore.index.ntotal}")
        
# main routine
with st.sidebar:
    upload_file()

rag_document()
