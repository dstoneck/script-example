#!/usr/bin/python3

# This script is meant to pull data through SSM to collect the needed compliance information.


import boto3
import os

commands_dict = {}
config_names = {}
instances_by_rule = {}
n=50
agents=[]
operating_systems=[]
aws_account_id = ''
agents=os.getenv('Agents', 'Qualys,NewRelic').split(",")
operating_systems=os.getenv('OS', 'Linux,Windows').split(",")
region = os.environ['AWS_REGION']

def instance_list():
    client = boto3.client('config', region_name=region)
    for agent in agents:
        for op_sys in operating_systems:
            combined_name = (agent+'-'+op_sys)
            rule_name = f"{combined_name}-Compliance"
            if 'NewRelic' in combined_name:
                keyname = f"New-Relic-{op_sys}"
                instances_by_rule[keyname] = []
            else:
                keyname = combined_name
                instances_by_rule[keyname] = []
            response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['NON_COMPLIANT'])"
            output = eval (response)
            try:
                for evaluation in output['EvaluationResults']:
                    instances_by_rule[keyname].append(evaluation['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])
            except:
                pass
            try:
                while output['NextToken'] != "":
                    nexttoken = output['NextToken']
                    response = f"client.get_compliance_details_by_config_rule(ConfigRuleName='{rule_name}',ComplianceTypes=['NON_COMPLIANT'], NextToken=nexttoken)"
                    output = eval (response)
                    try: 
                        for evaluation in output['EvaluationResults']:
                            instances_by_rule[keyname].append(evaluation['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])
                    except:
                        pass
                    try:
                        nexttoken = output['NextToken']
                    except:
                        nexttoken = ""
            except:
                pass
            
    return (instances_by_rule)

def kickoff_ssm(instances_by_rule,aws_account_id):
    ssmclient = boto3.client('ssm', region_name=region)
    IAM_role = f"arn:aws:iam::{aws_account_id}:role/Config-SSM-Remediation"
    for agent in instances_by_rule.keys():
        if len(instances_by_rule[agent]) < 50:
            ssm_doc_name = f"Install-"+agent
            print ("Instance List for %s less than 50" % agent)
            try:
                response = ssmclient.send_command(
                    Targets=[
                        {
                        'Key': 'InstanceIds',
                        'Values': instances_by_rule[agent]
                        },
                    ],
                    DocumentName=ssm_doc_name,
                    TimeoutSeconds=600,
                    MaxConcurrency='25',
                    MaxErrors='100%',
                    ServiceRoleArn=IAM_role,
                )
                print (response)
            except Exception as e: 
                print(e)
        else:
            instanceids = [instances_by_rule[agent][i * n:(i + 1) * n] for i in range((len(instances_by_rule[agent]) + n - 1) // n )]
            print ("Instance List for %s more than 50" % agent)
            for i in range(len(instanceids)):
                ssm_doc_name = f"Install-"+agent
                try:
                    response = ssmclient.send_command(
                        Targets=[
                            {
                            'Key': 'InstanceIds',
                            'Values': instanceids[i]
                            },
                        ],
                        DocumentName=ssm_doc_name,
                        TimeoutSeconds=600,
                        MaxConcurrency='25',
                        MaxErrors='100%',
                        ServiceRoleArn=IAM_role,
                    )
                    print (response)
                except Exception as e: 
                    print(e)


def handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    instance_list()
    print (instances_by_rule)
    print (aws_account_id)
    kickoff_ssm(instances_by_rule,aws_account_id)


