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
