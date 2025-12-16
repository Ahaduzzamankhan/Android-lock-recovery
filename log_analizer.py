"""
Log Analyzer - Analyze Android logs for security issues and debugging
"""

import re
import time
from datetime import datetime
from collections import defaultdict
from adb_manager import ADBManager

class LogAnalyzer:
    def __init__(self):
        self.adb = ADBManager()
        self.logs = []
        self.patterns = {
            'security': [
                (r'(FAILED|invalid|wrong|incorrect).*(password|pin|pattern)', 'Failed authentication attempts'),
                (r'Biometric.*(FAILED|REJECTED)', 'Failed biometric authentication'),
                (r'FRP.*(lock|protection|verify)', 'FRP related events'),
                (r'(root|su|magisk|superuser)', 'Root access attempts'),
                (r'(adb|debugging).*(enabled|connected)', 'ADB activities'),
                (r'(permission denied|security exception)', 'Permission violations'),
                (r'(lock screen|keyguard).*(unlock|bypass)', 'Lock screen activities'),
                (r'(factory.*reset|wipe.*data)', 'Factory reset attempts'),
                (r'(bootloader|fastboot).*(unlock|lock)', 'Bootloader activities'),
            ],
            'authentication': [
                (r'(authenticat|auth).*(success|failed)', 'Authentication results'),
                (r'(password|pin|pattern).*(set|change|remove)', 'Credential changes'),
                (r'TrustAgentService', 'Smart Lock activities'),
                (r'FaceService|FingerprintService', 'Biometric services'),
            ],
            'errors': [
                (r'ERROR|CRITICAL|FATAL', 'Critical errors'),
                (r'Exception|RuntimeException', 'Java exceptions'),
                (r'ANR.*(Application Not Responding)', 'App not responding'),
                (r'boot.*(fail|error)', 'Boot failures'),
            ],
            'network': [
                (r'(wifi|bluetooth).*(connect|disconnect)', 'Network connections'),
                (r'(ip address|mac address)', 'Network addressing'),
                (r'(vpn|proxy).*(connect|disconnect)', 'VPN/Proxy activities'),
            ],
        }
    
    def capture_logs(self, duration=30, log_type='main'):
        """Capture Android logs for specified duration"""
        print(f"\n📝 CAPTURING LOGS ({duration} seconds)")
        print("=" * 60)
        
        if not self.adb.check_adb_installed():
            print("ADB not available")
            return []
        
        log_commands = {
            'main': ['logcat', '-v', 'time'],
            'events': ['logcat', '-b', 'events', '-v', 'time'],
            'system': ['logcat', '-b', 'system', '-v', 'time'],
            'radio': ['logcat', '-b', 'radio', '-v', 'time'],
            'kernel': ['dmesg'],
        }
        
        if log_type not in log_commands:
            print(f"Unknown log type: {log_type}")
            return []
        
        cmd = log_commands[log_type]
        print(f"Log type: {log_type}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Duration: {duration} seconds")
        print("\nCapturing... (Ctrl+C to stop early)")
        
        logs = []
        start_time = time.time()
        
        try:
            # Start logcat process
            import subprocess
            process = subprocess.Popen(
                ['adb'] + cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read logs for specified duration
            while time.time() - start_time < duration:
                line = process.stdout.readline()
                if line:
                    logs.append(line.strip())
                    print(f"Lines captured: {len(logs)}", end='\r')
            
            # Terminate process
            process.terminate()
            
        except KeyboardInterrupt:
            print("\n\nCapture interrupted by user")
        except Exception as e:
            print(f"\nError capturing logs: {e}")
        
        print(f"\n✓ Captured {len(logs)} log entries")
        self.logs = logs
        return logs
    
    def analyze_logs(self, logs=None):
        """Analyze captured logs for security issues"""
        if logs is None:
            logs = self.logs
        
        if not logs:
            print("No logs to analyze")
            return {}
        
        print("\n🔍 ANALYZING LOGS")
        print("=" * 60)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_entries': len(logs),
            'categories': defaultdict(list),
            'timeline': [],
            'security_issues': [],
            'statistics': defaultdict(int),
        }
        
        # Analyze each log entry
        for i, entry in enumerate(logs):
            if not entry.strip():
                continue
            
            # Extract timestamp if present
            timestamp = self._extract_timestamp(entry)
            if timestamp:
                analysis['timeline'].append({
                    'time': timestamp,
                    'entry': entry[:100] + '...' if len(entry) > 100 else entry
                })
            
            # Check against patterns
            for category, patterns in self.patterns.items():
                for pattern, description in patterns:
                    if re.search(pattern, entry, re.IGNORECASE):
                        analysis['categories'][category].append({
                            'entry': entry,
                            'pattern': pattern,
                            'description': description,
                            'line': i + 1
                        })
                        
                        if category == 'security':
                            analysis['security_issues'].append({
                                'issue': description,
                                'entry': entry[:200],
                                'line': i + 1
                            })
                        
                        analysis['statistics'][category] += 1
                        break  # Only count first match per category
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def search_logs(self, search_terms, logs=None):
        """Search logs for specific terms"""
        if logs is None:
            logs = self.logs
        
        if not logs:
            print("No logs to search")
            return []
        
        print(f"\n🔎 SEARCHING LOGS FOR: {search_terms}")
        
        results = []
        search_terms = search_terms.lower().split()
        
        for i, entry in enumerate(logs):
            entry_lower = entry.lower()
            
            # Check if all search terms are present
            if all(term in entry_lower for term in search_terms):
                results.append({
                    'line': i + 1,
                    'entry': entry,
                    'context': self._get_context(logs, i)
                })
        
        print(f"Found {len(results)} matches")
        return results
    
    def _extract_timestamp(self, log_entry):
        """Extract timestamp from log entry"""
        # Common log formats
        timestamp_patterns = [
            r'(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})',  # 01-01 12:00:00.000
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',   # 2024-01-01 12:00:00
            r'(\d{2}/\d{2} \d{2}:\d{2}:\d{2})',         # 01/01 12:00:00
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_entry)
            if match:
                return match.group(1)
        
        return None
    
    def _get_context(self, logs, index, context_lines=2):
        """Get context around a log entry"""
        start = max(0, index - context_lines)
        end = min(len(logs), index + context_lines + 1)
        
        context = []
        for i in range(start, end):
            prefix = '> ' if i == index else '  '
            context.append(f"{prefix}{logs[i]}")
        
        return '\n'.join(context)
    
    def _generate_summary(self, analysis):
        """Generate analysis summary"""
        summary = {
            'total_matches': sum(analysis['statistics'].values()),
            'by_category': dict(analysis['statistics']),
            'security_risk_level': 'low',
            'notable_findings': []
        }
        
        # Determine security risk level
        security_count = analysis['statistics'].get('security', 0)
        if security_count > 20:
            summary['security_risk_level'] = 'high'
        elif security_count > 5:
            summary['security_risk_level'] = 'medium'
        
        # Extract notable findings
        notable_patterns = [
            'FAILED.*password',
            'root.*access',
            'factory.*reset',
            'bootloader.*unlock',
            'FRP.*lock',
        ]
        
        for category_entries in analysis['categories'].values():
            for entry_info in category_entries:
                entry = entry_info['entry']
                for pattern in notable_patterns:
                    if re.search(pattern, entry, re.IGNORECASE):
                        summary['notable_findings'].append({
                            'pattern': pattern,
                            'entry': entry[:150],
                            'line': entry_info['line']
                        })
                        break
        
        return summary
    
    def save_logs(self, filename=None, logs=None):
        """Save logs to file"""
        if logs is None:
            logs = self.logs
        
        if not logs:
            print("No logs to save")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"android_logs_{timestamp}.txt"
        
        filepath = filename if '/' in filename else f"./{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Android Logs - {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, entry in enumerate(logs, 1):
                    f.write(f"{i:6d}: {entry}\n")
            
            print(f"✓ Logs saved to: {filepath}")
            print(f"  Total entries: {len(logs)}")
            
            return filepath
            
        except Exception as e:
            print(f"Error saving logs: {e}")
            return None
    
    def real_time_monitor(self, duration=300):
        """Real-time log monitoring"""
        print("\n👁️  REAL-TIME LOG MONITOR")
        print("=" * 60)
        print(f"Monitoring for {duration} seconds")
        print("Press Ctrl+C to stop\n")
        
        import subprocess
        import signal
        import sys
        
        def signal_handler(sig, frame):
            print("\n\nMonitoring stopped by user")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keywords to highlight
        keywords = {
            'ERROR': 'RED',
            'FAILED': 'RED',
            'SUCCESS': 'GREEN',
            'authenticat': 'YELLOW',
            'password': 'CYAN',
            'root': 'MAGENTA',
            'FRP': 'BLUE',
        }
        
        try:
            process = subprocess.Popen(
                ['adb', 'logcat', '-v', 'time'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            start_time = time.time()
            line_count = 0
            
            while time.time() - start_time < duration:
                line = process.stdout.readline()
                if line:
                    line_count += 1
                    
                    # Check for keywords
                    colored_line = line
                    for keyword, color in keywords.items():
                        if keyword.lower() in line.lower():
                            # Simple color coding (ANSI)
                            color_codes = {
                                'RED': '\033[91m',
                                'GREEN': '\033[92m',
                                'YELLOW': '\033[93m',
                                'BLUE': '\033[94m',
                                'MAGENTA': '\033[95m',
                                'CYAN': '\033[96m',
                            }
                            
                            if color in color_codes:
                                colored_line = colored_line.replace(
                                    keyword,
                                    f"{color_codes[color]}{keyword}\033[0m"
                                )
                    
                    print(colored_line, end='')
            
            process.terminate()
            print(f"\n\n✓ Monitoring complete")
            print(f"Total lines processed: {line_count}")
            
        except Exception as e:
            print(f"\nError during monitoring: {e}")
    
    def forensic_analysis(self, log_file):
        """Forensic analysis of log files"""
        print("\n🔬 FORENSIC LOG ANALYSIS")
        print("=" * 60)
        
        if not os.path.exists(log_file):
            print(f"Log file not found: {log_file}")
            return None
        
        print(f"Analyzing: {log_file}")
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                logs = f.readlines()
            
            print(f"Total lines: {len(logs)}")
            
            # Look for forensic evidence
            evidence = {
                'timeline': self._build_timeline(logs),
                'user_activities': self._extract_user_activities(logs),
                'security_events': self._extract_security_events(logs),
                'device_state_changes': self._extract_state_changes(logs),
            }
            
            # Generate forensic report
            report = self._generate_forensic_report(evidence)
            
            print("\n✓ Forensic analysis complete")
            return report
            
        except Exception as e:
            print(f"Error in forensic analysis: {e}")
            return None
    
    def _build_timeline(self, logs):
        """Build timeline of events"""
        timeline = []
        
        for line in logs:
            timestamp = self._extract_timestamp(line)
            if timestamp and any(keyword in line for keyword in ['boot', 'shutdown', 'crash', 'ANR']):
                timeline.append({
                    'timestamp': timestamp,
                    'event': line[:100]
                })
        
        return timeline
    
    def _extract_user_activities(self, logs):
        """Extract user activity patterns"""
        activities = []
        
        patterns = [
            (r'screen_(on|off)', 'Screen state'),
            (r'user_(present|absent)', 'User presence'),
            (r'keyguard_(shown|hidden)', 'Lock screen'),
            (r'app_launch', 'App launches'),
            (r'notification', 'Notifications'),
        ]
        
        for line in logs:
            for pattern, description in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    activities.append({
                        'activity': description,
                        'line': line[:150]
                    })
                    break
        
        return activities
    
    def _extract_security_events(self, logs):
        """Extract security-related events"""
        security_events = []
        
        security_patterns = [
            (r'authentication.*(success|fail)', 'Authentication'),
            (r'password.*(set|change)', 'Password change'),
            (r'factory_reset', 'Factory reset'),
            (r'bootloader.*(unlock|lock)', 'Bootloader'),
            (r'encryption.*(start|complete)', 'Encryption'),
        ]
        
        for line in logs:
            for pattern, event_type in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    security_events.append({
                        'type': event_type,
                        'details': line[:200]
                    })
                    break
        
        return security_events
    
    def _extract_state_changes(self, logs):
        """Extract device state changes"""
        states = []
        
        state_patterns = [
            (r'battery.*(level|charging)', 'Battery'),
            (r'wifi.*(enable|disable|connect)', 'WiFi'),
            (r'bluetooth.*(on|off)', 'Bluetooth'),
            (r'airplane.*mode', 'Airplane mode'),
            (r'roaming.*(on|off)', 'Roaming'),
        ]
        
        for line in logs:
            for pattern, state_type in state_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    states.append({
                        'state': state_type,
                        'change': line[:150]
                    })
                    break
        
        return states
    
    def _generate_forensic_report(self, evidence):
        """Generate forensic report"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'total_timeline_events': len(evidence['timeline']),
                'total_user_activities': len(evidence['user_activities']),
                'total_security_events': len(evidence['security_events']),
                'total_state_changes': len(evidence['device_state_changes']),
            },
            'evidence': evidence,
            'findings': []
        }
        
        # Generate findings
        if evidence['security_events']:
            report['findings'].append("Security events detected in logs")
        
        if len(evidence['timeline']) > 100:
            report['findings'].append("High number of system events")
        
        # Look for suspicious patterns
        suspicious = any(
            'factory_reset' in event['details'].lower() 
            for event in evidence['security_events']
        )
        
        if suspicious:
            report['findings'].append("Factory reset activity detected")
        
        return report