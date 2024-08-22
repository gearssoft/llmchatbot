# as 상담봇 관리자

## pm2로 실행하기

```bash
pm2 start run_app.sh --name "as-bot"
pm2 start run_editor.sh --name "as-bot-editor"

#or

pm2 start ecosystem.config.js

``` 

