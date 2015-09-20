from filecmp import cmp, clear_cache
import requests
from configparser import ConfigParser
import shutil
import os

#Check if config is present
if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")
    bolPath = config.get('paths', 'bol', raw=True)
else:
    print("Config not found!")
    exit()

#Define User-Agent header, for compatibility with some servers
user_agent = {'User-agent' : 'Mozilla/5.0'}

#Download and ompare remote files against local files
for option in config.options('scripts'):
    #Get file from URL to temp file.
    req = requests.get(config.get('scripts', option, raw=True), headers = user_agent)
    with open("tmp.lua", "wb") as tmp:
        tmp.write(req.content)
    tmp.close()

    #Add .lua extension if not present.
    if ".lua" not in option:
        option = option + ".lua"

    # Check and compare files in a simple if-else
    if not os.path.isfile(bolPath + option):
        print("No file! Copying")
        shutil.copyfile("tmp.lua", bolPath + option)
    elif cmp("tmp.lua", bolPath + option, shallow=False):
        print("Files identical! " + option)
    else:
        print('Files differ! Copy newer file! ' + option)
        shutil.copyfile("tmp.lua", bolPath + option)

#Cleanup and exit
clear_cache()
os.remove("tmp.lua")
print("All done!")
input('Press enter to Exit')
