## setup 

```bash
git clone <your_repo_url>
cd ChatAPP_AI_solution
```

install the requirements:

```bash
pip install -r requirements.txt
```

download Ollama for Windows:

```url
https://ollama.com/download
```

then verify the installation:

```bash
ollama --version
```

if you see the version, that means it's installed.  
if not, add the binary path of it to Windows environment variables and check again.

then pull the required model:

```bash
ollama pull llama3.1:8b
```

then run this to start the FastAPI endpoints:

```bash
uvicorn main:app --reload --port 4000
```

if you see any module error like `ModuleNotFoundError` (e.g. for `fastapi`), run this for each missing module:

```bash
pip install module_name  # for example: fastapi
```

then access:

```
localhost:4000/docs
```

to view the API documentation.

you also have a file called `api_test_curls.txt` — it has Postman test cases for each endpoint.
