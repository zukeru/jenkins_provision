#!/bin/bash -x

sudo python $WORKSPACE/build_asg.py --vpc_id $vpc_id --sg_tag $sg_tag --env $env_name --secret_key $AWS_SECRET_KEY --access_key $AWS_ACCESS_KEY --wd "$WORKSPACE" --provider-region "$provider_region" --min_size "$min_size" --max_size "$max_size" --asg_name "$asg_name" --azs "$azs" --desired_size "$desired_size" --force_delete "$force_delete" --hc_type "$hc_type" --hc_period "$hc_period" --lc_image_id "$lc_image_id" --lc_instance_type "$lc_instance_type" --lc_iam_instance_profile "$lc_iam_instance_profile" --lc_key_name "$lc_key_name" --in_user_data "$in_user_data" --tags "$tags" --block_devices "$block_devices" --asg_vpc_ident "$asg_vpc_ident" --cloud_stack "$cloud_stack" --cloud_environment "$cloud_environment" --cloud_domain "$cloud_domain" --cluster_monitor_bucket "$cluster_monitor_bucket" --cloud_cluster "$cloud_cluster" --cloud_auto_scale_group "$cloud_auto_scale_group" --cloud_launch_config "$cloud_launch_config" --cloud_dev_phase "$cloud_dev_phase" --cloud_revision "$cloud_revision" --role "$role" --security_groups "$security_groups"
sudo wget https://dl.bintray.com/mitchellh/terraform/terraform_0.5.3_linux_amd64.zip
sudo unzip terraform_0.5.3_linux_amd64.zip
sudo cat $WORKSPACE/Output.tf
sudo cat $WORKSPACE/user-data.txt
sudo $WORKSPACE/terraform apply $WORKSPACE
sudo rm -rf $WORKSPACE/*
