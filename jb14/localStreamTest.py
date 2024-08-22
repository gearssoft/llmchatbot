#%%
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough,RunnableLambda
from langchain.vectorstores import Chroma  # 예시용, 실제 설정에 맞게 변경하세요.
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.callbacks.base import BaseCallbackHandler

from dotenv import load_dotenv
load_dotenv()

class ChatCallbackHandler(BaseCallbackHandler):
    # message = ""

    def on_llm_start(self, *args, **kwargs):
        # self.message_box = st.empty()
        print("on_llm_start")

    def on_llm_end(self, *args, **kwargs):
        # save_message(self.message, "ai")
        print("on_llm_end")

    def on_llm_new_token(self, token, *args, **kwargs):
        print("on_llm_new_token : ", token)
        # self.message += token
        # self.message_box.markdown(self.message)
        
llm = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ],
)
        
# 체인을 위한 설정 (예시용, 실제 설정에 맞게 변경하세요)
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory='./stores/chroma_store', embedding_function=embeddings)
retriever = vectorstore.as_retriever()
#%%
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful assistant. Answer questions using only the following context. 
            context : {context}
            """,
        ),
        ("human", "{question}"),
    ]
)
def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)
#%%
chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
        )
#%%

chain.invoke("덕진공원은 어디에 있나요?")
# %%
