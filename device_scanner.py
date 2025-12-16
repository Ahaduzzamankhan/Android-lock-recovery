"""
Device Scanner - Detects and analyzes connected Android devices
"""

import re
import json
from datetime import datetime
from adb_manager import ADBManager

class DeviceScanner:
    def __init__(self):
        self.adb = ADBManager()
        self.scan_results = []
    
    def scan_devices(self):
        """Scan for connected Android devices"""
        print("🔍 Scanning for Android devices...")
        
        self.scan_results = []
        
        # Get list of devices
        result = self.adb.execute_command(['devices'])
        
        if not result['success']:
            print("Failed to scan devices")
            return []
        
        # Parse device list
        lines = result['output'].strip().split('\n')
        
        if len(lines) <= 1:
            print("No devices found")
            return []
        
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                serial = parts[0].strip()
                status = parts[1].strip()
                
                if status == 'device':
                    device_info = self._get_device_details(serial)
                    self.scan_results.append(device_info)
        
        return self.scan_results
    
    def _get_device_details(self, serial):
        """Get detailed information about a device"""
        device = {
            'serial': serial,
            'scan_time': datetime.now().isoformat(),
            'status': 'connected'
        }
        
        # Get basic info
        commands = {
            'model': 'shell getprop ro.product.model',
            'brand': 'shell getprop ro.product.brand',
            'manufacturer': 'shell getprop ro.product.manufacturer',
            'device': 'shell getprop ro.product.device',
            'android_version': 'shell getprop ro.build.version.release',
            'api_level': 'shell getprop ro.build.version.sdk',
            'security_patch': 'shell getprop ro.build.version.security_patch',
            'build_id': 'shell getprop ro.build.id',
            'build_type': 'shell getprop ro.build.type',
        }
        
        for key, cmd in commands.items():
            result = self.adb.execute_command(['-s', serial] + cmd.split())
            if result['success'] and result['output']:
                device[key] = result['output'].strip()
        
        # Check lock status
        device['lock_status'] = self._check_lock_status(serial)
        
        # Check USB debugging
        device['usb_debugging'] = self._check_usb_debugging(serial)
        
        # Check root access
        device['rooted'] = self._check_root_access(serial)
        
        # Check storage
        device['storage'] = self._get_storage_info(serial)
        
        # Check battery
        device['battery'] = self._get_battery_info(serial)
        
        return device
    
    def _check_lock_status(self, serial):
        """Check if device is locked and what type of lock"""
        # Method 1: Check via dumpsys
        result = self.adb.execute_command(['-s', serial, 'shell', 'dumpsys', 'trust'])
        
        if result['success']:
            output = result['output']
            
            if 'TrustAgentService' in output:
                # Parse lock type
                if 'FLAG_KEYGUARD_SECURE' in output:
                    # Check pattern/PIN/password
                    pattern_match = re.search(r'LockPatternUtils\.Pattern', output)
                    pin_match = re.search(r'PIN|PASSWORD', output, re.IGNORECASE)
                    
                    if pattern_match:
                        return 'pattern'
                    elif pin_match:
                        return 'pin/password'
                    else:
                        return 'secure'
            
            if 'FLAG_KEYGUARD' in output and 'SECURE' not in output:
                return 'swipe'
        
        # Method 2: Try to list locksettings
        result = self.adb.execute_command(['-s', serial, 'shell', 'ls', '/data/system/'])
        
        if result['success'] and 'gesture.key' in result['output']:
            return 'pattern'
        elif result['success'] and 'password.key' in result['output']:
            return 'password'
        
        return 'unknown'
    
    def _check_usb_debugging(self, serial):
        """Check if USB debugging is enabled"""
        result = self.adb.execute_command(['-s', serial, 'shell', 'settings', 'get', 'global', 'adb_enabled'])
        
        if result['success']:
            return result['output'].strip() == '1'
        
        return False
    
    def _check_root_access(self, serial):
        """Check if device has root access"""
        result = self.adb.execute_command(['-s', serial, 'shell', 'su', '-c', 'echo root_test'])
        
        if result['success'] and 'root_test' in result['output']:
            return True
        
        return False
    
    def _get_storage_info(self, serial):
        """Get storage information"""
        result = self.adb.execute_command(['-s', serial, 'shell', 'df', '/data'])
        
        if result['success']:
            lines = result['output'].strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    return {
                        'total': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'usage_percent': parts[4]
                    }
        
        return {}
    
    def _get_battery_info(self, serial):
        """Get battery information"""
        result = self.adb.execute_command(['-s', serial, 'shell', 'dumpsys', 'battery'])
        
        battery_info = {}
        
        if result['success']:
            lines = result['output'].strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    battery_info[key] = value
        
        return battery_info
    
    def generate_report(self):
        """Generate detailed device report"""
        if not self.scan_results:
            print("No devices scanned. Run scan_devices() first.")
            return None
        
        report = {
            'scan_time': datetime.now().isoformat(),
            'total_devices': len(self.scan_results),
            'devices': self.scan_results,
            'summary': self._generate_summary()
        }
        
        return report
    
    def _generate_summary(self):
        """Generate summary of scan results"""
        summary = {
            'locked_devices': 0,
            'unlocked_devices': 0,
            'rooted_devices': 0,
            'debugging_enabled': 0,
            'android_versions': {},
            'manufacturers': {}
        }
        
        for device in self.scan_results:
            # Count lock status
            if device.get('lock_status') not in ['swipe', 'unknown']:
                summary['locked_devices'] += 1
            else:
                summary['unlocked_devices'] += 1
            
            # Count rooted
            if device.get('rooted'):
                summary['rooted_devices'] += 1
            
            # Count USB debugging
            if device.get('usb_debugging'):
                summary['debugging_enabled'] += 1
            
            # Android versions
            version = device.get('android_version', 'Unknown')
            summary['android_versions'][version] = summary['android_versions'].get(version, 0) + 1
            
            # Manufacturers
            manufacturer = device.get('manufacturer', 'Unknown')
            summary['manufacturers'][manufacturer] = summary['manufacturers'].get(manufacturer, 0) + 1
        
        return summary
    
    def print_report(self):
        """Print formatted device report"""
        report = self.generate_report()
        
        if not report:
            return
        
        print("\n" + "=" * 60)
        print("DEVICE SCAN REPORT")
        print("=" * 60)
        print(f"Scan Time: {report['scan_time']}")
        print(f"Total Devices: {report['total_devices']}")
        print("-" * 60)
        
        summary = report['summary']
        print(f"Locked Devices: {summary['locked_devices']}")
        print(f"Unlocked Devices: {summary['unlocked_devices']}")
        print(f"Rooted Devices: {summary['rooted_devices']}")
        print(f"USB Debugging Enabled: {summary['debugging_enabled']}")
        
        print("\nAndroid Version Distribution:")
        for version, count in summary['android_versions'].items():
            print(f"  {version}: {count} device(s)")
        
        print("\nManufacturer Distribution:")
        for manufacturer, count in summary['manufacturers'].items():
            print(f"  {manufacturer}: {count} device(s)")
        
        print("\n" + "=" * 60)
        
        # Detailed device info
        for i, device in enumerate(report['devices'], 1):
            print(f"\n📱 Device {i}:")
            print(f"  Serial: {device.get('serial', 'N/A')}")
            print(f"  Model: {device.get('model', 'N/A')}")
            print(f"  Android: {device.get('android_version', 'N/A')}")
            print(f"  Lock Status: {device.get('lock_status', 'N/A')}")
            print(f"  Rooted: {'Yes' if device.get('rooted') else 'No'}")
            print(f"  USB Debugging: {'Enabled' if device.get('usb_debugging') else 'Disabled'}")