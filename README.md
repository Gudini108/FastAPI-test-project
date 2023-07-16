## FastAPI api test project

### How to lauch this project:

you would need Python, preferably latest version.

1. Clone this repo and move to project main directory:
    - git clone git@github.com:Gudini108/fastapi-test-project.git
    - cd fastapi-test-project

2. Create and activate virtual enviroment:
    - python3 -m venv venv
    - source venv/bin/activate

2.1. for windows based system:
    - python -m venv venv
    - source/Scripts/activate

3. upgrade pip:
    - python3 -m pip install --upgrade pip

3.1. for windows based system:
    - python -m pip install --upgrade pip

4. Install requirements.txt
    - pip install -r requirements.txt

5. Go to `settings.py`

6. Find line `EMAILHUNTERS_API_KEY = os.getenv('EMAILHUNTER_API_KEY')`

7. change `os.getenv('EMAILHUNTER_API_KEY')` to your emailhunters.co API key

8. Lauch project with `uvicorn main:app --reload` command

9. You would find Swagger documentation at `http://127.0.0.1:8000/docs/` or ReDoc documentation at `http://127.0.0.1:8000/redoc/`
