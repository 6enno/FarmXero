import requests
import json
import datetime
import time
import Addresses
import argparse

# This module scrapes data from filfox.info/ and populates a table[] of data
# This will be a 'table[]' of 'rows{}'
# May also output a csv with the following headers:
# MessageID, type, timestamp, transfer, collateral, miner-fee, burn-fee

MAX_MESSAGE_PAGES = 1000

minerAddress = Addresses.minerAddress

def messagesUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/messages?page='+str(page)+'&pageSize=100'

def messageDetailsUrl(address):
    return 'https://filfox.info/api/v1/message/'+address

def blocksUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/blocks?pageSize=100&page='+str(page)

def txnUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/transfers?pageSize=100&page='+str(page)

def printTableCsv(table):
    csvString = 'messageId, type, timestamp, transfer, collateral, miner-fee, burn-fee, slash, status\n'
    for r in table:
        csvString = csvString +\
            r['cid']+','+\
            r['type']+','+\
            str(r['timestamp']) + ',' +\
            str(r['transfer']) + ',' +\
            str(r['collateral']) + ',' +\
            str(r['miner-fee']) + ',' +\
            str(r['burn-fee']) + ',' +\
            str(r['slash']) + ',' +\
            str(r['status']) + '\n'
    return csvString

def writeTableToCSV(filename, table):
    f = open(filename, 'w+')
    f.write(printTableCsv(table))
    f.close()
    return 0

def printBlockTableCsv(table):
    csvString = 'messageId, type, timestamp, reward\n'
    for r in table:
        csvString = csvString +\
            r['cid']+','+\
            str(r['timestamp']) + ',' +\
            str(r['win']) + '\n'
    return csvString

def writeBlockTableToCSV(filename, table):
    f = open(filename, 'w+')
    f.write(printBlockTableCsv(table))
    f.close()
    return 0

def printTxnTableCsv(table):
    csvString = 'Height, Timestamp, Message, From, To, Value, Type\n'
    for r in table:
        csvRow = ', '.join('{}'.format(v) for k,v in r.items()) + '\n'
        csvString = csvString + csvRow
    return csvString

def writeTxnTableToCSV(filename, table):
    f = open(filename, 'w+')
    f.write(printTxnTableCsv(table))
    f.close()
    return 0

# This pull relevent data from messages over a date range
# Note that time works in reverse for timestamps start = latest time, end = earliest time
#
# @endDate is a datetime.date() type eg the start of the day you want to see msgs for
# @startDate is a datetime.date() time eg the start of the day where you want to stop getting msgs
# @wallet is a string eg f02xxxx for miner or longer for control
def getMessageTableForDateRange(endDate, startDate, wallet):
    table = []
    count = 0

    timeStart = int(time.mktime(startDate.timetuple())) #Local NZ time
    timeEnd = int(time.mktime(endDate.timetuple())) #Local NZ time
    timestampReached = False
    allMsgs = []

    for page in range(0, MAX_MESSAGE_PAGES):

        if timestampReached: break

        print('about to send page request: '+ messagesUrl(wallet, page))
        minerMessages = requests.get(messagesUrl(wallet, page)).json()

        if(len(minerMessages['messages']) == 0):
            print('Reached end of messages..')
            print(minerMessages)
            break

        for m in minerMessages['messages']:
            #count = count + 1
            #if count > 30:
            #    break

            # ==== TODO ==== Check if there is this message in the DB and skip if there is

            if m['timestamp'] > timeStart: #larger timestamps are later message > starttime
                print('timestamp ('+str(m['timestamp'])+') before timestart ' + str(timeStart))
                continue
            elif m['timestamp'] <= timeEnd:
                print('timestamp ('+str(m['timestamp'])+') after timeend ' + str(timeEnd))
                timestampReached = True
                break
            else:
                allMsgs.append(m)


    for m in allMsgs:
        # count = count + 1
        # print('found a message within timestamp range ' + str(count))
        try:
            row = {
                'cid':m['cid'],
                'type':m['method'],
                'timestamp':m['timestamp'],
                'transfer':0,
                'collateral':0,
                'miner-fee':0,
                'burn-fee':0,
                'slash':0,
                'status':int(m['receipt']['exitCode'])
            }
        except KeyError:
            print('message status unknown: '+m.get('cid'))
            continue


        # print('    getting msg deets...')
        messageDeets = requests.get(messageDetailsUrl(m['cid'])).json()
        # print('    got msg deets...')

        for t in messageDeets['transfers']:
            # transfers and collat can go out or in but always show positive in messages (lets reverse the ones that are from this wallet)
            direction = 1
            # we ignore burn fees, slashes, minerfees and collat if theyre not from this wallet to avoid double counting
            fromThis = 0
            if (t['from'] == wallet):
                direction = -1
                fromThis = 1

            if t['type'] == 'burn-fee':
                row['burn-fee'] = int(t['value']) * fromThis

            elif t['type'] == 'burn':
                row['slash'] = int(t['value']) * fromThis

            elif t['type'] == 'miner-fee':
                row['miner-fee'] = int(t['value']) * fromThis

            elif t['type'] == 'transfer':

                if row['status'] != 0:
                    pass
                elif messageDeets['method'] == 'PreCommitSector' or messageDeets['method'] == 'ProveCommitSector':
                    row['collateral'] = fromThis * int(t['value'])
                else:
                    row['transfer'] = direction * int(t['value'])
            else:
                print ('unknown message type: ' + t['type'])

        table.append(row)

    #print table
    #print 'found '+str(count)+ ' messages'
    print('found all '+str(len(allMsgs))+' messages for wallet ' + wallet)
    return table

