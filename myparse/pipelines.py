import MySQLdb

class MyparsePipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host="localhost",
                                    user="root",     
                                    passwd="root",
                                    db="quoka")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):  
        try:
            self.cursor.execute("""INSERT INTO quoka (OBID, Boersen_ID, erzugt_am, Anbieter_ID, Stadt, PLZ, Ueberschrift,
                                Beschreibung, Kaufpreis, Monat, url, Telefon, Erstellungsdatum, Gewerblich)
                                VALUES (%s, %s)""", 
                               (item['OBID'], item['Boersen_ID'], item["erzugt_am"],
                               item['Anbieter_ID'], item['Stadt'], item["PLZ"],
                               item['Ueberschrift'], item['Beschreibung'], item["Kaufpreis"],
                               item['Monat'], item['url'], item["Telefon"],
                               item['Erstellungsdatum'], item['Gewerblich']))

            self.conn.commit()
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        return item