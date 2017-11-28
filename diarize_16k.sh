#!/usr/bin/env bash

input=$1
outputfolder=$2

#mkdir -p $outputfolder

./ilp_diarization2.sh $input 120 $outputfolder

#why 120?
#http://www.mickael-rouvier.fr/files/cross-show_diarization.pdf




