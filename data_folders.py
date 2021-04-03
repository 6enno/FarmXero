# This is where to save audit trail stuff
import csv

MESSAGE_ARCHIVE = 'archive/messages/'
BLOCKS_ARCHIVE = 'archive/blocks/'
JOURNAL_ARCHIVE = 'archive/journals.csv'


#Returns total values in NZD (or nFIL if specified)
def getJournalTotals(valuesInNFIL=False):
    t = {}
    t['collat'] = 0
    t['minerFee'] = 0
    t['burnFee'] = 0
    t['slash'] = 0
    t['transfers'] = 0
    t['blockRewards'] = 0

    offset = 10
    if (valuesInNFIL):
        offset = 2

    with open(JOURNAL_ARCHIVE) as f:
        jnls = csv.reader(f, delimiter=',')
        i = 0
        for j in jnls:
            i += 1
            if (i == 1):
                continue
            # print(j)
            t['collat'] += float(j[offset+0])
            t['minerFee'] += float(j[offset+1])
            t['burnFee'] += float(j[offset+2])
            t['slash'] += float(j[offset+3])
            t['transfers'] += float(j[offset+4])
            t['blockRewards'] += float(j[offset+4])

    return t
