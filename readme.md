# Distemctl

This bot can remotely manipulate the systemd services of a server.

it is written by python.

## Usage(easy)

1. install python3, PyYAML and Discordpy.
2. open config/general.yml, fill blanks(bot token)
3. run `python3 distemctl.py`
4. inivite the bot to server
5. use `ctl.autoconigcreate [role.name]`(Administrator only)
6. open config/server_id.yml, fill blanks(service name to control)
7. create and edit /etc/sudoers.d/distemctl, you can use following template
```
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl start service_name
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl restart service_name
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl stop service_name
run_user ALL=(root) NOPASSWD: /usr/bin/systemctl status service_name
```

## Development

Distemctl is in development, feel free to:

* file bugs using issues
* pushing new futures / bug fixes with pull requests

## Special Thanks

* ozraru
  Refacted source code.

## コマンドリファレンス(Japanese)

you can see the english reference to use `ctl.help`

### ctl.help

使用可能なコマンドリストを表示します

### ctl.list

操作可能なサービスの一覧を表示します

### ctl.status service.name

systemctl statusコマンドを実行し、結果を表示します。

### ctl.start service.name

systemctl startコマンドを用いてサービスを起動させます。
許可されたロールまたは管理者権限を持つ方のみ使用できます。

### ctl.restart service.name

systemctl restartコマンドを用いてサービスを再起動させます。
許可されたロールまたは管理者権限を持つ方のみ使用できます。

### ctl.stop service.name

systemctl stopコマンドを用いてサービスを停止させます。
許可されたロールまたは管理者権限を持つ方のみ使用できます。

### ctl.autoconfigcreate [role.name]

サーバーコンフィグを上書き生成します。生成されたコンフィグファイルは`config/<server.id>.yml`となります。
管理者権限を持つ方のみ使用できます。