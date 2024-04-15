import uvicorn

from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from middlewares import CustomHeaderMiddleware

from src.database.db import get_db, db_redis
from src.routes import contacts, auth, users

app = FastAPI()

origins = ['*']

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')

app.add_middleware(CustomHeaderMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app, such as database connections.

    :return: A list of functions to be executed at the end of startup
    :doc-author: SergiyRus1974
    """
    r = await db_redis
    await FastAPILimiter.init(r)
    # FastAPICache.init(RedisBackend(r), prefix="fastapi-cache")


@app.get("/")
def index() -> dict:
    """
    The index function returns a dict with the message &quot;Contact management Application&quot;
        :return: {&quot;message&quot;: &quot;Contact management Application&quot;}


    :return: A dictionary with the key message and a value of contact management application
    :doc-author: SergiyRus1974
    """
    return {"message": "Contact management Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by executing a SQL query to check if it can connect to the database and retrieve data.

    :param db: AsyncSession: Inject the database session
    :return: A dictionary with a message
    :doc-author: SergiyRus1974
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == '__main__':
    # uvicorn.run(app, host="localhost", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
