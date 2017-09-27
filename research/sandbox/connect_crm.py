#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests  
import json
 
#set these values to retrieve the oauth token
crmorg = 'https://avakundeservice.crm4.dynamics.com' #base url for crm org  
clientid = '618fef7c-23ab-496d-a3d5-edd77989c8c4' #application client id  
username = 'BRUGERNAVN@avakundeservice.onmicrosoft.com' #username  
userpassword = 'RIGTIGT_PASSWORD_HER' #password  
tokenendpoint = 'https://login.windows.net/3b903b3d-c80c-4a6c-ade9-748d252e427e/oauth2/token' #oauth token endpoint
 
#set these values to query your crm data
crmwebapi = 'https://avakundeservice.api.crm4.dynamics.com/api/data/v8.2' #full path to web api endpoint  
crmwebapiquery = '/contacts?$select=fullname,contactid' #web api query (include leading /)
 
#build the authorization token request
tokenpost = {  
    'client_id':clientid,
    'resource':crmorg,
    'username':username,
    'password':userpassword,
    'grant_type':'password'
}
 
#make the token request
tokenres = requests.post(tokenendpoint, data=tokenpost)

print str(tokenres)

#set accesstoken variable to empty string
accesstoken = ''
 
#extract the access token
try:  
    jsn = tokenres.json()
    print jsn
    accesstoken = jsn['access_token']
except KeyError:  
    #handle any missing key errors
    print(jsn['error_description'])
    print('Could not get access token')
 
#if we have an accesstoken
if(accesstoken!=''):  
    #prepare the crm request headers
    crmrequestheaders = {
        'Authorization': 'Bearer ' + accesstoken,
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8',
        'Prefer': 'odata.maxpagesize=500',
        'Prefer': 'odata.include-annotations=OData.Community.Display.V1.FormattedValue'
    }
 
    #make the crm request
    crmres = requests.get(crmwebapi+crmwebapiquery, headers=crmrequestheaders)
 
    try:
        #get the response json
        crmresults = crmres.json()
 
        #loop through it
        for x in crmresults['value']:
            print (x['fullname'] + ' - ' + x['contactid'])
    except KeyError:
        #handle any missing key errors
        print('Could not parse CRM results')
