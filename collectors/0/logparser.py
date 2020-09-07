#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os
import re
import socket
import time
import json
from pygrok import Grok
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from utils import gen_config

def init_conf():
    parser_conf = gen_config("logparser", "logparser.ini")
    return parser_conf

# 初始化配置
logparser = init_conf().default
log_dirs = eval(logparser.log_directory)
watch_dir = logparser.watchdir
regex_file = logparser.regex_file
pattern = logparser.log_pattern
fromBegainning = logparser.from_begain
glob_watchfile = {}

# 正则匹配查询的日志文件
def findfile(logdir):
    regex_list = regex_file.split('.')
    regex = ".*" + regex_list[0] + "." + regex_list[1] + "$"
    file_pt = re.compile(regex)
    filelist = []
    for file in os.listdir(logdir):
        dir = logdir+'/'+file
        if os.path.isfile(dir):
            if file_pt.match(file):
                filelist.append(dir)
    return filelist

def start():
    global log_dirs
    global file_watch
    # 1. 判断缓存文件是否存在，不存在则创建
    is_exist = os.path.exists(watch_dir)

    if not is_exist:
        try:
            os.mkdir(watch_dir, mode=0o755)
        except Exception as e:
            print("make dir %s failed: %s" % (watch_dir, e))
            return
    file_watch = {}
    fixfilelist = []
    # 修正正则匹配的文件列表
    for dir in log_dirs:
        for files in findfile(dir):
            fixfilelist.append(files)
    log_dirs = fixfilelist

    # 第二步：判断各文件的缓存记录文件是否存在，不存在即创建，且在其中初始化记录log文件的（inode，seek）。seek初始化为0.
    # 存在即读取inode与seek记录。以便后续读取时做对比。

    for filename in log_dirs:
        # filewatch = {'name': filename+'.cache'}
        filewatch = {'offset': 0}
        # 初始化当前文件缓存记录文件地址
        filewatch['watchfile'] = os.path.join(watch_dir, os.path.basename(filename)+'.cache')

        if not os.path.exists(filename):
            print('filename: %s does not exist' % filename)
            return
        else:
            # 获取当前文件inode
            file_st = os.stat(filename)
            filewatch['inode'] = file_st.st_ino

        if not os.path.exists(filewatch['watchfile']):
            # 缓存文件不存在则创建
            f = open(filewatch['watchfile'], 'w')
            f.close()
            # 初始化offset
            filewatch['offset'] = 0
        else:
            # 缓存文件存在则读取信息
            with open(filewatch['watchfile']) as f:
                content = f.readlines()

                if content:
                    filewatch['inode'] = int(content[0])
                    # filewatch_offset = int(content[1])
                    #
                    # if filewatch_offset != filewatch['offset']:
                    #     filewatch['offset'] = 0
                    #     file = os.open(filewatch['watchfile'], os.O_WRONLY | os.O_TRUNC, 0o600)
                    #     os.close(file)
        file_watch[filename] = filewatch
    glob_watchfile['file_watch'] = file_watch


class TailHandler(FileSystemEventHandler):

    def __init__(self, path, grok):
        global glob_watchfile
        self.path = path
        self.grok = grok

    def close(self):
        self.file.close()

    def print_line(self):
        self.file = open(self.path, 'r')
        json_d = {}
        # 如果fromBegainning True，则重新开始读取
        if fromBegainning:
            pos = 0

        try:
            with open(glob_watchfile['file_watch'][self.path]['watchfile']) as f:
                cache_data = f.readlines()

                if cache_data:
                    pos = int(cache_data[1])
                    ino = int(cache_data[0])
                else:
                    pos = 0
                    ino = None
        except Exception as e:
            print(e)

        f_stat = os.stat(self.path)
        inode = f_stat.st_ino

        if inode == ino:
            off = self.file.seek(pos)
            # off None 表示日志文件发生变化，重新读取log
            if not off:
                self.file.seek(0,0)
        else:
            self.file.seek(0, 0)

        while True:
            line = self.file.readline()
            if not line:
                self.file.close()
                break
            result = self.grok.match(line.strip())
            pos = self.file.tell()
            glob_watchfile['file_watch'][self.path]['inode'] = inode
            glob_watchfile['file_watch'][self.path]['offset'] = pos
            watchfile = glob_watchfile['file_watch'][self.path]['watchfile']

            try:
                f = os.open(watchfile, os.O_WRONLY | os.O_TRUNC, 0o644)
            except Exception as e:
                print(e)

            content = str(inode) + '\n' + str(pos)
            os.write(f, content)
            os.close(f)
            tags = {'host_name': socket.gethostname(), 'instance': os.path.basename(self.path)[:-4],
                    'plugin_name': 'logparser', 'path': self.path}
            glob_watchfile['tags'] = tags
            json_d['tags'] = tags
            json_d['msg'] = result['msg']
            json_d['timestamp'] = round(time.time() * 1000)

            print(json.dumps(json_d)+'\n')
            time.sleep(0.01)

    def on_modified(self, event):
        if event.is_directory or self.path != event.src_path:
            return
        self.print_line()

def main():
    start()
    grok = Grok(pattern)
    observers = []
    handlers = []

    for file in log_dirs:
        observer = PollingObserver()
        handler = TailHandler(file, grok)
        observer.schedule(handler, os.path.dirname(file))
        observers.append(observer)
        handlers.append(handler)

    for ob in observers:
	ob.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for o in observers:
            o.unschedule_all()
            # stop observer if interrupted
            o.stop()

    for o in observers:
        # Wait until the thread terminates before exit
        o.join()

if __name__ == '__main__':
    sys.exit(main())
