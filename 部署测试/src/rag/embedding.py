"""
Embedding 模型封装模块
支持多种中文 Embedding 模型
"""

from typing import List, Union, Optional
import numpy as np

try:
    from FlagEmbedding import FlagModel
    FLAG_MODEL_AVAILABLE = True
except ImportError:
    FLAG_MODEL_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingModel:
    """Embedding 模型基类"""
    
    def __init__(self, model_name: str, dimension: int = 1024):
        self.model_name = model_name
        self.dimension = dimension
    
    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        raise NotImplementedError
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码"""
        return [self.encode(text) for text in texts]


class BGELargeZH(EmbeddingModel):
    """BGE-Large-ZH-v1.5 模型"""
    
    def __init__(self, model_name: str = 'BAAI/bge-large-zh-v1.5'):
        super().__init__(model_name, dimension=1024)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if FLAG_MODEL_AVAILABLE:
            try:
                self.model = FlagModel(self.model_name, use_fp16=False)
            except Exception as e:
                print(f"Warning: Failed to load FlagModel: {e}")
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Warning: Failed to load SentenceTransformer: {e}")
    
    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        if self.model is None:
            # 返回随机向量作为占位符
            return [0.0] * self.dimension
        
        if FLAG_MODEL_AVAILABLE and hasattr(self.model, 'encode_sentence'):
            embedding = self.model.encode_sentence(text)
        elif hasattr(self.model, 'encode'):
            embedding = self.model.encode(text)
        else:
            return [0.0] * self.dimension
        
        # 转换为列表
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return list(embedding)
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码"""
        if self.model is None:
            return [[0.0] * self.dimension for _ in texts]
        
        if hasattr(self.model, 'encode'):
            embeddings = self.model.encode(texts)
            if isinstance(embeddings, np.ndarray):
                return embeddings.tolist()
            return list(embeddings)
        
        return [self.encode(text) for text in texts]


class M3EBase(EmbeddingModel):
    """M3E-Base 模型"""
    
    def __init__(self, model_name: str = 'moka-ai/m3e-base'):
        super().__init__(model_name, dimension=768)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Warning: Failed to load M3E: {e}")
    
    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        if self.model is None:
            return [0.0] * self.dimension
        
        embedding = self.model.encode(text)
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return list(embedding)


# 模型工厂
def create_embedding_model(model_name: str = 'bge-large-zh-v1.5') -> EmbeddingModel:
    """
    创建 Embedding 模型
    
    Args:
        model_name: 模型名称
    
    Returns:
        EmbeddingModel 实例
    """
    if 'bge-large' in model_name:
        return BGELargeZH(model_name)
    elif 'm3e' in model_name:
        return M3EBase(model_name)
    else:
        # 默认使用 BGE-Large
        return BGELargeZH()


# 全局实例
_default_model: Optional[EmbeddingModel] = None


def get_default_model() -> EmbeddingModel:
    """获取默认 Embedding 模型"""
    global _default_model
    if _default_model is None:
        _default_model = BGELargeZH()
    return _default_model


def encode_text(text: str) -> List[float]:
    """便捷函数：编码文本"""
    model = get_default_model()
    return model.encode(text)


def encode_batch(texts: List[str]) -> List[List[float]]:
    """便捷函数：批量编码"""
    model = get_default_model()
    return model.encode_batch(texts)
