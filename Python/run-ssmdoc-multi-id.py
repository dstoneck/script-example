#!/usr/bin/python3
# this script is to run ssm document across multiple instance from list (file)

import boto3
import sys
import time

cdate = time.strftime("%Y%m%d")
sourcefile = sys.argv[1]
#ssm = boto3.client('ssm')
grouplist = ''

with open(sourcefile) as f:
    instanceinfo = f.read().splitlines()

for ininfo in instanceinfo:
    if ininfo.strip():
        ininfo = ininfo.split(",")
        region = ininfo[16]
        if region.endswith('a'):
            region = region[:-1]
        elif region.endswith('b'):
            region = region[:-1]
        elif region.endswith('c'):
            region = region[:-1]
        print("region: " + region + "\n" + "Profile: " + ininfo[0] + "\n" + "Instance ID: " + ininfo[2])
        account = boto3.session.Session(profile_name=ininfo[0])
        client = account.client('ssm',region_name=region)
        response = client.send_command(
        DocumentName = ("arn:aws:ssm:" + region +":927999915655:document/scan-usersandgroups"), 
        InstanceIds = [ininfo[2]]
        )
        job_id = response['Command']['CommandId']
        print("Pending for Job Completion\n" + job_id)
        while True:
            job_status = client.list_command_invocations(CommandId=job_id, Details=True)
            """ If the command hasn't started to run yet, keep waiting """
            if len(job_status['CommandInvocations']) == 0:
                time.sleep(1)
                continue
            invocation = job_status['CommandInvocations'][0]
            if invocation['Status'] not in ('Pending', 'InProgress', 'Cancelling'):
                break
            time.sleep(1)
        output = client.get_command_invocation(
            CommandId = response['Command']['CommandId'], 
            InstanceId = ininfo[2]
        )
        
        stdout = output['StandardOutputContent']
        print("raw: "+ stdout)
        with open("grouplist-" + cdate + ".csv", "a") as glist:
            glist.write(str(stdout) + "\n")
