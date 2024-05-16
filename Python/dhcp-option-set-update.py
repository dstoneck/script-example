# Imports
import boto3
import datetime

configfile = "~/.aws/config"
# List of regions
# Change region:
    # boto3.setup_default_session(region_name='us-west-2')
    # boto3.client('rds', region_name='us-west-2')
regions = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1"]

# Get account(s)
def account(confloc):
    accountnum = []
    # use the config file to get list of accounts?
    file = open("confloc","r")
    for line in file:
        if "[profile" in line:
            temp = line.replace("[profile ","")
            accountnum.append = temp[-1]
    return accountnum


# Old IP to New IP Replacement
def ipupdate(ipaddress):
    match ipaddress:
        case "oldip": return "updatedip";


# Get DHCP Option Sets
# test_dhcp_options.py line 151
def get_dhcp(region):
    ec2_client = boto3.client("ec2", region_name=region)
    options = ec2_client.describe_dhcp_options(DhcpOptionsIds="*")

    print("Region: " + region)
    for i in options:
        print("DHCP ID: " + i)

    return options



# Create New DHCP Option Set
def create_dhcp(region, ip1, ip2):
    ec2_client = boto3.client("ec2", region_name=region)
    
    dhcp_options = ec2_client.create_dhcp_options(
        DhcpConfigurations=[
            {"Key": "domain-name", "Values": "corp.dom"},
            {"Key": "domain-name-servers", "Values": ip1},
            {"Key": "network-time-protocol", "Values": ip1}
        ]
    )
    return dhcp_options


# Output the new DHCP Option Set # and Account # to JSON
def json_output(data):
    datestamp = datetime.datetime.now()
    fname = "dhcp-chg-" + datestamp.strftime("%Y%m%d")
    fwrite = open(fname,"a")
    fwrite.write(data)