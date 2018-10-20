# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: common.py 
@time: 2018/10/19
@github: github.com/ronething 

Less is more.
"""

import hashlib

"""
    工具类
"""


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print(get_md5("nihao"))