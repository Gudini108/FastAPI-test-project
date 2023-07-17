"""App settings"""

import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer


load_dotenv()


# App custom secret key
SECRET_KEY = 'SECRET_KEY'


# OaUTH2 password scheme
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='/login')


# API for email verification via emailhunter.co
EMAILHUNTERS_API_KEY = os.getenv('EMAILHUNTER_API_KEY')
EHUNT_ENDPOINT_WEB = 'https://api.hunter.io/v2/email-verifier?email='
EHUNT_ENDPOINT_API = f'&api_key={EMAILHUNTERS_API_KEY}'


# Password encoding algorythm
PASSWORD_ENCODING_ALGORITHM = 'HS256'


# Expire delta in minutes for JWT-access-token
ACCESS_TOKEN_EXPIRE_MINUTES = 60
