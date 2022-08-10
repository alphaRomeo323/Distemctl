# Distemctl

This bot can remotely manipulate the systemd services of a server.

it is written by python.

## Usage(easy)

1. install python3, PyYAML and Discord.py(Latest Dev).
2. open config/general.yml, fill blanks(bot token,guild_id,role names,service_name)
3. create and edit /etc/sudoers.d/distemctl, you can use following template
```
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl start service_name
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl stop service_name
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl status service_name
```
4. inivite the bot to server
5. run `python3 distemctl.py`


## Development

Distemctl is in development, feel free to:

* file bugs using issues
* pushing new futures / bug fixes with pull requests

## Special Thanks

* ozraru  
  Refacted source code.
