# jitter

Jitter monitoring and logging tool

Have problem with VOIP app frequently dropping calls, so I wrote this tool to
continuously monitor the data connection jitter and dropped packets to multiple
hosts

The tool is to be run on multiple devices at the same time and then correlate
results. Output is a log file with comma separated data that can be pasted into
spreadsheet. For easy correlation, timestamp is synchronized from worldtimeapi.org
and if measurement falls behind, empty timestamped lines are printed at the intervals
when measurement was not possible. 

Needs Python 3.6 and higher

## Windows

Needs package pythonping, which uses sockets directly, install with pip

I just run it from within SciTE text editor, but any IDE or even console
would work.

`python jitter.py`

## Linux

Needs system ping utility, should be present on any system.

Tested on Lubuntu 20.04. Run from the console terminal:

`python jitter.py`

## Android

This is the most interesting for me because I have not used phones
or Android for development before but Termux makes it so easy.

Install Termux from Play Store. Then run it and install openssh

`pkg upgrade`
`pkg install openssh`

After that start ssh server:

`sshd`

Find out your local IP, it will be the line starting with inet

`ifconfig wlan0`

Find your user name, and set your password, sshd will need it.

`whoami`
`passwd`

Now you have all info to connect from SSH/SFTP clients to port 8022

`pkg install python`

Finally ready to run the tool

`python jitter.py`

There is a script `gossh` that takaes care of keeping the WiFi alive
starting `sshd` daemon and figuring out the current IP. Next time you
need to connect to your phone via SSH, just type

`./gossh`

and then connect to it with given information. Start the script:

`nohup python jitter.py`

When ending your Termux session, type

`pkill jitter.py`
`termux-wake-unlock`
