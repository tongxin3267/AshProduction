import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from zhihu.corpus import ZhihuCrawler
@pytest.mark.asyncio
async def test_coro(event_loop):
    t = ZhihuCrawler()
    await t.run()