"""
缓存模块
使用 Redis 实现查询结果缓存
"""

import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class QueryCache:
    """查询缓存类"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", default_ttl: int = 3600):
        """
        初始化查询缓存
        
        Args:
            redis_url: Redis 连接 URL
            default_ttl: 默认过期时间（秒）
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.client = None
        
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(redis_url, decode_responses=True)
                self.client.ping()
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}")
                self.client = None
    
    def _generate_key(self, query: str, params: Optional[Dict] = None) -> str:
        """
        生成缓存键
        
        Args:
            query: 查询文本
            params: 额外参数
        
        Returns:
            缓存键
        """
        key_data = query
        if params:
            key_data += json.dumps(params, sort_keys=True)
        
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"query:{key_hash}"
    
    def get(self, query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            query: 查询文本
            params: 额外参数
        
        Returns:
            缓存结果，不存在返回 None
        """
        if not self.client:
            return None
        
        key = self._generate_key(query, params)
        
        try:
            cached = self.client.get(key)
            if cached:
                data = json.loads(cached)
                return data
        except Exception as e:
            print(f"Warning: Cache get failed: {e}")
        
        return None
    
    def set(self, query: str, result: Any, params: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
        """
        设置缓存
        
        Args:
            query: 查询文本
            result: 缓存结果
            params: 额外参数
            ttl: 过期时间（秒）
        
        Returns:
            是否成功
        """
        if not self.client:
            return False
        
        key = self._generate_key(query, params)
        ttl = ttl or self.default_ttl
        
        try:
            data = json.dumps(result, ensure_ascii=False)
            self.client.setex(key, ttl, data)
            return True
        except Exception as e:
            print(f"Warning: Cache set failed: {e}")
            return False
    
    def delete(self, query: str, params: Optional[Dict] = None) -> bool:
        """
        删除缓存
        
        Args:
            query: 查询文本
            params: 额外参数
        
        Returns:
            是否成功
        """
        if not self.client:
            return False
        
        key = self._generate_key(query, params)
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Warning: Cache delete failed: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有查询缓存
        
        Returns:
            是否成功
        """
        if not self.client:
            return False
        
        try:
            keys = self.client.keys("query:*")
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            print(f"Warning: Cache clear failed: {e}")
            return False
    
    def stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            统计信息
        """
        if not self.client:
            return {"available": False}
        
        try:
            keys = self.client.keys("query:*")
            return {
                "available": True,
                "total_keys": len(keys),
                "memory_usage": self.client.info("memory").get("used_memory_human", "N/A")
            }
        except Exception as e:
            return {"available": False, "error": str(e)}


class MemoryCache:
    """内存缓存（Redis 不可用时的备选方案）"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
    
    def _generate_key(self, query: str, params: Optional[Dict] = None) -> str:
        """生成缓存键"""
        key_data = query
        if params:
            key_data += json.dumps(params, sort_keys=True)
        
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"query:{key_hash}"
    
    def get(self, query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """获取缓存"""
        key = self._generate_key(query, params)
        
        if key in self.cache:
            entry = self.cache[key]
            expire_at = entry.get("expire_at")
            
            if expire_at and datetime.now() > expire_at:
                # 已过期，删除
                del self.cache[key]
                return None
            
            return entry.get("data")
        
        return None
    
    def set(self, query: str, result: Any, params: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        key = self._generate_key(query, params)
        ttl = ttl or self.default_ttl
        
        # 检查是否需要清理
        if len(self.cache) >= self.max_size:
            self._cleanup()
        
        expire_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        
        self.cache[key] = {
            "data": result,
            "created_at": datetime.now(),
            "expire_at": expire_at
        }
        
        return True
    
    def delete(self, query: str, params: Optional[Dict] = None) -> bool:
        """删除缓存"""
        key = self._generate_key(query, params)
        
        if key in self.cache:
            del self.cache[key]
            return True
        
        return False
    
    def clear(self) -> bool:
        """清空缓存"""
        self.cache.clear()
        return True
    
    def _cleanup(self):
        """清理过期条目"""
        now = datetime.now()
        expired_keys = [
            k for k, v in self.cache.items()
            if v.get("expire_at") and now > v["expire_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        self._cleanup()
        
        return {
            "available": True,
            "total_keys": len(self.cache),
            "max_size": self.max_size
        }


# 全局缓存实例
_default_cache = None


def get_default_cache(redis_url: str = "redis://localhost:6379/0", default_ttl: int = 3600):
    """获取默认缓存实例"""
    global _default_cache
    
    if _default_cache is None:
        if REDIS_AVAILABLE:
            _default_cache = QueryCache(redis_url, default_ttl)
        else:
            _default_cache = MemoryCache(default_ttl=default_ttl)
    
    return _default_cache


def cached_query(func):
    """缓存装饰器"""
    def wrapper(query: str, params: Optional[Dict] = None, **kwargs):
        cache = get_default_cache()
        
        # 尝试从缓存获取
        cached_result = cache.get(query, params)
        if cached_result is not None:
            return cached_result
        
        # 执行查询
        result = func(query, params, **kwargs)
        
        # 缓存结果
        cache.set(query, result, params)
        
        return result
    
    return wrapper


    def get_stats(self):
        """获取缓存统计"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': len(self.cache)
        }
