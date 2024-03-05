#!/usr/bin/env python3
from genericpath import isfile
import json
import logging
import os
import subprocess

################### Configurations ###########################
# Path to the logfile, make sure path exists
LOG_FILE = "/var/log/smart-monitoring/smart-monitoring.log"
# Statefile that saves the latest state of the smart data, make sure path exists
STATE_FILE = "/var/log/smart-monitoring/smart-monitoring.state"
# E-Mail address to send the mails to and from
TO_ADDR = "tgotowik@example.com"
FROM_ADDR = ""
# smartctl attributes from the table, you want to exclude from the monitoring
EXCLUDE_ATTRIBUTES = ["Airflow_Temperature_Cel", "temperature"]
# Type of drives you want to exlucde: Defaults: loop, zram, part, rom
EXCLUDE_DRIVES_TYPES = ["loop", "part", "zram", "rom"]
# Drives you want to exclude from monitoring
EXCLUDE_DRIVES = ["sdc"]
# This is the indicator of how close the value can come to the threshold
THRESHOLD_LIMIT = 10
##############################################################


def getDrives():
    """Execute the lsblk command to filter out drives to monitor

    Returns:
        list: drives names
    """
    drive_list = list()
    # Run the lsblk command and capture its output
    result = subprocess.run(['lsblk', '--output', 'NAME,TYPE', '--nodeps', '--json'], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        logging.ERROR("Error running lsblk command: {}".format(result.stderr))
        return drive_list
    
    # Parse the JSON output
    try:
        lsblk_info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logging.ERROR("Error parsing lsblk output: {}".format(e))
        return drive_list

    for lsblk_item in lsblk_info["blockdevices"]:
        if lsblk_item["type"] not in EXCLUDE_DRIVES_TYPES and lsblk_item["name"] not in drive_list:
            drive_list.append(lsblk_item["name"])

    return drive_list

def getSmartData(drives):
    """Execute smartctl command and process the data into a dictionary

    Args:
        drives (list): drives names

    Returns:
        dict: drive_name mapped to its smartctl output
    """
    smartctl_info = {}
    # Get smartctl info per drive
    for drive in drives:
        if drive not in EXCLUDE_DRIVES:
            try:
                command = ["sudo", "smartctl", "-A", "-H", f"/dev/{drive}", "--json"]
                result = subprocess.run(command, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                logging.ERROR(f"Error occured on getSmartdata: {e}")

            # Parse the JSON output
            try:
                smartctl_info[drive] = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logging.ERROR("Error parsing smartctl output: {}".format(e))
                return smartctl_info

    # Exclude attributes, remove them from dict        
    for attribute_to_delete in EXCLUDE_ATTRIBUTES:
        for drive in smartctl_info:
            if attribute_to_delete in smartctl_info[drive]:
                del smartctl_info[drive][attribute_to_delete]

    return smartctl_info   

# Pretty Print JSON string
def pprint(data):
    print(json.dumps(data, indent=4))

def writeStateFile(smart_data):
    """write state to file

    Args:
        smart_data (dict): actual state data
    """
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(smart_data, f)
    except Exception as e:
        logging.ERROR(f"Error writeStateData: {e}")

def readStateFile():
	if isfile(STATE_FILE):
		try:
			with open(STATE_FILE, 'r') as f:
				state_data = json.load(f)
			return state_data
		
		except Exception as e:
			logging.ERROR(f"Error reading STATE_FILE: {e}")

	else:
		return dict()

def compareSmartData(current_smart_data):
     diff = {}

     return diff

def checkThreshold():
     return None

if __name__ == "__main__":
    """Main entry point of the script
    """
    
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    drives = getDrives()
    smart_data = getSmartData(drives)
    writeStateFile(smart_data)
    pprint(readStateFile())