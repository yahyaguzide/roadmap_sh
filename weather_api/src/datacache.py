from dataclasses import dataclass, field
import json
import redis


class DataCacheError(Exception):
    pass


@dataclass(eq=False, match_args=False, slots=True)
class DataCache:
    host: str
    port: int
    _db: redis.Redis = field(init=False)

    def __post_init__(self):
        self._db = redis.Redis(host=self.host, port=self.port, decode_responses=True)

        try:
            self._db.ping()
        except redis.ConnectionError:
            raise DataCacheError("Redis Cache not reachable")

    def read_cache(self, key: str) -> str | None:
        if tmp_cache := self._db.get(key):
            return json.loads(str(tmp_cache))

    def set_cache(self, key: str, value: str, expiration: int = 43200) -> None:
        self._db.setex(name=key, time=expiration, value=value)
