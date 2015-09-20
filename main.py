#! python3

from filecmp import cmp, clear_cache
from configparser import ConfigParser
import shutil
import os

import requests


# Check if config is present
def check_config():
    if os.path.isfile("config.ini"):
        config = ConfigParser()
        config.read("config.ini")
        bol_path = config.get('paths', 'bol', raw=True)
        scripts_path = bol_path + 'Scripts\\'
        common_path = scripts_path + 'Common\\'
    else:
        print("Config not found!")
        conf = ConfigParser()
        conf['paths'] = {'bol': os.getcwd()}
        conf['scripts'] = {'Jinx': 'https://raw.githubusercontent.com/RalphLeague/BoL/master/Jinx.lua'}
        conf['common'] = {
            'SxOrbWalk.lua': 'https://raw.githubusercontent.com/Superx321/BoL/master/common/SxOrbWalk.lua'}
        with open("config.ini", 'w') as config_file:
            conf.write(config_file)
        print("Config file created. Check config.ini and edit it if necessary.")
        input('Press enter to exit')
        exit()
    return config, scripts_path, common_path


# Download and compare remote files against local files
def update(section, path):
    # Define User-Agent header, for compatibility with some servers
    user_agent = {'User-agent': 'Mozilla/5.0'}

    for option in config.options(section):
        # Get file from URL to temp file.
        req = requests.get(config.get(section, option, raw=True), headers=user_agent)
        with open("tmp.lua", "wb") as tmp:
            tmp.write(req.content)
        tmp.close()

        # Add .lua extension if not present.
        if ".lua" not in option:
            option = option + ".lua"

        # Check and compare files in a simple if-else
        if not os.path.isfile(path + option):
            print("No file! Copying " + option)
            shutil.copyfile("tmp.lua", path + option)
        elif cmp("tmp.lua", path + option, shallow=False):
            print("Files identical! " + option)
        else:
            print('Files differ! Copy newer file! ' + option)
            shutil.copyfile("tmp.lua", path + option)
    return "Ok"


# Call all the functions!
config, scripts_path, common_path = check_config()
update('scripts', scripts_path)
update('common', common_path)


# Cleanup and exit
clear_cache()
os.remove("tmp.lua")
print("All done!")
input('Press enter to Exit')
