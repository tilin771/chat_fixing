FROM python:3.13-alpine

# Crear usuario sin privilegios
RUN adduser -D appuser

WORKDIR /app

# Copiar requirements desde la subcarpeta
COPY chatbot_streamlit_lambda/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY chatbot_streamlit_lambda/ /app/

# Establecer permisos
RUN chown -R appuser:appuser /app
USER appuser

# Asegurar que Python encuentre los módulos
ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false"]
