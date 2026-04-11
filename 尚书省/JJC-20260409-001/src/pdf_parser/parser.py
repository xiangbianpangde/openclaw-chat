"""
PDF 解析引擎
"""

import fitz  # PyMuPDF
import pdfplumber
from loguru import logger
from typing import Dict, List, Optional, Generator
import os

from config.settings import settings


class PDFParseError(Exception):
    """PDF 解析异常"""
    pass


class FileTooLargeError(PDFParseError):
    """文件过大异常"""
    pass


class PDFParser:
    """PDF 解析器"""
    
    def __init__(self):
        self.max_file_size = settings.PDF_MAX_FILE_SIZE_MB * 1024 * 1024
        self.max_page_count = settings.PDF_MAX_PAGE_COUNT
        self.enable_chunking = settings.PDF_ENABLE_CHUNKING
        self.chunk_size = settings.PDF_CHUNK_SIZE_PAGES
    
    def parse(self, file_path: str) -> Dict:
        """
        解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            解析结果字典
        """
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            if self.enable_chunking:
                logger.warning(f"文件 {file_path} 超过限制，启用分块解析")
                return self._parse_chunked(file_path)
            else:
                raise FileTooLargeError(
                    f"文件大小 {file_size / 1024 / 1024:.2f}MB 超过上限 {self.max_file_size / 1024 / 1024:.2f}MB"
                )
        
        return self._parse_normal(file_path)
    
    def _parse_normal(self, file_path: str) -> Dict:
        """正常解析 PDF"""
        logger.info(f"解析 PDF: {file_path}")
        
        doc = fitz.open(file_path)
        
        # 检查页数
        if len(doc) > self.max_page_count:
            logger.warning(f"文件页数 {len(doc)} 超过建议值 {self.max_page_count}")
        
        results = {
            "file_path": file_path,
            "total_pages": len(doc),
            "pages": [],
            "tables": [],
            "text": ""
        }
        
        try:
            for page_num in range(len(doc)):
                page_result = self._parse_page(doc, page_num)
                results["pages"].append(page_result)
                results["text"] += page_result.get("text", "")
            
            logger.info(f"PDF 解析完成：{file_path}, 共 {len(doc)} 页")
            
        finally:
            doc.close()
        
        return results
    
    def _parse_chunked(self, file_path: str) -> Dict:
        """分块解析大 PDF"""
        logger.info(f"分块解析 PDF: {file_path}")
        
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        all_results = {
            "file_path": file_path,
            "total_pages": total_pages,
            "chunks": [],
            "text": ""
        }
        
        try:
            for start_page in range(0, total_pages, self.chunk_size):
                end_page = min(start_page + self.chunk_size, total_pages)
                
                chunk_result = self._parse_page_range(doc, start_page, end_page)
                all_results["chunks"].append({
                    "start_page": start_page,
                    "end_page": end_page,
                    "result": chunk_result
                })
                all_results["text"] += chunk_result.get("text", "")
                
                # 保存检查点
                self._save_checkpoint(file_path, end_page)
                logger.info(f"完成分块 {start_page}-{end_page}/{total_pages}")
            
        finally:
            doc.close()
        
        return all_results
    
    def _parse_page(self, doc: fitz.Document, page_num: int) -> Dict:
        """解析单页"""
        page = doc[page_num]
        
        # 提取文本
        text = page.get_text()
        
        # 提取表格
        tables = self._extract_tables(page, page_num)
        
        return {
            "page_num": page_num,
            "text": text,
            "tables": tables,
            "width": page.rect.width,
            "height": page.rect.height
        }
    
    def _parse_page_range(self, doc: fitz.Document, start_page: int, end_page: int) -> Dict:
        """解析页面范围"""
        results = {
            "start_page": start_page,
            "end_page": end_page,
            "pages": [],
            "text": "",
            "tables": []
        }
        
        for page_num in range(start_page, end_page):
            page_result = self._parse_page(doc, page_num)
            results["pages"].append(page_result)
            results["text"] += page_result.get("text", "")
            results["tables"].extend(page_result.get("tables", []))
        
        return results
    
    def _extract_tables(self, page: fitz.Page, page_num: int) -> List[Dict]:
        """提取页面中的表格"""
        tables = []
        
        try:
            # 使用 PyMuPDF 原生表格提取 API
            found_tables = page.find_tables()
            
            if found_tables and found_tables.tables:
                for table in found_tables.tables:
                    try:
                        table_data = table.extract()
                        if table_data:
                            tables.append({
                                "page_num": page_num,
                                "data": table_data,
                                "rows": len(table_data),
                                "cols": len(table_data[0]) if table_data else 0
                            })
                    except Exception as e:
                        logger.warning(f"单个表格提取失败，页码 {page_num}: {e}")
                        
        except Exception as e:
            logger.warning(f"表格提取失败，页码 {page_num}: {e}")
        
        return tables
    
    def _save_checkpoint(self, file_path: str, completed_pages: int):
        """保存解析检查点"""
        # TODO: 保存到数据库或文件系统
        logger.debug(f"保存检查点：{file_path}, 已完成 {completed_pages} 页")
    
    def parse_streaming(self, file_path: str) -> Generator[Dict, None, None]:
        """
        流式解析 PDF（节省内存）
        
        Yields:
            每页的解析结果
        """
        doc = fitz.open(file_path)
        
        try:
            for page_num in range(len(doc)):
                page_result = self._parse_page(doc, page_num)
                yield page_result
                
                # 显式释放内存
                del page_result
        finally:
            doc.close()


# 全局解析器实例
parser = PDFParser()


def parse_pdf(file_path: str) -> Dict:
    """便捷函数：解析 PDF"""
    return parser.parse(file_path)


def parse_pdf_streaming(file_path: str) -> Generator[Dict, None, None]:
    """便捷函数：流式解析 PDF"""
    return parser.parse_streaming(file_path)
