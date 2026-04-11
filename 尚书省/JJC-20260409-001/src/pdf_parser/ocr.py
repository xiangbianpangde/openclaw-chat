"""
OCR 识别模块
使用 PaddleOCR 进行扫描版 PDF 文字识别
"""

import os
from typing import Dict, List, Optional, Tuple
from loguru import logger

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.warning("PaddleOCR 未安装，OCR 功能将不可用")


class OCRRecognitionError(Exception):
    """OCR 识别异常"""
    pass


class PDFTextExtractor:
    """PDF 文本提取器（支持 OCR）"""
    
    def __init__(self, use_ocr: bool = False, lang: str = 'ch'):
        """
        初始化 PDF 文本提取器
        
        Args:
            use_ocr: 是否启用 OCR
            lang: OCR 语言（'ch' 中文，'en' 英文）
        """
        self.use_ocr = use_ocr
        self.lang = lang
        self.ocr_engine = None
        
        if use_ocr and PADDLEOCR_AVAILABLE:
            self._init_ocr_engine()
    
    def _init_ocr_engine(self):
        """初始化 PaddleOCR 引擎"""
        try:
            # PaddleOCR v2.x API
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang=self.lang,
                use_gpu=False,
                show_log=False
            )
            logger.info("PaddleOCR v2.9.1 引擎初始化成功")
        except Exception as e:
            logger.error(f"PaddleOCR 初始化失败：{e}")
            self.use_ocr = False
    
    def extract_text(self, pdf_path: str, page_num: int = 0) -> Dict:
        """
        提取 PDF 页面文本
        
        Args:
            pdf_path: PDF 文件路径
            page_num: 页码（0-based）
            
        Returns:
            {
                "text": str,  # 提取的文本
                "has_text_layer": bool,  # 是否有文本层
                "use_ocr": bool,  # 是否使用了 OCR
                "confidence": float,  # 置信度（OCR 时）
                "boxes": list  # 文本框位置（OCR 时）
            }
        """
        import fitz  # PyMuPDF
        
        result = {
            "text": "",
            "has_text_layer": False,
            "use_ocr": False,
            "confidence": 1.0,
            "boxes": []
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            if page_num >= len(doc):
                logger.warning(f"页码 {page_num} 超出范围，文件共 {len(doc)} 页")
                doc.close()
                return result
            
            page = doc[page_num]
            
            # 1. 尝试提取文本层
            text = page.get_text().strip()
            
            if text and len(text) > 50:  # 有足够的文本
                result["text"] = text
                result["has_text_layer"] = True
                logger.debug(f"页面 {page_num} 有文本层，提取 {len(text)} 字符")
            else:
                # 2. 文本层不足，使用 OCR
                if self.use_ocr and self.ocr_engine:
                    logger.info(f"页面 {page_num} 文本层不足，启用 OCR")
                    ocr_result = self._ocr_page(page)
                    result["text"] = ocr_result["text"]
                    result["use_ocr"] = True
                    result["confidence"] = ocr_result.get("confidence", 0.0)
                    result["boxes"] = ocr_result.get("boxes", [])
                else:
                    logger.warning(f"页面 {page_num} 无文本层且 OCR 未启用")
                    result["text"] = text  # 返回少量文本
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PDF 文本提取失败：{pdf_path}, 页码 {page_num}, 错误：{e}")
            raise OCRRecognitionError(f"PDF 文本提取失败：{e}")
        
        return result
    
    def _ocr_page(self, page) -> Dict:
        """
        对单页进行 OCR 识别
        
        Args:
            page: PyMuPDF Page 对象
            
        Returns:
            {
                "text": str,
                "confidence": float,
                "boxes": list
            }
        """
        import cv2
        import numpy as np
        
        try:
            # 将 PDF 页面转换为图片
            mat = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x 缩放提高识别率
            img_data = mat.tobytes("png")
            
            # 转换为 numpy 数组
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise OCRRecognitionError("图片解码失败")
            
            # 执行 OCR
            ocr_result = self.ocr_engine.ocr(img, cls=True)
            
            # 解析 OCR 结果
            text_lines = []
            boxes = []
            confidences = []
            
            if ocr_result and ocr_result[0]:
                for line in ocr_result[0]:
                    if line:
                        # line[0]: 文本框坐标，line[1]: (文本，置信度)
                        box = line[0]
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        text_lines.append(text)
                        boxes.append(box)
                        confidences.append(confidence)
            
            # 计算平均置信度
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "text": "\n".join(text_lines),
                "confidence": avg_confidence,
                "boxes": boxes
            }
            
        except Exception as e:
            logger.error(f"OCR 识别失败：{e}")
            return {
                "text": "",
                "confidence": 0.0,
                "boxes": []
            }
    
    def extract_text_all_pages(self, pdf_path: str) -> List[Dict]:
        """
        提取 PDF 所有页面文本
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            每页的提取结果列表
        """
        import fitz
        
        results = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                result = self.extract_text(pdf_path, page_num)
                result["page_num"] = page_num
                results.append(result)
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PDF 全页提取失败：{pdf_path}, 错误：{e}")
            raise OCRRecognitionError(f"PDF 全页提取失败：{e}")
        
        return results
    
    def detect_pdf_type(self, pdf_path: str) -> Dict:
        """
        检测 PDF 类型（扫描版/标准版）
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            {
                "is_scanned": bool,  # 是否为扫描版
                "has_text_layer": bool,
                "total_pages": int,
                "text_layer_pages": int,
                "scanned_pages": int
            }
        """
        import fitz
        
        result = {
            "is_scanned": False,
            "has_text_layer": True,
            "total_pages": 0,
            "text_layer_pages": 0,
            "scanned_pages": 0
        }
        
        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            
            text_layer_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()
                
                if text and len(text) > 50:
                    text_layer_count += 1
            
            doc.close()
            
            result["text_layer_pages"] = text_layer_count
            result["scanned_pages"] = len(doc) - text_layer_count
            
            # 如果超过 50% 的页面无文本层，判定为扫描版
            if text_layer_count < len(doc) * 0.5:
                result["is_scanned"] = True
                result["has_text_layer"] = False
            
        except Exception as e:
            logger.error(f"PDF 类型检测失败：{pdf_path}, 错误：{e}")
        
        return result


# 全局提取器实例
text_extractor = PDFTextExtractor(use_ocr=True)


def extract_pdf_text(pdf_path: str, page_num: int = 0) -> Dict:
    """便捷函数：提取 PDF 文本"""
    return text_extractor.extract_text(pdf_path, page_num)


def extract_pdf_text_all_pages(pdf_path: str) -> List[Dict]:
    """便捷函数：提取 PDF 所有页面文本"""
    return text_extractor.extract_text_all_pages(pdf_path)


def detect_pdf_type(pdf_path: str) -> Dict:
    """便捷函数：检测 PDF 类型"""
    return text_extractor.detect_pdf_type(pdf_path)
