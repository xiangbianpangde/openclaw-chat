"""
集成测试脚本
测试 API 端点、NL2SQL 集成、RAG 集成
"""

import pytest
import requests
import json
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:8000/api/v1"


class TestAPIEndpoints:
    """API 端点测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.session = requests.Session()
    
    def test_health_endpoint(self):
        """测试健康检查接口"""
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_version_endpoint(self):
        """测试版本信息接口"""
        response = self.session.get(f"{BASE_URL}/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert data["api_version"] == "v1"
    
    def test_root_endpoint(self):
        """测试根路径接口"""
        response = self.session.get(f"{BASE_URL}/../")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
    
    def test_docs_endpoint(self):
        """测试 API 文档接口"""
        response = self.session.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
    
    def test_query_endpoint(self):
        """测试查询接口"""
        response = self.session.post(
            f"{BASE_URL}/query",
            json={"query": "贵州茅台 2024 年的营业收入是多少？"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data


class TestNL2SQLIntegration:
    """NL2SQL 集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.session = requests.Session()
    
    def test_nl2sql_simple_query(self):
        """测试简单 NL2SQL 查询"""
        response = self.session.post(
            f"{BASE_URL}/nl2sql",
            json={
                "query": "贵州茅台 2024 年的营业收入",
                "schema": "CREATE TABLE financial_reports (...)"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sql" in data
    
    def test_nl2sql_cache(self):
        """测试 NL2SQL 缓存"""
        query = "测试缓存查询"
        
        # 第一次请求
        response1 = self.session.post(
            f"{BASE_URL}/nl2sql",
            json={"query": query, "schema": "..."}
        )
        assert response1.status_code == 200
        
        # 第二次请求（应该命中缓存）
        response2 = self.session.post(
            f"{BASE_URL}/nl2sql",
            json={"query": query, "schema": "..."}
        )
        assert response2.status_code == 200
        assert response1.json() == response2.json()


class TestRAGIntegration:
    """RAG 集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.session = requests.Session()
    
    def test_rag_simple_query(self):
        """测试简单 RAG 查询"""
        response = self.session.post(
            f"{BASE_URL}/rag",
            json={"query": "白酒行业发展趋势", "n_results": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_rag_n_results(self):
        """测试 RAG 返回结果数量"""
        n_results = 3
        response = self.session.post(
            f"{BASE_URL}/rag",
            json={"query": "测试查询", "n_results": n_results}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= n_results


class TestFusionIntegration:
    """融合查询集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.session = requests.Session()
    
    def test_fusion_fact_query(self):
        """测试事实查询"""
        response = self.session.post(
            f"{BASE_URL}/fusion",
            json={
                "query": "贵州茅台 2024 年的营业收入是多少？",
                "intent": "fact",
                "n_results": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
    
    def test_fusion_analysis_query(self):
        """测试分析查询"""
        response = self.session.post(
            f"{BASE_URL}/fusion",
            json={
                "query": "对比贵州茅台和五粮液的营收",
                "intent": "analysis",
                "n_results": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_fusion_cache(self):
        """测试融合查询缓存"""
        query = "测试缓存查询"
        
        # 第一次请求
        response1 = self.session.post(
            f"{BASE_URL}/fusion",
            json={"query": query, "intent": "fact"}
        )
        assert response1.status_code == 200
        
        # 第二次请求（应该命中缓存）
        response2 = self.session.post(
            f"{BASE_URL}/fusion",
            json={"query": query, "intent": "fact"}
        )
        assert response2.status_code == 200
        assert response1.json() == response2.json()


class TestAuthentication:
    """认证测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.session = requests.Session()
    
    def test_login_success(self):
        """测试登录成功"""
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_failure(self):
        """测试登录失败"""
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "wrong_password"}
        )
        assert response.status_code == 401


def run_integration_tests():
    """运行集成测试"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_integration_tests()
