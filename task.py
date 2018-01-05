import boto3
import socket
import sys
import os
import datetime
import time

abc = ['a.opsworks.pp.ua','b.opsworks.pp.ua','c.opsworks.pp.ua']

ec2 = boto3.resource('ec2')
ec = boto3.client('ec2')

user_tempfile = '/tmp/user_tempfile'

if os.path.isfile(user_tempfile):
    os.remove(user_tempfile)

ec2_instances_ip_file = open(user_tempfile,'w')

print('List of ip of instances:')
for i in ec2.instances.all():
    print(i.public_ip_address)
    ec2_instances_ip_file.write(str(i.public_ip_address) + os.linesep)

print('----------------------------')

ec2_public_ip_address_file = open(user_tempfile,'r')
ec2_public_ip_address_file = ec2_public_ip_address_file.read()

print('List of ip of domains for instances:')
for i in abc:
    print(i)
    y = socket.gethostbyname(i)
    if y in ec2_public_ip_address_file:
        print(y)

print('----------------------------')

print('Please choose: a,b,c')
print('a: a.opsworks.pp.ua')
print('b: b.opsworks.pp.ua')
print('c: c.opsworks.pp.ua')
input = sys.stdin.readline()[: -1]

temp = ''

if input == 'a':
    print('You have chosen: ' + input)
    temp = socket.gethostbyname('a.opsworks.pp.ua')
    print('IP of this domains is: ' + temp)
elif input == 'b':
    print('You have chosen: ' + input)
    temp = socket.gethostbyname('b.opsworks.pp.ua')
    print('IP of this domains is: ' + temp)
elif input == 'c':
    print('You have chosen: ' + input)
    temp = socket.gethostbyname('c.opsworks.pp.ua')
    print('IP of this domains is: ' + temp)
else:
    print('You should to chose only one from a,b,c')
    sys.exit(2)

for i in ec2.instances.all():
    if i.public_ip_address == temp:
        print('The instance is exists')
        print('The instance id: ' + i.id)
        if i.state['Name'] == 'stopped':
            print('The instance is stopped. We should make AMI')
            instancename = ''
            for y in i.tags:
                if y["Key"] == 'Name':
                    instancename = y["Value"]
                    date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                    description = instancename + '_' + date
                    temp_id = i.id
                    ec.create_image(InstanceId=i.id,Name=description,Description=description,NoReboot=True)
        else:
            print('The instance is running. We should not do anything. Run script again and choose other domain. Exiting ...')
            sys.exit(2)

print('Waiting for backup please for 60 sec ...')
time.sleep(60)

for i in ec2.images.filter(Owners=['self']):
    names = i.name
    if description in names:
        print('Image is exists. We can terminate server')
        ec.terminate_instances(InstanceIds=[temp_id])
        break
else:
    print('The AMI image does not exists. Please check.')
    sys.exit(2)

for i in ec2.instances.all():
    instancename = ''
    for y in i.tags:
        if y["Key"] == 'Name':
            instancename = y["Value"]
    print("Id: {0}\tState: {1}\tPub. IP: {2}\tName: {3}".format(
        i.id,
        i.state['Name'],
        i.public_ip_address,
        instancename
    ))
