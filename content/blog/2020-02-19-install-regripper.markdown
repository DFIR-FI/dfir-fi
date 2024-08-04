---
layout: post
title:  "[0x4] Installing RegRipper on Linux"
subtitle: "https://github.com/keydet89/RegRipper2.8.git"
date:   2020-02-19 09:00:00
categories: [tools]
draft: false
author: whois
listImage: "default_post.png"
---

> RegRipper is a tool made by H. Carvey (keydet89) for Windows registry analysis. The tool is perl script that is made to run on Windows. The tool can be installed on Linux distros but I haven't yet found good instructions how to do it to share so I decided to make my own. I use the tool on the forensic courses I teach. Kudos to keydet89 for making this awesome tool.

~~If you are lazy, [here's](https://github.com/who1s/install_regripper) an installation script for Ubuntu/Debian.~~
**Update 2021**: This blog post is obsolete, please refer official documentation: https://github.com/keydet89/RegRipper3.0

First install dependencies we need in running this tool. For some reason at the time I am writing this blogpost, tests fail after building the Win32Registry module. For this reason, we need to use more force in installation. If you don't want to install the module to the default location, you may want to use -l parameter to give an it another location (f.e. /usr/share/regripper/perlmodules/).

```
$ sudo apt-get update && sudo apt-get install -y cpanminus git
$ sudo cpanm Parse::Win32Registry --force
```


After installing the dependencies, we clone the repo.

```
$ git clone https://github.com/keydet89/RegRipper2.8.git
$ cd RegRipper2.8/
```


As the script is made for Windows, we need to tune it a little. I am going to move the plugins to /usr/share/regripper/ so I need to sed the path into the script. I also want to uncomment all the Linux stuff.

```
$ tail -n +2 rip.pl > rip
$ perl -pi -e 'tr[\r][]d' rip
$ sed -i "1i #\!$(which perl)" rip
$ sed -i 's/\#my\ \$plugindir/\my\ \$plugindir/g' rip
$ sed -i 's/\#push/push/' rip
$ sed -i 's/\"plugins\/\"\;/\"\/usr\/share\/regripper\/plugins\/\"\;/' rip
$ sed -i 's/(\"plugins\")\;/(\"\/usr\/share\/regripper\/plugins\")\;/' rip
```


Now move the plugins to /usr/share/regripper

```
$ sudo mkdir -p /usr/share/regripper/
$ sudo cp -r plugins/ /usr/share/regripper/
```


Lastly we need to move our new script to path and reload our configuration

```
$ sudo mv rip /usr/local/bin/rip.pl
$ chmod +x /usr/local/bin/rip.pl
$ source ~/.bashrc
```


Now running rip.pl -c -l shoud list you all plugins. :)

```
 whois@ghost  ~  rip.pl -c -l
Plugin,Version,Hive,Description
ssh_host_keys,20120809,NTUSER.DAT,Extracts Putty/WinSCP SSH Host Keys
typedurlstime,20120613,NTUSER.DAT,Returns contents of user's TypedURLsTime key.
fw_config,20080328,System,Gets the Windows Firewall config from the System hive
yahoo_lm,20101219,SOFTWARE,Yahoo Messenger parser
...


 whois@ghost  ~/Courses/MemForensics/materials/registry  rip.pl -r registry.0xffffbb02f1b77000.SAM.reg -p samparse
Launching samparse v.20160203
samparse v.20160203
(SAM) Parse SAM file for user & group mbrshp info


User Information
-------------------------
Username        : Administrator [500]
SID             : S-1-5-21-4219245480-2226696944-1083947594-500
Full Name       : 
User Comment    : Built-in account for administering the computer/domain
Account Type    : 
Name            :  
Last Login Date : Never
Pwd Reset Date  : Never
Pwd Fail Date   : Never
Login Count     : 0
  --> Normal user account
  --> Password does not expire
  --> Account Disabled
...
``` 
