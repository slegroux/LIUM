#!/usr/bin/env bash
CONTAINER_ID=$1
WAV_FILE=$2
OUTPUT_FOLDER=DiarizationOut
BASE_NAME=$(basename $WAV_FILE)
NAME="${BASE_NAME%.*}"

# PD STUFF
CONTENT_TYPE="application/json"
DESCRIPTION="bad things™ are happening"
URL="https://events.pagerduty.com/generic/2010-04-15/create_event.json"
service_key=$PD_KEY

function pd_trigger () {
  curl -H "${CONTENT_TYPE}" \
       -X POST \
       -d "{ \"service_key\": \"$service_key\", \"event_type\": \"trigger\", \"description\": \"$1\" }" "${URL}"
}


echo '--- Check audio sample rate is 16kHz'
is_16kHz=$(soxi $WAV_FILE |grep -i 'sample rate'|cut -f2 -d":"| xargs -I{} echo {} == 16000 | bc)
if [ $is_16kHz -eq 1 ]; then
    docker exec $CONTAINER_ID bash -c "./diarize_16k.sh ../Data/$WAV_FILE ../Data/DiarizationOut"
    cp $OUTPUT_FOLDER/$NAME/$NAME.ev_is.120.seg $OUTPUT_FOLDER
    echo '--- load to S3 bucket'
    aws s3 cp $OUTPUT_FOLDER/$NAME/$NAME.ev_is.120.seg s3://workfit-diarization
    rm -rf $$OUTPUT_FOLDER
    exit 0
else
  err_msg="[Diarization]: this feature works only for 16kHz audio for now !"
  echo $err_msg
  pd_trigger "$err_msg"
  exit 1
fi

