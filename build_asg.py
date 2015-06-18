import argparse
import subprocess
import sys
import boto.ec2
import random
import multiprocessing
import time
import collections

parser = argparse.ArgumentParser()    
parser.add_argument('--secret_key', help='', required=False)
parser.add_argument('--access_key', help='', required=False)
parser.add_argument('--provider-region', help='', required=False)
parser.add_argument('--autoscale_group', help='', required=False)
parser.add_argument('--min_size', help='', required=False)
parser.add_argument('--max_size', help='', required=False)
parser.add_argument('--asg_name', help='', required=False)
parser.add_argument('--azs', help='', required=False)
parser.add_argument('--desired_size', help='', required=False)
parser.add_argument('--force_delete', help='', required=False)
parser.add_argument('--hc_type', help='', required=False)
parser.add_argument('--hc_period', help='', required=False)
parser.add_argument('--lc_name', help='', required=False)
parser.add_argument('--lc_image_id', help='', required=False)
parser.add_argument('--lc_instance_type', help='', required=False)
parser.add_argument('--lc_iam_instance_profile', help='', required=False)
parser.add_argument('--lc_key_name', help='', required=False)
parser.add_argument('--in_user_data', help='', required=False)
parser.add_argument('--lc_public_ip', help='', required=False)
parser.add_argument('--launch_config', help='', required=False)
parser.add_argument('--tags', help='', required=False)
parser.add_argument('--block_devices', help='', required=False)
parser.add_argument('--asg_vpc_ident', help='', required=False)
parser.add_argument('--cloud_stack', help='', required=False)
parser.add_argument('--cloud_environment', help='', required=False)
parser.add_argument('--cloud_domain', help='', required=False)
parser.add_argument('--cluster_monitor_bucket', help='', required=False)
parser.add_argument('--cloud_cluster', help='', required=False)
parser.add_argument('--cloud_auto_scale_group', help='', required=False)
parser.add_argument('--cloud_launch_config', help='', required=False)
parser.add_argument('--cloud_dev_phase', help='', required=False)
parser.add_argument('--cloud_revision', help='', required=False)
parser.add_argument('--role', help='', required=False)
parser.add_argument('--security_groups', help='', required=False)

args = parser.parse_args()
secret_key = args.secret_key
access_key = args.access_key
provider_region = args.provider_region
security_groups = args.security_groups
autoscale_group = args.autoscale_group #boolean for deploying autoscale group
launch_configuration = args.launch_config #boolean for launch config

cloud_stack = args.cloud_stack 
cloud_environment = args.cloud_environment
cloud_domain = args.cloud_domain
cluster_monitor_bucket = args.cluster_monitor_bucket
cloud_cluster =  args.cloud_cluster
cloud_auto_scale_group = args.cloud_auto_scale_group
cloud_launch_config = args.cloud_launch_config
cloud_dev_phase = args.cloud_dev_phase
cloud_revision = args.cloud_revision
role = args.role
#asg arguments
min_size = args.autoscale_group
max_size = args.autoscale_group
desired_size = args.autoscale_group
azs = args.autoscale_group
asg_name = args.autoscale_group
force_delete = args.autoscale_group
tags = args.tags
hc_type = args.hc_type
hc_period = args.hc_period
az_list = args.azs
vpc_zone_ident = args.asg_vpc_ident

#launch configuration values
lc_name = args.lc_name
lc_image_id = args.lc_image_id
lc_instance_type = args.lc_instance_type
lc_iam_instance_profile = args.lc_iam_instance_profile
lc_key_name = args.lc_key_name
in_user_data = args.in_user_data
lc_public_ip = args.lc_public_ip
block_device_mapping = args.block_devices
security_group_name = []
security_groups = ''

