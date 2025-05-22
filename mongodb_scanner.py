#!/usr/bin/env python3

import subprocess
import platform
import sys
import argparse
import os
import requests
from typing import List, Optional
import json

def check_mongosh_installed() -> bool:
    """Check if mongosh is installed and available in PATH"""
    try:
        subprocess.run(['mongosh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_os_info() -> dict:
    """Get OS information for mongosh download"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map platform to MongoDB download format
    os_map = {
        'linux': {
            'x86_64': 'linux-x64',
            'aarch64': 'linux-arm64',
            'arm64': 'linux-arm64'
        },
        'darwin': {
            'x86_64': 'macos-x64',
            'arm64': 'macos-arm64'
        },
        'windows': {
            'amd64': 'win32-x64'
        }
    }
    
    return {
        'system': system,
        'machine': machine,
        'download_type': os_map.get(system, {}).get(machine, 'unknown')
    }

def get_latest_mongosh_version() -> Optional[str]:
    """Get latest mongosh version from MongoDB website"""
    try:
        response = requests.get('https://www.mongodb.com/try/download/shell')
        # This is a simplified version - in reality, you'd need to parse the HTML
        # or use their API to get the latest version
        return "2.5.1"  # Placeholder - implement proper version detection
    except Exception as e:
        print(f"Error getting latest version: {e}")
        return None

def scan_mongodb(host: str, port: int = 27017) -> bool:
    """Scan a single MongoDB instance"""
    try:
        # Run mongosh command
        cmd = f"mongosh --host {host} --port {port} --eval 'show dbs'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n[+] Successfully connected to {host}:{port}")
            print("Databases found:")
            print(result.stdout)
            return True
        else:
            print(f"[-] Failed to connect to {host}:{port}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[-] Error scanning {host}:{port} - {str(e)}")
        return False

def scan_from_file(file_path: str) -> None:
    """Scan multiple MongoDB instances from a file"""
    try:
        with open(file_path, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
        
        for target in targets:
            if ':' in target:
                host, port = target.split(':')
                port = int(port)
            else:
                host = target
                port = 27017
            
            scan_mongodb(host, port)
            
    except FileNotFoundError:
        print(f"[-] File not found: {file_path}")
    except Exception as e:
        print(f"[-] Error reading file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='MongoDB Scanner')
    parser.add_argument('-t', '--target', help='Single target (host:port)')
    parser.add_argument('-l', '--list', help='File containing list of targets')
    
    args = parser.parse_args()
    
    # Check if mongosh is installed
    if not check_mongosh_installed():
        print("[-] mongosh is not installed")
        os_info = get_os_info()
        latest_version = get_latest_mongosh_version()
        
        if latest_version and os_info['download_type'] != 'unknown':
            print(f"\n[!] Please install mongosh version {latest_version}")
            print(f"Download URL: https://www.mongodb.com/try/download/shell")
            print(f"Your system: {os_info['system']} {os_info['machine']}")
            print(f"Download type: {os_info['download_type']}")
        sys.exit(1)
    
    # Process targets
    if args.target:
        if ':' in args.target:
            host, port = args.target.split(':')
            scan_mongodb(host, int(port))
        else:
            scan_mongodb(args.target)
    elif args.list:
        scan_from_file(args.list)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
