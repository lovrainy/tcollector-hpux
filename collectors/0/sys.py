#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
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

def sysCpuMemLoad():
    data = {'name': '', 'tags': {}, 'timestamp': '', 'val': ''}
    data['tags']['host_name'] = socket.gethostname()
    m = subprocess.Popen("cat /var/adm/syslog/syslog.log|grep Physical", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    m_out = m.stdout.readlines()[0]
    mem_info = m_out.split()

    total_n = mem_info.index('Physical:')
    avl_n = mem_info.index('available:')

    total_mem = int(mem_info[total_n+1])
    data['name'] = 'total'
    data['timestamp'] = time.time()
    data['val'] = total_mem
    print(json.dumps(data))

    avl_mem = int(mem_info[avl_n+1])
    data['name'] = 'available'
    data['timestamp'] = time.time()
    data['val'] = avl_mem
    print(json.dumps(data))

    used_mem = total_mem-avl_mem
    data['name'] = 'used'
    data['timestamp'] = time.time()
    data['val'] = used_mem
    print(json.dumps(data))

    p = subprocess.Popen("top -n 1 > top.txt", shell=True)
    time.sleep(5)
    with open('top.txt', 'r') as f:
	result = f.readline().split('\r')[1:13]
        cpu_param = ''
        for i in range(len(result)):
            if i == 0:
                load = result[i].strip().split(':')
                load1 = float(load[-1].split(',')[0].strip())
                data['name'] = 'load1'
                data['timestamp'] = time.time()
                data['val'] = load1
                print(json.dumps(data))

                load5 = float(load[-1].split(',')[1].strip())
                data['name'] = 'load5'
                data['timestamp'] = time.time()
                data['val'] = load5
                print(json.dumps(data))
                load15 = float(load[-1].split(',')[2].strip()[:4])
                data['name'] = 'load15'
                data['timestamp'] = time.time()
                data['val'] = load15
                print(json.dumps(data))
            elif i == 3:
                cpu_param = str(result[i]).strip().split()
                cpu_param[-1] = cpu_param[-1][:4]
                cpu_param = cpu_param[2:]
            elif i == 9:
                cpus = result[i].strip().split()
                for i in range(len(cpu_param)):
                    cpu = float(cpus[i+2].split('%')[0])/100
                    data['name'] = cpu_param[i]
                    data['timestamp'] = time.time()
                    data['val'] = cpu
                    print(json.dumps(data))
            elif i == 11:
                mem = result[i].strip().split()
                free_n = mem.index('free') - 1
                free_mem = int(mem[free_n].split('K')[0])
                data['name'] = 'free'
                data['timestamp'] = time.time()
                data['val'] = free_mem
                print(json.dumps(data))


def main():
    while True:
        sysDisk()
        sysCpuMemLoad()
        time.sleep(60)
            

if __name__ == "__main__":
    sys.exit(main())
