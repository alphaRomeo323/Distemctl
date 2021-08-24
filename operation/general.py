import sys
import os
import subprocess
import codecs
import yaml

class ConfigFileOperator:
    loadedToken = ''
    configDirectory = 'config'

    def __init__(self):
        try:
            #print(subprocess.run("ls", shell=True).stdout) #debug
            with open(f'{self.configDirectory}/general.yml') as file:
                yml = yaml.safe_load(file)
                self.loadedToken = yml['token']
        except Exception as e:
            print('Exception occurred while loading general.yml...', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)

    def passToken(self):
        return self.loadedToken
    
    def checkFileForm(self, ID: int):
        if os.path.isfile(f'{self.configDirectory}/{ID}.yml') == False:
            print(f'{ID}.yml does not exist...')
            return False
        with open(f'{self.configDirectory}/{ID}.yml') as file:
            try:
                yml = yaml.safe_load(file)
                print(yml['Service'])
                print(yml['Role'])
            except Exception as e:
                print(f'Exception occurred while loading {ID}.yml...', file=sys.stderr)
                print(e, file=sys.stderr)
                return False
        return True

    def createNewServerConfig(self, ID: int, AllowedRole: list):
        yml = {'Service': [''], 'Role': AllowedRole}
        with codecs.open(f'{self.configDirectory}/{ID}.yml', 'w', 'utf-8') as f:
            yaml.dump(yml, f, encoding='utf-8', allow_unicode=True)

    def getServiceList(self, ID: int):
        with open(f'{self.configDirectory}/{ID}.yml') as file:
            yml = yaml.safe_load(file)
            return yml['Service']
    
    def getRoleList(self, ID: int):
        with open(f'{self.configDirectory}/{ID}.yml') as file:
            yml = yaml.safe_load(file)
            return yml['Role']
    