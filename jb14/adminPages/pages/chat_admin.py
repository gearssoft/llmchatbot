#%%

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

import time


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
    page_title="Chat Admin",
    page_icon="📃",
)

st.title("Chat Admin")

# 모델 및 체인 초기화
# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma(persist_directory='./stores/chroma_store', embedding_function=embeddings)

folder_path = os.getenv('DATA_PATH')
chche_path = os.getenv('CACHE_PATH')

def load_vector_store():
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # 모든 데이터를 로드하여 하나의 리스트에 저장
    all_data = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        loader = CSVLoader(file_path=file_path)
        print(f'loading {file_path}')
        st.write(f'loading {file_path}')
        data = loader.load()
        all_data.extend(data)
        
    print( f'document size : {len(all_data)}' )
    st.write( f'vector documents size : {len(all_data)}' )
    
    with st.spinner('vector base training...'):

        embeddings = OpenAIEmbeddings()
        cache_dir = LocalFileStore(chche_path)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
        vectorstore = FAISS.from_documents( 
                                        documents=all_data,
                                        embedding=cached_embeddings)

        # retriever = vectorstore.as_retriever()
        
        # time.sleep(1)
        # st.success('vector base training done')
        
        return vectorstore

    # retriever = vectorstore.as_retriever()

vector_store = load_vector_store()
retriever = vector_store.as_retriever()
    
if st.button("make vector store") :
    
    vector_store = load_vector_store() 
    retriever = vector_store.as_retriever()
    
    
    
    # csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # # 모든 데이터를 로드하여 하나의 리스트에 저장
    # all_data = []
    # for file in csv_files:
    #     file_path = os.path.join(folder_path, file)
    #     loader = CSVLoader(file_path=file_path)
    #     print(f'loading {file_path}')
    #     st.write(f'loading {file_path}')
    #     data = loader.load()
    #     all_data.extend(data)
        
    # print( f'document size : {len(all_data)}' )
    # st.write( f'vector documents size : {len(all_data)}' )
    
    # with st.spinner('vector base training...'):

    #     embeddings = OpenAIEmbeddings()
    #     cache_dir = LocalFileStore(chche_path)
    #     cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    #     vectorstore = FAISS.from_documents( 
    #                                     documents=all_data,
    #                                     embedding=cached_embeddings)

    #     retriever = vectorstore.as_retriever()
        
        # time.sleep(1)
        # st.success('vector base training done')

with st.sidebar:
    instruction = st.text_area("Instructions", 
                """
You are a helpful assistant. 
your job is to answer questions about the geography of Jeollabuk-do.
Answer questions using only the following context. If you don't know the answer just say you don't know, don't make it up
Answer questions using only korean language.
    """
                , height=200)
    
if st.button("clear cache") : 
    cache_dir.clear()
    st.write("cache cleared")
if st.button("info") :
    st.write(f"api key : {os.getenv('OPENAI_API_KEY')}")
    st.write(f"model name : {os.getenv('OPENAI_MODEL_NAME')}")

    

llm = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'), 
    # max_new_tokens=32, 
    temperature=0.1,
    timeout=10
    )
#%%

def create_chain(instruction):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
    다음 명령에 따라 답변하세요.
    명령 : {instruction}\n\n
    \n\n
                =====================================
                context :
                {{context}}
                """,
            ),
            ("human", "{question}"),
        ]
    )
    

    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt | rbLogChain
        | llm
    )
    
    return chain

#%%
question = st.chat_input("Ask anything about your file...")

if question :
    st.write(f"instruction : {instruction}")
    st.write(f"you : {question}")
    
    chain = create_chain(instruction)
    
    _answer = chain.invoke(question)
    st.write(_answer.content)
    
