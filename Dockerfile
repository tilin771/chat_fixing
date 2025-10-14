FROM python:3.13-alpine
 
# Create and switch to non-root user
RUN adduser -D appuser
 
WORKDIR /app
 
# Install dependencies
COPY chatbot_streamlit_lambda/* /app
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy application code and set ownership
COPY . /app
RUN chown -R appuser:appuser /app
 
USER appuser

ENV PYTHONPATH=/app

EXPOSE 8501
 
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false"]
