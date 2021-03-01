import requests
import json
import datetime
import time
import Addresses

# This module scrapes data from filfox.info/ and populates a table[] of data
# This will be a 'table[]' of 'rows{}'
# May also output a csv with the following headers:
# MessageID, type, timestamp, transfer, collateral, miner-fee, burn-fee

MAX_MESSAGE_PAGES = 50

minerAddress = Addresses.minerAddress

def messagesUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/messages?page='+str(page)+'&pageSize=100'

def messageDetailsUrl(address):
    return 'https://filfox.info/api/v1/message/'+address

def blocksUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/blocks?pageSize=100&page='+str(page)

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

    for page in range(0, MAX_MESSAGE_PAGES):

        if timestampReached: break

        print('about to send page request')
        minerMessages = requests.get(messagesUrl(minerAddress, page)).json()

        if(len(minerMessages['messages']) == 0):
            print('Reached end of messages..')
            print(minerMessages)
            break

        for m in minerMessages['messages']:
            #count = count + 1
            #if count > 30:
            #    break

            if m['timestamp'] > timeStart: #larger timestamps are later message > starttime
                # print('timestamp ('+str(m['timestamp'])+') before timestart ' + str(timeStart))
                continue
            if m['timestamp'] <= timeEnd:
                # print('timestamp ('+str(m['timestamp'])+') after timeend ' + str(timeEnd))
                timestampReached = True
                break

            count = count + 1
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
                if t['type'] == 'burn-fee':
                    row['burn-fee'] = int(t['value'])

                elif t['type'] == 'burn':
                    row['slash'] = int(t['value'])

                elif t['type'] == 'miner-fee':
                    row['miner-fee'] = int(t['value'])

                elif t['type'] == 'transfer':
                    if row['status'] != 0:
                        pass
                    elif messageDeets['method'] == 'PreCommitSector' or messageDeets['method'] == 'ProveCommitSector':
                        row['collateral'] = int(t['value'])
                    else:
                        row['transfer'] = int(t['value'])
                else:
                    print ('unknown message type: ' + t['type'])

            table.append(row)

    #print table
    #print 'found '+str(count)+ ' messages'
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

    for page in range(0, 10):

        if timestampReached: break

        print('about to send page request')
        minerBlocks = requests.get(blocksUrl(minerAddress, page)).json()
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


#printTableCsv(getMessageTableForDateRange(datetime.date(2021,2,10), datetime.date(2021,2,11), minerAddress))
