import os
from requests_html import HTMLSession
from core import util
from core.data.raw.entities import Params, RawData
from multiprocessing import Pool
from dotenv import load_dotenv
load_dotenv()

SCRAP_ENDPOINT = os.getenv("SCRAP_ENDPOINT")

class Scrapper:
    positif_fields = ['total', 'dirawat', 'sembuh', 'meninggal', 'rumah', 'gedung', 'rs']
    odp_fields = ['total', 'belum_dipantau', 'dirawat', 'selesai_dipantau', 'meninggal', 'rumah', 'gedung', 'rs']
    pdp_fields = ['total', 'belum_diawasi', 'dirawat', 'sehat', 'meninggal', 'rumah', 'gedung', 'rs']
    
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or SCRAP_ENDPOINT
        
        #multiprocess doesn't even recognize Scrapper type
        self.positif_fields = Scrapper.positif_fields
        self.odp_fields = Scrapper.odp_fields
        self.pdp_fields = Scrapper.pdp_fields

    def _get_select_opts(self, r, query):
        #find the select element
        select = r.html.find(query)[0]
        els = select.find("option")
        return els

    def _get_select_vals(self, r, query):
        els = self._get_select_opts(r, query)
        vals = [k.attrs["value"] for k in els] 
        #we want to skip empty dates since they're useless, but not the empty kabko because it's the aggregate of all other kabko
        #it's always the first item from a list
        if 'kabko' not in query:
            vals.pop(0)
        return vals
        
    def scrap_params(self, params=['kabko', 'tanggal', 'sampai']):
        session = HTMLSession()
        r = session.get(self.endpoint)
        f = self._get_select_vals
        vals = dict([(p, f(r, "#"+p)) for p in params])
        return Params(**vals)

    def _parse_card(self, card, fields):
        els = card.find("h3")
        vals = [util.parse_int(e.text) for e in els]
        parsed = dict(zip(fields, vals))
        return parsed
    
    def _parse_card_single(self, card):
        val = util.parse_int(card.find("h3")[0].text)
        return val
    
    def scrap(self, kabko, tanggal, sampai=None):
        session = HTMLSession()
        
        #prepare the request
        if not sampai:
            sampai = tanggal
        data = {
            'kabko': kabko,
            'tanggal': tanggal,
            'sampai': sampai
        }

        #send request
        r = session.post(self.endpoint, data=data)

        #get cards
        row = r.html.find(".container .row")[0]
        card_groups = row.find("div.col-md-6")[:2]
        cards = card_groups[0].find("div.card") + card_groups[1].find("div.card")

        #name the cards
        positif_card = cards[0].find(".card-block")[0]
        odp_card = cards[1].find(".card-block")[0]
        pdp_card = cards[2].find(".card-block")[0]
        otg_card = cards[3].find(".card-body")[0]
        odr_card = cards[4].find(".card-body")[0]

        #get and pack the values
        vals = {
            'kabko':kabko,
            'tanggal':tanggal,
            #'sampai':sampai,
            'positif':self._parse_card(positif_card, self.positif_fields),
            'odp':self._parse_card(odp_card, self.odp_fields),
            'pdp':self._parse_card(pdp_card, self.pdp_fields),
            'otg':self._parse_card_single(otg_card),
            'odr':self._parse_card_single(odr_card)
        }

        return RawData(**vals)
    
    
    def scrap_bulk(self, kabko, tanggal, max_process_count=10):
        
        #we might not need this after all, but whatever
        data = {k:{t:None for t in tanggal} for k in kabko}
        
        #prepare the args
        #scrap(kabko, tanggal)
        args = [(k, t) for t in tanggal for k in kabko]
        
        #we prepare the pool
        #pool in this context is like collection of available tabs
        pool = Pool(processes=max_process_count)

        #now we execute it
        #we use starmap instead of map because there are multiple arguments
        try:
            output = pool.starmap(self.scrap, args)
            pool.close()
            pool.join()
        except ConnectionError as ex:
            raise
        finally:
            pool.terminate()
            del pool
        return output
