## 프롬프트 템플릿 정의
프롬프트 템플릿은 챗봇이 사용자의 질문에 어떻게 응답할지를 정의하는 역할을 합니다. 여기에서는 ChatPromptTemplate을 사용하여 시스템 메시지와 사용자 메시지를 설정하고, 대화의 흐름을 정의합니다.

```python
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="당신은 사람들과 도움이 되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)
```

### ChatPromptTemplate.from_messages 사용

* ChatPromptTemplate 클래스는 프롬프트를 구성하는 데 사용됩니다.  
* from_messages 메서드는 일련의 메시지를 받아 프롬프트 템플릿을 생성합니다.  

### 시스템 메시지 (SystemMessage)  

SystemMessage는 챗봇의 성격과 대화 방식을 정의합니다.
여기서는 "당신은 사람들과 도움이 되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다."라는 메시지를 사용하여 챗봇이 도움이 되는 대화를 한국어로 진행할 것임을 명시합니다.

```python

SystemMessage(content="당신은 사람들과 도움이 되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다.")

```
### 메시지 플레이스홀더 (MessagesPlaceholder)
MessagesPlaceholder는 대화의 역사(이전 대화 기록)를 삽입할 위치를 지정합니다.
variable_name="history"는 이 플레이스홀더가 history 변수로 교체될 것임을 나타냅니다.
```python

MessagesPlaceholder(variable_name="history")

```
### 인간의 메시지 (("human", "{question}"))
인간의 메시지를 나타내는 튜플입니다.
("human", "{question}")는 사용자의 질문이 {question} 자리표시자에 의해 전달될 것임을 나타냅니다. 실제 질문 내용은 런타임 시 입력으로 제공됩니다.

```python
("human", "{question}")
```

### 전체적인 흐름
이 프롬프트 템플릿은 챗봇이 다음과 같은 순서로 메시지를 처리하도록 구성합니다:

시스템 메시지: 챗봇의 역할과 대화 방식 설명.
이전 대화 기록 (history): 대화의 맥락을 유지하기 위해 이전 메시지들을 포함.  
사용자 질문 ({question}): 현재 사용자의 질문을 포함.  

### 예시
만약 사용자가 "오늘 날씨가 어때?"라고 질문한다면, 실제로 챗봇에게 전달되는 프롬프트는 다음과 같이 구성될 수 있습니다.

```txt
당신은 사람들과 도움이 되는 대화를 하는 챗봇입니다. 대화는 한글로 진행됩니다.
<이전 대화 기록>
사용자: 오늘 날씨가 어때?
```

