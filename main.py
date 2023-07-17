"""App description and launch"""

from fastapi import FastAPI, APIRouter

from routers.auth import router as auth_router
from routers.posts import router as posts_router
from routers.reactions import router as reactions_router
from routers.users import router as users_router


API_DESCRIPTION = """
Simple RESTful API using FastAPI for a social networking application

## Functions

* **Signup as a new user**
* **Login as a registered user and obtain JWT-token**
* **Create, Delete, Edit and View Posts**
* **Like and Dislike other user's Posts**
"""

app = FastAPI(
    title='Webtronics FastAPI test project',
    description=API_DESCRIPTION,
    version='1.0.0'
)
router = APIRouter()


@app.get('/', tags=['Root'])
def root():
    """Root endpoint with links to /signup, /login and /posts"""
    return {
        'signup': app.url_path_for('signup'),
        'login': app.url_path_for('login'),
        'posts': app.url_path_for('get_posts')
    }


api_prefx = '/api/v1'
app.include_router(router, prefix=api_prefx)
app.include_router(auth_router, prefix=api_prefx)
app.include_router(users_router, prefix=api_prefx)
app.include_router(posts_router, prefix=api_prefx)
app.include_router(reactions_router, prefix=api_prefx)


# TODO: add redis cache for likes and dislikes

# @app.on_event('startup')
# async def startup():
#     redis = aioredis.from_url('redis://localhost')
#     FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
