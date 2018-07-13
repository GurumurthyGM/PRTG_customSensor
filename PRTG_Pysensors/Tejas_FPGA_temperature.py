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
#data = {"host":"172.25.28.222"}

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

connection.write(b"/usr/sbin/tejas/fpga_scripts/temsense.sh | grep 'Read value' \n")
fpgadata = connection.read_until(b">", reading_timeout)

if b'Value of offset' not in fpgadata:
    connection.write(b"/usr/sbin/tejas/fpga_scripts/temsense_6.sh | grep 'Read value' \n")
    fpgadata = connection.read_until(b">", reading_timeout)

fpgadata = fpgadata.splitlines()[1:-1]

result = CustomSensorResult("FPGA temperature monitoring @: {}".format(ip))

for fno, fpga in enumerate(fpgadata):
    temp = eval(fpga.split(b"=")[1].split()[0]) - eval('0x180')
    result.add_channel(channel_name="FPGA_"+str(fno), unit="Temperature", value=temp)

print(result.get_json_result())
