#%%
from dotenv import load_dotenv
import os

from langchain.storage import LocalFileStore
# from langchain_community.llms import OpenAI
from langchain_openai import OpenAI,OpenAIEmbeddings
# from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader
# from langchain_community.embeddings import OpenAIEmbeddings


from langchain.embeddings import CacheBackedEmbeddings

from langchain_community.vectorstores import Chroma,FAISS

from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain import __version__ as langchain_version

# .env 파일 로드
load_dotenv()

print(f'langchain version : {langchain_version}')

#%%
#srcData/ 폴더에 있는 csv 파일을 모두읽어서 하나의 데이터로 만든다.

# srcData 폴더 내의 모든 CSV 파일 찾기
folder_path = 'srcData/'
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 모든 데이터를 로드하여 하나의 리스트에 저장
all_data = []
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    loader = CSVLoader(file_path=file_path)
    print(f'loading {file_path}')
    data = loader.load()
    all_data.extend(data)
    
print( f'document size : {len(all_data)}' )

#%%
# print(all_data[0].page_content)

#%%

openai = OpenAI()
# OpenAI 임베딩 모델 초기화
embeddings = OpenAIEmbeddings()
cache_dir = LocalFileStore("./.cache/")
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
vectorstore = FAISS.from_documents(all_data, cached_embeddings)

#%% vector store 정보 표시
# print(vectorstore)
print(f"vector store size : {vectorstore.index.ntotal}")
