"""
跨页表格合并模块
支持续表标记检测、表头一致性判断、跨页合并
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import re


@dataclass
class TableFragment:
    """表格片段"""
    page_num: int
    rows: List[List[str]]
    headers: List[str]
    has_continuation_marker: bool = False
    continuation_marker: str = ""
    
    def to_dict(self) -> dict:
        return {
            "page_num": self.page_num,
            "rows": self.rows,
            "headers": self.headers,
            "has_continuation_marker": self.has_continuation_marker,
            "continuation_marker": self.continuation_marker
        }


class CrossPageTableMerger:
    """跨页表格合并器"""
    
    def __init__(self):
        # 跨页标记关键词
        self.continuation_keywords = [
            '续表', '接上页', 'continued', '续',
            '续表（续）', '(续)', '续表 1', '续表 2'
        ]
    
    def merge_tables(self, fragments: List[TableFragment]) -> List[Dict]:
        """
        合并跨页表格
        
        :param fragments: 表格片段列表（按页码排序）
        :return: 合并后的完整表格列表
        """
        if not fragments:
            return []
        
        merged_tables = []
        current_table = None
        
        for frag in fragments:
            if current_table is None:
                # 开始新表格
                current_table = {
                    'headers': frag.headers,
                    'rows': [row[:] for row in frag.rows],  # 深拷贝
                    'start_page': frag.page_num,
                    'end_page': frag.page_num,
                    'total_rows': len(frag.rows)
                }
            else:
                # 判断是否延续当前表格
                if self._is_continuation(current_table, frag):
                    # 合并（跳过重复的表头）
                    rows_to_add = self._remove_duplicate_headers(frag.rows, current_table['headers'])
                    current_table['rows'].extend(rows_to_add)
                    current_table['end_page'] = frag.page_num
                    current_table['total_rows'] += len(rows_to_add)
                    
                    logger.debug(f"合并第{frag.page_num}页表格，当前总行数：{current_table['total_rows']}")
                else:
                    # 保存当前表格，开始新表格
                    merged_tables.append(current_table)
                    current_table = {
                        'headers': frag.headers,
                        'rows': [row[:] for row in frag.rows],
                        'start_page': frag.page_num,
                        'end_page': frag.page_num,
                        'total_rows': len(frag.rows)
                    }
        
        # 保存最后一个表格
        if current_table:
            merged_tables.append(current_table)
        
        logger.info(f"跨页表格合并完成：{len(fragments)}个片段 → {len(merged_tables)}个完整表格")
        
        return merged_tables
    
    def _is_continuation(self, current_table: Dict, frag: TableFragment) -> bool:
        """
        判断是否为表格延续
        
        :param current_table: 当前表格
        :param frag: 新片段
        :return: 是否延续
        """
        # 1. 检查续表标记
        if frag.has_continuation_marker:
            logger.debug(f"第{frag.page_num}页检测到续表标记")
            return True
        
        # 2. 检查表头是否一致
        if self._headers_match(current_table['headers'], frag.headers):
            logger.debug(f"第{frag.page_num}页表头一致")
            return True
        
        # 3. 检查列数是否一致
        if self._column_count_match(current_table['rows'], frag.rows):
            logger.debug(f"第{frag.page_num}页列数一致")
            return True
        
        return False
    
    def _headers_match(self, headers1: List[str], headers2: List[str]) -> bool:
        """
        检查表头是否匹配
        
        :param headers1: 表头 1
        :param headers2: 表头 2
        :return: 是否匹配
        """
        if not headers1 or not headers2:
            return False
        
        if len(headers1) != len(headers2):
            return False
        
        # 计算相似度
        matches = sum(1 for h1, h2 in zip(headers1, headers2) if self._normalize_text(h1) == self._normalize_text(h2))
        similarity = matches / len(headers1)
        
        return similarity >= 0.8  # 80% 相似度阈值
    
    def _column_count_match(self, rows1: List[List[str]], rows2: List[List[str]]) -> bool:
        """
        检查列数是否匹配
        
        :param rows1: 表格 1 的行
        :param rows2: 表格 2 的行
        :return: 是否匹配
        """
        if not rows1 or not rows2:
            return False
        
        # 获取典型列数（取第一行）
        cols1 = len(rows1[0]) if rows1[0] else 0
        cols2 = len(rows2[0]) if rows2[0] else 0
        
        # 允许 1 列的误差（可能有无内容的空列）
        return abs(cols1 - cols2) <= 1
    
    def _remove_duplicate_headers(self, rows: List[List[str]], headers: List[str]) -> List[List[str]]:
        """
        移除重复的表头行
        
        :param rows: 原始行
        :param headers: 表头
        :return: 移除表头后的行
        """
        if not rows or not headers:
            return rows
        
        # 检查第一行是否为表头
        if self._headers_match(headers, rows[0]):
            return rows[1:]
        
        return rows
    
    def _normalize_text(self, text: str) -> str:
        """
        标准化文本（去除空格、标点）
        
        :param text: 原始文本
        :return: 标准化文本
        """
        # 去除空格和常见标点
        text = re.sub(r'[\s,.,,,;,!,?,:]+', '', text)
        return text.strip()
    
    def detect_continuation_marker(self, text: str) -> Tuple[bool, str]:
        """
        检测跨页标记
        
        :param text: 页面文本
        :return: (是否检测到，标记内容)
        """
        for keyword in self.continuation_keywords:
            if keyword in text:
                logger.debug(f"检测到跨页标记：{keyword}")
                return True, keyword
        
        return False, ""


class TableOCREngine:
    """表格 OCR 引擎"""
    
    def __init__(self, use_ocr: bool = True):
        self.use_ocr = use_ocr
        
        if use_ocr:
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
                logger.info("PaddleOCR 引擎初始化成功")
            except Exception as e:
                logger.warning(f"PaddleOCR 初始化失败：{e}，将使用备用方案")
                self.use_ocr = False
                self.ocr = None
    
    def extract_table_from_image(self, image_data) -> Dict:
        """
        从图片中提取表格
        
        :param image_data: 图片数据（numpy 数组或 bytes）
        :return: 表格数据
        """
        if not self.use_ocr or self.ocr is None:
            return {'rows': [], 'headers': [], 'confidence': 0.0}
        
        try:
            import cv2
            import numpy as np
            
            # 确保是 numpy 数组
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = image_data
            
            # OCR 识别
            result = self.ocr.ocr(img, cls=True)
            
            # 解析 OCR 结果
            rows = []
            current_row = []
            last_y = None
            
            if result and result[0]:
                for block in result[0]:
                    bbox, (text, confidence) = block
                    x, y = bbox[0][0], bbox[0][1]
                    
                    # 简单的行分组（基于 y 坐标）
                    if last_y is not None and abs(y - last_y) > 20:
                        if current_row:
                            rows.append(current_row)
                            current_row = []
                    
                    current_row.append(text)
                    last_y = y
                
                if current_row:
                    rows.append(current_row)
            
            # 假设第一行为表头
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            return {
                'rows': data_rows,
                'headers': headers,
                'confidence': sum(block[1][1] for block in result[0]) / len(result[0]) if result and result[0] else 0.0
            }
            
        except Exception as e:
            logger.error(f"表格 OCR 识别失败：{e}")
            return {'rows': [], 'headers': [], 'confidence': 0.0}


# 全局实例
table_merger = CrossPageTableMerger()
table_ocr = TableOCREngine(use_ocr=True)


def merge_cross_page_tables(fragments: List[TableFragment]) -> List[Dict]:
    """便捷函数：合并跨页表格"""
    return table_merger.merge_tables(fragments)


def extract_table_from_image(image_data) -> Dict:
    """便捷函数：从图片提取表格"""
    return table_ocr.extract_table_from_image(image_data)
