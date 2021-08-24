import logging
import subprocess
from subprocess import PIPE

import discord

from operation import general

logging.basicConfig(level=logging.INFO)

client = discord.Client()
config = general.ConfigFileOperator()

#Set error message.
error_Incorrect_configuration = 'Incorrect configuration: Either the config file does not exist or the format is different.'
error_Not_found = 'Not found: This service is not registered in the config file.'
error_Permission_denied_1 = 'Permission denied: This command can be executed by only administrator'
error_Permission_denied_2 = 'Permission denied: You do not have the role to use this command.'

# Global Function
def CheckPermission(User: discord.Member, ID: int):
    if User.guild_permissions.administrator:
        return True
    allowedRoles = config.getRoleList(ID)
    memberRoles = User.roles
    for memberRole in memberRoles:
        for allowedRole in allowedRoles:
            if memberRole.name == allowedRole:
                return True
    return False

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return


    # ctl.help : show the list of commands
    if message.content.startswith('ctl.help'):
        file = open('help.txt', 'r')
        description = file.read()
        await message.channel.send(description)


    # ctl.list : Show the list of services.
    if message.content.startswith('ctl.list'):
        server = message.guild.id
        if config.checkFileForm(server) == False:
            await message.channel.send('Either the config file does not exist or the format of the file is different.')
            return
        await message.channel.send(f'```\n{config.getServiceList(server)}\n```')

    # ctl.autoconfigcreate [role.name] : Create config yml file.
    if message.content.startswith('ctl.autoconfigcreate'):
        arg = message.content.replace("ctl.autoconfigcreate ", "")
        server = message.guild.id
        roles = arg.split()
        if message.author.guild_permissions.administrator:
            config.createNewServerConfig(server,roles)
            await message.channel.send(f'Created server config into config/{server}.yml .\nplease add some service name on the file.')
        else:
            await message.channel.send(error_Permission_denied_1)
    
    # ctl.status <service.name> : Show the service's status.
    if message.content.startswith('ctl.status'):
        arg = message.content.replace("ctl.status ", "")
        if arg == '':
            message.channel.send('Please type service name.')
            return
        server = message.guild.id
        if config.checkFileForm(server) == False:
            await message.channel.send(error_Incorrect_configuration)
            return
        services = config.getServiceList(server)
        if arg in services:
            command = f'sudo systemctl status {arg}'
            proc = subprocess.run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            result = proc.stdout
            await message.channel.send(f'```\n{result}\n```')
        else:
            await message.channel.send(error_Not_found)

    # ctl.start <service.name> : Start the service.
    if message.content.startswith('ctl.start'):
        server = message.guild.id
        if config.checkFileForm(server) == False:
            await message.channel.send(error_Incorrect_configuration)
            return
        
        if CheckPermission(message.author, server) == False:
            await message.channel.send(error_Permission_denied_2)
            return
        
        arg = message.content.replace("ctl.start ", "")
        if arg == '':
            message.channel.send('Please type service name.')
            return

        services = config.getServiceList(server)
        if arg in services:
            command = f'sudo systemctl start {arg}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'Service was failed to start with error code {result}. \nplease use `ctl.status {arg}` to see status.')
            else:
                await message.channel.send(f'Done!\nplease use `ctl.status {arg}` to see status.')
        else:
            await message.channel.send(error_Not_found)
    
    # ctl.restart <service.name> : Restart the service.
    if message.content.startswith('ctl.restart'):
        server = message.guild.id
        if config.checkFileForm(server) == False:
            await message.channel.send(error_Incorrect_configuration)
            return

        if CheckPermission(message.author, server) == False:
            await message.channel.send(error_Permission_denied_2)
            return
        
        arg = message.content.replace("ctl.restart ", "")
        if arg == '':
            message.channel.send('Please type service name.')
            return

        services = config.getServiceList(server)
        if arg in services:
            command = f'sudo systemctl retart {arg}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'Service was failed to retart with error code {result}. \nplease use `ctl.status {arg}` to see status.')
            else:
                await message.channel.send(f'Done!\nplease use `ctl.status {arg}` to see status.')
            return
        else:
            await message.channel.send(error_Not_found)

    # ctl.stop <service.name> : Stop the service.
    if message.content.startswith('ctl.stop'):
        server = message.guild.id
        if config.checkFileForm(server) == False:
            await message.channel.send(error_Incorrect_configuration)
            return

        if CheckPermission(message.author, server) == False:
            await message.channel.send(error_Permission_denied_2)
            return
        
        arg = message.content.replace("ctl.stop ", "")
        if arg == '':
            message.channel.send('Please type service name.')
            return

        services = config.getServiceList(server)
        if arg in services:
            command = f'sudo systemctl stop {arg}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'Service was failed to stop with error code {result}. \nplease use `ctl.status {arg}` to see status.')
            else:
                await message.channel.send(f'Done!\nplease use `ctl.status {arg}` to see status.')
        else:
            await message.channel.send(error_Not_found)


client.run(config.passToken())