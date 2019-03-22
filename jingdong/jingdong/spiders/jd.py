# -*- coding: utf-8 -*-
import scrapy
import urllib.request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from jingdong.items import JingdongItem
import re #本次采用正则

class JdSpider(CrawlSpider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = ['http://www.jd.com/']

    rules = (
        Rule(LinkExtractor(allow=''), callback='parse_item', follow=True),
    )   #链接提取规则：不设限，整站爬

    def parse_item(self, response):
        try:
            i = JingdongItem()
            #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
            #i['name'] = response.xpath('//div[@id="name"]').extract()
            #i['description'] = response.xpath('//div[@id="description"]').extract()

            thisurl=response.url #回调当前页面，判断页面类型
            pat="item.jd.com/(.*?).html" #商品页面特征
            x=re.search(pat,thisurl)  #判断是否商品页面
            if(x):
                thisid=re.compile(pat).findall(thisurl)[0] #为列表，通过0下标取出
                print("正在爬取商品号："+thisid)

                #提取不用抓包的信息：商品、店铺及店铺链接
                title=response.xpath("//html/head/title/text()").extract()
                shop=response.xpath("//a/[@clstag='shangpin|keycount|product|dianpuname1']/text()").extract()
                shoplink=response.xpath("//a/[@clstag='shangpin|keycount|product|dianpuname1']/@href").extract()

                #抓包分析找到价格及评论链接
                priceurl="http://p.3.cn/prices/mgets?callback=jQuery3480115&type=1&area=1&pdtk=&pduid=579773820&pdpin=&pin=null&pdbp=0&skuIds=J_"+str(thisid)
                commenturl="http://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv9114&productId="+str(thisid)+"&score=0&sortType=5&page=0&pageSize=10  "

                #爬取价格及好评率
                pricedata=urllib.request.urlopen(priceurl).read().decode("utf-8","ignore")
                commentdata=urllib.request.urlopen(commenturl).read().decode("utf-8", "ignore")
                pricepat='"p":"(.*?)"'
                commentpat='"goodRateShow":(.*?),'

                #正则提取对应信息
                price=re.compile(pricepat).findall(pricedata)
                comment=re.compile(commentpat).findall(commentdata)

                #当且仅当以下数值不为空时，才进行处理
                if(len(title) and len(shop) and len(shoplink) and len(comment)):
                #此处可导入数据库
                    def parse(self, response):
                        item = JingdongItem()
                        item['title'] = title
                        item['shop'] = shop
                        item['price'] = price
                        item['comment'] = comment
                        yield item
                else:
                    pass
            else:
                pass

            return i

        except Exception as e:
            print(e)

