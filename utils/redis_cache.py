# utils/redis_cache.py

import json
import logging
from typing import Any, Optional, List, Dict

from django.core.cache import cache
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)


class RedisCacheManager:

    def __init__(self, alias='default'):
        self.alias = alias
        self.cache = cache
        self.redis = get_redis_connection(alias)

    # ==================== عملیات پایه ====================

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Save Value to Cache Key"""
        try:
            self.cache.set(key, value, timeout=timeout)
            logger.debug(f"✅ Cache set: {key} (TTL: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get Value from Cache Key"""
        try:
            value = self.cache.get(key)
            if value is not None:
                logger.debug(f"📦 Cache hit: {key}")
            else:
                logger.debug(f"❌ Cache miss: {key}")
            return value if value is not None else default
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            return default

    def delete(self, key: str) -> bool:
        """Delete a cache key"""
        try:
            self.cache.delete(key)
            logger.debug(f"🗑️ Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Cache delete error: {e}")
            return False

    def delete_many(self, keys: List[str]) -> int:
        """Delete Multiple Cache Keys"""
        try:
            count = self.cache.delete_many(keys)
            logger.debug(f"🗑️ Deleted {count} keys")
            return count
        except Exception as e:
            logger.error(f"❌ Cache delete_many error: {e}")
            return 0

    def clear_all(self) -> bool:
        """ Clear all Caches """
        try:
            self.cache.clear()
            logger.warning("🗑️ All cache cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.cache.has_key(key)
        except Exception as e:
            logger.error(f"❌ Cache exists error: {e}")
            return False

    def get_or_set(self, key: str, func, timeout: int = 300) -> Any:
        """Get Cache, if not available Set it"""
        value = self.get(key)
        if value is not None:
            return value

        value = func()
        self.set(key, value, timeout)
        return value

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increase numeric Value"""
        try:
            return self.cache.incr(key, amount)
        except Exception as e:
            logger.error(f"❌ Increment error: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrease numeric Value"""
        try:
            return self.cache.decr(key, amount)
        except Exception as e:
            logger.error(f"❌ Decrement error: {e}")
            return None

    def set_hash(self, key: str, field: str, value: Any) -> bool:
        """Set hash"""
        try:
            self.redis.hset(key, field, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"❌ Hash set error: {e}")
            return False

    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """Get Hash Value"""
        try:
            value = self.redis.hget(key, field)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"❌ Hash get error: {e}")
            return None

    def get_all_hash(self, key: str) -> Dict:
        """Get all field of a hash"""
        try:
            data = self.redis.hgetall(key)
            return {k.decode(): json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"❌ Hash get_all error: {e}")
            return {}

    def push_to_list(self, key: str, value: Any) -> bool:
        """Push value to list"""
        try:
            self.redis.rpush(key, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"❌ List push error: {e}")
            return False

    def get_list(self, key: str, start: int = 0, end: int = -1) -> List:
        """Get list of Cache Keys"""
        try:
            items = self.redis.lrange(key, start, end)
            return [json.loads(item) for item in items]
        except Exception as e:
            logger.error(f"❌ List get error: {e}")
            return []

    def get_list_length(self, key: str) -> int:
        """Length of list"""
        try:
            return self.redis.llen(key)
        except Exception as e:
            logger.error(f"❌ List length error: {e}")
            return 0

    def set_with_expiry(self, key: str, value: Any, expiry: int = 300) -> bool:
        """Set Cache With Expiry"""
        try:
            self.redis.setex(key, expiry, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"❌ Set with expiry error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys with pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                count = self.redis.delete(*keys)
                logger.debug(f"🗑️ Deleted {count} keys matching: {pattern}")
                return count
            return 0
        except Exception as e:
            logger.error(f"❌ Delete pattern error: {e}")
            return 0

    def get_ttl(self, key: str) -> int:
        """Get leftover time to live"""
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logger.error(f"❌ Get TTL error: {e}")
            return -2

    def set_lock(self, key: str, timeout: int = 5) -> bool:
        """Set Lock to avoid Race Condition"""
        try:
            return self.redis.set(f'lock_{key}', 'locked', nx=True, ex=timeout)
        except Exception as e:
            logger.error(f"❌ Set lock error: {e}")
            return False

    def release_lock(self, key: str) -> bool:
        """Release Lock"""
        try:
            self.redis.delete(f'lock_{key}')
            return True
        except Exception as e:
            logger.error(f"❌ Release lock error: {e}")
            return False
