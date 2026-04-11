"""
PDF 管理接口
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import os
import hashlib

from config.settings import settings

router = APIRouter()


def calculate_file_hash(file_path: str) -> str:
    """计算文件 SHA256 哈希"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    company_code: str = None,
    report_year: int = None,
    report_type: str = None
):
    """上传 PDF 文件"""
    
    # 检查文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.PDF_MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 {settings.PDF_MAX_FILE_SIZE_MB}MB"
        )
    
    # 保存文件
    upload_dir = f"./data/raw/{company_code or 'unknown'}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 计算文件哈希
    file_hash = calculate_file_hash(file_path)
    
    return {
        "message": "上传成功",
        "file_path": file_path,
        "file_size": file_size,
        "file_hash": file_hash,
        "company_code": company_code,
        "report_year": report_year
    }


@router.post("/batch-upload")
async def batch_upload_pdfs(files: List[UploadFile] = File(...)):
    """批量上传 PDF 文件"""
    
    results = []
    for file in files:
        try:
            content = await file.read()
            file_size = len(content)
            
            if file_size > settings.PDF_MAX_FILE_SIZE_MB * 1024 * 1024:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": f"文件大小超过限制"
                })
                continue
            
            # 保存文件
            upload_dir = "./data/raw/batch"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = f"{upload_dir}/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(content)
            
            file_hash = calculate_file_hash(file_path)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "success": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


@router.get("/parse-status/{task_id}")
async def get_parse_status(task_id: str):
    """查询解析任务状态"""
    # TODO: 从数据库查询任务状态
    return {
        "task_id": task_id,
        "status": "pending",
        "total_files": 0,
        "completed_files": 0,
        "failed_files": 0,
        "progress": 0.0
    }
