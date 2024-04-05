import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_URL = str(os.environ["DB_URL"])


config = Config

