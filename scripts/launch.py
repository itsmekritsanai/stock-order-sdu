"""
Launch Script for Suan Dusit University - Digital Stock & Requisition System
Starts Unified Web & MySQL REST API Server (backend/server.py) on port 8080 and opens browser.
"""

import os
import socket
import subprocess
import sys
import time
import webbrowser

PORT = 8080
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_SCRIPT = os.path.join(PROJECT_ROOT, "backend", "server.py")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    print("=" * 65)
    print("  ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต")
    print("  Suan Dusit University - Stock Order SDU (MySQL Edition v2.0.0)")
    print("=" * 65)

    if is_port_in_use(PORT):
        print(f"[*] เซิร์ฟเวอร์กำลังทำงานอยู่ที่พอร์ต {PORT} (Active)")
    else:
        print(f"[*] กำลังเริ่มทำงาน Web & MySQL REST API Server บนพอร์ต {PORT}...")
        subprocess.Popen([sys.executable, SERVER_SCRIPT], cwd=PROJECT_ROOT)
        time.sleep(1.5)

    url = f"http://localhost:{PORT}/portal.html"
    print(f"[*] กำลังเปิดเว็บเบราว์เซอร์: {url}")
    webbrowser.open(url)
    print("[+] เปิดหน้าเว็บเรียบร้อยแล้ว!")


if __name__ == "__main__":
    main()
