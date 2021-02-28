# This aggregates the Table data from the scrapers and creates journals
# Also writes data to a file for accurate record keeping.

import json
import datetime
import time
import FilfoxScraper
import Addresses
import coingeckoScraper

from xero_python.accounting import AccountingApi, ManualJournal, ManualJournalLine

def nanoFilToFil(nanoFil):
    return nanoFil*(10**-18)

startDate = datetime.date(2021,2,23)
endDate = datetime.date(2021,2,28)

table = FilfoxScraper.getMessageTableForDateRange(startDate, endDate, Addresses.minerAddress)
blocksWon = FilfoxScraper.getBlocksTableForDateRange(startDate, endDate, Addresses.minerAddress)

transfers = 0
collat = 0
minerFee = 0
burnFee = 0
slash = 0
numTransactions = 0
blockRewards = 0
numBlocksWon = 0

for r in table:
    transfers = transfers + r['transfer']
    collat = collat + r['collateral']
    minerFee = minerFee + r['miner-fee']
    burnFee = burnFee + r['burn-fee']
    slash = slash + r['slash']
    numTransactions = numTransactions + 1

for b in blocksWon:
    blockRewards = blockRewards + int(b['win'])
    numBlocksWon = numBlocksWon + 1

exchRate = coingeckoScraper.getFilecoinNZDPriceOnDay(startDate)
transfers = nanoFilToFil(transfers) * exchRate
collat = nanoFilToFil(collat) * exchRate
minerFee = nanoFilToFil(minerFee) * exchRate
burnFee = nanoFilToFil(burnFee) * exchRate
slash = nanoFilToFil(slash) * exchRate
blockRewards = -nanoFilToFil(blockRewards)*exchRate#Rewards are credits therefore are -ve
minerBalance = -(transfers + collat + minerFee + burnFee + blockRewards)
jnlNarration = 'Filfox data for the period ' + startDate.strftime('%d-%m-%Y') + ' to ' + endDate.strftime('%d-%m-%Y')

print(jnlNarration)
print('Dr collat ' + str(collat))
print('Dr miner fee ' + str(minerFee))
print('Dr burn fee ' + str(burnFee))
print('Dr slash ' + str(slash))
print('Dr/cr transfers ' + str(transfers))
print('     Cr block rewards ' + str(blockRewards))
print('     Cr minerbalance (b/s) ' + str(minerBalance))
print('values in NZD')
print('blocks won: ' + str(numBlocksWon))

f = open('test.csv', 'w')
f.write(FilfoxScraper.printTableCsv(table))
f.close()


# printTableCsv()
