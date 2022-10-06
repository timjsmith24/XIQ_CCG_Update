#!/usr/bin/env python3
import logging
import argparse
from math import floor
import sys
import os
import sys
import inspect
import getpass
import json
import pandas as pd
from pprint import pprint as pp
from app.ccg_logger import logger
from app.xiq_ccg_api import XIQ
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger('CCG_Updater.Main')

XIQ_API_token = ''

pageSize = 100


parser = argparse.ArgumentParser()
parser.add_argument('--external',action="store_true", help="Optional - adds External Account selection, to use an external VIQ")
args = parser.parse_args()

PATH = current_dir

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0;0m"

def yesNoLoop(question):
    validResponse = False
    while validResponse != True:
        response = input(f"{question} (y/n) ").lower()
        if response =='n' or response == 'no':
            response = 'n'
            validResponse = True
        elif response == 'y' or response == 'yes':
            response = 'y'
            validResponse = True
        elif response == 'q' or response == 'quit':
            sys.stdout.write(RED)
            sys.stdout.write("script is exiting....\n")
            sys.stdout.write(RESET)
            raise SystemExit
    return response

## XIQ EXPORT
if XIQ_API_token:
    x = XIQ(token=XIQ_API_token)
else:
    print("Enter your XIQ login credentials")
    username = input("Email: ")
    password = getpass.getpass("Password: ")
    x = XIQ(user_name=username,password = password)
#OPTIONAL - use externally managed XIQ account
if args.external:
    accounts, viqName = x.selectManagedAccount()
    if accounts == 1:
        validResponse = False
        while validResponse != True:
            response = input("No External accounts found. Would you like to import data to your network?")
            if response == 'y':
                validResponse = True
            elif response =='n':
                sys.stdout.write(RED)
                sys.stdout.write("script is exiting....\n")
                sys.stdout.write(RESET)
                raise SystemExit
    elif accounts:
        validResponse = False
        while validResponse != True:
            print("\nWhich VIQ would you like to import the floor plan and APs too?")
            accounts_df = pd.DataFrame(accounts)
            count = 0
            for df_id, viq_info in accounts_df.iterrows():
                print(f"   {df_id}. {viq_info['name']}")
                count = df_id
            print(f"   {count+1}. {viqName} (This is Your main account)\n")
            selection = input(f"Please enter 0 - {count+1}: ")
            try:
                selection = int(selection)
            except:
                sys.stdout.write(YELLOW)
                sys.stdout.write("Please enter a valid response!!")
                sys.stdout.write(RESET)
                continue
            if 0 <= selection <= count+1:
                validResponse = True
                if selection != count+1:
                    newViqID = (accounts_df.loc[int(selection),'id'])
                    newViqName = (accounts_df.loc[int(selection),'name'])
                    x.switchAccount(newViqID, newViqName)

building = input("Please enter the name of the building: ")
print("Collecting Location information")
location_df = x.gatherLocations()
location_df.set_index('id',inplace=True)
filt = (location_df['type'] == 'FLOOR') & (location_df['parent'] == building)
floor_list = location_df.loc[filt].index.tolist()

if not floor_list:
    print(f"There was no floors or no building found with the name {building}")
    print("script is exiting....")
    raise SystemExit


for floor_id in floor_list:
    print(f"Collecting Devices for floor '{location_df.loc[floor_id,'name']}'...")
    ## Collect Devices
    device_data = x.collectDevices(pageSize,location_id=floor_id)
    #pp(device_data)
    device_df = pd.DataFrame(device_data)
    device_df.set_index('id',inplace=True)
    print(f"Found {len(device_df.index)} Devices")

ccg_input = input("Enter the names of the CCG's (seperated by a comma) ")
ccg_list = ccg_input.split(" ")

print("Collecting CCGs...")
## Collect CCGs
ccg_data = x.collectCCG(pageSize)
#pp(ccg_data)
ccg_df = pd.DataFrame(ccg_data)
ccg_df.set_index('id',inplace=True)



confirm_changes = False
preview = yesNoLoop("Would you like to preview CCG changes before pushing to XIQ?")
if preview == 'y':
    confirm_changes = True


for ccg_name in ccg_list:
    print(f"\nStarting CCG {ccg_name}")
    if ccg_name not in ccg_df['name'].tolist():
        sys.stdout.write(RED)
        print(f"CCG {ccg_name} was not found!")
        print("script is exiting....")
        raise SystemExit

    filt = ccg_df['name'] == ccg_name
    ccg_device_list = ccg_df.loc[filt,'device_ids'].values[0]
    ccg_id = ccg_df.loc[filt].index.values[0]
    #print(ccg_id)
    #print(ccg_device_list)

    #filt = device_df['hostname'].str.contains('492')
    filt = device_df['hostname'].str.contains('AP-')
    ids = device_df[filt].index.values.tolist()
    add_device_list = []
    hostnames = []
    for device_id in ids:
        if device_id in ccg_device_list:
            sys.stdout.write(YELLOW)
            print(f"device {device_df.loc[device_id,'hostname']} was found in CCG {ccg_name}")
            sys.stdout.write(RESET)
        else:
            add_device_list.append(device_id)
            hostnames.append(device_df.loc[device_id,'hostname'])

    payload = {
        "name": ccg_df.loc[ccg_id,'name'],
        "description": ccg_df.loc[ccg_id,'description'],
        "device_ids": ids
    }
    filt = device_df

    
    if hostnames:
        if confirm_changes:
            print(f"\nThe following APs will be added to CCG {ccg_name}\n  ",end="")
            print(*hostnames, sep="\n  ")
            print("\n\n")
            response = yesNoLoop("Would you like to add these APs to the CCG?")
            if response == 'n':
                print(f"Ok, CCG edit will be skipped for CCG {ccg_name}.\n")
                continue
        print(f"\nStarting to add {str(len(add_device_list))} devices to CCG {ccg_name}")
        response = x.updateCCG(str(ccg_id), payload)
        if response != "Success":
            log_msg = (f"Failed to set the following devices to CGG {ccg_name}\n  ")
            sys.stdout.write(RED)
            sys.stdout.write(log_msg)
            print(*hostnames, sep='\n  ')
            sys.stdout.write(RESET)
            logging.error(log_msg + hostnames)
        else:
            sys.stdout.write(GREEN)
            print(f"Successfully added devices to CCG {ccg_name}")
            logger.info(f"Devices {hostnames} were added to CCG {ccg_name}")
            sys.stdout.write(RESET)
    
    