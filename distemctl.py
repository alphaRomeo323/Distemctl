from io import StringIO
import logging
import subprocess
from subprocess import PIPE

import discord

from operation import general

logging.basicConfig(level=logging.INFO)

PREFIX = "ctl."
COMMANDS = ["help","autoconfigcreate","list","status","status-file","start","restart","stop"]

client = discord.Client()
config = general.ConfigFileOperator()

#Set error message.
error_Incorrect_configuration = 'Incorrect configuration: Either the config file does not exist or the format is different.'
error_Permission_denied_1 = 'Permission denied: This command can be executed by only administrator'
error_Permission_denied_2 = 'Permission denied: You do not have the role to use this command.'
error_over_length_message = f'Too large: Result is more than 2000 characters. To send by file, {PREFIX}status-file'

# Global Function
def check_permission(User: discord.Member, ID: int):
    if User.guild_permissions.administrator:
        return True
    allowedRoles = config.get_role_list(ID)
    memberRoles = User.roles
    for memberRole in memberRoles:
        if memberRole.name in allowedRoles:
            return True
    return False

def parse_arg(message: str):
    return message.split()[1:] #split message and remove first

def convert_services(args: list, server_id: int) -> list[str]:
    valid_services = config.get_service_list(server_id)
    args_services: list = []
    for arg in args:
        if arg in valid_services:
            args_services.append(valid_services[arg])
        else:
            raise KeyError(arg)
    return args_services


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(PREFIX):
        return

    # When add command, you should add to COMMANDS in start of file

    if not message.content.split()[0].replace(PREFIX, "") in COMMANDS:
        await message.channel.send("Command not found")
        return

    # PREFIX+help : show the list of commands
    if message.content.startswith(PREFIX+'help'):
        file = open('help.txt', 'r')
        description = file.read()
        await message.channel.send(description)
        return

    # PREFIX+autoconfigcreate [role.name] : Create config yml file.
    if message.content.startswith(PREFIX+'autoconfigcreate'):
        args = parse_arg(message.content)
        if message.author.guild_permissions.administrator:
            config.create_new_server_config(message.guild.id,args)
            await message.channel.send(f'Created server config into config/{message.guild.id}.yml .\nplease add some service name on the file.')
        else:
            await message.channel.send(error_Permission_denied_1)
        return
    
    ##### need config
    
    if config.check_file_form(message.guild.id) == False:
        await message.channel.send(error_Incorrect_configuration)
        return

    # PREFIX+list : Show the list of services.
    if message.content.startswith(PREFIX+'list'):
        await message.channel.send(f'```\n{config.get_service_list(message.guild.id).keys()}\n```')
        return
    
    ##### with service name

    try:
        args = parse_arg(message.content)
        if len(args) == 0:
            await message.channel.send('Please type service name.')
            return
        services = convert_services(args, message.guild.id) # raise keyerror when not found in config
    except KeyError as e:
        await message.channel.send(f'Not found: {e} service is not registered in the config file.')
        return

    # PREFIX+status <service.name> : Show the service's status.
    if message.content.startswith(PREFIX+'status'):
        file: bool = message.content.startswith(PREFIX+'status-file')
        for service in services:
            command = f'sudo systemctl status {service}'
            proc = subprocess.run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            result = proc.stdout
            if file:
                result_file: discord.File = discord.File(StringIO(result), filename=service+".txt")
                await message.channel.send("", file=result_file)
            else:
                if len(f'```\n{result}\n```') > 2000:
                    await message.channel.send(error_over_length_message)
                    return
                await message.channel.send(f'```\n{result}\n```')
        return

    ##### need permission

    if check_permission(message.author, message.guild.id) == False:
        await message.channel.send(error_Permission_denied_2)
        return

    # PREFIX+start <service.name> : Start the service.
    if message.content.startswith(PREFIX+'start'):
        for service in services:
            command = f'sudo systemctl start {service}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'{service} was failed to retart with error code {result}. \nplease use `{PREFIX}status {" ".join(args)}` to see status.')
                return
        
        await message.channel.send(f'Done!\nplease use `{PREFIX}status {" ".join(args)}` to see status.')
        return
    
    # PREFIX+restart <service.name> : Restart the service.
    if message.content.startswith(PREFIX+'restart'):
        for service in services:
            command = f'sudo systemctl restart {service}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'{service} was failed to retart with error code {result}. \nplease use `{PREFIX}status {" ".join(args)}` to see status.')
                return
        
        await message.channel.send(f'Done!\nplease use `{PREFIX}status {" ".join(args)}` to see status.')
        return

    # PREFIX+stop <service.name> : Stop the service.
    if message.content.startswith(PREFIX+'stop'):
        for service in services:
            command = f'sudo systemctl stop {service}'
            result = subprocess.run(command, shell=True).returncode
            if result != 0:
                await message.channel.send(f'{service} was failed to retart with error code {result}. \nplease use `{PREFIX}status {" ".join(args)}` to see status.')
                return
        
        await message.channel.send(f'Done!\nplease use `{PREFIX}status {" ".join(args)}` to see status.')
        return


client.run(config.pass_token())