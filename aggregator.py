# This aggregates the Table data from the scrapers and creates journals
# Also writes data to a file for accurate record keeping.

import FilfoxScraper
import json
import datetime
import time
import Addresses

def nanoFilToFil(nanoFil):
    return nanoFil*(10**-18)

startDate = datetime.date(2021,2,23)
endDate = datetime.date(2021,2,28)

table = FilfoxScraper.getMessageTableForDateRange(startDate, endDate, Addresses.minerAddress)

jnlNarration = 'Filfox data for the period ' + startDate.strftime('%d-%m-%Y') + ' to ' + endDate.strftime('%d-%m-%Y')


# print(table)
transfers = 0
collat = 0
minerFee = 0
burnFee = 0

for r in table:
    transfers = transfers + r['transfer']
    collat = collat + r['collateral']
    minerFee = minerFee + r['miner-fee']
    burnFee = burnFee + r['burn-fee']

transfers = nanoFilToFil(transfers)
collat = nanoFilToFil(collat)
minerFee = nanoFilToFil(minerFee)
burnFee = nanoFilToFil(burnFee)
minerBalance = -(transfers + collat + minerFee + burnFee)

print(jnlNarration)
print('Dr collat ' + str(collat))
print('Dr miner fee ' + str(minerFee))
print('Dr burn fee ' + str(burnFee))
print('Dr/cr transfers' + str(transfers))
print('     Cr minerbalance (b/s)' + str(minerBalance))
print('values in FIL')


# printTableCsv()
