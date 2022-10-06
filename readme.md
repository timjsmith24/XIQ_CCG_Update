# XCQ - Add devices in a building to CCG(s)
## XIQ_CCG_update.py
### Purpose
This script will collect devices for all floors of a building and make sure they are added to a single or multiple CCGs

### Needed files
The XIQ_CCG_update.py script uses several other files. If these files are missing the script will not function.
In the same folder as the XIQ_CCG_update.py script there should be an /app/ folder. Inside this folder should be a ccg_logger.py and a xiq_ccg_api.py script. After running the script a new file 'ccg_importer.log will be created.


## User input
The script will prompt user for needed information. 
This includes:
- XIQ user credentials
- Name of building to collect devices from
- name(s) of the CCG(s) 
>Note: if multiple CCGs are needed, seperate the names with a comma
- yes/no questions - preview changes before being made, proceeding with change, etc

## included files
## Log file
upon running the script a ccg_importer.log file will be created. This file will include information about errors if encountered and will list the names of the APs that are moved.

### flags
There is an optional flag that can be added to the script when running.
```
--external
```
This flag will allow you to collect the locations, devices, and CCGs and then move Devices into CCGs on an XIQ account you are an external user on. After logging in with your XIQ credentials the script will give you a numeric option of each of the XIQ instances you have access to. Choose the one you would like to use.

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
