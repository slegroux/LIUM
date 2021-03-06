#!/usr/bin/env bash
#
# Usage:
#$./s3_diarize_16k.sh s3://workfit-diarization-input-staging/input.wav  s3://workfit-diarization-output-staging
#
s3_input=$1
s3_output=$2
bn=$(basename $s3_input)
dn=$(dirname $s3_input)

#fn=$(basename $s3_input .wav)
ext="${bn##*.}"
fn="${bn%.*}"

#echo 'basename:'$bn 'dirname:'$dn 'ext: '$ext 'filename: '$fn

aws s3 cp $s3_input ./tmp

if [ $ext = 'mp3' ]; then
   # resample to 16k and convert to wav
   sox ./tmp/$bn --rate 16k ./tmp/$fn.wav
   bn=$fn.wav
   echo $bn
fi


./ilp_diarization2.sh ./tmp/$bn 120 ./tmp/

./seg2json.py ./tmp/$bn ./tmp/$fn/$fn.ev_is.120.seg ./tmp/$fn/$fn.json ./tmp

aws s3 cp ./tmp/$fn/$fn.json $s3_output
# TODO: uncomment if tyler is interested in getting audio file segments for UI
# aws s3 cp ./tmp/*.wav $s3_output
rm -rf ./tmp/*
rm *.seg
 
#why 120?
#http://www.mickael-rouvier.fr/files/cross-show_diarization.pdf

