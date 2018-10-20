# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

import MySQLdb
from MySQLdb.cursors import DictCursor
import codecs
import json


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义 json 文件的导出
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调用 scrapy 提供的 JsonExporter 导出 json 文件
    def __init__(self):
        self.file = open("articleExporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 同步机制 较慢 爬虫的数据远远快于数据插入速度
    def __init__(self):
        # 以下需要修改为自己的配置 host user passwd dbname charset
        self.conn = MySQLdb.connect("127.0.0.1", "root", "root", "article_spider", charset="utf8mb4", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into t_jobbole_article(title, create_date, url, url_object_id, front_image_url, 
            front_image_path, praise_nums, comment_nums, fav_nums, content, tags) 
            values 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"],
                                         item["create_date"],
                                         item["url"],
                                         item["url_object_id"],
                                         item["front_image_url"],
                                         item["front_image_path"],
                                         item["praise_nums"],
                                         item["comment_nums"],
                                         item["fav_nums"],
                                         item["content"],
                                         item["tags"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    # 异步机制
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # scrapy 会先调用这个方法 from_settings
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset="utf8mb4",
            cursorclass=DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用 twisted 将 mysql 插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        # 处理异步插入的异常
        # TODO 后期加入系统错误日志
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
              insert into t_jobbole_article(title, create_date, url, url_object_id, front_image_url, 
              front_image_path, praise_nums, comment_nums, fav_nums, content, tags) 
              values 
              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          """
        cursor.execute(insert_sql, (item["title"],
                                    item["create_date"],
                                    item["url"],
                                    item["url_object_id"],
                                    item["front_image_url"],
                                    item["front_image_path"],
                                    item["praise_nums"],
                                    item["comment_nums"],
                                    item["fav_nums"],
                                    item["content"],
                                    item["tags"]))


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        # 路径存在 results 里面
        if "front_image_url" in item:
            for ok, value in results:
                front_image_path = value["path"]
            item["front_image_path"] = front_image_path

        return item