def build_lc(lc_name, lc_name2, lc_image_id, lc_instance_type, lc_public_ip, lc_security_groups, lc_iam_instance_profile, lc_user_data, lc_key_name,block_device_mapping):
    launch_config_dict = collections.OrderedDict()
    if lc_name:
        launch_config_dict['lcname'] = lc_name
    if lc_name2:
        launch_config_dict['name'] = lc_name2
    if lc_image_id:
        launch_config_dict['image_id'] = lc_image_id
    if lc_instance_type:
        launch_config_dict['instance_type'] = lc_instance_type
    if lc_public_ip:
        launch_config_dict['associate_public_ip_address'] = lc_public_ip
    if lc_security_groups:
        launch_config_dict['security_groups'] = str(lc_security_groups).replace("'",'"')
    if lc_iam_instance_profile:
        launch_config_dict['iam_instance_profile'] = lc_iam_instance_profile
    if lc_user_data:
        launch_config_dict['user_data'] = lc_user_data
    if lc_key_name:
        launch_config_dict['key_name'] = lc_key_name
    if block_device_mapping:
        launch_config_dict['block_device'] = block_device_mapping

    lc_string = '\nresource "aws_launch_configuration" "%s" {\n' % launch_config_dict['lcname']

    for key, value in launch_config_dict.iteritems():
        if value != None:
            if key == 'lcname':
                continue
            if key != 'block_device':
                if key != 'security_groups':
                    lc_string = lc_string + '        %s="%s"\n' % (key, value)
                else:
                    lc_string = lc_string + '        %s=%s\n' % (key, value)
            else:
                lc_string = lc_string + '        %s\n' % (value)
    lc_string = lc_string + '\n    }'
    return lc_string

def build_tags(tags):
    built_tags = ''
    tags = tags.split(',')
    for tag in tags:
        if len(tag) > 5:
            values = tag.split(':')
            built_tags = built_tags + """
            tag {
                key = "%s"
                value = "%s"
                propagate_at_launch = %s
                }                                   
            """ % (values[0],values[1],values[2])
    return built_tags

def build_block_devices(block_devices):
    built_devices = ''
    block_devices = block_devices.split(',')
    for device in block_devices:
        values = device.split(':')
        built_devices = built_devices + '''
            ebs_block_device{
                device_name = "%s"
                volume_type = "%s"
                volume_size = %s
                delete_on_termination = %s
                iops = %s
            }
        ''' % (values[0].split('=')[1],values[1].split('=')[1],values[2].split('=')[1],values[3].split('=')[1],values[4].split('=')[1])
    return built_devices

def build_az_list(azs):
    az_list = []
    az_values = azs.split(',')
    for az in az_values:
        az_list.append('%s' % az)
    return az_list

def build_rules(name,rules):
    build_string = ''
    for rule in rules.split(':'):
        if len(rule) > 10:
            build_string = build_string + '''
                    %s {
                        from_port = %s
                        to_port = %s
                        protocol = "%s"
                        %s = %s
                        }
                        ''' % (name, 
                               rule.split('=')[1].split(';')[0].split('|')[1], 
                               rule.split('=')[1].split(';')[1].split('|')[1], 
                               rule.split('=')[1].split(';')[2].split('|')[1], 
                               rule.split('=')[1].split(';')[3].split('|')[0],
                               rule.split('=')[1].split(';')[3].split('|')[1])
    return build_string

#Dynamically builds ASG, and won't include values  if they dont exist. Need to do errors when its required.
def build_asg(**kwargs):
    asg_string = '\nresource "aws_autoscaling_group" "%s" {\n' % kwargs['asgname']
    order_dict = collections.OrderedDict()
    if kwargs['name']:
        order_dict['name'] = kwargs['name']
    if kwargs['availability_zones']:
        order_dict['availability_zones'] = str(kwargs['availability_zones']).replace("'",'"')
    if kwargs['max_size']:
        order_dict['max_size'] = kwargs['max_size']
    else:
        order_dict['max_size'] = 1
    if kwargs['min_size']:
        order_dict['min_size'] = 1
    else:
        order_dict['min_size'] = kwargs['min_size']
    if kwargs['launch_configuration']:
        order_dict['launch_configuration'] = kwargs['launch_configuration']
    if kwargs['health_check_grace_period']:
        order_dict['health_check_grace_period'] = kwargs['health_check_grace_period']
    if kwargs['health_check_type']:
        order_dict['health_check_type'] = kwargs['health_check_type']
    if kwargs['desired_capacity']:
        order_dict['desired_capacity'] = kwargs['desired_capacity']
    if kwargs['force_delete']:
        order_dict['force_delete'] = kwargs['force_delete']
    if kwargs['vpc_zone_identifier']: 
        order_dict['vpc_zone_identifier'] = kwargs['vpc_zone_identifier']
    if kwargs['built_tags']: 
        order_dict['built_tags'] = kwargs['built_tags']
        
    for key, value in order_dict.iteritems():
        if value != None:
            if key == 'asgname':
                continue
            if key != 'built_tags':
                if key != 'force_delete' and key != 'health_check_grace_period' and key != 'min_size' and key != 'max_size' and key != 'desired_capacity' and key != 'availability_zones' and key != 'vpc_zone_identifier':
                    asg_string = asg_string + '        %s = "%s"\n' % (key, value)
                else:
                    asg_string = asg_string + '        %s = %s\n' % (key, value)
            else:
                asg_string = asg_string + '        %s\n' % (value)
    asg_string = asg_string + '\n    }'
    return asg_string
                        
