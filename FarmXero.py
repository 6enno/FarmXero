import requests
import json

# Current Goal - Output CSV of the following from miner messages:
# MessageID, type, timestamp, transfer, collateral, miner-fee, burn-fee
# This will be a 'table[]' of 'rows{}'

minerAddress = 'f021716'

def messagesUrl(address, page):
    return 'https://filfox.info/api/v1/address/'+address+'/messages?page='+page+'&pageSize=100'

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


minerMessages = requests.get(messagesUrl(minerAddress, 1)).json()

#print(minerMessages['messages'][0])

cids = []
table = []

count = 0

for m in minerMessages['messages']:
    count = count + 1
#    if count > 100:
#        break
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


    messageDeets = requests.get(messageDetailsUrl(m['cid'])).json()

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
print 'found '+str(count)+ ' messages'

printTableCsv(table)
