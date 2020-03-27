


import random
import requests
import json
import playground.settings as s

"""
Early version of an adaptation of CoinMarketCapAPI for early data mining
"""
class CoinMarketCapAPI():

    def __init__(self, *args, **kwargs):
        self.key = s.CMC_PRO_API_KEY
        return super().__init__(*args, **kwargs)

    
    def top_hundred_by_mc(self):
        _listings = self.get_listings()
        data = []

        top100 = self.get_currency_quotes(start=1, end=100)
        print(top100)
        
        for item in _listings:
            print(item)
            if str(item['id']) in top100.keys():
                obj = {}
                obj['id'] = item['id']
                obj['symbol'] = item['symbol']
                obj['name'] = item['name']
                obj['circulating_supply'] = top100[ str(item['id']) ]['circulating_supply']
                if top100[ str(item['id']) ]['max_supply']:
                    obj['perc_circulating'] = ( top100[ str(item['id']) ]['circulating_supply'] / top100[ str(item['id']) ]['max_supply'] ) * 100
                else:
                    obj['perc_circulating'] = 'N/A'
                obj['price'] = top100[str(item['id'])]['quotes']['USD']['price']
                obj['market_cap'] = top100[str(item['id'])]['quotes']['USD']['market_cap']
                obj['volume_24h'] = top100[str(item['id'])]['quotes']['USD']['volume_24h']
                obj['percent_change_7d'] = top100[str(item['id'])]['quotes']['USD']['percent_change_7d']
                obj['percent_change_1h'] = top100[str(item['id'])]['quotes']['USD']['percent_change_1h']
                obj['percent_change_24h'] = top100[str(item['id'])]['quotes']['USD']['percent_change_24h']

                data.append(obj)
            else:
                pass 

        return data


    def get_listings(self):
        headers= { 'X-CMC_PRO_API_KEY' : self.key  }
        r =  requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map', headers=headers)
        if r.status_code == requests.codes.ok:
            listings = json.loads(r.text)
            return listings['data']


    def get_global_info(self):
        headers= { 'X-CMC_PRO_API_KEY' : self.key  }
        r = requests.get('https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest', headers=headers)
        
        if r.status_code == requests.codes.ok:
            global_info = json.loads(r.text)
            
            response = {}
            response['active_cryptocurrencies'] = global_info['data']['active_cryptocurrencies']
            response['active_market_pairs'] = global_info['data']['active_market_pairs']
            response['active_exchanges'] = global_info['data']['active_exchanges']
            response['btc_dominance'] = global_info['data']['btc_dominance']
            response['eth_dominance'] = global_info['data']['eth_dominance']
            response['total_market_cap'] = global_info['data']['quote']['USD']['total_market_cap']
            response['total_volume_24h'] = global_info['data']['quote']['USD']['total_volume_24h']
            
            return response


    def get_currency_quotes(self, start, end):
        headers= { 'X-CMC_PRO_API_KEY' : self.key }
        if start and end:
            url = 'https://api.coinmarketcap.com/v2/ticker/?start=' + str(start) + '&limit=' + str(end)
        r = requests.get(url)

        if r.status_code == requests.codes.ok:
            currency = json.loads(r.text)
            print(currency)
            return currency['data']
