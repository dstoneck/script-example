#!/usr/bin/python3
import boto3
region_list=['us-east-1', 'eu-central-1', 'ap-southeast-1']
ip_list=['19.11.99.170','19.11.185.239','19.11.153.134']
dhcpoption_ids={}
profile_list=''

with open('acct_list.txt') as f:
    profile_list = f.read().splitlines()

for profile in profile_list:
    for region in region_list:
        account = boto3.session.Session(profile_name=profile)
        client = account.client('ec2',region_name=region)
        response = client.describe_dhcp_options(
            Filters=[
                {
                    'Name': 'key',
                    'Values': [
                        'domain-name-servers',
                    ]
                },
                {
                    'Name': 'value',
                    'Values': [
                        '19.10.5.134',
                        '19.10.166.170',
                        '19.10.185.239'
                    ]
                }
            ]
        )
        for dhcp_sets in response['DhcpOptions']:
            for dhcp_config in dhcp_sets['DhcpConfigurations']:
                if dhcp_config['Key'] == "domain-name-servers":
                    for dcip in dhcp_config['Values']:
                        if dcip['Value'] in ip_list:
                            print(profile + "," + region + "," + dhcp_sets['DhcpOptionsId'] + "," + dcip['Value'])
                            dhcpoption_ids[region] = {dhcp_sets['DhcpOptionsId']: dcip['Value']}
                            output_file = "output/%s" % profile
                            with open("output_file.csv", "a") as f:
                                # for key, value in dhcpoption_ids.items():
                                #     f.write('%s:%s\n' % (key, value))
                                f.write(profile + "," + region + "," + dhcp_sets['DhcpOptionsId'] + "," + dcip['Value'] + "\n")