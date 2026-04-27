FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY .streamlit ./.streamlit
COPY new_app_output.py ./
COPY video ./video

RUN pip install --no-cache-dir pyserial streamlit requests

EXPOSE 8501

CMD ["streamlit", "run", "new_app_output.py", "--server.address=0.0.0.0", "--server.port=8501"]