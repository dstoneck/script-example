#!/usr/bin/python3

# This script is meant to share an existing document from one to different accounts and regions.

import boto3
import sys

regions = ["us-east-1", "eu-central-1", "ap-southeast-1"]
defaultacct = "997789995655"
sourcefile = sys.argv[1]
docname = "scan-usersandgroups"

with open(sourcefile) as f:
    accountids = f.read().splitlines()

accountlist = ",".join(accountids)

for region in regions:
    docname='arn:aws:ssm:'+region+':'+defaultacct+':document/'+docname
    account = boto3.session.Session(profile_name=defaultacct)
    client = account.client('ssm',region_name=region)
    response = client.modify_document_permission(
        Name=docname,
        PermissionType='Share',
        AccountIdsToAdd=[
            accountlist
        ],
        SharedDocumentVersion='string'
    )