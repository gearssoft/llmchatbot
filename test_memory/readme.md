# ConversationSummaryBufferMemory

```python
from langchain.memory import ConversationSummaryBufferMemory  
```

ConversationSummaryBufferMemory  를 사용하면, 대화의 요약을 저장할 수 있습니다.  
대화의 요약은 ConversationSummaryBufferMemory 의 conversation_summary_buffer 에 저장됩니다.  
conversation_summary_buffer 는 ConversationSummaryBufferMemory 의 conversation_summary_buffer_size 만큼의 요약을 저장합니다.  

```python
memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=120,
            return_messages=True,
        )
```

위와 같이 ConversationSummaryBufferMemory 를 생성합니다.

```python
memory.save_context(
    {"input": prompt},
    {"output": result.content},
)
```
대화의 요약을 저장할 때는 save_context 를 사용합니다.  
save_context 는 입력과 출력을 저장합니다.  

```python
history = memory.load_memory_variables({}).get("history", [])
```



