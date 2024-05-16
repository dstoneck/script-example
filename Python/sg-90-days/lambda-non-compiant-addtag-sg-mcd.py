#!/bin/python3

import boto3
from botocore.exceptions import ClientError
import json
import datetime

penddate = 90
regions = ['us-east-1']
configrule = "security-group-test"
tagname = "pend-date"
compstate = ['NON_COMPLIANT','COMPLIANT']


instances_by_rule = {}
now = datetime.date.today()
datestamp = str(now + datetime.timedelta(days=penddate))

def lambda_handler(event, context):
    region = "us-east-1"

# Add date tag, sgid has to passed as a tuple []
# Have to run describe_security_groups before adding tags are possible
def add_sg_tag(con_region,sgid,keytag,valtag):
    client = boto3.client('ec2',region_name=con_region)
    print("Adding Tag")
    sgid=[sgid]
    client.create_tags(Resources=sgid,Tags=[{'Key': keytag,'Value': valtag}])

# add_sg_tag("us-east-1",['sg-0116fed5cb9dee5d8'],tagname,"broken")

# Remove date tag, sgid has to passed as a tuple []
# Have to run describe_security_groups before adding tags are possible
def del_sg_tag(con_region,sgid,keytag):
    client = boto3.client('ec2',region_name=con_region)
    print(sgid)
    sgid=[sgid]
    client.delete_tags(Resources=sgid,Tags=[{'Key': keytag}])

# del_sg_tag("us-east-1",['sg-00be9849cef7d3818', 'sg-0116fed5cb9dee5d8', 'sg-05f5aeeaf7cd79a6e', 'sg-06badeee92b793627', 'sg-06d52149c495e38fa', 'sg-075637025d17fc45f', 'sg-075dc6471120be7c0', 'sg-08d77c8f58a2807d3', 'sg-08ed087276c43b8f2', 'sg-0949ae12b35d33b45', 'sg-0a40ace46c389578d', 'sg-0e067cdb73aa2d51f'],tagname)

# Call the config: ec2-security-group-attached-to-eni-periodic
def config_sg_list(con_region,rule_name,state):
    client = boto3.client('config',region_name=con_region)
    response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['{state}'])"
    output = eval(response)
    instances_by_rule[rule_name] = []
    try:
        for evaluation in output['EvaluationResults']:
            instances_by_rule[rule_name].append(evaluation['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])
    except:
        pass
    
    try:
        while output['NextToken'] != "":
            nexttoken = output['NextToken']
            response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['NON_COMPLIANT'], NextToken=nexttoken)"
            output = eval (response)
            try:
                for evaluation in output['EvaluationResults']:
                    instances_by_rule[rule_name].append(evaluation['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])
            except:
                pass
            try:
                nexttoken = output['NextToken']
            except:
                nexttoken = ""
    except:
        pass
    return(instances_by_rule)
    
# config_sg_list("us-east-1","security-group-test")

# Compliant/noncompliant tag update - checking if tag exists
def add_tags_sg(con_region,sgid):
    client = boto3.client('ec2',region_name=con_region)
    try:
        response = f"client.describe_security_groups(GroupIds=['{sgid}'])"
    except ClientError as e:
        print(e)
    output = eval(response)
    sgjson = json.dumps(output) # Converts the string to Json Dump
    sgload = json.loads(sgjson) # Makes the Json Python readable
    try:
        sgvalue = (sgload["SecurityGroups"][0]["Tags"])
        for i in sgvalue:
            if i['Key'] == tagname:
                print("Found: " + i['Value'])
                return
            else:
                print("Not Found " + sgid)
                addtag = True

    except:
        print("except: Tag Missing," + sgid)
        addtag=True
    print(addtag)
    if addtag:
        
        add_sg_tag(con_region,sgid,tagname,datestamp)
        #add_tags_sg(con_region,sgid)


def remove_tags_sg(con_region,sgid):
    client = boto3.client('ec2',region_name=con_region)
    rmtag = False
    try:
        response = f"client.describe_security_groups(GroupIds=['{sgid}'])"
    except ClientError as e:
        print(e)
    output = eval(response)
    sgjson = json.dumps(output) # Converts the string to Json Dump
    sgload = json.loads(sgjson) # Makes the Json Python readable
    try:
        sgvalue = (sgload["SecurityGroups"][0]["Tags"])
        for i in sgvalue:
            # move the if statement out of loop and variable of SG missing tags
            # remove duplicates if possible
            if i['Key'] == tagname:
                print("Found: " + i['Value'])
                rmtag = True
            else:
                print("Not Found " + sgid)

    except:
        print("No Tag: "+ sgid)
        #addtag=True
        return
    if rmtag:
        #print("Removing")
        del_sg_tag(con_region,sgid,tagname)
        # remove_tags_sg(con_region,sgid)

# Run task functions
for region in regions:

    # Discovery for Non-Compliant
    try:
        print(compstate[0])
        sglist = config_sg_list(region,configrule,compstate[0])
        #print(sglist["security-group-test"])
    except:
        print("no config rule found")
    for sgo in sglist["security-group-test"]:
        add_tags_sg(region,sgo)
    # Discovery for Compliant
    try:
        print(compstate[1])
        sglist = config_sg_list(region,configrule,compstate[1])
        # print(sglist["security-group-test"])
    except:
        print("no config rule found")
    for sgo in sglist["security-group-test"]:
        print(sgo)
        remove_tags_sg(region,sgo)