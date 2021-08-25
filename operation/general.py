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

    def pass_token(self):
        return self.loadedToken
    
    def check_file_form(self, ID: int):
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

    def create_new_server_config(self, ID: int, AllowedRole: list):
        yml = {'Service': {"control_name": "service_name"}, 'Role': AllowedRole}
        with codecs.open(f'{self.configDirectory}/{ID}.yml', 'w', 'utf-8') as f:
            yaml.dump(yml, f, encoding='utf-8', allow_unicode=True)

    def get_service_list(self, ID: int):
        with open(f'{self.configDirectory}/{ID}.yml') as file:
            yml = yaml.safe_load(file)
            return yml['Service']
    
    def get_role_list(self, ID: int):
        with open(f'{self.configDirectory}/{ID}.yml') as file:
            yml = yaml.safe_load(file)
            return yml['Role']
    