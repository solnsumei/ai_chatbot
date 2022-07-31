import asyncio

from src.redis.config import RedisService


async def main():
    redis = RedisService()
    redis = await redis.create_connection()
    print(redis)
    await redis.set("key", "value")


if __name__ == "__main__":
    asyncio.run(main())
