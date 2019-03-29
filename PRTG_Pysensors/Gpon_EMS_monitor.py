import paramiko
import sys,json
import re
from paepy.ChannelDefinition import CustomSensorResult
from time import sleep, time
try :
    data = json.loads(sys.argv[1])
except :
    data = {"host":"172.25.101.27","params":"172.25.101.27"}

serverip = data['host']
dbserverip = data['params']

if not dbserverip:
    result = CustomSensorResult()
    result.add_error("@ Additional Parameters while adding sensor, enter DBserverIP")
    print(result.get_json_result())
    sys.exit(-1)

port=22
username='root'
password='iltwat'


def execute_ssh(command, raw=0):
    _,stdout,_=ssh.exec_command(command)
    data = stdout.read().decode('utf-8')
    if raw:
        return data
    return data.strip().splitlines()

#ssh to nms server
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(serverip,port,username,password)

getEth="ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\\ ]+).*/\\1/p'"
EthPort = execute_ssh(getEth)[0]


getNMSProc = "jps -v"
NMSProcs = execute_ssh(getNMSProc)

process = {}
for proc in NMSProcs:
    if "TejAdapterServer" in proc:
        process["TejAdapterServer"] = proc.split()[0]
    elif "NmsServerMain" in proc:
        process["NmsServerMain"] = proc.split()[0]
    elif "AAAServer" in proc:
        process["AAAServer"] = proc.split()[0]
    elif "RegistryImpl" in proc:
        process["RegistryImpl"] = proc.split()[0]
    elif "activemq" in proc:
        process["activemq"] = proc.split()[0]

    elif "/opt/nms/release/apache-tomcat-8.0.30/conf/logging.properties" in proc:
        process["tomcat"] = proc.split()[0]


if not process:
    result = CustomSensorResult()
    result.add_error("NMS is not running...!")
    print(result.get_json_result())
    sys.exit(-1)

getTop = "top -bn1"

topout = execute_ssh(getTop, 1)

top =    re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+[\d\.]+\s+[\d\.]+\s+[:\.\d]+\s+\w+")
_cpu =   re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+([\d\.]+)\s+[\d\.]+\s+[:\.\d]+\s+\w+")
cpumem = re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+([\d\.]+)\s+([\d\.]+)\s+[:\.\d]+\s+\w+")
processlist = top.findall(topout)
TotalCpu = sum(map(float,_cpu.findall(topout)))

procusage={}

for proc in processlist:
    if process['TejAdapterServer'] in proc:
        procusage['TejAdapterServer'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['NmsServerMain'] in proc:
        procusage['NmsServerMain'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['AAAServer'] in proc:
        procusage['AAAServer'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['RegistryImpl'] in proc:
        procusage['RegistryImpl'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['tomcat'] in proc:
        procusage['tomcat'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['activemq'] in proc:
        procusage['activemq'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))

    

_BW = "cat /proc/net/dev | grep "+EthPort+" | awk '{print $2, $10}'"

BW1 = execute_ssh(_BW, 1)
sleep(1)
BW2 = execute_ssh(_BW, 1)


BW1 = BW1.strip().split()
rx1, tx1 = tuple(map(int,BW1))

BW2 = BW2.strip().split()
rx2, tx2 = tuple(map(int,BW2))

Tin = (rx2 - rx1)/1024
Tout = (tx2 - tx1)/1024

TotalMemoryUsed = execute_ssh("free -m | " + "grep 'Mem' | " + "awk '{print $3}'")[0] 
CPUs = execute_ssh('grep -c ^processor /proc/cpuinfo')[0]
RAM = execute_ssh("free -m | " + "grep 'Mem' | " + "awk '{print $2}'")[0]
ssh.close()

#ssh to DB server
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(dbserverip,port,username,password)

getMysqlProc = "cat /var/run/mysqld/mysqld.pid"
mysql = execute_ssh(getMysqlProc)[0]

getdbTop = "top -bn1"
topdbout = execute_ssh(getdbTop, 1)
processlistdb = top.findall(topdbout)

for procdb in processlistdb:
    if mysql in procdb:
        dbprocusage = dict(zip(('cpu','mem'),cpumem.findall(procdb)[0]))
        

dbCPUs = execute_ssh('grep -c ^processor /proc/cpuinfo')[0]
dbRAM = execute_ssh("free -m | " + "grep 'Mem' | " + "awk '{print $2}'")[0]
ssh.close()

result = CustomSensorResult("NMS monitor: {} --> CPUs={} RAM={} MB \u2665\u2665 DBserver {} --> CPUs={} RAM={} MB".format(serverip,CPUs,RAM,dbserverip,dbCPUs,dbRAM))
result.add_channel(channel_name="TotalCPU", unit="cores", value=float(TotalCpu)/100, is_float=True, decimal_mode='Auto' )
for k,v in procusage.items():
    result.add_channel(channel_name="{}_{}".format(k,"CPU"), unit="core", value=float(procusage[k]["cpu"])/100, is_float=True, decimal_mode='Auto' )

result.add_channel(channel_name="TotalRAMUsed", unit="MB", value=TotalMemoryUsed)
for k,v in procusage.items():
    result.add_channel(channel_name="{}_{}".format(k,"RAM"), unit="MB", value=float(procusage[k]["mem"])*int(RAM)/100, is_float=True, decimal_mode='Auto'  )

result.add_channel(channel_name="{}_{}".format("Mysql","CPU"), unit="core", value=float(dbprocusage["cpu"])/100, is_float=True, decimal_mode='Auto' )
result.add_channel(channel_name="{}_{}".format("Mysql","RAM"), unit="MB", value=float(dbprocusage["mem"])*int(dbRAM)/100, is_float=True, decimal_mode='Auto'  )

result.add_channel(channel_name="Traffic-OUT", unit="KB/s", value=Tout, is_float=True, decimal_mode='Auto' )
result.add_channel(channel_name="Traffic-IN", unit="KB/s", value=Tin, is_float=True, decimal_mode='Auto')

print(result.get_json_result())
