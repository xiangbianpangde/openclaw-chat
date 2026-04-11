"""
向量存储模块
使用 ChromaDB 实现向量存储和检索
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import uuid


class VectorStore:
    """向量存储类"""
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "financial_reports"):
        """
        初始化向量存储
        
        Args:
            persist_dir: 持久化目录
            collection_name: 集合名称
        """
        # 创建客户端（持久化配置）
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "财报文档向量库"},
            get_or_create=True
        )
        
        self.persist_dir = persist_dir
        self.collection_name = collection_name
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        添加文档到向量库
        
        Args:
            documents: 文档列表
            embeddings: 向量列表
            ids: 文档 ID 列表（可选，自动生成）
            metadatas: 元数据列表（可选）
        
        Returns:
            添加的文档 ID 列表
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # 添加到集合
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        # 持久化
        self.client.persist()
        
        return ids
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: List[str] = ["documents", "metadatas", "distances"]
    ) -> Dict[str, Any]:
        """
        向量检索
        
        Args:
            query_embeddings: 查询向量列表
            n_results: 返回结果数量
            where: 过滤条件（元数据过滤）
            include: 包含字段
        
        Returns:
            检索结果
        """
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=include
        )
        
        return results
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """
        删除文档
        
        Args:
            ids: 文档 ID 列表
            where: 过滤条件
        """
        self.collection.delete(ids=ids, where=where)
        self.client.persist()
    
    def count(self) -> int:
        """获取文档总数"""
        return self.collection.count()
    
    def reset(self):
        """重置向量库"""
        self.client.reset()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "财报文档向量库"}
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        return {
            "name": self.collection.name,
            "metadata": self.collection.metadata,
            "count": self.count(),
            "persist_dir": self.persist_dir
        }


class ChromaDBManager:
    """ChromaDB 管理器"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        初始化 ChromaDB 管理器
        
        Args:
            persist_dir: 持久化目录
        """
        self.persist_dir = persist_dir
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        self.stores: Dict[str, VectorStore] = {}
    
    def create_store(self, collection_name: str) -> VectorStore:
        """
        创建向量存储
        
        Args:
            collection_name: 集合名称
        
        Returns:
            VectorStore 实例
        """
        store = VectorStore(self.persist_dir, collection_name)
        self.stores[collection_name] = store
        return store
    
    def get_store(self, collection_name: str) -> Optional[VectorStore]:
        """
        获取向量存储
        
        Args:
            collection_name: 集合名称
        
        Returns:
            VectorStore 实例或 None
        """
        if collection_name in self.stores:
            return self.stores[collection_name]
        
        # 尝试从持久化加载
        try:
            store = VectorStore(self.persist_dir, collection_name)
            self.stores[collection_name] = store
            return store
        except Exception:
            return None
    
    def list_collections(self) -> List[str]:
        """列出所有集合"""
        return [col.name for col in self.client.list_collections()]
    
    def delete_collection(self, collection_name: str):
        """删除集合"""
        self.client.delete_collection(collection_name)
        if collection_name in self.stores:
            del self.stores[collection_name]
    
    def persist(self):
        """持久化"""
        self.client.persist()


# 全局实例
_default_store: Optional[VectorStore] = None


def get_default_store(persist_dir: str = "./chroma_db") -> VectorStore:
    """获取默认向量存储"""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore(persist_dir)
    return _default_store


def add_document(
    text: str,
    embedding: List[float],
    doc_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """便捷函数：添加单个文档"""
    store = get_default_store()
    ids = [doc_id] if doc_id else None
    metadatas = [metadata] if metadata else None
    result = store.add_documents([text], [embedding], ids, metadatas)
    return result[0]


def search_documents(
    query_embedding: List[float],
    n_results: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """便捷函数：检索文档"""
    store = get_default_store()
    return store.query([query_embedding], n_results, filters)
