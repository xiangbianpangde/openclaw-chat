"""
文档分块模块
实现智能文档分块策略
"""

from typing import List, Dict, Any, Optional
import re


class DocumentChunker:
    """文档分块器"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        初始化分块器
        
        Args:
            chunk_size: 块大小（token 数）
            chunk_overlap: 块重叠大小
            min_chunk_size: 最小块大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str) -> List[str]:
        """
        分块文档
        
        Args:
            text: 文档文本
        
        Returns:
            分块列表
        """
        # 1. 按段落分割
        paragraphs = self._split_by_paragraph(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)
            
            if current_length + para_tokens > self.chunk_size:
                # 保存当前块
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    if len(chunk_text) >= self.min_chunk_size:
                        chunks.append(chunk_text)
                
                # 开始新块，保留重叠
                if self.chunk_overlap > 0 and current_chunk:
                    # 保留最后 1-2 个段落作为重叠
                    overlap_start = max(0, len(current_chunk) - 2)
                    overlap_text = '\n'.join(current_chunk[overlap_start:])
                    current_chunk = [overlap_text, para]
                    current_length = self._estimate_tokens(overlap_text) + para_tokens
                else:
                    current_chunk = [para]
                    current_length = para_tokens
            else:
                current_chunk.append(para)
                current_length += para_tokens
        
        # 保存最后一个块
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
        
        return chunks
    
    def _split_by_paragraph(self, text: str) -> List[str]:
        """按段落分割"""
        # 按双换行符分割
        paragraphs = text.split('\n\n')
        
        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _estimate_tokens(self, text: str) -> int:
        """估算 token 数（中文字符数/4）"""
        # 简单估算：中文字符数 / 4
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return (chinese_chars + english_words) // 4 + 1
    
    def chunk_with_metadata(
        self,
        text: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        分块文档（带元数据）
        
        Args:
            text: 文档文本
            doc_id: 文档 ID
            metadata: 元数据
        
        Returns:
            分块列表（带元数据）
        """
        chunks = self.chunk(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'doc_id': doc_id,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk)
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            result.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return result


class SentenceChunker(DocumentChunker):
    """句子级分块器"""
    
    def _split_by_paragraph(self, text: str) -> List[str]:
        """按句子分割"""
        # 按中文句号、问号、感叹号分割
        sentences = re.split(r'[.!?!.!?]', text)
        
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences


# 便捷函数
def chunk_document(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """便捷函数：分块文档"""
    chunker = DocumentChunker(chunk_size, chunk_overlap)
    return chunker.chunk(text)


def chunk_with_metadata(
    text: str,
    doc_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 512,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """便捷函数：分块文档（带元数据）"""
    chunker = DocumentChunker(chunk_size, chunk_overlap)
    return chunker.chunk_with_metadata(text, doc_id, metadata)
