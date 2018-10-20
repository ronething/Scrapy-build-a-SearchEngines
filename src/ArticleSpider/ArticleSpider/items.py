# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re

from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    # 自定义 itemloader
    # TakeFirst 默认取 list 的第一个元素
    default_output_processor = TakeFirst()


# 格式化日期
def date_convert(value):
    # 正则没有办法匹配 \r\n 吗？ 记得查询一下 设置 re.DOTALL 即可
    regex_str = ".*?([12]{1}[0-9]{3}/[01]{0,1}[0-9]{1}/[0-3]{0,1}[0-9]{1}).*"
    match_obj = re.match(regex_str, value, re.DOTALL)
    if match_obj:
        try:
            create_date = datetime.datetime.strptime(match_obj.group(1), "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
    else:
        create_date = datetime.datetime.now().date()

    return create_date


# 获取 点赞数 收藏数 评论数
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


# 格式化 tags_list
def remove_comment_tags(value):
    value = value.strip()
    if not value.endswith("评论"):
        return value
    else:
        return


# 不做任何修改
def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):

    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )


