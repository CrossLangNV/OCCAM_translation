FROM tiangolo/uvicorn-gunicorn:python3.8

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dependencies
# COPY ./api/ /app/API/translation
# Copy all the subdirs.
# COPY ./CEF-eTranslation_connector/ /app
# COPY ./multilingual_pageXML/ /app/multilingual_pageXML

# OCCAM Transcription
RUN pip install git+https://github.com/CrossLangNV/OCCAM_transcription.git

WORKDIR "/app"
