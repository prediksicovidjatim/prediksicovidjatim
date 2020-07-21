import os
from requests_html import HTMLSession
from core import util
from core.data.kapasitas_rs.entities import KapasitasRSRaw, KapasitasRSCollection
from dotenv import load_dotenv
load_dotenv()

SCRAP_ENDPOINT = os.getenv("SCRAP_ENDPOINT")

class KapasitasRSScrapper:
    
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or SCRAP_ENDPOINT
        
    def _parse_row(self, row):
        args = (
            row[2].text, 
            util.parse_date(row[0].text.split(" ")[0]), 
            util.parse_int(row[5].text)
                + util.parse_int(row[8].text)
                + util.parse_int(row[11].text)
        )
        return KapasitasRSRaw(*args)
            
        
    def scrap(self):
        session = HTMLSession()

        #send request
        r = session.get(self.endpoint)

        #get cards
        table = r.html.find("tbody")[0]
        rows = [r.find("td") for r in table.find("tr")]
        data = [self._parse_row(r) for r in rows]
        
        collection = KapasitasRSCollection()
        for d in data:
            collection.add(d)
        
        collected = collection.collect()
        
        return collected