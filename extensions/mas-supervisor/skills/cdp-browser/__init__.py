"""
CDP Browser Skill

Chrome DevTools Protocol 浏览器自动化技能
提供 DOM 快照、截图、导航、交互等能力
"""

from .cdp_client import CDPSession
from .dom_analyzer import DOMAnalyzer
from .screenshot import ScreenshotCapture
from .navigator import Navigator
from .interactor import Interactor
from .console_logger import ConsoleLogger

__version__ = "1.0.0"
__author__ = "MAS Supervisor"

__all__ = [
    "CDPSession",
    "DOMAnalyzer",
    "ScreenshotCapture",
    "Navigator",
    "Interactor",
    "ConsoleLogger",
]
