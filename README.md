# FarmXero
Automating some of the accounting for Filecoin Mining

## Purpose
This is currently being developed for a specific purpose to scrape, colate and log information about specific
filecoin wallets and then automatically push journals into the Xero accounting system.

Although this is a very specific usecase, you can feel free to use the code as you like, I am not liable for any use of it.

To use it as it stands you will need a filecoin mining setup and a Xero accounting login (basic or free will work). If you
don't have Xero or dont want to use it, you can simply output to a file to get similar information for tax purposes etc.
Again, I am not liable for this code or any of the information you get from using it. Please seek professional tax advice.

If you do use and modify it to add exta connections feel free to submit a pull request, there is not many tools for automated
accounting in the crypto world so it would be cool to build this beyond Xero and perhaps beyond Filecoin. Sorry, you cannot
use my Filecoin miner or Xero accounts for testing and you will not find any keys in the repo. Pull requests with any keys
or private info will not be accepted.

## Install
_note these are incomplete notes for now_

Create the folders if the git repo didn't already do it

```
mkdir archive
mkdir archive/messages
mkdir archive/blocks
```

Copy the `Secrets.py_Example` to `Secrets.py` and fill in api keys if you want to use Xero
Copy the `Addresses.py_Example` to `Addresses.py` and fill in your wallets (note that these are never shared on Git or by the code)

Install dependencies (install the xero one even if you don't want to use xero, it has some handy journal structures internally)

```
python -m pip install xero_python
python -m pip install requests
```

## Usage

Realistically, you're probably here just to scrape some Filecoin transactions from your miner and associated wallets. You can just use the scraper module as below:

Notes:
Dates must be entered in the form `yyyy-mm-dd`
use `-t` if you want transactions or use `-b` if you want blocks instead (only applies to miner addresses).

```
FilfoxScraper.py -t -s <start_date> -e <end_date> -f <filename.csv> -w <wallet_address>
```
