FROM python:3.11-slim

WORKDIR /mcp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py .

EXPOSE 9000

CMD ["python", "mcp_server.py"]
