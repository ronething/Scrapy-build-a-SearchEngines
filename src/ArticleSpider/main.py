# -*- coding:utf-8 _*-  
""" 
@author: ronething 
@file: main.py 
@time: 2018/10/19
@github: github.com/ronething 

Less is more.
"""

from scrapy.cmdline import execute

import sys
import os

# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(__file__))
execute(["scrapy", "crawl", "jobbole"])