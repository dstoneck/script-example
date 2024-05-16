#!/bin/python3

import boto3
from botocore.exceptions import ClientError
import json
import datetime

regions = ['us-east-1']
configrule = "security-group-test"
tagname = "pend-deletation-date"
now = datetime.date.today()

instances_by_rule = {}


def del_sg(con_region,sgid):
    client = boto3.client('ec2',region_name=con_region)
    client.delete_security_group(GroupId=sgid)

# Gets config rule results
def config_sg_list(con_region,rule_name):
    instances_by_rule = {}
    client = boto3.client('config',region_name=con_region)
    response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['NON_COMPLIANT'])"
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
            response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['COMPLIANT'], NextToken=nexttoken)"
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

# Check tags assigned to Security Gropus
def check_tags_sg(con_region,sgid):
    client = boto3.client('ec2',region_name=con_region)
    rmtag = False
    try:
        response = f"client.describe_security_groups(GroupIds=['{sgid}'])"
    except ClientError as e:
        print(e)
    output = eval(response)
    sgjson = json.dumps(output)
    sgload = json.loads(sgjson)
    try:
        sgvalue = (sgload["SecurityGroups"][0]["Tags"])
        for i in sgvalue:

            if i['Key'] == tagname:
                print("Tag Found " + sgid)
                date_object = datetime.datetime.strptime(i['Value'], '%Y-%m-%d').date()
                if date_object <= now:
                    remaining = now - date_object
                    print ("slated to delete " + str(remaining))
                    print("Deleting Security Group: " + sgid)
                    del_sg(con_region,sgid)
                elif date_object > now:
                    remaining = now - date_object
                    print("pending for date " + str(remaining))

    except ClientError as e:
        print(e)


def lambda_handler(event, context):
    # Run task function
    for region in regions:
        try:
            sglist = config_sg_list(region,configrule)
            #print(sglist["security-group-test"])
        except:
            print("no config rule found")
        for sgo in sglist["security-group-test"]:
            check_tags_sg(region,sgo)
