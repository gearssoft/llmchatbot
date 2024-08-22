#%%

# file name : generator_fast.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse,StreamingResponse,PlainTextResponse
from pydantic import BaseModel
from fastapi import Request
import asyncio
# from flask_cors import CORS
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncIterable, Awaitable

import os

from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.callbacks import AsyncIteratorCallbackHandler

from langchain.storage import LocalFileStore

# .env 파일 로드 및 환경 변수 설정
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

load_dotenv()

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

# 모델 및 체인 초기화
# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma(persist_directory='./stores/chroma_store', embedding_function=embeddings)

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

embeddings = OpenAIEmbeddings()
cache_dir = LocalFileStore("./.cache/")
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
vectorstore = FAISS.from_documents( 
                                   documents=all_data,
                                   embedding=cached_embeddings)

retriever = vectorstore.as_retriever()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant. 
            your job is to answer questions about the geography of Jeollabuk-do.
            Answer questions using only the following context. If you don't know the answer to a question, you can say "죄송합니다. 해당 질문에 대한 답변은 추후 업데이트하여 데이터를 축적하겠습니다.".
            Answer questions using only korean language.
            if you get one word question, you answer to human like this.
            Q: Jeonju
            A: Jeonju is a city in Jeollabuk-do.
            Q: gochang
            A: gochang is a county in Jeollabuk-do. and it is located in the west of Jeollabuk-do.
            Q: Gunsan
            A: Gunsan is a city in Jeollabuk-do. and it is located in the west of Jeollabuk-do.
            Q: Iksan
            A: Iksan is a city in Jeollabuk-do. and it is located in the center of Jeollabuk-do.
            context :
            {context}
            """,
        ),
        ("human", "{question}"),
    ]
)

llm = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'), 
    # max_new_tokens=100, 
    temperature=0.5,
    streaming=True,
    # callbacks=[
        # StreamingStdOutCallbackHandler(),
    # ]
    )

llm_noneStreaming = ChatOpenAI(
    model_name=os.getenv('OPENAI_MODEL_NAME'), 
    # max_new_tokens=32, 
    temperature=0.1,
    timeout=10
    # streaming=True,
    # callbacks=[
        # StreamingStdOutCallbackHandler(),
    # ]
    )

noneStreaming_qa_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm_noneStreaming
)
#%%
# FastAPI 앱 생성
app = FastAPI(
    title="JB14 chatbot api",
    description="전라북도 14개시도 지리 전문가 대화형 챗봇 API",
)
# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://gears001.iptime.org:22280"],  # 특정 출처 허용
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

async def send_message(message: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    
    llm.callbacks = [callback]

    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
        try:
            await fn
        except Exception as e:
            # TODO: handle exception
            print(f"Caught exception: {e}")
        finally:
            # Signal the aiter to stop.
            event.set()

    # Begin a task that runs in the background.
    task = asyncio.create_task(wrap_done(
        llm.agenerate(
            messages=[[HumanMessage(content=message)]]),
            callback.done
            ),
    )
    
    # 모델에 메시지 전송 및 스트리밍 시작
    # await model.agenerate(messages=[[HumanMessage(content=message)]])

    async for token in callback.aiter():
        # Use server-sent-events to stream the response
        print(f"Streaming token: {token}")  # 여기에 print 문 추가
        yield token

    await task

@app.get("/")
async def root():
    return {"info": "jb14 chatbot api v1.0.0"}

# QA 엔드포인트
@app.post("/jb14/qa")
async def handle_qa(request: Request):
    try:
        body = await request.body()
        question = body.decode("utf-8")
        
        response = noneStreaming_qa_chain.invoke(question)
        # print(response)
        # return response['content']
    # 'AIMessage' 객체의 'content' 속성 반환
        return PlainTextResponse(response.content)
        
    except Exception as e:
        # e.print_stack()
        raise HTTPException(status_code=500, detail=str(e))

# Streaming QA 엔드포인트
@app.post("/jb14/qa_stream")
async def handle_qa_stream(request: Request):
    try :
        
        body = await request.body()
        question = body.decode("utf-8")
        
        print(f"question : {question}")
        
        _chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
        )
        _result = _chain.invoke(question)
        
        return StreamingResponse(send_message(
            _result.messages[0].content + '\n\n\n 위의 내용을 가지고 다음 질문에 답하세요 \n : ' + _result.messages[1].content
            ),
            media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# prompt 엔드포인트  
@app.post("/jb14/prompt")
async def handle_retriever(request: Request):
    try:
        body = await request.body()
        question = body.decode("utf-8")
        _chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
        )
        _result = _chain.invoke(question)
        print(_result.messages)
        return JSONResponse(content={"r": "ok", "content": _result.messages[0].content})
        
    except Exception as e:
        e.print_stack()
        raise HTTPException(status_code=500, detail=str(e))

# 앱 실행
if __name__ == "__main__":
    port = int(os.getenv('API_PORT', 8000))  # 기본 포트를 8000으로 설정
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
else:
    print("run dev mode")