def build_security_group(security_groups, cluster_name):
    security_group = ''
    for group in security_groups.split(','):
            if 'name' in str(group):
                name = group.split(':')[0].split('=')[1]
                name2 = group.split(':')[0].split('=')[1]
                security_group_name.append("${aws_security_group.%s.id}" % name)
                description = group.split(':')[1].split('=')[1]
                rules = group.split('!')[1]
                rule_name = group.split(':')[2].split('=')[0].replace('!','')
                rules = build_rules(rule_name, rules)
                security_group = security_group + '''
                resource "aws_security_group" "%s" {
                    name = "%s"
                    description = "%s"
                    %s
                }''' % (name, name2, description, rules)   
            else:
                break   
    return_list = (security_group,security_group_name)    
    return return_list  



asg_name = asg_name + '_' + lc_image_id + '_' + role
cluster_name = asg_name
security_groups = build_security_group(security_groups, cluster_name)
security_group_name = security_groups[1]
security_groups = security_groups[0]
lc_security_groups = security_group_name

    
if tags:
    built_tags = build_tags(tags)
else:
    built_tags = ''
    
user_data_ins = [('export CLOUD_ENVIRONMENT=%s\n' % cloud_environment),
                 ('export CLOUD_MONITOR_BUCKET=%s\n' % cluster_monitor_bucket),
                 ('export CLOUD_APP=%s\n' % cluster_name),
                 ('export CLOUD_STACK=%s\n' % cloud_stack),
                 ('export CLOUD_CLUSTER=%s\n' % cloud_cluster),
                 ('export CLOUD_AUTO_SCALE_GROUP=%s\n'% cloud_auto_scale_group),
                 ('export CLOUD_LAUNCH_CONFIG=%s\n'% cloud_launch_config),
                 ('export EC2_REGION=%s\n' % provider_region),
                 ('export CLOUD_DEV_PHASE=%s\n'% cloud_dev_phase),
                 ('export CLOUD_REVISION=%s\n'% cloud_revision),
                 ('export CLOUD_DOMAIN=%s\n'% cloud_domain),]

for var in in_user_data.split('|'):
    user_data_ins.append(var + '\n')

text_file = open("user-data.txt", "wa")

for line in user_data_ins:
    text_file.write(line)
    
text_file.close()
lc_user_data = '${file("user-data.txt")}'

launch_config_variable = "${aws_launch_configuration.%s.id}" % lc_name

launch_configuration = build_lc(lc_name,lc_name, lc_image_id, lc_instance_type, lc_public_ip, lc_security_groups, lc_iam_instance_profile, lc_user_data, lc_key_name,block_device_mapping)

autoscale_group = build_asg(built_tags = built_tags if built_tags else None,
                              asgname = asg_name, 
                              availability_zones = az_list, 
                              name = asg_name, 
                              max_size = max_size, 
                              min_size = min_size, 
                              launch_configuration = launch_config_variable, 
                              health_check_grace_period = hc_period if hc_period else None, 
                              health_check_type = hc_type if hc_type else None, 
                              desired_capacity = desired_size if desired_size else None, 
                              force_delete = force_delete if force_delete else None,
                              vpc_zone_identifier = vpc_zone_ident if vpc_zone_ident else None
                              )   


#always
provider = """
        provider "aws" {
            access_key = "%s"
            secret_key = "%s"
            region = "%s"
        }
""" % (access_key, secret_key, provider_region)

text_file = open("Output.tf", "wa")
text_file.write(provider)
text_file.write(security_groups)
text_file.write(launch_configuration)
text_file.write(autoscale_group)
text_file.close()
