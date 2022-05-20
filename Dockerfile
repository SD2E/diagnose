FROM continuumio/miniconda3:latest

WORKDIR /data-diagnose
COPY conda_env.yml setup.py README.md git_version.txt ./
ADD src/ ./src/

# from the gitlab ci
RUN apt update
RUN apt-get install --yes gcc --fix-missing
RUN conda env create --file conda_env.yml
RUN [ "/bin/bash", "-c", "source activate gda_data_diagnose && pip install ." ]
RUN echo "source activate gda_data_diagnose" > ~/.bashrc
RUN export PYTHONPATH=/data-diagnose:$PYTHONPATH
