"""This is an example of how to use async langchain with fastapi and return a streaming response.
The latest version of Langchain has improved its compatibility with asynchronous FastAPI,
making it easier to implement streaming functionality in your applications.
"""
import asyncio
import os
from typing import AsyncIterable, Awaitable
from flask_cors import CORS

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel

# Two ways to load env variables
# 1.load env variables from .env file
load_dotenv()

# # 2.manually set env variables
# if "OPENAI_API_KEY" not in os.environ:
#     os.environ["OPENAI_API_KEY"] = ""

app = FastAPI()
CORS(app)  # Enable CORS for all routes

model = ChatOpenAI(
        streaming=True,
        verbose=True,
        # callbacks=[callback],
)

async def send_message(message: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    
    model.callbacks = [callback]

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
        model.agenerate(messages=[[HumanMessage(content=message)]]),
        callback.done),
    )
    
    # 모델에 메시지 전송 및 스트리밍 시작
    # await model.agenerate(messages=[[HumanMessage(content=message)]])

    async for token in callback.aiter():
        # Use server-sent-events to stream the response
        # print(f"Streaming token: {token}")  # 여기에 print 문 추가
        yield f"{token}"

    await task


class StreamRequest(BaseModel):
    """Request body for streaming."""
    message: str


@app.post("/stream")
def stream(body: StreamRequest):
    return StreamingResponse(send_message(body.message), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=8000, app=app)