# This is where to save audit trail stuff
import csv
import datetime
import os

MESSAGE_ARCHIVE = 'archive/messages/'
BLOCKS_ARCHIVE = 'archive/blocks/'
JOURNAL_ARCHIVE = 'archive/journals.csv'

def nanoFilToFil(nanoFil):
    return nanoFil*(10**-18)

#Returns total values in NZD (or FIL if specified)
def getJournalTotals(startDate, endDate, valuesInFIL=False):
    t = {}
    t['collat'] = 0
    t['minerFee'] = 0
    t['burnFee'] = 0
    t['slash'] = 0
    t['transfers'] = 0
    t['blockRewards'] = 0

    offset = 10
    multiplier = 1
    if (valuesInFIL):
        offset = 2
        multiplier = nanoFilToFil(1)

    with open(JOURNAL_ARCHIVE) as f:
        jnls = csv.reader(f, delimiter=',')
        i = 0
        for j in jnls:
            i += 1
            if (i == 1):
                continue
            # print(j)
            # print(type(j[0]))
            date = datetime.datetime.strptime(j[0], '%d-%m-%Y').date()

            if(date >= startDate and date <= endDate):
                t['collat'] += float(j[offset+0]) * multiplier
                t['minerFee'] += float(j[offset+1]) * multiplier
                t['burnFee'] += float(j[offset+2]) * multiplier
                t['slash'] += float(j[offset+3]) * multiplier
                t['transfers'] += float(j[offset+4]) * multiplier
                t['blockRewards'] += float(j[offset+4]) * multiplier

    return t

def getMessagesTotals(startDate, endDate):
    t = {}
    t['collat'] = 0
    t['minerFee'] = 0
    t['burnFee'] = 0
    t['slash'] = 0
    t['transfers'] = 0

    _, _, filenames = next(os.walk(MESSAGE_ARCHIVE))

    # print(filenames);

    for f in filenames:
        date = datetime.datetime.strptime(f, 'msgs_%d-%m-%Y.csv').date()
        if(date >= startDate and date <= endDate):
            mt = getMessageTotals(MESSAGE_ARCHIVE + f)
            t['collat'] += mt['collat']
            t['minerFee'] += mt['minerFee']
            t['burnFee'] += mt['burnFee']
            t['slash'] += mt['slash']
            t['transfers'] += mt['transfers']

    return t

def getMessageTotals(filename):
    t = {}
    t['collat'] = 0
    t['minerFee'] = 0
    t['burnFee'] = 0
    t['slash'] = 0
    t['transfers'] = 0

    with open(filename) as f:
        msgs = csv.reader(f, delimiter=',')
        i = 0
        for m in msgs:
            i += 1
            if (i == 1):
                continue
            # print(m)

            t['collat'] += nanoFilToFil(float(m[4]))
            t['minerFee'] += nanoFilToFil(float(m[5]))
            t['burnFee'] += nanoFilToFil(float(m[6]))
            t['slash'] += nanoFilToFil(float(m[7]))
            t['transfers'] += nanoFilToFil(float(m[3]))

    # print(t)
    return t

# This is a quick rec that checks messages have been totaled and checks this
# against the archived Journals in FIL
# Does not check for errored or duplicated messages
def quickRecFIL(startDate, endDate, tolerance=0.001):
    mTotal = getMessagesTotals(startDate, endDate)
    jTotal = getJournalTotals(startDate, endDate, valuesInFIL=True)
    print(mTotal)
    print(jTotal)

    if(abs(mTotal['collat'] - jTotal['collat']) > tolerance):
        print('collat did not rec!!' + str(mTotal['collat'] - jTotal['collat']))
        return 1

    if(abs(mTotal['minerFee'] - jTotal['minerFee']) > tolerance):
        print('minerFee did not rec!!')
        return 1

    if(abs(mTotal['burnFee'] - jTotal['burnFee']) > tolerance):
        print('burnFee did not rec!!')
        return 1

    if(abs(mTotal['slash'] - jTotal['slash']) > tolerance):
        print('slash did not rec!!')
        return 1

    if(abs(mTotal['transfers'] - jTotal['transfers']) > tolerance):
        print('transfers did not rec!!')
        return 1

    print('all recs checked')
    return 0
