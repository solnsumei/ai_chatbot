import os
from dotenv import load_dotenv
import aioredis
from rejson import Client

load_dotenv()


class RedisService:
    connection = None
    redis_json = None

    def __init__(self):
        """Initialize connection"""
        self.REDIS_URL = os.getenv('REDIS_URL')
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
        self.REDIS_USER = os.getenv('REDIS_USER')
        self.REDIS_PORT = os.getenv('REDIS_PORT')
        self.connection_url = f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_URL}:{self.REDIS_PORT}"

    async def create_connection(self):
        self.connection = aioredis.from_url(
            self.connection_url, db=0
        )

        return self.connection

    def create_rejson_connection(self):
        self.redis_json = Client(
            host=self.REDIS_URL,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            username=self.REDIS_USER,
            decode_responses=True
        )

        return self.redis_json
