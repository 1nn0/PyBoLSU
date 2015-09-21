#! python3

from filecmp import cmp, clear_cache
from configparser import ConfigParser
import shutil
import os

import workerpool
import requests


# Check if config is present
# TODO: логика дубовая, всю эту функцию переработать надо.
def check_config():

    scripts_path = ""
    common_path = ""


    if os.path.isfile("config.ini"):
        config = ConfigParser()
        config.read("config.ini")
        bol_path = config.get('paths', 'bol', raw=True)
        scripts_path = bol_path + 'Scripts\\'
        common_path = scripts_path + 'Common\\'

    else:
        # Very stupid config generation
        # TODO Сделать нормальный генератор конфига, в зависимости от скриптов у пользователя.
        print("Config not found!")
        conf = ConfigParser()
        conf['paths'] = {'bol': os.getcwd()}
        conf['scripts'] = {'Jinx': 'https://raw.githubusercontent.com/RalphLeague/BoL/master/Jinx.lua'}
        conf['common'] = {'SxOrbWalk.lua': 'https://raw.githubusercontent.com/Superx321/BoL/master/common/SxOrbWalk.lua'}
        with open("config.ini", 'w') as config_file:
            conf.write(config_file)
        print("Config file created. Check config.ini and edit it if necessary.")
        input('Press enter to exit')
        exit()
    return config, scripts_path, common_path


def gen_config():
    scripts = {}
    libs = {}
    bol = os.getcwd()
    bol_scripts = bol + '\\\\Scripts'
    bol_libs = bol_scripts + '\\\\Common'
    database=ConfigParser()
    database.read("config.ini")
    scripts_base = dict(database.items('scripts', raw=True))
    libs_base = dict(database.items('common', raw=True))

    for script in os.listdir(bol_scripts):
        if os.path.isfile(bol_scripts + '\\' + script):
            scripts[script.lower()] = ''

    for lib in os.listdir(bol_libs):
        if os.path.isfile(bol_libs + '\\' + lib):
            libs[lib.lower()] = ''

    for key in libs.keys():
        for key1 in libs_base.keys():
            if key == key1:
                libs[key] = libs_base[key]

    for key in scripts.keys():
        for key1 in scripts_base.keys():
            if key == key1:
                scripts[key] = scripts_base[key]

    config = ConfigParser()
    config['paths'] = {'bol' : bol}
    config['scripts'] = scripts
    config['common'] = libs

    with open("test.ini", "w") as test:
        config.write(test)


# Main logic of a job
class Updater(workerpool.Job):
    def __init__(self, script, url, path):
        self.script = script
        self.path = path
        self.url = url

    def run(self):
        # Define user-agent header. This is needed for compatibility with some servers
        user_agent = {'User-agent': 'Mozilla/5.0'}
        tmp_name = self.script
        # Downloading file...
        req = requests.get(self.url, headers=user_agent)
        with open(tmp_name, "wb") as tmp:
            tmp.write(req.content)

        # TODO: работа с архивами (Evadee, DivinePrediction) лучше универсальную.

        # ... checking if it exists and comparing with a downloaded one.
        if not os.path.isfile(self.path + self.script):
            print("No file! Copying " + self.script)
            shutil.copyfile(tmp_name, self.path + self.script)
        elif cmp(tmp_name, self.path + self.script, shallow=False):
            print("Files identical! " + self.script)
        else:
            print('Files differ! Copy newer file! ' + self.script)
            shutil.copyfile(tmp_name, self.path + self.script)

        # cleaning
        tmp.close()
        os.remove(tmp_name)


# I don't like it here.
pool = workerpool.WorkerPool(size=10)


# Get script name and URL from config and put a job in the pool
def update(section, path):
    for option in config.options(section):
        work = Updater(option, config.get(section, option, raw=True), path)
        pool.put(work)


# Call all the functions!
config, scripts_path, common_path = check_config()
update('scripts', scripts_path)
update('common', common_path)

# Cleanup and exit
clear_cache()
pool.shutdown()
pool.wait()
print(os.listdir(scripts_path))
print("All done!")
input('Press enter to Exit')
