# 전북14개 시도 안내 도우미 인공지능

## test
```bash
curl -X POST http://localhost:21090/jb14/qa -H "Content-Type: text/plain" -d "익산시에서 가볼만한곳좀 추천해줘"
curl -X POST http://gears001.iptime.org:21090/jb14/qa -H "Content-Type: text/plain" -d "익산시에서 가볼만한곳좀 추천해줘"
curl -X POST http://localhost:21090/jb14/qa -H "Content-Type: text/plain" -d "정읍사를 가지고 유행어를 만든 코메디언은?"
curl -X POST http://localhost:21090/jb14/qa_stream -H "Content-Type: text/plain" -d "남원시에서 가볼만 한곳 추천해줘"

```

## 서버 실행

```bash
# uvicorn
uvicorn generator_fast:app --reload --port 21090

# python
python generator_fast.py


#pm2 
pm2 start generator_fast.py --name "jb14-chatbot" --interpreter /home/gbox3d/work/llm-works/horse_house/chatbot/jb14/.venv/bin/python
```

## 관리자 툴 

```bash
# streamlit 관리자 앱
streamlit run chat_admin.py
```

**관리자 앱 설정**  
./streamlit/config.toml 을 아래와 같이 설정한다.  

```toml
[server]
enableCORS = false
enableXsrfProtection = false
```

