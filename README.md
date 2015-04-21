# HRlo (aka accaerralo)

[![](https://raw.githubusercontent.com/wiki/so07/HRlo/zucchetti.png)](https://www.youtube.com/watch?v=8Cfo06DvA5M)

## INSTALL:
```
git clone https://github.com/so07/HRlo.git
cd HRlo
sudo python3 setup.py install
```

## SIMPLE USAGE:

- print help
```
accaerralo -h 
HRlo -h
```

- Today report
```
accaerralo -u USER -i IDEMPLOY -a hr.HOST.org
Password:
```
- Save authentication options to default config file
```
accaerralo -u USER -i IDEMPLOY -a hr.HOST.org -s
```
- Save authentication options to a config file
```
accaerralo -u USER -i IDEMPLOY -a hr.HOST.org -s -c CONFIG_FILE
```
- Weekly report:
```
accaerralo -w
```
- Monthly report:
```
accaerralo -m
```
