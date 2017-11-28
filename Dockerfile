FROM ubuntu:16.04
MAINTAINER Sylvain Le Groux (sylvainlg@voicera.ai)

#RUN apt-get update -yqq
RUN apt-get install -yqq git
RUN apt-get install -yqq emacs-nox

RUN apt-get install -yqq software-properties-common python-software-properties
RUN add-apt-repository ppa:openjdk-r/ppa
#RUN apt-get update
RUN apt-get install -yqq openjdk-7-jdk
RUN apt-get install -yqq glpk-utils

RUN git clone https://github.com/slegroux/LIUM
#RUN git clone https://github.com/gcuisinier/jenv.git ~/.jenv
#RUN echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.bash_profile

WORKDIR /root/LIUM

#ENTRYPOINT ["/bin/cat"]
#CMD ["/etc/passwd"]