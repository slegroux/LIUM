#!/usr/bin/env python
import boto3
import json
import subprocess
import shlex
import logging

from IPython import embed

sqs = boto3.resource('sqs')
queue_name = 'workfit-diarization-test'
queue = sqs.get_queue_by_name(QueueName=queue_name)
URL = 'https://sqs.us-west-2.amazonaws.com/709167633498/workfit-diarization-test'

def process(bucket_name, file_name):
    print(bucket_name, file_name)
    cmd='./s3_diarize_16k.sh s3://workfit-diarization-input-staging/'+ file_name + ' s3://workfit-diarization-output-staging'
    subprocess.call(shlex.split(cmd))


while 1:
    messages = queue.receive_messages(WaitTimeSeconds=20)
    
    for message in messages:
        try:
            jb = json.loads(message.body)
        except ValueError:
            print("message has no body")
            
        try:
           event_name = jb['Records'][0]['eventName']
           if event_name =='ObjectCreated:Put':
               bucket_name = jb['Records'][0]['s3']['bucket']['name']
               file_name = jb['Records'][0]['s3']['object']['key']
               process(bucket_name, file_name)
        except KeyError:
            print("irrelevant event type")
        message.delete()
