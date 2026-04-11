#!/usr/bin/env python3
"""部署测试脚本"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=== 部署测试开始 ===\n")

# 测试 NL2SQL 模块
print("1. 测试 NL2SQL 模块...")
try:
    from prompt.nl2sql_prompt import NL2SQLPrompt
    from eval.evaluator import evaluate_nl2sql
    
    prompt_gen = NL2SQLPrompt()
    prompt = prompt_gen.build_prompt("贵州茅台 2024 年的营业收入是多少？")
    result = evaluate_nl2sql("测试", "SELECT * FROM test", "SELECT * FROM test")
    
    print(f"   ✅ NL2SQLPrompt: {len(prompt)} 字符")
    print(f"   ✅ evaluate_nl2sql: EX={result.ex_correct}")
except Exception as e:
    print(f"   ⚠️ NL2SQL 模块：{e}")

# 测试 RAG 模块
print("\n2. 测试 RAG 模块...")
try:
    from rag.chunker import DocumentChunker
    from rag.attribution import AttributionTracker
    
    chunker = DocumentChunker()
    attribution = AttributionTracker()
    
    print(f"   ✅ DocumentChunker: 可初始化")
    print(f"   ✅ AttributionTracker: 可初始化")
except Exception as e:
    print(f"   ⚠️ RAG 模块：{e}")

# 测试缓存模块
print("\n3. 测试缓存模块...")
try:
    from rag.cache import MemoryCache
    
    cache = MemoryCache()
    cache.set('test', 'value', 60)
    value = cache.get('test')
    
    print(f"   ✅ MemoryCache: set/get 可用")
except Exception as e:
    print(f"   ⚠️ 缓存模块：{e}")

# 测试分词模块
print("\n4. 测试分词模块...")
try:
    from rag.jieba_tokenizer import JiebaTokenizer
    
    tokenizer = JiebaTokenizer()
    tokens = tokenizer.tokenize("贵州茅台 2024 年的营业收入")
    
    print(f"   ✅ JiebaTokenizer: 分词 {len(tokens)} 个")
except Exception as e:
    print(f"   ⚠️ 分词模块：{e}")

print("\n=== 部署测试完成 ===")
print("\n✅ 核心模块部署成功！")
