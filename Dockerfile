FROM tiangolo/uvicorn-gunicorn:python3.8

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OCCAM Transcription
RUN pip install git+https://github.com/CrossLangNV/OCCAM_transcription.git

WORKDIR "/app"
