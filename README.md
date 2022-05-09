# SUS-skins-bot
Unofficial bot for publishing skins for SUS Horror.

# Features
The bot accepts .png or GIF images with a signature of the ```<name>|<description>|<author>``` format. <br/>
After the administrator accepts the skin, all bot users can see it.

# Commands list
```help``` - Shows all available commands. <br/>
```list``` - Shows list of all skins. <br/>
```skin <id>``` - Shows skin by id. <br/>
```credits``` - Shows all skins authors. Comibg soon. <br/>
```approve-all <Administrator password>``` - Approves all new skins. <br/>
```refresh <Administrator password>``` - Refreshes all skins data. <br/>

# Installation

Install python3: <br/>
Windows: https://www.python.org/downloads/. <br/>
Linux: install it using your favorite package manager in your favorite OS.

Install dependencies:
```
pip install pytelegrambotapi
```

Then create new bot in BotFather, configure it as you want and paste token in config file.

# config.py
```
token = "<token>"
admin_pass = "<Administrator password>"
```
