#!/bin/python
import discord
from discord.commands import permissions, Option
import yaml
import codecs
import sys
import subprocess
from subprocess import PIPE

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
bot = discord.Bot()
config = ConfigFileOperator()

# slash commands
# with guild_id in general.yml
for id_enable in config.get_guild_ids():

    #/ping
    @bot.slash_command(guild_ids=[id_enable])
    async def ping(ctx):
        """Pong!"""
        proc = subprocess.run("ping -c 2 -i 0.5 discord.com | sed -n -e 5p -e 7p ", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        await ctx.respond(proc.stdout)

    #/help
    @bot.slash_command(guild_ids=[id_enable])
    async def help(ctx):
        """Show the command list"""
        await ctx.respond("\
            `/ping`: Pong!\n\
            `/help`: show the command list\n\
            `/services`: Show the list of services.\n\
            `/status <service>`: Show the service's status.\n\
            ** With Permission**:\n\
            `/start <service>`: Start the service.\n\
            `/stop <service>`: Stop the service.\
            ")
    ##### with service list
    service_list = config.get_service_list(id_enable)

    #/services
    @bot.slash_command(guild_ids=[id_enable])
    async def services(ctx):
        """Show the list of services."""
        tmp = ''
        for service in service_list:
            tmp += service + "\n"
        await ctx.respond('```\n' + tmp + '```')

    ##### with service name

    #/status <service>
    @bot.slash_command(guild_ids=[id_enable])
    async def status(
        ctx,
        service: Option(str, "Service you want to check the status of", choices=service_list)
    ):
        """Show the service's status."""
        proc = subprocess.run(f"systemctl status {config.get_service(id_enable, service)}", shell=True, stdout=PIPE, stderr=PIPE, text=True)
        await ctx.respond("```\n" + proc.stdout + "\n```")

    ##### need permission

    roles=config.get_permitted_roles(id_enable)
    if len(roles) > 0:

        #/start <service>
        @bot.slash_command(guild_ids=[id_enable])
        @permissions.has_any_role(roles)
        async def start(
            ctx,
            service: Option(str, "Service you want to start", choices=service_list)
        ):
            """Start the service."""
            proc = subprocess.run(f"systemctl start {config.get_service(id_enable, service)}", shell=True, stdout=PIPE, stderr=PIPE, text=True)
            if proc.stderr:
                await ctx.respond("```\n" + proc.stderr + "\n```")
            else:
                await ctx.respond("Process was done. Check if it is active with`/ctl status`. ")

        #/stop <service>
        @bot.slash_command(guild_ids=[id_enable])
        @permissions.has_any_role(roles)
        async def stop(
            ctx,
            service: Option(str, "Service you want to stop", choices=service_list)
        ):
            """Stop the service."""
            try:
                proc = subprocess.run(f"systemctl stop {config.get_service(id_enable, service)}", shell=True, stdout=PIPE, stderr=PIPE, text=True,timeout=1)
            # respond timeout countermeasures
            except subprocess.TimeoutExpired as e:
                print(e)
                await ctx.respond("Process was timed out. Check if it is stoped with`/ctl status`. ")
                return
            if proc.stderr:
                await ctx.respond("```\n" + proc.stderr + "\n```")
            else:
                await ctx.respond("Process was done. Check if it is stoped with`/ctl status`. ")

bot.run(config.pass_token())