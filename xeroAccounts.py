#Just holds Xero Account code defs
import re

COLLAT = 601
MINER_FEE = 311
BURN_FEE = 312
SLASH = 319
TRANSFERS = 990
BLOCK_REWARDS = 200
MINER_BALANCE = 601


def getTb(accountingApi, tennant, date, printIt=False):
    tb = {}
    report = accountingApi.get_report_trial_balance(tennant, date=date)

    rows = report.reports[0].rows
    for r in rows:
        try:
            for rr in r.rows:
                try:
                    debits = float(rr.cells[3].value)
                except:
                    debits = 0
                try:
                    credits = float(rr.cells[4].value)
                except:
                    credits = 0

                amount = debits - credits
                description = rr.cells[0].value
                account = re.findall((r'\((\d+)\)'), description)[0]
                tb[account] = amount;
                # print(str(account))

                if (printIt):
                    print(str(rr.cells[0].value) +' | '+ str(amount))
        except:
            pass
    return tb
