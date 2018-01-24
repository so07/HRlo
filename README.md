# HRlo (aka accaerralo)

HR manager

[![](https://raw.githubusercontent.com/wiki/so07/HRlo/zucchetti.png)](https://www.youtube.com/watch?v=8Cfo06DvA5M)

### INSTALL
```
sudo pip3 install HRlo
```

```
git clone https://github.com/so07/HRlo.git
cd HRlo
sudo python3 setup.py install
```

### USAGE

###### help
```
accaerralo -h 
HRlo -h
```

###### Simple usage for today report
```
accaerralo -u USER -i IDEMPLOY -a HR_COMPANY_URL
Password:
```


#### Authentication options

###### Save authentication options to default config file
```
accaerralo -u USER -i IDEMPLOY -a HR_COMPANY_URL -s
```
###### Save authentication options to a config file
```
accaerralo -u USER -i IDEMPLOY -a HR_COMPANY_URL -s -c CONFIG_FILE
```
###### Save also password to default config file
```
accaerralo -u USER -i IDEMPLOY -a HR_COMPANY_URL -s --save-password
```

#### Reports

###### Daily report
```
accaerralo -d
```
###### Weekly report
```
accaerralo -w
```
###### Monthly report
```
accaerralo -m
```
###### Monthly report week by week
```
accaerralo -M
```
###### Include today in reports
```
accaerralo -mw -t
```
###### Report for a range of days
```
accaerralo --from YYYY-MM-DD --to YYYY-MM-DD
```

#### Phone numbers

###### Get phone number from worker name
```
accaerralo -p SURNAME
```

###### Get worker name from phone number
```
accaerralo -n PHONE_NUMBER
```

#### Worker presence

```
accaerralo --in SURNAME
```

#### Worker totalizators

```
accaerralo --tot
```



## `HRlo` Telegram bot, aka `HRbot`

This wiki is about how to create and run a `HRlo` bot in [Telegram](https://telegram.org/)

### Create a Telegram bot

Talk to [@BotFather](https://telegram.me/botfather) and type `/newbot` for a new bot and follow the instructions
```
you:
/newbot

BotFather:
Alright, a new bot. How are we going to call it? Please choose a name for your bot.

you:
HRlo

BotFather:
Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

you:
HRlo_bot

BotFather:
....

Use this token to access the HTTP API:
TOKEN
```
Save the TOKEN and paste it in the token key of HRbot section in the HRlo configuration file
```
$ vi ~/.HRlo
```

```
[HRauth]
...
[HRbot]
token = TOKEN
```

### Run `HRbot`

Launch `HRbot` executable on a server with a working installation of `HRlo`
```
$ HRbot
```
Open Telegram App or go to [Telegram Web](https://web.telegram.org) in a browser and start talk with `HRlo` bot.

### Talk with `HRbot`

List of simple commands to run in telegram bot.

help of commands
```
/help
```
 launch simple inline button interface
```
/hrlo
```
 estimated exit times report
 ```
 /exit
 ```
 today times report
 ```
 /time
 ```
 today time stamps report
 ```
 /stamp
 ```
 check status of worker
 ```
 /in name [name ...]
 ```
 get worker's phone number
 ```
 /phone name [name ...]
 ```
 get worker's name from a phone number
 ```
 /name 12345 [12345 ...]
 ```


