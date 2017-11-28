#!/urs/bin/env bash
CONTAINER_ID=$1
WAV_FILE=$2
docker exec $CONTAINER_ID bash -c "diarize_16k.sh /root/Data/ $WAV_FILE"
