FROM ubuntu:16.04
MAINTAINER Sylvain Le Groux (sylvainlg@voicera.ai)

RUN apt-get update -yqq
RUN apt-get install -yqq git
RUN apt-get install -yqq emacs-nox

RUN apt-get install -yqq software-properties-common python-software-properties
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update
RUN apt-get install -yqq openjdk-7-jdk
RUN apt-get install -yqq glpk-utils
RUN apt-get update
RUN apt-get install -yqq python-pip python-dev build-essential 
RUN pip install --upgrade pip
RUN pip install awscli --upgrade --user
RUN pip install boto3
ENV PATH="~/.local/bin:${PATH}"

RUN git clone https://github.com/slegroux/LIUM /root/LIUM
#RUN git clone https://github.com/gcuisinier/jenv.git ~/.jenv
#RUN echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.bash_profile

RUN mkdir -p /root/Data
RUN mkdir -p /root/LIUM/tmp
RUN mkdir -p /root/.aws
WORKDIR /root/LIUM
COPY s3_diarize_16k.sh /root/LIUM
COPY seg2json.py /root/LIUM
COPY sqs_poll.py /root/LIUM


ENV DATA /root/Data
ENV LIUM /root/LIUM

#ENTRYPOINT ["/root/LIUM/sqs_poll.py"]
#ENTRYPOINT ["/bin/bash", "-c", "/root/LIUM/diarize_16k.sh", "/root/LIUM/test_wav/t001.wav", "/root/LIUM/test_out"]
#CMD ["../Data/Tests/diarizationExample.wav", "../Data/DiarizationOut"]
#CMD ["./test_wav/t001.wav", "./test_out"]
