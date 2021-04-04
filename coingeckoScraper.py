# Pull data from Coin Gecko
import datetime
import requests

BASE_URL = 'https://api.coingecko.com/api/v3/'
HIST_EXT_URL = 'coins/filecoin/history'

#NOTE: Cannot query before mainnet launch 15-Oct-2020

def getRequestUrl(date):
    params = '?date=' + date.strftime('%d-%m-%Y') + '&localization=true'
    url = BASE_URL + HIST_EXT_URL + params
    return url

def getDataForDate(date):
    url = getRequestUrl(date)
    response = requests.get(url).json()
    return response

def getFilecoinNZDPriceOnDay(date):
    ret = getDataForDate(date)
    print(ret)
    price = ret['market_data']['current_price']['nzd']
    return price

# Tests
# d = datetime.date(2020,10,15)
# print(getFilecoinNZDPriceOnDay(d))
