# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test test_jianshu
   Description :
   Author :      LateautunmLin 
   date：          2018/9/8
-------------------------------------------------
   Change Activity:
                   2018/9/8:
-------------------------------------------------
"""
__author__ = 'LateautunmLin'
import pytest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from jianshu.productions.add_page_views import JianshuPageView
@pytest.mark.asyncio
async def test_jianshu_add_page_views() -> None:
    d = JianshuPageView()
    # 测试输入用户ID
    await d.run(userId="e9fdf09df277")
    # 测试输入文章ID
    # await d.run(articleId="4a526bc6276b")