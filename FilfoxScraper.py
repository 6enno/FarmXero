import requests
import json
import datetime
import time

# This module scrapes data from filfox.info/ and populates a table[] of data
# This will be a 'table[]' of 'rows{}'
# May also output a csv with the following headers:
# MessageID, type, timestamp, transfer, collateral, miner-fee, burn-fee

minerAddress = 'f021716'

def messagesUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/messages?page='+str(page)+'&pageSize=100'

def messageDetailsUrl(address):
    return 'https://filfox.info/api/v1/message/'+address

def printTableCsv(table):
    print 'messageId, type, timestamp, transfer, collateral, miner-fee, burn-fee, status'
    for r in table:
        print(
            r['cid']+','+
            r['type']+','+
            str(r['timestamp']) + ',' +
            str(r['transfer']) + ',' +
            str(r['collateral']) + ',' +
            str(r['miner-fee']) + ',' +
            str(r['burn-fee']) + ',' +
            str(r['status'])
            )
    return



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

    for page in range(1, 50):

        if timestampReached: break
        
        print 'about to send page request'
        minerMessages = requests.get(messagesUrl(minerAddress, page)).json()

        for m in minerMessages['messages']:
            #count = count + 1
            #if count > 30:
            #    break
            
            if m['timestamp'] > timeStart: #larger timestamps are later message > starttime
                print 'timestamp ('+str(m['timestamp'])+') before timestart ' + str(timeStart)
                continue
            if m['timestamp'] <= timeEnd:
                print 'timestamp ('+str(m['timestamp'])+') after timeend ' + str(timeEnd)
                timestampReached = True
                break

            count = count + 1
            print 'found a message within timestamp range ' + str(count)
            row = {
                'cid':m['cid'], 
                'type':m['method'], 
                'timestamp':m['timestamp'], 
                'transfer':0, 
                'collateral':0, 
                'miner-fee':0, 
                'burn-fee':0,
                'status':int(m['receipt']['exitCode'])
            }


            print '    getting msg deets...'
            messageDeets = requests.get(messageDetailsUrl(m['cid'])).json()
            print '    got msg deets...'

            for t in messageDeets['transfers']:
                if t['type'] == 'burn-fee':
                    row['burn-fee'] = int(t['value'])

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
                    print 'unknown message type'

            table.append(row)

    #print table
    #print 'found '+str(count)+ ' messages'
    return table



printTableCsv(getMessageTableForDateRange(datetime.date(2021,02,10), datetime.date(2021,02,11), minerAddress))
