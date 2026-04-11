"""
文档检索模块
实现向量检索、BM25 关键词检索和混合检索功能
"""

from typing import List, Dict, Any, Optional
import numpy as np
import re
from collections import Counter

try:
    from FlagEmbedding import FlagReranker
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False


class Retriever:
    """文档检索器"""
    
    def __init__(self, vector_store, embedding_model):
        """
        初始化检索器
        
        Args:
            vector_store: 向量存储实例
            embedding_model: Embedding 模型实例
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filters: 过滤条件
        
        Returns:
            检索结果
        """
        # 生成查询向量
        query_embedding = self.embedding_model.encode(query)
        
        # 向量检索
        results = self.vector_store.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters
        )
        
        return results
    
    def retrieve_with_scores(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档（带分数）
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filters: 过滤条件
        
        Returns:
            带分数的检索结果列表
        """
        results = self.retrieve(query, n_results, filters)
        
        # 转换为带分数的格式
        formatted_results = []
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            for i, doc in enumerate(docs):
                formatted_results.append({
                    'document': doc,
                    'score': 1.0 / (1.0 + distances[i]) if i < len(distances) else 0.0,
                    'metadata': metadatas[i] if i < len(metadatas) else {}
                })
        
        return formatted_results


class Reranker:
    """重排序器"""
    
    def __init__(self, model_name: str = 'bge-reranker-base'):
        """
        初始化重排序器
        
        Args:
            model_name: 重排序模型名称
        """
        self.model_name = model_name
        self.reranker = None
        
        if RERANKER_AVAILABLE:
            try:
                self.reranker = FlagReranker(model_name, use_fp16=False)
            except Exception as e:
                print(f"Warning: Failed to load reranker: {e}")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        重排序文档
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前 K 个结果
        
        Returns:
            重排序后的文档列表（带分数）
        """
        if not self.reranker or not documents:
            # 无重排序器，返回原始顺序
            return [{'document': doc, 'score': 0.0} for doc in documents[:top_k]]
        
        # 计算查询 - 文档对得分
        pairs = [[query, doc] for doc in documents]
        
        try:
            scores = self.reranker.compute_score(pairs)
        except Exception as e:
            print(f"Warning: Reranking failed: {e}")
            scores = [0.0] * len(pairs)
        
        # 按得分排序
        if isinstance(scores, tuple):
            scores = scores[0]
        
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        # 返回前 K 个结果
        results = []
        for idx in ranked_indices[:top_k]:
            results.append({
                'document': documents[idx],
                'score': float(scores[idx]),
                'original_index': idx
            })
        
        return results
    
    def rerank_retrieval_results(
        self,
        query: str,
        retrieval_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        重排序检索结果
        
        Args:
            query: 查询文本
            retrieval_results: 检索结果列表
            top_k: 返回前 K 个结果
        
        Returns:
            重排序后的结果
        """
        documents = [r['document'] for r in retrieval_results]
        reranked = self.rerank(query, documents, top_k)
        
        # 合并原始元数据
        for result in reranked:
            orig_idx = result['original_index']
            if orig_idx < len(retrieval_results):
                result['metadata'] = retrieval_results[orig_idx].get('metadata', {})
        
        return reranked


class BM25Retriever:
    """BM25 关键词检索器"""
    
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        """
        初始化 BM25 检索器
        
        Args:
            documents: 文档列表
            k1: BM25 参数（词频饱和度）
            b: BM25 参数（长度归一化）
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        
        # 预处理文档
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        
        # 计算 IDF
        self.idf = self._calculate_idf()
    
    def _tokenize(self, text: str) -> List[str]:
        """分词（简单按字符分割）"""
        # 中文分词：按字符分割
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        # 英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        
        return chinese_chars + english_words
    
    def _calculate_idf(self) -> Dict[str, float]:
        """计算 IDF"""
        num_docs = len(self.documents)
        doc_freq = Counter()
        
        for tokens in self.tokenized_docs:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1
        
        idf = {}
        for token, df in doc_freq.items():
            idf[token] = np.log((num_docs - df + 0.5) / (df + 0.5) + 1)
        
        return idf
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        BM25 检索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
        
        Returns:
            检索结果列表（带分数）
        """
        query_tokens = self._tokenize(query)
        
        scores = []
        for i, doc_tokens in enumerate(self.tokenized_docs):
            score = self._bm25_score(query_tokens, doc_tokens)
            scores.append((i, score))
        
        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前 N 个结果
        results = []
        for idx, score in scores[:n_results]:
            if score > 0:
                results.append({
                    'document': self.documents[idx],
                    'score': score,
                    'index': idx,
                    'method': 'bm25'
                })
        
        return results
    
    def _bm25_score(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """计算 BM25 分数"""
        score = 0.0
        doc_len = len(doc_tokens)
        
        # 计算词频
        doc_tf = Counter(doc_tokens)
        
        for token in query_tokens:
            if token not in doc_tf:
                continue
            
            tf = doc_tf[token]
            idf = self.idf.get(token, 0.0)
            
            # BM25 公式
            numerator = idf * tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / len(self.documents[0].split()) if self.documents else 1)
            
            score += numerator / denominator
        
        return score


class HybridRetriever:
    """混合检索器（向量 + BM25）"""
    
    def __init__(
        self,
        vector_store,
        embedding_model,
        documents: Optional[List[str]] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """
        初始化混合检索器
        
        Args:
            vector_store: 向量存储实例
            embedding_model: Embedding 模型实例
            documents: 文档列表（用于 BM25）
            vector_weight: 向量权重（0-1）
            keyword_weight: 关键词权重（0-1）
        """
        self.vector_retriever = Retriever(vector_store, embedding_model)
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # BM25 检索器
        if documents:
            self.bm25_retriever = BM25Retriever(documents)
        else:
            self.bm25_retriever = None
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        混合检索（向量 + BM25）
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            filters: 过滤条件
        
        Returns:
            检索结果列表
        """
        # 向量检索
        vector_results = self.vector_retriever.retrieve_with_scores(
            query, n_results * 2, filters
        )
        
        # BM25 检索
        if self.bm25_retriever:
            bm25_results = self.bm25_retriever.search(query, n_results * 2)
        else:
            bm25_results = []
        
        # 融合结果
        fused_results = self._fuse_results(vector_results, bm25_results, n_results)
        
        return fused_results
    
    def _fuse_results(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        n_results: int
    ) -> List[Dict[str, Any]]:
        """
        融合向量检索和 BM25 结果
        
        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            n_results: 返回结果数量
        
        Returns:
            融合后的结果
        """
        # 构建文档到分数的映射
        doc_scores = {}
        
        # 向量检索分数
        for result in vector_results:
            doc = result['document']
            score = result['score']
            
            if doc not in doc_scores:
                doc_scores[doc] = {'vector': 0.0, 'bm25': 0.0, 'metadata': result.get('metadata', {})}
            
            doc_scores[doc]['vector'] = max(doc_scores[doc]['vector'], score)
        
        # BM25 分数
        for result in bm25_results:
            doc = result['document']
            score = result['score']
            
            if doc not in doc_scores:
                doc_scores[doc] = {'vector': 0.0, 'bm25': 0.0, 'metadata': result.get('metadata', {})}
            
            doc_scores[doc]['bm25'] = max(doc_scores[doc]['bm25'], score)
        
        # 归一化分数
        max_vector = max((r['vector'] for r in doc_scores.values()), default=1.0)
        max_bm25 = max((r['bm25'] for r in doc_scores.values()), default=1.0)
        
        # 计算最终分数
        final_results = []
        for doc, scores in doc_scores.items():
            normalized_vector = scores['vector'] / max_vector if max_vector > 0 else 0
            normalized_bm25 = scores['bm25'] / max_bm25 if max_bm25 > 0 else 0
            
            final_score = (
                self.vector_weight * normalized_vector +
                self.keyword_weight * normalized_bm25
            )
            
            final_results.append({
                'document': doc,
                'final_score': final_score,
                'vector_score': normalized_vector,
                'bm25_score': normalized_bm25,
                'metadata': scores['metadata']
            })
        
        # 按最终分数排序
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return final_results[:n_results]


# 便捷函数
def create_retriever(vector_store, embedding_model) -> Retriever:
    """创建检索器"""
    return Retriever(vector_store, embedding_model)


def create_reranker(model_name: str = 'bge-reranker-base') -> Reranker:
    """创建重排序器"""
    return Reranker(model_name)
