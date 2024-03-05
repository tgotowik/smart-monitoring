#!/usr/bin/env python3
import json
import logging
import subprocess

################### Configurations ###########################
# Path to the logfile
LOG_FILE = "./log"
# E-Mail address to send the mails to and from
TO_ADDR = "tgotowik@example.com"
FROM_ADDR = ""
# Attributes you want to exclude from the monitoring
EXCLUDE_ATTRIBUTES = ["Power_On_Hours", "Power_Cycle_Count","Airflow_Temperature_Cel"]
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
        print("Error running lsblk command: {}".format(result.stderr))
        return drive_list
    
    # Parse the JSON output
    try:
        lsblk_info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Error parsing lsblk output: {}".format(e))
        return drive_list

    for lsblk_item in lsblk_info["blockdevices"]:
        if lsblk_item["type"] not in EXCLUDE_DRIVES_TYPES and lsblk_item["name"] not in drive_list:
            drive_list.append(lsblk_item["name"])

    return drive_list
    

if __name__ == "__main__":
    """Main entry point of the script
    """
    
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    drives = getDrives()
    print(drives)