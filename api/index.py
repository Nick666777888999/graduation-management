from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = {
            "status": "success", 
            "message": "畢業管理系統 API",
            "endpoints": ["/api/health", "/api/admin/users"]
        }
        self.wfile.write(str(message).encode())
        return
