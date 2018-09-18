# -*- coding: utf-8 -*-
'''
------------------------------------------------------------
File Name: test_zhihu.py
Description : 
Project: test
Last Modified: Monday, 17th September 2018 4:45:42 pm
-------------------------------------------------------------
'''

import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from zhihu.corpus import ZhihuCrawler
@pytest.mark.asyncio
async def test_coro(event_loop):
    t = ZhihuCrawler()
    await t.run()