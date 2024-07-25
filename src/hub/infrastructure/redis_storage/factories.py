from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisEventIsolation, RedisStorage

from .config import RedisConfig


def create_redis_fsm_storage(config: RedisConfig) -> RedisStorage:
    return RedisStorage.from_url(
        url=config.full_url,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
    )


def create_redis_event_isolation(config: RedisConfig) -> RedisEventIsolation:
    return RedisEventIsolation.from_url(
        url=config.full_url,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
    )
