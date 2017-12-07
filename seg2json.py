#!/usr/bin/env python

import json
import logging
import sys
from IPython import embed
from decimal import Decimal

LOG = logging.getLogger(__name__)

file_name = sys.argv[1]
output  = sys.argv[2]

def seg_to_dict(file_name, output):
        """Convert LIUM output to json"""
        diarize_dict = dict()
        diarize_dict['diarized_transcript']=[]
        diarize_dict['status']='ready'
        with open(file_name, 'r') as file_:
            line_list = file_.readlines()
            for line in line_list:
                segment = {}
                words = line.strip().split()
                if words[0] != ';;':
                    speaker_gender = words[7] + '-' + words[4]
                    start_time = Decimal(words[2]) / 100
                    end_time = (Decimal(words[2]) + Decimal(words[3])) / 100
                    segment['speaker'] = speaker_gender
                    segment['start_time'] = str(start_time)
                    segment['end_time'] = str(end_time)
                    diarize_dict['diarized_transcript'].append(segment)
        with open(output, 'w') as file_out:
            json.dump(diarize_dict, file_out, sort_keys=True, indent=4)
        LOG.info('seg_to_dict: %s: Completed.', words[0])

seg_to_dict(file_name, output)
