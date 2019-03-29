##########################
__author__="Guru"
#
#Parameters_required = NONE
#
##########################


import telnetlib
import sys,os
import json

from paepy.ChannelDefinition import CustomSensorResult


data = json.loads(sys.argv[1])
#data = {"host":"192.168.105.65"}

ip=data['host']


#Define telnet parameters    
username = b'guest'
password = b'iltwat'
supassword = b'swtn100tj'
port = 2023
connection_timeout = 5
reading_timeout = 5
    
    #Logging into device
connection = telnetlib.Telnet(ip, port, connection_timeout)
        
router_output = connection.read_until(b"login:", reading_timeout)
connection.write(username + b'\n')      
router_output = connection.read_until(b"Password:", reading_timeout)

connection.write(password + b'\n')
router_output = connection.read_until(b'>', reading_timeout)        
connection.write(b"su -\n")
router_output = connection.read_until(b"Password:", reading_timeout)

connection.write(supassword + b" \n")
router_output = connection.read_until(b">", reading_timeout)

connection.write(b'echo "0 9 0 A 0 B 0 C 0 D 0 E 0 F q" | /usr/sbin/tejas/test /dev/slot15/fanfpga0 | grep "Read value" \n')
fandata = connection.read_until(b">", reading_timeout)

connection.close()

if b'Value of offset' not in fandata:
    result = CustomSensorResult()
    result.add_error("Sorry! the node might not support to view FAN speed")
    print(result.get_json_result())
    sys.exit(-1)

fandata = [fn for fn in fandata.splitlines() if b"Value of offset" in fn]

result = CustomSensorResult("Fan speed monitoring @: {}".format(ip))

for fno, fan in enumerate(fandata):
    speed = eval(fan.split(b"=")[1].split()[0])
    if fno < 6:
        result.add_channel(channel_name="FAN_"+str(fno+1), unit="%", value=speed*100/255, decimal_mode='Auto')

print(result.get_json_result())
