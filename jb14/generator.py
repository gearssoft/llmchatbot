#%%
# from flask import Flask, request, jsonify
from flask import Flask, request, Response
import json
from flask_cors import CORS

from dotenv import load_dotenv
import os

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever

# .env 파일 로드
load_dotenv()

#%%
# 임베딩 모델 초기화
openai_embeddings = OpenAIEmbeddings()

# 저장된 벡터 저장소 로드
chroma_store = Chroma(
    persist_directory='./stores/chroma_store',
    embedding_function=openai_embeddings
                      )

#%%
#retriever 생성

llm = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'),
    max_tokens=100,
    temperature=0)
qa_chain = RetrievalQA.from_chain_type(llm,retriever=chroma_store.as_retriever())

print(f'model_name: {llm.model_name}')
print(f'QA Chain retriever: {qa_chain.retriever}')

#%%
# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Endpoint for QA
@app.route('/jb14/qa', methods=['POST'])
def handle_qa():
    try:
        # Extract question as plain text from the request body
        question = request.data.decode('utf-8')
        
        print(f'question: {question}')
        
        # Process the question using Langchain
        _response = qa_chain({"query": question})
        
        # 평문으로 변환 ,_response['result'] 
        
        return _response['result']
        
        
        
        
        # Manually encode the response as JSON with non-ASCII characters
        # response_json = json.dumps({'r': 'ok', 'content': _response['result']}, ensure_ascii=False)
        # Create a custom response with the correct content type
        #return Response(response_json, content_type="application/json; charset=utf-8")

    except Exception as e:
        # In case of any error
        error_json = json.dumps({'r': 'error', 'content': str(e)}, ensure_ascii=False)
        return Response(error_json, content_type="application/json; charset=utf-8")



# Run the app
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))  # Default to 5000 if not set
    app.run(debug=False,host='0.0.0.0', port=port)
    
    
# #%%
# question = '덕진공원 에 대해서 알려줘'
# #%%
# retriever_from_llm = MultiQueryRetriever.from_llm(
#     llm=llm,
#     retriever=chroma_store.as_retriever()
#     )
# docs = retriever_from_llm.get_relevant_documents(question)
# print(docs) 

# # %%
# qa_chain = RetrievalQA.from_chain_type(llm,retriever=chroma_store.as_retriever())
# result = qa_chain({"query": "정읍사에 대해서 알려줘" })
# print(result)

# # %%
# docs = chroma_store.similarity_search(question, k=10)

# for doc in docs:
#     print(doc)
    

# %%
