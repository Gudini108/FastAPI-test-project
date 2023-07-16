## FastAPI api test project

### How to lauch this project:

you would need Python, preferably latest version.

#### Clone this repo and move to project main directory:
    git clone https://github.com/Gudini108/FastAPI-test-project.git


#### Create and activate virtual enviroment:
#### for linux based systems:
    python3 -m venv venv
    source venv/bin/activate

#### for windows based systems:
    python -m venv venv
    source venv/Scripts/activate


#### upgrade pip:
#### for linux based systems:
    python3 -m pip install --upgrade pip

#### for windows based systems:
    python -m pip install --upgrade pip
    

#### Install requirements.txt
    pip install -r requirements.txt
    

### Set up emailhunters.co API key
#### Go to `settings.py`

1. Find line `EMAILHUNTERS_API_KEY = os.getenv('EMAILHUNTER_API_KEY')`

2. change `os.getenv('EMAILHUNTER_API_KEY')` to your emailhunters.co API key

3. Remove `import os` from the top

#### Alternative way:

1. In the main directory create `.env` file

2. Write in it your emailhunters.co api key like this `EMAILHUNTERS_API_KEY = 'your_api_key'` where `'your_api_key'` is your emailhunters.co personal API key

3. Save changes in this file


#### Lauch project with `uvicorn main:app --reload` command

#### You would find Swagger documentation at `http://127.0.0.1:8000/docs/` or ReDoc documentation at `http://127.0.0.1:8000/redoc/`
