import contextlib
import redis.asyncio as redis_async
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import settings


class DatabaseSessionManager:
    def __init__(self, url: str):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and sessionmaker, which will be used for all queries.

        :param self: Represent the instance of the class
        :param url: str: Create the engine and session maker
        :return: The instance of the class
        :doc-author: SergiyRus1974
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a coroutine that returns an async context manager.
        The context manager yields a database session, and then closes it when the block exits.
        If there's an exception in the block, it rolls back any changes to the session before closing it.

        :param self: Represent the instance of the class
        :return: A context manager that can be used to manage the session
        :doc-author: SergiyRus1974
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.db_url)


async def get_db():
    """
    The get_db function is a coroutine that returns an open database session.
    It uses the sessionmanager to create a new Session object, and then yields it.
    The yield from expression calls the __aenter__ method of the Session object, which opens a transaction on the connection pool.
    When get_db finishes executing, Python automatically calls __aexit__ on the Session object to close it.

    :return: A session object
    :doc-author: SergiyRus1974
    """
    async with sessionmanager.session() as session:
        yield session


db_redis = redis_async.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                             decode_responses=True)

