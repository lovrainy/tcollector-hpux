#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import time
import json
import socket
import subprocess

types = ['total', 'free', 'used', 'used_percent']


def sysDisk():
    p = subprocess.Popen("df -P", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = p.stdout.readlines()[1:]

    for res in out:
        res = res.split()
        for name in types:
            data = {'name': '', 'tags': {}, 'timestamp': '', 'val': ''}
            data['name'] = name
            data['tags']['device'] = res[0]
            data['tags']['fstype'] = ''
            data['tags']['host_name'] = socket.gethostname()
            data['tags']['mode'] = 'rw'
            data['tags']['path'] = res[-1]
            data['timestamp'] = time.time()
            if name == 'used_percent':
                val = res[types.index(name)+1]
                data['val'] = float(val[:-1])/100
            else:
                data['val'] = int(res[types.index(name)+1])
            
            print(json.dumps(data))


def main():
    while True:
        sysDisk()
        time.sleep(10)
            

if __name__ == "__main__":
    sys.exit(main())
