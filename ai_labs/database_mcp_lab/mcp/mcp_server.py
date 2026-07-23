import socket
import mysql.connector
import json

def run_query(query):
    try:
        conn = mysql.connector.connect(
            host="db",  # docker service name
            user="demo",
            password="demo123",
            database="demo_db"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        conn.close()
        return {"columns": columns, "rows": results}
    except Exception as e:
        return {"error": str(e)}

def main():
    host, port = "0.0.0.0", 9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    print(f"MCP server listening on {port}...")

    while True:
        conn, addr = sock.accept()
        data = conn.recv(4096).decode()
        try:
            req = json.loads(data)
            sql = req.get("sql", "")
            resp = run_query(sql)
        except Exception as e:
            resp = {"error": str(e)}
        conn.send(json.dumps(resp).encode())
        conn.close()

if __name__ == "__main__":
    main()
