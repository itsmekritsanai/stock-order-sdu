"""
Launch Script for Suan Dusit University - Digital Stock & Requisition System
Starts local HTTP server on port 8080 (if not already running) and opens browser.
"""

import sys
import os
import socket
import webbrowser
import subprocess
import time

PORT = 8080

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("=" * 65)
    print("  ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต")
    print("  Suan Dusit University - Stock Order SDU")
    print("=" * 65)

    if is_port_in_use(PORT):
        print(f"[*] เว็บเซิร์ฟเวอร์กำลังทำงานอยู่ที่พอร์ต {PORT} (Active)")
    else:
        print(f"[*] กำลังเริ่มทำงาน Local Web Server บนพอร์ต {PORT}...")
        subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], cwd=os.path.dirname(os.path.abspath(__file__)))
        time.sleep(1.5)

    url = f"http://localhost:{PORT}/portal.html"
    print(f"[*] กำลังเปิดเว็บเบราว์เซอร์: {url}")
    webbrowser.open(url)
    print("[+] เปิดหน้าเว็บเรียบร้อยแล้ว!")

if __name__ == '__main__':
    main()
