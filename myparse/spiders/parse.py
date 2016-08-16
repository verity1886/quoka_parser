# -*- coding: utf-8 -*-

import re

from datetime import datetime, timedelta
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from myparse.items import QuokaItem

class QuokaSpider(Spider):
    name = "quoka"
    allowed_domains = ["www.quoka.de"]
    start_urls = ["http://www.quoka.de/immobilien/bueros-gewerbeflaechen/"]
    
    def parse(self, response):
        #get all links to object
        page_links = response.xpath(".//*[@id='ResultListData']/ul/li/div[2]/a/@href").extract()
        for i,link in enumerate(page_links):
            yield Request("http://www.quoka.de" + link, callback=self.preParseItems)
        if response.meta and "page" in response.meta:
            if response.meta["page"] <= 20: #response.meta["page_amount"]:
                if response.meta["page"] <= 10:
                    yield Request("http://www.quoka.de/kleinanzeigen/cat_27_2710_ct_0_page_"+ str(int(response.meta["page"])+1) +".html",
                                  callback=self.parse, meta={"page" : int(response.meta["page"])+1, 
                                                             "page_amount" : response.meta["page_amount"]})
                else:
                    yield Request("http://www.quoka.de/qmca/search/search.html?redirect=0&catid=27_2710&pageNo="+str(int(response.meta["page"])+1),
                                  callback=self.parse, meta={"page" : int(response.meta["page"])+1,
                                                             "page_amount" : response.meta["page_amount"]})
            else:
                yield False
                return
                
        else:
            page_amount = response.xpath("body/div[3]/div[2]/div[1]/main/div[8]/div/div/div/ul/li[1]/a/strong[2]/text()").extract()[0]
            yield Request("http://www.quoka.de/kleinanzeigen/cat_27_2710_ct_0_page_2.html",
                          callback=self.parse, meta={"page" : 2, "page_amount" : int(page_amount)})
    
    
    def preParseItems(self, response):
        try:
            ajax = response.xpath(".//*[@id='Handy1']/a/@onclick").extract()[0]
            match_link = re.search(r"(?P<link>(\/ajax\/detail\/displayphonenumber.php\?){1,1}[\w\d\s=\-\&\+]+)", ajax)
            if match_link:
                return Request("http://www.quoka.de" + match_link.group("link"),
                       callback=self.parseItems, meta={"respPage" : response })
            else:
                return self.parseItems(response)
        except IndexError:
            return self.parseItems(response)
        
    
    def parseItems(self, response):
        if "respPage" in response.meta:
            respPage = response.meta["respPage"]
            tel = response.xpath("body/span/text()").extract()[0]
        else:
            respPage = response
            tel = ""
        item = QuokaItem()
        item["Boersen_ID"] = 21
        item["OBID"] = int(respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[3]/div[2]/div[2]/strong[1]/text()").extract()[0].strip())
        item["erzeugt_am"] = datetime.now()
        item["Anbieter_ID"] = ""
        item["Stadt"] = respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[3]/div[2]/div[1]/strong/span/a/span/text()").extract()[0]
        item["PLZ"] = respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[3]/div[2]/div[1]/strong/span/span/span[2]/text()").extract()[0]
        item["Ueberschrift"] = str(respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[1]/h1/text()").extract()[0].encode("utf-8"))
        item["Beschreibung"] = str(respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[3]/div[3]/div/text()").extract()[0].encode("utf-8"))
        try:
            item["Kaufpreis"]  = respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[2]/strong/span/text()").extract()[0]
        except IndexError:
            item["Kaufpreis"] = ""
        item["Monat"] = datetime.now().strftime('%m') # current month in number format | %b to string (Aug)
        item["url"] = respPage.url
        item["Telefon"] = tel
        obj_creating_date = respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[3]/div[2]/div[2]/text()[7]").extract()[0]
        item["Erstellungsdatum"] = self.getObjCreatingDate(obj_creating_date)
        is_gewerblich = respPage.xpath("body/div[3]/div[2]/div[1]/main/div[4]/div/div[4]/div[1]/div/div[2]/text()").extract()[0]
        item["Gewerblich"] = self.isGewerblich(is_gewerblich)
        yield item
            
        
    def getObjCreatingDate(self, date):
        if re.search(r"(Gestern)", date):
            return datetime.now() - timedelta(days=1)
        elif re.search(r"(Heute)", date):
            return datetime.now().date()
        else:
            date
        
    def isGewerblich(self, string):
        if re.search("Gewerblicher Inserent", string):
            return 1
        else:
            return 0