"""
Security Checker - Analyze device security and vulnerabilities
"""

import re
import json
from datetime import datetime
from adb_manager import ADBManager

class SecurityChecker:
    def __init__(self):
        self.adb = ADBManager()
        self.results = {}
    
    def run_full_security_scan(self):
        """Run comprehensive security scan"""
        print("\n🔒 SECURITY AUDIT")
        print("=" * 60)
        
        if not self.adb.check_adb_installed():
            print("ADB not available")
            return {}
        
        print("Running security checks...")
        
        # Run all checks
        checks = [
            ("System Information", self.check_system_info),
            ("Lock Security", self.check_lock_security),
            ("Bootloader Status", self.check_bootloader),
            ("ADB Status", self.check_adb_status),
            ("USB Debugging", self.check_usb_debugging),
            ("Developer Options", self.check_developer_options),
            ("Root Status", self.check_root_status),
            ("FRP Status", self.check_frp_status),
            ("Encryption Status", self.check_encryption),
            ("Security Patches", self.check_security_patches),
            ("Installed Apps", self.check_installed_apps),
            ("Network Security", self.check_network_security),
        ]
        
        for check_name, check_func in checks:
            print(f"\n✓ {check_name}...")
            result = check_func()
            self.results[check_name] = result
        
        # Generate report
        report = self.generate_security_report()
        
        print("\n" + "=" * 60)
        print("SECURITY SCAN COMPLETE")
        print("=" * 60)
        
        return report
    
    def check_system_info(self):
        """Check basic system information"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'device_info': self.adb.get_device_info(),
        }
        
        # Get Android version
        result = self.adb.execute_command(['shell', 'getprop', 'ro.build.version.release'])
        if result['success']:
            info['android_version'] = result['output'].strip()
        
        # Get security patch
        result = self.adb.execute_command(['shell', 'getprop', 'ro.build.version.security_patch'])
        if result['success']:
            info['security_patch'] = result['output'].strip()
        
        # Get kernel version
        result = self.adb.execute_command(['shell', 'uname', '-r'])
        if result['success']:
            info['kernel_version'] = result['output'].strip()
        
        return info
    
    def check_lock_security(self):
        """Check lock screen security"""
        security = {
            'lock_type': 'unknown',
            'strength': 'unknown',
            'vulnerabilities': []
        }
        
        # Check lock files
        result = self.adb.execute_command(['shell', 'ls', '/data/system/'])
        
        if result['success']:
            output = result['output']
            
            if 'gesture.key' in output:
                security['lock_type'] = 'pattern'
                security['strength'] = 'medium'
            elif 'password.key' in output:
                security['lock_type'] = 'password'
                # Check file size for password strength hint
                result2 = self.adb.execute_command(['shell', 'ls', '-la', '/data/system/password.key'])
                if result2['success']:
                    lines = result2['output'].split('\n')
                    for line in lines:
                        if 'password.key' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                size = parts[4]
                                security['password_hash_size'] = size
                                if int(size) > 100:
                                    security['strength'] = 'strong'
                                else:
                                    security['strength'] = 'weak'
            
            # Check for biometrics
            result2 = self.adb.execute_command(['shell', 'dumpsys', 'fingerprint'])
            if result2['success'] and 'FingerprintService' in result2['output']:
                security['has_biometric'] = True
                security['lock_type'] += '+fingerprint'
                security['strength'] = 'strong'
        
        # Check lock timeout
        result = self.adb.execute_command(['shell', 'settings', 'get', 'secure', 'lock_screen_lock_after_timeout'])
        if result['success'] and result['output']:
            timeout = result['output'].strip()
            if timeout == '0':
                security['vulnerabilities'].append('No lock timeout - insecure')
        
        return security
    
    def check_bootloader(self):
        """Check bootloader status"""
        bootloader = {
            'status': 'unknown',
            'security_level': 'unknown'
        }
        
        # Check verified boot state
        result = self.adb.execute_command(['shell', 'getprop', 'ro.boot.verifiedbootstate'])
        if result['success']:
            state = result['output'].strip().lower()
            bootloader['verified_boot_state'] = state
            
            if state == 'green':
                bootloader['status'] = 'locked'
                bootloader['security_level'] = 'high'
            elif state == 'orange':
                bootloader['status'] = 'unlocked'
                bootloader['security_level'] = 'medium'
            elif state == 'yellow':
                bootloader['status'] = 'unlocked_with_warning'
                bootloader['security_level'] = 'low'
        
        # Check via fastboot if possible
        try:
            import subprocess
            fastboot_result = subprocess.run(['fastboot', 'oem', 'device-info'],
                                           capture_output=True, text=True, timeout=5)
            
            if 'unlocked: yes' in fastboot_result.stdout.lower():
                bootloader['status'] = 'unlocked'
                bootloader['security_level'] = 'low'
            elif 'unlocked: no' in fastboot_result.stdout.lower():
                bootloader['status'] = 'locked'
                bootloader['security_level'] = 'high'
        except:
            pass
        
        return bootloader
    
    def check_adb_status(self):
        """Check ADB security status"""
        adb_status = {
            'enabled': False,
            'authorized': False,
            'security_risks': []
        }
        
        # Check if ADB is enabled
        result = self.adb.execute_command(['shell', 'settings', 'get', 'global', 'adb_enabled'])
        if result['success'] and result['output'].strip() == '1':
            adb_status['enabled'] = True
            adb_status['security_risks'].append('ADB enabled - security risk')
        
        # Check ADB authorization
        result = self.adb.execute_command(['devices'])
        if result['success']:
            lines = result['output'].strip().split('\n')
            for line in lines:
                if '\tdevice' in line:
                    adb_status['authorized'] = True
                elif '\tunauthorized' in line:
                    adb_status['authorized'] = False
                    adb_status['security_risks'].append('ADB unauthorized - connection possible')
        
        return adb_status
    
    def check_usb_debugging(self):
        """Check USB debugging status"""
        usb = {
            'enabled': False,
            'risks': []
        }
        
        # Same as ADB enabled check
        result = self.adb.execute_command(['shell', 'settings', 'get', 'global', 'adb_enabled'])
        if result['success'] and result['output'].strip() == '1':
            usb['enabled'] = True
            usb['risks'].append('USB debugging enabled - allows data access when connected to PC')
        
        return usb
    
    def check_developer_options(self):
        """Check developer options status"""
        dev_options = {
            'enabled': False,
            'risks': []
        }
        
        # Check if developer options are enabled
        result = self.adb.execute_command(['shell', 'settings', 'get', 'global', 'development_settings_enabled'])
        if result['success'] and result['output'].strip() == '1':
            dev_options['enabled'] = True
        
        # Check individual developer options
        checks = [
            ('stay_awake', 'Stay awake when charging'),
            ('usb_debugging', 'USB debugging'),
            ('verify_apps_over_usb', 'Verify apps over USB'),
            ('wireless_debugging', 'Wireless debugging'),
            ('demo_mode', 'Demo mode'),
        ]
        
        for setting, description in checks:
            result = self.adb.execute_command(['shell', 'settings', 'get', 'global', f'development_{setting}'])
            if result['success'] and result['output'].strip() == '1':
                dev_options['risks'].append(f'{description} enabled')
        
        return dev_options
    
    def check_root_status(self):
        """Check if device is rooted"""
        root = {
            'rooted': False,
            'method': 'unknown',
            'risks': []
        }
        
        # Check for su binary
        result = self.adb.execute_command(['shell', 'which', 'su'])
        if result['success'] and '/su' in result['output']:
            root['rooted'] = True
            root['method'] = 'su binary present'
            root['risks'].append('Device rooted - full system access possible')
        
        # Check for Magisk
        result = self.adb.execute_command(['shell', 'magisk', '-v'], wait_for_device=False)
        if result['success']:
            root['rooted'] = True
            root['method'] = 'Magisk'
        
        # Check for SuperSU
        result = self.adb.execute_command(['shell', 'ls', '/system/app/SuperSU/'])
        if result['success'] and 'No such file' not in result['error']:
            root['rooted'] = True
            root['method'] = 'SuperSU'
        
        return root
    
    def check_frp_status(self):
        """Check Factory Reset Protection status"""
        frp = {
            'enabled': False,
            'protection_level': 'unknown'
        }
        
        # Check Google account presence
        result = self.adb.execute_command(['shell', 'cmd', 'account', 'list'])
        if result['success'] and 'com.google' in result['output']:
            frp['enabled'] = True
            frp['protection_level'] = 'Google FRP'
        
        # Check for other manufacturer accounts
        manufacturers = ['samsung', 'xiaomi', 'huawei', 'oppo', 'vivo']
        for manufacturer in manufacturers:
            if manufacturer in result['output'].lower():
                frp['enabled'] = True
                frp['protection_level'] = f'{manufacturer.capitalize()} FRP'
        
        return frp
    
    def check_encryption(self):
        """Check device encryption status"""
        encryption = {
            'encrypted': False,
            'type': 'unknown',
            'strength': 'unknown'
        }
        
        # Check encryption status
        result = self.adb.execute_command(['shell', 'getprop', 'ro.crypto.state'])
        if result['success']:
            state = result['output'].strip()
            encryption['encrypted'] = state == 'encrypted'
        
        # Check crypto type
        result = self.adb.execute_command(['shell', 'getprop', 'ro.crypto.type'])
        if result['success']:
            crypto_type = result['output'].strip()
            encryption['type'] = crypto_type
            
            if crypto_type == 'file':
                encryption['strength'] = 'medium'
            elif crypto_type == 'block':
                encryption['strength'] = 'high'
            elif 'metadata' in crypto_type:
                encryption['strength'] = 'high'
        
        # Check for forced encryption
        result = self.adb.execute_command(['shell', 'getprop', 'ro.forceencrypt'])
        if result['success'] and result['output']:
            encryption['forced_encryption'] = True
        
        return encryption
    
    def check_security_patches(self):
        """Check security patch level"""
        patches = {
            'current_patch': 'unknown',
            'days_behind': 0,
            'vulnerable': False
        }
        
        # Get security patch date
        result = self.adb.execute_command(['shell', 'getprop', 'ro.build.version.security_patch'])
        if result['success'] and result['output']:
            patch_date = result['output'].strip()
            patches['current_patch'] = patch_date
            
            try:
                # Parse date and calculate days behind
                from datetime import datetime
                patch_dt = datetime.strptime(patch_date, '%Y-%m-%d')
                current_dt = datetime.now()
                
                days_behind = (current_dt - patch_dt).days
                patches['days_behind'] = days_behind
                
                if days_behind > 90:  # More than 3 months old
                    patches['vulnerable'] = True
                    patches['risk'] = f'Security patches {days_behind} days old'
            except:
                pass
        
        return patches
    
    def check_installed_apps(self):
        """Check installed apps for security risks"""
        apps = {
            'total_apps': 0,
            'system_apps': 0,
            'user_apps': 0,
            'unknown_sources': False,
            'risky_apps': []
        }
        
        # Get all packages
        result = self.adb.execute_command(['shell', 'pm', 'list', 'packages'])
        if result['success']:
            packages = [pkg.replace('package:', '').strip() 
                       for pkg in result['output'].split('\n') if pkg]
            apps['total_apps'] = len(packages)
        
        # Get user apps
        result = self.adb.execute_command(['shell', 'pm', 'list', 'packages', '-3'])
        if result['success']:
            user_packages = [pkg.replace('package:', '').strip() 
                           for pkg in result['output'].split('\n') if pkg]
            apps['user_apps'] = len(user_packages)
            apps['system_apps'] = apps['total_apps'] - apps['user_apps']
        
        # Check for unknown sources
        result = self.adb.execute_command(['shell', 'settings', 'get', 'secure', 'install_non_market_apps'])
        if result['success'] and result['output'].strip() == '1':
            apps['unknown_sources'] = True
            apps['risky_apps'].append('Unknown sources enabled - can install apps outside Play Store')
        
        # Check for risky permissions (simplified)
        risky_permissions = [
            'android.permission.READ_SMS',
            'android.permission.READ_CONTACTS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.RECORD_AUDIO',
            'android.permission.CAMERA',
        ]
        
        return apps
    
    def check_network_security(self):
        """Check network security settings"""
        network = {
            'wifi_security': {},
            'bluetooth': {},
            'vulnerabilities': []
        }
        
        # Check WiFi security
        result = self.adb.execute_command(['shell', 'dumpsys', 'wifi'])
        if result['success']:
            # Parse for saved networks
            if 'SSID:' in result['output']:
                network['wifi_security']['saved_networks'] = 'Present'
        
        # Check Bluetooth visibility
        result = self.adb.execute_command(['shell', 'settings', 'get', 'global', 'bluetooth_discoverability'])
        if result['success'] and result['output'].strip() == '1':
            network['bluetooth']['discoverable'] = True
            network['vulnerabilities'].append('Bluetooth discoverable - visible to nearby devices')
        
        return network
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'summary': {
                'total_checks': len(self.results),
                'security_score': 0,
                'high_risks': 0,
                'medium_risks': 0,
                'low_risks': 0,
            },
            'detailed_results': self.results,
            'recommendations': []
        }
        
        # Calculate security score
        score = 100
        risks = []
        
        # Analyze results
        for check_name, result in self.results.items():
            if isinstance(result, dict):
                # Check for risks
                if 'vulnerabilities' in result and result['vulnerabilities']:
                    for vuln in result['vulnerabilities']:
                        risks.append(f"{check_name}: {vuln}")
                        score -= 5
                
                if 'risks' in result and result['risks']:
                    for risk in result['risks']:
                        risks.append(f"{check_name}: {risk}")
                        score -= 5
                
                if 'security_risks' in result and result['security_risks']:
                    for risk in result['security_risks']:
                        risks.append(f"{check_name}: {risk}")
                        score -= 5
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        report['summary']['security_score'] = score
        report['summary']['risks_found'] = risks
        report['summary']['total_risks'] = len(risks)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(risks)
        
        return report
    
    def _generate_recommendations(self, risks):
        """Generate security recommendations based on risks"""
        recommendations = []
        
        risk_map = {
            'ADB enabled': 'Disable USB debugging in Developer Options',
            'USB debugging enabled': 'Disable USB debugging when not needed',
            'No lock timeout': 'Set screen lock timeout in Security settings',
            'Device rooted': 'Consider unrooting for better security',
            'Security patches old': 'Update to latest security patch',
            'Unknown sources enabled': 'Disable "Install unknown apps" in Security',
            'Bluetooth discoverable': 'Turn off Bluetooth visibility',
            'lock timeout - insecure': 'Set automatic lock in Security settings',
        }
        
        for risk in risks:
            for key, recommendation in risk_map.items():
                if key.lower() in risk.lower():
                    if recommendation not in recommendations:
                        recommendations.append(recommendation)
        
        # Add general recommendations
        general_recs = [
            'Use strong password/PIN (6+ digits/characters)',
            'Enable Find My Device',
            'Use biometric authentication if available',
            'Keep Android updated',
            'Install apps only from Google Play Store',
            'Review app permissions regularly',
            'Use VPN on public WiFi',
            'Enable encryption if not already enabled',
        ]
        
        recommendations.extend(general_recs)
        
        return list(set(recommendations))  # Remove duplicates
    
    def print_report(self):
        """Print formatted security report"""
        report = self.generate_security_report()
        
        print("\n" + "=" * 60)
        print("SECURITY REPORT")
        print("=" * 60)
        
        print(f"\nScan Date: {report['scan_date']}")
        print(f"Security Score: {report['summary']['security_score']}/100")
        print(f"Total Risks Found: {report['summary']['total_risks']}")
        
        if report['summary']['risks_found']:
            print("\n⚠️  IDENTIFIED RISKS:")
            for i, risk in enumerate(report['summary']['risks_found'], 1):
                print(f"{i}. {risk}")
        
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'][:10], 1):  # Top 10
                print(f"{i}. {rec}")
        
        # Security rating
        score = report['summary']['security_score']
        print(f"\n🔒 SECURITY RATING: ", end='')
        
        if score >= 80:
            print("GOOD 👍")
        elif score >= 60:
            print("FAIR ⚠️")
        elif score >= 40:
            print("POOR 👎")
        else:
            print("CRITICAL 🚨")
        
        print("\n" + "=" * 60)