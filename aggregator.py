# This aggregates the Table data from the scrapers and creates journals
# Also writes data to a file for accurate record keeping.

import json
import datetime
import time
import os
import FilfoxScraper
import Addresses
import coingeckoScraper
import xeroAccounts as xa
import data_folders

from xero_python.accounting import ManualJournal, ManualJournalLine

# from xero_python.accounting import AccountingApi, ManualJournal, ManualJournalLine

def nanoFilToFil(nanoFil):
    return nanoFil*(10**-18)

def getJournalForDay(walletAddress, day, printJnl=True, archive=True):

    startDate = day
    endDate = day + datetime.timedelta(days=1)

    table = FilfoxScraper.getMessageTableForDateRange(startDate, endDate, walletAddress)
    msgFn = data_folders.MESSAGE_ARCHIVE + 'msgs_' + startDate.strftime('%d-%m-%Y') + '.csv'
    FilfoxScraper.writeTableToCSV(msgFn, table)

    blocksWon = FilfoxScraper.getBlocksTableForDateRange(startDate, endDate, walletAddress)
    blockFn = data_folders.BLOCKS_ARCHIVE + 'blocks_' + startDate.strftime('%d-%m-%Y') + '.csv'
    FilfoxScraper.writeBlockTableToCSV(blockFn, blocksWon)

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

    nCollat = "Collat: " + str(nanoFilToFil(collat)) + " FIL"
    nMinerFee = "Miner Fee: " + str(nanoFilToFil(minerFee)) + " FIL"
    nBurnFee = "Burn Fee: " + str(nanoFilToFil(burnFee)) + " FIL"
    nSlash = "Slash: " + str(nanoFilToFil(slash)) + " FIL"
    nTransfers = "Transfers: " + str(nanoFilToFil(transfers)) + " FIL"
    nBlockRewards = "Block Rewards: " + str(nanoFilToFil(blockRewards)) + " FIL (" + str(numBlocksWon)+") blocks won"
    nMinerBalance = "Miner Balance: " #+ str(nanoFilToFil(minerBalance)) + "FIL"

    exchRate = coingeckoScraper.getFilecoinNZDPriceOnDay(endDate)
    collatNzd = nanoFilToFil(collat) * exchRate
    minerFeeNzd = nanoFilToFil(minerFee) * exchRate
    burnFeeNzd = nanoFilToFil(burnFee) * exchRate
    slashNzd = nanoFilToFil(slash) * exchRate
    transfersNzd = nanoFilToFil(transfers) * exchRate
    blockRewardsNzd = -nanoFilToFil(blockRewards) * exchRate#Rewards are credits therefore are -ve
    minerBalanceNzd = -(transfersNzd + collatNzd + minerFeeNzd + burnFeeNzd + blockRewardsNzd)
    jnlNarration = 'Filfox data for the day ' + startDate.strftime('%d-%m-%Y') #+ ' to ' + endDate.strftime('%d-%m-%Y')

    jnlLinesAll = [
            ManualJournalLine(line_amount=collatNzd, account_code=xa.COLLAT, description=nCollat),
            ManualJournalLine(line_amount=minerFeeNzd, account_code=xa.MINER_FEE, description=nMinerFee),
            ManualJournalLine(line_amount=burnFeeNzd, account_code=xa.BURN_FEE, description=nBurnFee),
            ManualJournalLine(line_amount=slashNzd, account_code=xa.SLASH, description=nSlash),
            ManualJournalLine(line_amount=transfersNzd, account_code=xa.TRANSFERS, description=nTransfers),
            ManualJournalLine(line_amount=blockRewardsNzd, account_code=xa.BLOCK_REWARDS, description=nBlockRewards),
            ManualJournalLine(line_amount=minerBalanceNzd, account_code=xa.MINER_BALANCE, description=nMinerBalance)
            ]
    jnlLines = []

    for l in jnlLinesAll:
        if(l.line_amount != 0):
            jnlLines.append(l)


    mj = ManualJournal(narration=jnlNarration, journal_lines=jnlLines, date=startDate)

    if(archive):
        ARCHIVE_HEADER = 'date, narration, \
        collat, Miner Fee, Burn Fee, Slash, Transfers, Block rewards, \
        Blocks won, exch rate, \
        NZD collat, NZD Miner Fee, NZD Burn Fee, NZD Slash, NZD Transfers, NZD Block rewards, NZD Balance\n'
        if(os.path.exists(data_folders.JOURNAL_ARCHIVE) == False):
            with open(data_folders.JOURNAL_ARCHIVE, 'w') as f:
                f.write(ARCHIVE_HEADER)
        csvLine = startDate.strftime('%d-%m-%Y')+','+str(jnlNarration)+','+\
        str(collat)+','+str(minerFee)+','+str(burnFee)+','+str(slash)+','+str(transfers)+','+str(blockRewards)+','+\
        str(numBlocksWon)+','+str(exchRate)+','+\
        str(collatNzd)+','+str(minerFeeNzd)+','+str(burnFeeNzd)+','+str(slashNzd)+','+str(transfersNzd)+','+str(blockRewardsNzd)+','+str(minerBalanceNzd)+'\n'
        with open(data_folders.JOURNAL_ARCHIVE, 'a') as f:
            f.write(csvLine)


    if(printJnl):
        print(jnlNarration)
        print('Dr collat (601)' + str(collatNzd)) # collat is represented within miner balance
        print('Dr miner fee (311)' + str(minerFeeNzd))
        print('Dr burn fee (312)' + str(burnFeeNzd))
        print('Dr slash (319)' + str(slashNzd))
        print('Dr/cr transfers (990)' + str(transfersNzd)) #These are transferred out of info.farm accounts for now
        print('     Cr block rewards (200)' + str(blockRewardsNzd))
        print('     Cr minerbalance (601) ' + str(minerBalanceNzd))
        print('values in NZD')
        print('blocks won: ' + str(numBlocksWon))

    return mj


#getJournalForDay(Addresses.minerAddress, datetime.date(2021,3,12))
