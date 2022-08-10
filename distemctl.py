#!/bin/python
from http import client
import discord
import yaml
import codecs
import sys
import subprocess
from subprocess import PIPE


# var

PREFIX = "ctl."
TIMEOUT = 5 #sec
COMMANDS = ["help","ping","services","status","start","restart","stop"]
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

error_unknown_guild = "This server is not listed in config."
error_Permission_denied = "Permission denied: You do not have the role to use this command."

#Class
### load general.yml
class ConfigFileOperator:
    configDirectory = 'config'

    def __init__(self):
        try:
            #print(subprocess.run("ls", shell=True).stdout) #debug
            with open(f'{self.configDirectory}/general.yml') as file:
                self.yml = yaml.safe_load(file)
        except Exception as e:
            print('Exception occurred while loading general.yml...', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)

    # get token
    def pass_token(self):
        return self.yml['token']

    #get guild_id
    def get_guild_ids(self):
        guild_list=[]
        for guild_data in self.yml['guilds']:
            guild_list.append(guild_data['id'])
        return guild_list

    # get role names
    def get_permitted_roles(self, guild_id):
        role_list=[]
        for guild_data in self.yml['guilds']:
            if guild_data['id'] == guild_id:
                try:
                    return guild_data['permitted_roles']
                except:
                    print('Exception occurred while loading general.yml...')
                    return []

    # get systemd service name
    def get_service(self, guild_id, masked_service):
        role_list=[]
        for guild_data in self.yml['guilds']:
            if guild_data['id'] == guild_id:
                try:
                    return guild_data['services'][masked_service]
                except:
                    print(f"'{masked_service}' is not found")
                    return ''

    # get list of services
    def get_service_list(self, guild_id):
        for guild_data in self.yml['guilds']:
            if guild_data['id'] == guild_id:
                try:
                    return list(guild_data['services'].keys())
                except:
                    print('Exception occurred while loading general.yml...')
                    return []

# add objects
client = discord.Client(intents=intents)
config = ConfigFileOperator()

# Global Function
def parse_arg(message: str):
    return message.split()[1:] #split message and remove first

def check_permission(User: discord.Member, ID: int):
    if User.guild_permissions.administrator:
        return True
    allowedRoles = config.get_permitted_roles(ID)
    memberRoles = User.roles
    for memberRole in memberRoles:
        if memberRole.name in allowedRoles:
            return True
    return False


# commands

@client.event
async def on_message(message):
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
    
    # PREFIX+ping : Pong!
    if message.content.startswith(PREFIX+'ping'):
        proc = subprocess.run("ping -c 1 -i 0.5 discord.com | sed -n -e 5p -e 7p ", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        await message.channel.send(proc.stdout)
        return

    ##### with service list
    service_list = config.get_service_list(message.guild.id)
    if not service_list:
        await message.channel.send(error_unknown_guild)
        return
    
    # PREFIX+services : Show the list of services.
    if message.content.startswith(PREFIX+'services'):
        tmp = ''
        for service in service_list:
            tmp += service + "\n"
        await message.channel.send('```\n' + tmp + '```')
        return
    
    ##### with service name
    args = parse_arg(message.content)
    if len(args) == 0:
        await message.channel.send('Please type service name.')
        return
    service = config.get_service(message.guild.id, args[0])
    if not service:
        await message.channel.send(f'Not found: {args[0]} service is not registered in the config file.')
        return

    
    # PREFIX+status : Show the service status.
    if message.content.startswith(PREFIX+'status'):
        proc = subprocess.run(f"systemctl status {service}", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        await message.channel.send('```\n' + proc.stdout + '```')
        return
    
    ##### need permission
    if not check_permission(message.author,message.guild.id):
            await message.channel.send(error_Permission_denied)
            return
    
    # PREFIX+start <service.name> : Start the service.
    if message.content.startswith(PREFIX+'start'):
            try:
                proc = subprocess.run(f"sudo systemctl start {service}", shell=True, stdout=PIPE, stderr=PIPE, text=True,timeout=TIMEOUT)
            # respond timeout countermeasures
            except subprocess.TimeoutExpired as e:
                print(e)
                await message.channel.send("Process was timed out. Check if it is stoped with`/ctl status`. ")
                return
            if proc.stderr:
                await message.channel.send("```\n" + proc.stderr + "\n```")
            else:
                await message.channel.send("Process was done. Check if it is stoped with`/ctl status`. ")
            return
    
    # PREFIX+restart <service.name> : Restart the service.
    if message.content.startswith(PREFIX+'restart'):
            try:
                proc = subprocess.run(f"sudo systemctl restart {service}", shell=True, stdout=PIPE, stderr=PIPE, text=True,timeout=TIMEOUT)
            # respond timeout countermeasures
            except subprocess.TimeoutExpired as e:
                print(e)
                await message.channel.send("Process was timed out. Check if it is stoped with`/ctl status`. ")
                return
            if proc.stderr:
                await message.channel.send("```\n" + proc.stderr + "\n```")
            else:
                await message.channel.send("Process was done. Check if it is stoped with`/ctl status`. ")
            return

    # PREFIX+stop <service.name> : Stop the service.
    if message.content.startswith(PREFIX+'stop'):
            try:
                proc = subprocess.run(f"sudo systemctl stop {service}", shell=True, stdout=PIPE, stderr=PIPE, text=True,timeout=TIMEOUT)
            # respond timeout countermeasures
            except subprocess.TimeoutExpired as e:
                print(e)
                await message.channel.send("Process was timed out. Check if it is stoped with`/ctl status`. ")
                return
            if proc.stderr:
                await message.channel.send("```\n" + proc.stderr + "\n```")
            else:
                await message.channel.send("Process was done. Check if it is stoped with`/ctl status`. ")
            return

client.run(config.pass_token())