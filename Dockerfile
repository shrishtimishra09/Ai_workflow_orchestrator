FROM python:3.11-slim
WORKDIR /app
COPY backend/ backend/
COPY ai_agent/ ai_agent/
COPY frontend/build/ frontend/build/
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
EXPOSE 5000 5001
CMD ["sh", "-c", "python backend/app.py & python ai_agent/ai_agent.py"]
