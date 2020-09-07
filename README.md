# hpux agent采集端操作指南
## 一、项目结构
```shell
tree agent_hpux_v1.0.0 -L 2 
agent_hpux_v1.0.0
├── README.md
├── collectors
│   ├── 0
│   │   ├── logparser.py    ## 监控脚本
│   │   └── sys.py          ## 监控脚本
│   ├── __init__.py
│   ├── etc              ## 指标搜集脚本单独的配置文件存放目录
│   └── lib              ## 指标搜集脚本用到的外部依赖
├── config.ini           ## 全局配置文件
├── kafka                ## kafka依赖包
├── tcollector           ## 启动脚本
├── tcollector.log       ## 日志
├── tcollector.pid       ## pid
└── tcollector.py        ## 主python运行脚本
```
## 二、 配置
> config.ini
```vim
[default]
## dryrun 为true为打印屏幕，false为发送到kafka
dryrun = false
logfile = /root/tcollector/tcollector.log
cdir = /root/tcollector/collectors
pidfile = /root/tcollector/tcollector.pid
## 以下内容可以为默认
verbose = false
no_tcollector_stats = false
evictinterval = 6000
dedupinterval = 300
deduponlyzero = false
allowed_inactivity_time = 600
maxtags = 8
## max_bytes: 64 * 1024 * 1024
max_bytes = 67108864
http_password = false
reconnectinterval = 0
http_username = false
port = 4243
http = false
http_api_path = api/put
remove_inactive_collectors = false
host = localhost
backup_count = 1
ssl = false
stdin = false
daemonize = false
hosts = false
monitoring_interface = none
monitoring_port = 13280

[kafka]
# kafka配置
kafka_addr = 192.168.6.116:9092, 192.168.6.117:9092, 192.168.6.118:9092
security_protocol = SASL_PLAINTEXT
sasl_plain_username = kafka
sasl_plain_password = redhat
sasl_mechanism = PLAIN
topic = testkafka
```

## 三、 前置条件与安装说明
> 找到hpux服务器的python路径，在tcollector中添加
```vim
which_python () {
    for python in /usr/bin/python2.7 /usr/bin/python2.6 /usr/bin/python2.5 /usr/bin/python /usr/local/bin/python; do
        test -x "$python" && echo "$python" && return
    done
    echo >&2 'Could not find a Python interpreter'
    exit 1
}
```
> 无需安装，解压后修改配置文件后，在tcollector启动脚本所在目录使用启动指令进行启动

## 四、 采集指标
> 1. 系统指标
```
# 内存指标
name            # 服务器名称
total           # 内存总量
available       # 应用程序可使用的内存大小
used            # 已使用容量
load1           # 平均1分钟负载
load5           # 平均5分钟负载
load15          # 平均15分钟负载
free            # 剩余可使用的物理内存

# cpu指标
user            # 用户cpu使用率
load            # cpu负载率
nice            # 代表低优先级用户态CPU时间
sys             # 系统CPU使用率
idle            # 代表空闲时间

# disk指标
name            # 服务器名称
device          # 设备文件
fstype          # 文件系统  
hostname        # 主机名称
mode            # 挂载权限
path            # 挂载路径
used_percent    # 使用率
```
> 2. 业务指标 agent_hpux_v1.0.0/collectors/etc/logparser.ini
```vim
[default]
# 业务日志监控目录
log_directory = ["/weblogic/bea923/user_projects/domains/logs"]
# 检测日志文件变化的缓存路径
watchdir = /home/weblogic/agent_hpux_v1.0.0/collectors/cache
# 日志匹配类型
regex_file = _app.log
# 输出的日志格式
log_pattern = %{GREEDYDATA:msg}
# 是否从开始读取日志
from_begain = False
```

## 五、日志文件管理接口
> 查看日志列表
```
URL：http://主机IP:Port/file/list
Params: 
    {
        data: 要查看的日志目录路径
    }
```
> 删除日志文件
```
URL：http://主机IP:Port/file/delete
Params:
    {
        data: 要删除的指定日志文件路径
    }
```

## 五、 管理指令
> 启动
```shell
$ ./tcollector start
```
> 关闭
```shell
$ ./tcollector stop
```
> 状态查看
```shell
$ ./tcollector status
```
> 重启
```shell
$ ./tcollector restart
```