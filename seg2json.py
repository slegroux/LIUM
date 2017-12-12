#!/usr/bin/env python

import json
import logging
import sys
import os
from IPython import embed
from decimal import Decimal
import subprocess
import shlex
import io

LOG = logging.getLogger(__name__)

audio_file = sys.argv[1]
segment = sys.argv[2]
output = sys.argv[3]
output_dir  = sys.argv[4]

# [START def_transcribe_gcs]
def transcribe_gcs_with_word_time_offsets(gcs_uri):
    """Transcribe the given audio file asynchronously and output the word time
    offsets."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_word_time_offsets=True)

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    result = operation.result(timeout=90)

    # for result in result.results:
    #     alternative = result.alternatives[0]
    #     print('Transcript: {}'.format(alternative.transcript))
    #     print('Confidence: {}'.format(alternative.confidence))

    #     for word_info in alternative.words:
    #         word = word_info.word
    #         start_time = word_info.start_time
    #         end_time = word_info.end_time
    #         print('Word: {}, start_time: {}, end_time: {}'.format(
    #             word,
    #             start_time.seconds + start_time.nanos * 1e-9,
    #             end_time.seconds + end_time.nanos * 1e-9))
    res = {}
    for result in result.results:
        alternative = result.alternatives[0]
#        print('Transcript: {}'.format(alternative.transcript))
        res['text'] = alternative.transcript
        res['alignments'] = []
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            word_alignment = {}
            # print('Word: {}, start_time: {}, end_time: {}'.format(
            #     word,
            #     start_time.seconds + start_time.nanos * 1e-9,
            #     end_time.seconds + end_time.nanos * 1e-9))
            word_alignment['word'] = word
            word_alignment['start_time'] = start_time.seconds + start_time.nanos * 1e-9
            word_alignment['end_time'] = end_time.seconds + end_time.nanos * 1e-9
            res['alignments'].append(word_alignment)
    return(res)
#    print(json.dumps(res))


# [END def_transcribe_gcs]


def transcribe_file_with_word_time_offsets(speech_file):
    """Transcribe the given audio file synchronously and output the word time
    offsets."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()
    res = {}

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    AUDIO = TYPES.RECOGNITIONAUDIO(CONTENT=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_word_time_offsets=True)

    response = client.recognize(config, audio)

    for result in response.results:
        alternative = result.alternatives[0]
#        print('Transcript: {}'.format(alternative.transcript))
        res['text'] = alternative.transcript
        res['alignments'] = []
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            word_alignment = {}
            # print('Word: {}, start_time: {}, end_time: {}'.format(
            #     word,
            #     start_time.seconds + start_time.nanos * 1e-9,
            #     end_time.seconds + end_time.nanos * 1e-9))
            word_alignment['word'] = word
            word_alignment['start_time'] = start_time.seconds + start_time.nanos * 1e-9
            word_alignment['end_time'] = end_time.seconds + end_time.nanos * 1e-9
            res['alignments'].append(word_alignment)
#    print(json.dumps(res))
    return(res)
        
def split_and_transcribe(file_name, start_time, end_time, output):
    base_name = os.path.basename(file_name)
    name = os.path.splitext(base_name)[0]
    output_name = name + '.' + str(round(start_time * 1000)) + '.' + str(round(end_time * 1000)) + os.path.splitext(base_name)[1]
    output_name = os.path.join(output, output_name)
    cmd_list = ['sox', file_name, output_name, 'trim ', start_time, end_time - start_time]
    cmd = " ".join(str(item) for item in cmd_list)
    subprocess.call(shlex.split(cmd))
    gs_bucket = 'gs://word-alignments'
    cmd_list = ['gsutil', 'cp', output_name, gs_bucket]
    cmd = " ".join(str(item) for item in cmd_list)
    subprocess.call(shlex.split(cmd))
    gs_uri = gs_bucket + '/' + os.path.basename(output_name)
 
    # res = transcribe_file_with_word_time_offsets(output_name)
    # embed()
    res = transcribe_gcs_with_word_time_offsets(gs_uri)
    return(res)
        

def seg_to_dict(audio_file, file_name, output, output_dir):
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
                    length = Decimal(words[3]) / 100
                    end_time = (Decimal(words[2]) + Decimal(words[3])) / 100
                    segment['speaker'] = speaker_gender
                    segment['start_time'] = str(start_time)
                    segment['end_time'] = str(end_time)
                    res =  split_and_transcribe(audio_file, start_time, end_time, output_dir)
                    if res:
                        segment['text'] = res['text']
                        segment['alignments'] = res['alignments']
                        
                    diarize_dict['diarized_transcript'].append(segment)
                        
        with open(output, 'w') as file_out:
            json.dump(diarize_dict, file_out, sort_keys=True, indent=4)
        LOG.info('seg_to_dict: %s: Completed.', words[0])




def main(argv):
    seg_to_dict(audio_file, segment, output, output_dir)
#    split_and_transcribe(audio_file, 0, 10, output_dir)
#    split_and_transcribe(audio_file, 10, 20, output_dir)
    


if __name__ == "__main__":
    main(sys.argv)
    
