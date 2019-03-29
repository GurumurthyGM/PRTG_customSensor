import paramiko
import sys,json
import re
from paepy.ChannelDefinition import CustomSensorResult
from time import sleep, time

data = {"host":"172.25.101.181"}
data = json.loads(sys.argv[1])

serverip = data['host']
port=22
username='root'
password='iltwat'

def execute_ssh(command, raw=0):
    stdin,stdout,stderr=ssh.exec_command(command)
    data = stdout.read().decode('utf-8')
    if raw:
        return data
    return data.strip().splitlines()

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(serverip,port,username,password)

getEth="ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\\ ]+).*/\\1/p'"
EthPort = execute_ssh(getEth)[0]


getEMSProc = "jps -m"
EMSProcs = execute_ssh(getEMSProc)

process = {}
for proc in EMSProcs:
    if "EMSCommonDomain" in proc:
        process["EMSCommonDomain"] = proc.split()[0]
    elif "PerformanceDomain" in proc:
        process["PerformanceDomain"] = proc.split()[0]
    elif "TMFDomain" in proc:
        process["TMFDomain"] = proc.split()[0]
    elif "NotifyEventChannelFactory" in proc:
        process["NotifyEventChannelFactory"] = proc.split()[0]
    elif "webswing" in proc:
        process["webswing"] = proc.split()[0]
    elif "activemq" in proc:
        process["activemq"] = proc.split()[0]
    elif "NameServer" in proc:
        process["NameServer"] = proc.split()[0]



if not process:
    result = CustomSensorResult()
    result.add_error("EMS is not running...!")
    print(result.get_json_result())
    sys.exit(-1)

getMysqlProc = "cat /var/run/mysqld/mysqld.pid"
mysql = execute_ssh(getMysqlProc)[0]
process['mysql'] = mysql


getTop = "top -bn1"

topout = execute_ssh(getTop, 1)

top =    re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+[\d\.]+\s+[\d\.]+\s+[:\.\d]+\s+\w+")
_cpu =   re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+([\d\.]+)\s+[\d\.]+\s+[:\.\d]+\s+\w+")
cpumem = re.compile(r"\d+\s+\w+\s+\w+\s+-?\d+\s+[\.\w]+\s+[\.\w]+\s+\d+\s+\w\s+([\d\.]+)\s+([\d\.]+)\s+[:\.\d]+\s+\w+")
processlist = top.findall(topout)
TotalCpu = sum(map(float,_cpu.findall(topout)))
procusage={}

for proc in processlist:
    if process['EMSCommonDomain'] in proc:
        procusage['EMSCommonDomain'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['PerformanceDomain'] in proc:
        procusage['PerformanceDomain'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['TMFDomain'] in proc:
        procusage['TMFDomain'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['NotifyEventChannelFactory'] in proc:
        procusage['NotifyEventChannelFactory'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['webswing'] in proc:
        procusage['webswing'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['activemq'] in proc:
        procusage['activemq'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['NameServer'] in proc:
        procusage['NameServer'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    elif process['mysql'] in proc:
        procusage['mysql'] = dict(zip(('cpu','mem'),cpumem.findall(proc)[0]))
    


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


result = CustomSensorResult("EMS monitor: {} --> CPUs={} RAM={} MB".format(serverip,CPUs,RAM))
result.add_channel(channel_name="TotalCPU", unit="%", value=TotalCpu, is_float=True, decimal_mode='Auto' )
for k,v in procusage.items():
    result.add_channel(channel_name="{}_{}".format(k,"CPU"), unit="%", value=procusage[k]["cpu"], is_float=True, decimal_mode='Auto' )

result.add_channel(channel_name="TotalRAMUsed", unit="MB", value=TotalMemoryUsed)

for k,v in procusage.items():
    result.add_channel(channel_name="{}_{}".format(k,"RAM"), unit="%", value=procusage[k]["mem"], is_float=True, decimal_mode='Auto')

result.add_channel(channel_name="Traffic-OUT", unit="KB/s", value=Tout, is_float=True, decimal_mode='Auto' )
result.add_channel(channel_name="Traffic-IN", unit="KB/s", value=Tin, is_float=True, decimal_mode='Auto' )

print(result.get_json_result())
