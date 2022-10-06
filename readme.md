# XCQ - Add devices in a building to CCG(s)
## XIQ_CCG_update.py
###
This script will collect devices for all floors of a building and make sure they are added to a single or multiple CCGs

## User input
The script will prompt user for needed information. 
This includes:
- XIQ user credentials
- Name of building to collect devices from
- name(s) of the CCG(s) 
>Note: if multiple CCGs are needed, seperate the names with a comma
- yes/no questions - preview changes before being made, proceeding with change, etc

## Log file
upon running the script a ccg_importer.log file will be created. This file will include information about errors if encountered and will list the names of the APs that are moved.

## Requirements
the following modules will need to be installed in order for the python script to run.
```
requests
pandas
```
there is a requirements.txt file included that lists these modules. The txt file can also be used to install the modules using pip
```
pip install -r requirements.txt
```
