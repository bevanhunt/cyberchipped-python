## Threaded Web Assistant Example

### Setup
Rename .env.setup to .env with your OPENAI_API_KEY

### Install
    pipenv --python 3.11.6 && pipenv install

### Run
In one terminal run: ```bash ./dev.sh```

In another terminal run: ```curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"text":"hello world", "thread_id":"123"}'```

### Output
![Screenshot](./screenshot.png)

