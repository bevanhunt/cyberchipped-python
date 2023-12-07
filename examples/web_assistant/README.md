## Web Assistant Example

### Setup
Rename .env.setup to .env with your OPENAI_API_KEY

### Install
    pipenv --python 3.11.6 && pipenv install

### Run
In one terminal run:
```bash
bash ./dev.sh
```

In another terminal run:
```bash 
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"text":"hello world", "user_id":"123"}'
```

### Output
```json
{"ai_message":"Hello there! How can I assist you today?"}
```
