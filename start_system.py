import socket
import threading
import webbrowser
import time
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import os

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def get_network_info():
    """獲取網路資訊"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "無法取得"
            
        return {
            'hostname': hostname,
            'local_ip': local_ip,
            'public_ip': public_ip
        }
    except:
        return {
            'hostname': 'unknown',
            'local_ip': '127.0.0.1',
            'public_ip': '無法取得'
        }

def start_backend():
    """啟動後端伺服器"""
    print("啟動後端伺服器...")
    try:
        subprocess.run(['python', 'app.py'], check=True)
    except subprocess.CalledProcessError:
        print("後端啟動失敗，嘗試使用 Python3...")
        subprocess.run(['python3', 'app.py'], check=True)

def start_frontend():
    """啟動前端伺服器"""
    print("啟動前端伺服器...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server = HTTPServer(('0.0.0.0', 8000), CORSHTTPRequestHandler)
    print("前端伺服器運行在 http://0.0.0.0:8000")
    server.serve_forever()

def main():
    """主程式"""
    network_info = get_network_info()
    
    print("=" * 60)
    print("          畢業資料管理系統 - 一鍵啟動")
    print("=" * 60)
    print(f"電腦名稱: {network_info['hostname']}")
    print(f"區域網路 IP: {network_info['local_ip']}")
    print(f"公共 IP: {network_info['public_ip']}")
    print("-" * 60)
    
    # 啟動後端（在新線程中）
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 等待後端啟動
    print("等待後端伺服器啟動...")
    time.sleep(3)
    
    # 啟動前端（在新線程中）
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # 等待前端啟動
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("系統啟動完成！")
    print("=" * 60)
    print("訪問地址:")
    print(f"📍 本機訪問: http://localhost:8000")
    print(f"📍 區域網路: http://{network_info['local_ip']}:8000")
    
    if network_info['public_ip'] != "無法取得":
        print(f"📍 外網訪問: http://{network_info['public_ip']}:8000")
        print("   💡 注意: 外網訪問需要設置路由器端口轉發")
    
    print("\n📱 手機訪問:")
    print(f"   請在手機瀏覽器輸入: http://{network_info['local_ip']}:8000")
    print("   確保手機和電腦在同一 WiFi 網路")
    
    print("\n🛡️  管理員帳號:")
    print("   帳號: Nick20130104")
    print("   密碼: Nick20130104")
    
    print("=" * 60)
    print("按 Ctrl+C 可停止系統")
    
    # 自動打開瀏覽器
    try:
        webbrowser.open('http://localhost:8000')
    except:
        pass
    
    try:
        # 保持主程式運行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n系統正在關閉...")

if __name__ == '__main__':
    main()