# This gets all the blocks that the miner has won over a length of time
# Note that time works in reverse for timestamps start = latest time, end = earliest time
#
# @endDate is a datetime.date() type eg the start of the day you want to see msgs for
# @startDate is a datetime.date() time eg the start of the day where you want to stop getting msgs
# @wallet is a string that represents a miner wallet eg f02xxxx for miner or longer for control
def getBlocksTableForDateRange(endDate, startDate, wallet):
    table = []
    count = 0

    timeStart = int(time.mktime(startDate.timetuple())) #Local NZ time
    timeEnd = int(time.mktime(endDate.timetuple())) #Local NZ time
    timestampReached = False

    for page in range(0, MAX_MESSAGE_PAGES):

        if timestampReached: break

        print('about to send page request')
        minerBlocks = requests.get(blocksUrl(wallet, page)).json()
        print('total blocks: ' + str(minerBlocks['totalCount']))

        if(len(minerBlocks['blocks']) == 0):
            print('Reached end of blocks')
            break

        for b in minerBlocks['blocks']:

            # print('reward '+str(b['reward']))
            #count = count + 1
            #if count > 30:
            #    break

            if b['timestamp'] > timeStart: #larger timestamps are later message > starttime
                # print('timestamp ('+str(b['timestamp'])+') before timestart ' + str(timeStart))
                continue
            if b['timestamp'] <= timeEnd:
                # print('timestamp ('+str(b['timestamp'])+') after timeend ' + str(timeEnd))
                timestampReached = True
                break

            count = count + 1
            # print('found a block within timestamp range ' + str(count))
            row = {
                'cid':b['cid'],
                'timestamp':b['timestamp'],
                'win':b['reward'],
            }

            table.append(row)

    #print table
    #print 'found '+str(count)+ ' messages'
    return table

def getSimpleTxnJson(endDate, startDate, wallet):
    table = []
    count = 0

    timeStart = int(time.mktime(startDate.timetuple())) #Local NZ time
    timeEnd = int(time.mktime(endDate.timetuple())) #Local NZ time
    timestampReached = False

    for page in range(0, MAX_MESSAGE_PAGES):

        if timestampReached: break

        print('about to send txn page request pg ' + str(page))
        txns = requests.get(txnUrl(wallet, page)).json()

        if(txns['totalCount'] == 0):
            print('Reached end of txns')
            break

        for t in txns['transfers']:

            if t['timestamp'] > timeStart: #larger timestamps are later message > starttime
                print('timestamp ('+str(t['timestamp'])+') before timestart ' + str(timeStart))
                continue
            if t['timestamp'] <= timeEnd:
                print('timestamp ('+str(t['timestamp'])+') after timeend ' + str(timeEnd))
                timestampReached = True
                break

            count = count + 1
            # print('found a block within timestamp range ' + str(count))

            try:
                msg = t['message']
            except KeyError:
                msg = 'official'

            row = {
                'Height':t['height'],
                'Timestamp':t['timestamp'],
                'Message': msg,
                'From':t['from'],
                'To':t['to'],
                'Value':t['value'],
                'Type':t['type'],
            }
            # print('row logged')
            table.append(row)

    #print table
    #print 'found '+str(count)+ ' messages'
    return table





# Can run this as standalone to grab filfox transactions
if __name__ == '__main__':
    p = argparse.ArgumentParser(description='FilfoxScraper - Get data from Filfox')
    p.add_argument('-b', '--blocks', help='get blocks instead of messages (only applies to miner addresses)', required=False, default=False, action='store_true')
    p.add_argument('-t', '--transactions', help='get simple list of transactions', required=False, default=False, action='store_true')
    p.add_argument('-w', '--wallet', help='specify the wallet address you want transactions for', required=False, default=Addresses.minerAddress)
    p.add_argument('-s', '--start', help='specify the start date that you want to get transactions from (format yyyy-mm-dd)', required=False, default='2020-01-01')
    p.add_argument('-e', '--end', help='specify the end date that you want to get transactions until (format yyyy-mm-dd)', required=False, default=datetime.date.today().isoformat())
    p.add_argument('-f', '--filesave', help='specify the file to save the csv output to', required=False)
    args = p.parse_args()

    # startDate = datetime.date.fromisoformat(args.start)
    startDate = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    # endDate = datetime.date.fromisoformat(args.end)
    endDate = datetime.datetime.strptime(args.end, "%Y-%m-%d")

    print(startDate)
    print(endDate)

    table = {}
    if (args.blocks):
        table = getBlocksTableForDateRange(startDate, endDate, args.wallet)
        printBlockTableCsv(table)
        if(args.filesave):
            writeBlockTableToCSV(args.filesave, table)
    elif(args.transactions):
        table = getSimpleTxnJson(startDate, endDate, args.wallet)
        print(printTxnTableCsv(table))
        if(args.filesave):
            writeTxnTableToCSV(args.filesave, table)
    else:
        table = getMessageTableForDateRange(startDate, endDate, args.wallet)
        printTableCsv(table)
        if(args.filesave):
            writeTableToCSV(args.filesave, table)



# addr = Addresses.minerAddress
# # addr = Addresses.wallet5
#
# t = getMessageTableForDateRange(datetime.date(2021,3,25), datetime.date(2021,3,26), addr)
# print(t)
