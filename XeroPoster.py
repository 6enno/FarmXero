# Goal: Push a journal to Xero

import json
import requests
import Secrets

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

url = 'https://api.xero.com/api.xro/2.0/ManualJournals'
refreshUrl = "https://identity.xero.com/connect/token"
connectUrl ='https://api.xero.com/connections' 

scope = ['offline_access', 'accounting.transactions', 'openid', 'profile', 'email', 'accounting.contacts', 'accounting.settings']

tenant = Secrets.tenant
auth = Secrets.auth
clientId = Secrets.clientId
clientSecret = Secrets.clientSecret

auth = requests.auth.HTTPBasicAuth(clientId, clientSecret)

client = BackendApplicationClient(client_id=clientId, scope=scope)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url=connectUrl, auth=auth)

print token

payload='''{ 'Narration': 'Test Journal 5 - from PYTHON',
    'JournalLines': [
    {
      'LineAmount': 20000,
      'AccountCode': '200'
    },
:::
      'LineAmount': -20000,
      'AccountCode': '210'
    }
  ]
}'''


headers = {
  'xero-tenant-id': tenant,
  'Authorization': 'Bearer ' + auth,
  'Accept': 'application/json',
  'Content-Type': 'application/json'
}



refreshPayload={'grant_type': 'refresh_token',
    'refresh_token': 'e65ce7c0cfafd010b7be071c638706b8a489b12443632f64229e39197db4245d',
    'client_id': '467E283E84B045C9B3A549B3CCD415F6',
    'client_secret': 'sBq2m3GQNRwwIFVIaOyZzTF6aTEm_1WHc3s-nclllooTHXw-'
}

files=[]

refreshHeaders = {
  'grant_type': 'refresh_token',
  'Accept': '*/*'#,
  #'Content-Type': 'application/json'
}


# Do the stuff______________________________________________________

#refreshResponse = requests.request('POST', refreshUrl, headers=refreshHeaders, data=refreshPayload, files=files)
#response = requests.request('POST', url, headers=headers, data=payload)

#print(refreshResponse.text)
#print(response.text)

