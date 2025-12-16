"""
ADB Manager - Handles all ADB communication
"""

import subprocess
import time
import os
import re
from pathlib import Path

class ADBManager:
    def __init__(self):
        self.adb_path = self.find_adb()
        self.devices = []
        self.timeout = 30
    
    def find_adb(self):
        """Find ADB executable in common locations"""
        possible_paths = [
            "adb",
            "/usr/bin/adb",
            "/usr/local/bin/adb",
            "C:\\Android\\platform-tools\\adb.exe",
            str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe"),
            str(Path.home() / "Library/Android/sdk/platform-tools/adb"),
        ]
        
        for path in possible_paths:
            if self._check_adb_path(path):
                return path
        
        return None
    
    def _check_adb_path(self, path):
        """Check if ADB executable exists and works"""
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_adb_installed(self):
        """Check if ADB is properly installed"""
        if not self.adb_path:
            print("ADB not found. Please install Android Platform Tools.")
            print("Download from: https://developer.android.com/studio/releases/platform-tools")
            return False
        return True
    
    def execute_command(self, command, wait_for_device=False):
        """Execute ADB command with error handling"""
        if not self.adb_path:
            raise Exception("ADB not found")
        
        full_command = [self.adb_path] + command
        
        try:
            if wait_for_device:
                self.wait_for_device()
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    def wait_for_device(self, max_attempts=30):
        """Wait for device to be available"""
        print("Waiting for device...", end='', flush=True)
        
        for i in range(max_attempts):
            result = self.execute_command(['devices'])
            if 'device\n' in result['output']:
                print(" ✓ Device connected")
                return True
            
            print('.', end='', flush=True)
            time.sleep(1)
        
        print(" ✗ Device not found")
        return False
    
    def get_device_info(self, device_id=None):
        """Get detailed device information"""
        commands = [
            ('shell getprop ro.product.model', 'Model'),
            ('shell getprop ro.build.version.release', 'Android Version'),
            ('shell getprop ro.build.version.security_patch', 'Security Patch'),
            ('shell getprop ro.product.manufacturer', 'Manufacturer'),
            ('shell getprop ro.serialno', 'Serial Number'),
            ('shell getprop ro.bootloader', 'Bootloader'),
            ('shell getprop ro.hardware', 'Hardware'),
        ]
        
        info = {}
        
        for cmd, key in commands:
            result = self.execute_command(cmd.split())
            if result['success'] and result['output']:
                info[key] = result['output'].strip()
        
        return info
    
    def reboot_device(self, mode='system'):
        """Reboot device to different modes"""
        modes = {
            'system': '',
            'recovery': 'recovery',
            'bootloader': 'bootloader',
            'fastboot': 'bootloader',
            'download': 'download',
            'sideload': 'sideload',
        }
        
        if mode not in modes:
            print(f"Invalid mode: {mode}")
            return False
        
        cmd = ['reboot']
        if modes[mode]:
            cmd.append(modes[mode])
        
        result = self.execute_command(cmd)
        
        if result['success']:
            print(f"Device rebooting to {mode} mode...")
            time.sleep(5)
            return True
        
        return False
    
    def is_device_rooted(self):
        """Check if device has root access"""
        result = self.execute_command(['shell', 'su', '-c', 'echo root_check'])
        
        if result['success'] and 'root_check' in result['output']:
            return True
        
        # Alternative check
        result = self.execute_command(['shell', 'which', 'su'])
        return result['success'] and '/su' in result['output']
    
    def push_file(self, local_path, device_path):
        """Push file to device"""
        if not os.path.exists(local_path):
            print(f"Local file not found: {local_path}")
            return False
        
        result = self.execute_command(['push', local_path, device_path])
        
        if result['success']:
            print(f"File pushed: {local_path} -> {device_path}")
            return True
        
        print(f"Failed to push file: {result['error']}")
        return False
    
    def pull_file(self, device_path, local_path):
        """Pull file from device"""
        result = self.execute_command(['pull', device_path, local_path])
        
        if result['success']:
            print(f"File pulled: {device_path} -> {local_path}")
            return True
        
        print(f"Failed to pull file: {result['error']}")
        return False
    
    def shell_command(self, command, root=False):
        """Execute shell command on device"""
        if root:
            command = f'su -c "{command}"'
        
        result = self.execute_command(['shell', command])
        return result