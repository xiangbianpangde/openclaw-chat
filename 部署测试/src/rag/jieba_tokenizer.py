"""
jieba 中文分词模块
优化 BM25 检索的中文分词效果
"""

from typing import List, Dict, Any, Optional
import re

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


class JiebaTokenizer:
    """jieba 分词器"""
    
    def __init__(self, use_hmm: bool = True, use_pos: bool = False):
        """
        初始化 jieba 分词器
        
        Args:
            use_hmm: 是否使用 HMM 模型（用于新词识别）
            use_pos: 是否使用词性标注
        """
        self.use_hmm = use_hmm
        self.use_pos = use_pos
        
        if JIEBA_AVAILABLE:
            # 加载自定义词典（可选）
            self._load_custom_dict()
    
    def _load_custom_dict(self):
        """加载自定义词典"""
        # 财务领域专业词汇
        financial_terms = [
            '营业收入', '净利润', '毛利率', '净利率',
            '总资产', '净资产', '资产负债率', '流动比率',
            '每股收益', '市盈率', '市净率', '净资产收益率',
            '经营活动现金流', '投资活动现金流', '筹资活动现金流',
            '贵州茅台', '五粮液', '泸州老窖', '洋河股份',
            '白酒行业', '金融行业', '房地产行业', '医药行业'
        ]
        
        for term in financial_terms:
            jieba.add_word(term)
    
    def tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
        
        Returns:
            分词结果列表
        """
        if not JIEBA_AVAILABLE:
            # 降级到简单分词
            return self._simple_tokenize(text)
        
        # 使用 jieba 精确模式分词
        tokens = list(jieba.cut(text, HMM=self.use_hmm))
        
        # 过滤空白和标点
        tokens = [t.strip() for t in tokens if t.strip() and not self._is_punctuation(t)]
        
        return tokens
    
    def tokenize_for_search(self, text: str) -> List[str]:
        """
        搜索分词（用于 BM25 检索）
        
        Args:
            text: 输入文本
        
        Returns:
            分词结果列表
        """
        if not JIEBA_AVAILABLE:
            return self._simple_tokenize(text)
        
        # 使用 jieba 搜索引擎模式分词
        tokens = list(jieba.cut_for_search(text, HMM=self.use_hmm))
        
        # 过滤空白和标点
        tokens = [t.strip() for t in tokens if t.strip() and not self._is_punctuation(t)]
        
        return tokens
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回前 K 个关键词
        
        Returns:
            关键词列表
        """
        if not JIEBA_AVAILABLE:
            return self.tokenize(text)[:top_k]
        
        # 使用 TF-IDF 提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k)
        
        return keywords
    
    def _simple_tokenize(self, text: str) -> List[str]:
        """
        简单分词（jieba 不可用时的降级方案）
        
        Args:
            text: 输入文本
        
        Returns:
            分词结果列表
        """
        # 中文按字符分割
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        # 英文单词
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        
        # 数字
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        return chinese_chars + english_words + numbers
    
    def _is_punctuation(self, token: str) -> bool:
        """
        判断是否为标点符号
        
        Args:
            token: 分词
        
        Returns:
            是否为标点
        """
        punctuation = set('，。！？；：、""''（）【】《》〈〉「」『』…—～·•')
        return token in punctuation or len(token) == 0


class BM25WithJieba:
    """集成 jieba 分词的 BM25 检索器"""
    
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
        self.tokenizer = JiebaTokenizer()
        
        # 预处理文档
        self.tokenized_docs = [self.tokenizer.tokenize_for_search(doc) for doc in documents]
        
        # 计算 IDF
        self.idf = self._calculate_idf()
    
    def _calculate_idf(self) -> Dict[str, float]:
        """计算 IDF"""
        from collections import Counter
        
        num_docs = len(self.documents)
        doc_freq = Counter()
        
        for tokens in self.tokenized_docs:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1
        
        idf = {}
        import numpy as np
        
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
        query_tokens = self.tokenizer.tokenize_for_search(query)
        
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
                    'method': 'bm25+jieba'
                })
        
        return results
    
    def _bm25_score(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """计算 BM25 分数"""
        from collections import Counter
        
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
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / 100)
            
            score += numerator / denominator
        
        return score


# 便捷函数
def tokenize(text: str, use_search_mode: bool = False) -> List[str]:
    """便捷函数：分词"""
    tokenizer = JiebaTokenizer()
    
    if use_search_mode:
        return tokenizer.tokenize_for_search(text)
    else:
        return tokenizer.tokenize(text)


def extract_keywords(text: str, top_k: int = 5) -> List[str]:
    """便捷函数：提取关键词"""
    tokenizer = JiebaTokenizer()
    return tokenizer.extract_keywords(text, top_k)


def create_bm25_retriever(documents: List[str], k1: float = 1.5, b: float = 0.75):
    """便捷函数：创建 BM25 检索器"""
    return BM25WithJieba(documents, k1, b)
