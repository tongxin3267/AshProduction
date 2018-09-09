# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     AshProduction enum_data
   Description :
   Author :       LateautunmLin
   date：          2018/9/9
-------------------------------------------------
   Change Activity:
                   2018/9/9:
-------------------------------------------------
"""
__author__ = 'LateautunmLin'

from typing import List,Dict
import aiohttp
EnumTypes = List[str]
Data = Dict[str,str]
EnumDatas = List[Data]

async def get_enum_data(enum_types:EnumTypes) -> EnumDatas:
    data = {}
    headers = {
        "Cookie":"lastCity=101010100; JSESSIONID=""; __g=-; __l=r=https%3A%2F%2Fwww.zhipin.com%2F&l=%2Fwww.zhipin.com%2Fjob_detail%2F%3Fquery%3D%26scity%3D101010100%26industry%3D%26position%3D; __a=73876760.1536460137.1536460137.1536460372.3.2.2.3; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fjob_detail%2F%3Fquery%3D%26scity%3D101010100%26industry%3D%26position%3D100101; __c=1536460372",
        "Host": "www.zhipin.com",
        "Referer": "www.zhipin.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
    }
    data_url_map = {
        "oldindustry":"https://www.zhipin.com/common/data/oldindustry.json",
        "position":"https://www.zhipin.com/common/data/city.json",
        "city":"https://www.zhipin.com/common/data/position.json"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        for enum_type in enum_types:
            async with session.get(data_url_map[enum_type]) as response:
                data[enum_type] = await response.json()
    return data



