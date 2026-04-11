"""
性能测试脚本
测试响应时间、并发能力、缓存命中率
"""

import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import requests

# API 基础 URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试查询列表
TEST_QUERIES = [
    "贵州茅台 2024 年的营业收入是多少？",
    "五粮液 2023 年的净利润是多少？",
    "查询贵州茅台的基本信息",
    "2024 年营收最高的公司是哪家？",
    "查询所有白酒行业的公司",
]


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_response_time(self, n_requests: int = 100) -> Dict[str, Any]:
        """
        测试响应时间
        
        Args:
            n_requests: 请求数量
        
        Returns:
            响应时间统计
        """
        all_times = []
        
        for i in range(n_requests):
            query = TEST_QUERIES[i % len(TEST_QUERIES)]
            
            start = time.time()
            try:
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query}
                )
                elapsed = time.time() - start
                all_times.append(elapsed)
            except Exception as e:
                print(f"Request failed: {e}")
                all_times.append(-1)
        
        # 过滤失败请求
        success_times = [t for t in all_times if t > 0]
        
        if not success_times:
            return {"error": "All requests failed"}
        
        # 统计
        all_times_sorted = sorted(success_times)
        n = len(all_times_sorted)
        
        return {
            "min": min(all_times_sorted),
            "max": max(all_times_sorted),
            "avg": statistics.mean(all_times_sorted),
            "median": statistics.median(all_times_sorted),
            "p50": all_times_sorted[n // 2],
            "p95": all_times_sorted[int(n * 0.95)],
            "p99": all_times_sorted[int(n * 0.99)],
            "std": statistics.stdev(all_times_sorted) if n > 1 else 0,
            "total_requests": n_requests,
            "success_requests": len(success_times)
        }
    
    def test_concurrency(self, n_workers: int = 10, n_requests_per_worker: int = 10) -> Dict[str, Any]:
        """
        测试并发能力
        
        Args:
            n_workers: 并发 worker 数
            n_requests_per_worker: 每个 worker 的请求数
        
        Returns:
            并发测试结果
        """
        def worker(worker_id: int):
            times = []
            for i in range(n_requests_per_worker):
                query = TEST_QUERIES[i % len(TEST_QUERIES)]
                
                start = time.time()
                try:
                    response = self.session.post(
                        f"{self.base_url}/query",
                        json={"query": query}
                    )
                    elapsed = time.time() - start
                    times.append(elapsed)
                except Exception as e:
                    times.append(-1)
            
            return times
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(n_workers)]
            all_times = []
            for future in as_completed(futures):
                all_times.extend(future.result())
        
        total_time = time.time() - start
        
        # 过滤失败
        success_times = [t for t in all_times if t > 0]
        failed_count = len(all_times) - len(success_times)
        
        # 计算 QPS
        qps = len(success_times) / total_time if total_time > 0 else 0
        
        return {
            "total_time": total_time,
            "total_requests": len(all_times),
            "success_requests": len(success_times),
            "failed_requests": failed_count,
            "qps": qps,
            "avg_time": statistics.mean(success_times) if success_times else 0,
            "workers": n_workers
        }
    
    def test_cache_hit_rate(self, n_requests: int = 100) -> Dict[str, Any]:
        """
        测试缓存命中率
        
        Args:
            n_requests: 请求数量
        
        Returns:
            缓存命中率统计
        """
        # 使用重复查询测试缓存
        query = TEST_QUERIES[0]
        cache_hits = 0
        
        for i in range(n_requests):
            start = time.time()
            try:
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query}
                )
                elapsed = time.time() - start
                
                # 第一次请求未命中，后续应该命中
                if i > 0 and elapsed < 0.1:  # 缓存请求通常<100ms
                    cache_hits += 1
            except Exception as e:
                print(f"Request failed: {e}")
        
        # 计算命中率（排除第一次）
        hit_rate = cache_hits / (n_requests - 1) if n_requests > 1 else 0
        
        return {
            "total_requests": n_requests,
            "cache_hits": cache_hits,
            "hit_rate": hit_rate
        }


def main():
    """主函数"""
    print("=" * 60)
    print("  性能测试")
    print("=" * 60)
    print()
    
    tester = PerformanceTester()
    results = {}
    
    # 1. 响应时间测试
    print("1. 响应时间测试（100 次请求）...")
    results["response_time"] = tester.test_response_time(100)
    print(f"   平均响应时间：{results['response_time']['avg']*1000:.1f}ms")
    print(f"   P95 响应时间：{results['response_time']['p95']*1000:.1f}ms")
    print()
    
    # 2. 并发测试
    print("2. 并发测试（10 workers，100 次请求）...")
    results["concurrency"] = tester.test_concurrency(10, 10)
    print(f"   QPS: {results['concurrency']['qps']:.1f}")
    print(f"   总时间：{results['concurrency']['total_time']:.1f}s")
    print()
    
    # 3. 缓存命中率测试
    print("3. 缓存命中率测试（100 次请求）...")
    results["cache_hit_rate"] = tester.test_cache_hit_rate(100)
    print(f"   缓存命中率：{results['cache_hit_rate']['hit_rate']*100:.1f}%")
    print()
    
    # 保存结果
    with open("tests/performance_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("✅ 性能测试完成，结果已保存到 tests/performance_results.json")
    
    return results


if __name__ == "__main__":
    main()
