import copy
import logging
import os

import boto3

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'ERROR'))

ec2 = boto3.client('ec2', region_name='eu-west-1')
ebs = boto3.resource('ec2', region_name='eu-west-1')
logger = logging.getLogger(__name__)


def tag_snapshots():

    #Define an empty Array for the list of snapshots
    snapshots = {}

    #Populate the Aaary as a dict
    for response in ec2.get_paginator('describe_snapshots').paginate(OwnerIds=['self']):
        snapshots.update([(snapshot['SnapshotId'], snapshot) for snapshot in response['Snapshots']])

    #Run over the array and tag
    for snapshot in snapshots.values():

        #Check If the Name Tag already exists
        try:
            snapshot_tags=(boto3_tag_list_to_dict(snapshot.get('Tags', [])))
            Name = snapshot_tags['Name']
        except:
            Name = "NoName" 
       
        #If the Snapshot Name is empty lets treat it as NoName 
        if Name == '':
            Name = "NoName"

        #If the snapshot has NoName we carry on
        if Name == "NoName":
            
            #Check if the snapshot has a Volume reference
            try:
                VolumeName = snapshot['VolumeId']
            except:
                VolumeName = "NoVolumeName"

            #Check if snapshot has VolumeName
            if VolumeName != "NoVolumeName":

                #Lets get the name Tag from the Volume
                volume = ebs.Volume(VolumeName)
                snapshot_tag_name = {}
                try:
                    snapshot_tag_name['Name']=boto3_tag_list_to_dict(volume.tags)['Name']
                except:
                    snapshot_tag_name['Name']="Source Unknown"

                print("Tagging snapshot ",snapshot['SnapshotId']," with tag Name ",snapshot_tag_name['Name'])
                ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=dict_to_boto3_tag_list(snapshot_tag_name))
            else:
                snapshot_tag_name['Name']="Source Unknown"
                print("Tagging snapshot ",snapshot['SnapshotId']," with tag Name ",snapshot_tag_name['Name'])
                ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=dict_to_boto3_tag_list(snapshot_tag_name))
        else:
            print("Snapshot ",snapshot['SnapshotId']," is already tagged")
 
def boto3_tag_list_to_dict(tags_list):
    tags_dict = {}
    for tag in tags_list:
        if 'key' in tag and not tag['key'].startswith('aws:'):
            tags_dict[tag['key']] = tag['value']
        elif 'Key' in tag and not tag['Key'].startswith('aws:'):
            tags_dict[tag['Key']] = tag['Value']

    return tags_dict


def dict_to_boto3_tag_list(tags_dict):
    tags_list = []
    for k, v in tags_dict.items():
        tags_list.append({'Key': k, 'Value': v})

    return tags_list


if __name__ == '__main__':
    tag_snapshots()

