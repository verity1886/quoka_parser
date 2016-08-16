# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class QuokaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Boersen_ID = Field()
    OBID = Field()
    erzeugt_am = Field()
    Anbieter_ID = Field()
    Stadt = Field()
    PLZ = Field()
    Ueberschrift = Field()
    Beschreibung = Field()
    Kaufpreis = Field()
    Monat = Field()
    url = Field()
    Telefon = Field()
    Erstellungsdatum = Field()
    Gewerblich = Field()