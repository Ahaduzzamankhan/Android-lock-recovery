"""
Data Extractor - Extract data from locked Android devices
Uses various methods to recover data before reset
"""

import os
import sqlite3
import json
import zipfile
from datetime import datetime
from pathlib import Path
from adb_manager import ADBManager

class DataExtractor:
    def __init__(self):
        self.adb = ADBManager()
        self.extraction_dir = Path.home() / "AndroidDataExtraction"
        self.extraction_dir.mkdir(exist_ok=True)
    
    def extract_data(self, data_type='all'):
        """Extract specific or all data types"""
        print("\n🔍 DATA EXTRACTION")
        print("=" * 60)
        
        if not self.adb.check_adb_installed():
            return False
        
        # Check if device is accessible
        print("Checking device accessibility...")
        result = self.adb.execute_command(['shell', 'echo', 'test'])
        
        if not result['success']:
            print("Device not accessible. May be locked.")
            
            # Try alternative methods for locked devices
            if input("\nTry locked device extraction? (y/n): ").lower() == 'y':
                return self._extract_from_locked_device()
            else:
                return False
        
        extraction_methods = {
            'all': self.extract_all_data,
            'contacts': self.extract_contacts,
            'messages': self.extract_messages,
            'photos': self.extract_photos,
            'whatsapp': self.extract_whatsapp,
            'call_logs': self.extract_call_logs,
            'documents': self.extract_documents,
            'app_data': self.extract_app_data,
        }
        
        if data_type in extraction_methods:
            return extraction_methods[data_type]()
        else:
            print(f"Unknown data type: {data_type}")
            return False
    
    def extract_all_data(self):
        """Extract all possible data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_path = self.extraction_dir / f"full_extraction_{timestamp}"
        extraction_path.mkdir(exist_ok=True)
        
        print(f"\n📦 FULL DATA EXTRACTION")
        print(f"Saving to: {extraction_path}")
        
        extraction_results = {
            'timestamp': timestamp,
            'extraction_path': str(extraction_path),
            'results': {}
        }
        
        # Extract different data types
        data_types = [
            ('Contacts', self.extract_contacts, extraction_path),
            ('Messages', self.extract_messages, extraction_path),
            ('Photos', self.extract_photos, extraction_path),
            ('Call Logs', self.extract_call_logs, extraction_path),
            ('Documents', self.extract_documents, extraction_path),
            ('WhatsApp', self.extract_whatsapp, extraction_path),
        ]
        
        for name, extract_func, path in data_types:
            print(f"\nExtracting {name}...")
            try:
                result = extract_func(save_path=path)
                extraction_results['results'][name] = {
                    'status': 'success',
                    'data': result
                }
                print(f"  ✓ {name} extracted")
            except Exception as e:
                extraction_results['results'][name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"  ✗ {name} failed: {e}")
        
        # Save extraction report
        report_file = extraction_path / "extraction_report.json"
        with open(report_file, 'w') as f:
            json.dump(extraction_results, f, indent=2)
        
        print(f"\n✅ Full extraction completed!")
        print(f"Report: {report_file}")
        
        return extraction_path
    
    def extract_contacts(self, save_path=None):
        """Extract contacts from device"""
        if save_path is None:
            save_path = self.extraction_dir / "contacts"
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        print("Extracting contacts...")
        
        # Method 1: Via content provider (requires unlocked device)
        result = self.adb.execute_command([
            'shell', 'content', 'query',
            '--uri', 'content://com.android.contacts/data',
            '--projection', 'display_name:data1:data2:data3'
        ])
        
        contacts = []
        
        if result['success'] and result['output']:
            lines = result['output'].strip().split('\n')
            for line in lines:
                if 'Row:' in line:
                    # Parse contact data
                    parts = line.split(',')
                    contact = {}
                    for part in parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            contact[key.strip()] = value.strip()
                    
                    if contact:
                        contacts.append(contact)
        
        # Method 2: Try to pull contacts database
        if self.adb.is_device_rooted():
            print("  Trying database extraction (root)...")
            db_path = '/data/data/com.android.providers.contacts/databases/contacts2.db'
            local_db = save_path / "contacts.db"
            
            if self.adb.pull_file(db_path, str(local_db)):
                # Extract from SQLite
                contacts.extend(self._extract_contacts_from_db(local_db))
        
        # Save contacts
        if contacts:
            # Save as JSON
            json_file = save_path / "contacts.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            
            # Save as VCF
            vcf_file = save_path / "contacts.vcf"
            self._save_as_vcf(contacts, vcf_file)
            
            print(f"  ✓ Extracted {len(contacts)} contacts")
            return {
                'count': len(contacts),
                'json_file': str(json_file),
                'vcf_file': str(vcf_file)
            }
        else:
            print("  ✗ No contacts found")
            return {'count': 0}
    
    def extract_messages(self, save_path=None):
        """Extract SMS/MMS messages"""
        if save_path is None:
            save_path = self.extraction_dir / "messages"
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        print("Extracting messages...")
        
        messages = []
        
        # Try to extract SMS
        result = self.adb.execute_command([
            'shell', 'content', 'query',
            '--uri', 'content://sms',
            '--projection', '_id:address:date:body:type'
        ])
        
        if result['success'] and result['output']:
            lines = result['output'].strip().split('\n')
            for line in lines:
                if 'Row:' in line:
                    # Parse message
                    msg_data = self._parse_sms_line(line)
                    if msg_data:
                        messages.append(msg_data)
        
        # Try MMS
        result = self.adb.execute_command([
            'shell', 'content', 'query',
            '--uri', 'content://mms',
            '--projection', '_id:date:text'
        ])
        
        if result['success'] and result['output']:
            lines = result['output'].strip().split('\n')
            for line in lines:
                if 'Row:' in line:
                    msg_data = self._parse_mms_line(line)
                    if msg_data:
                        messages.append(msg_data)
        
        # Save messages
        if messages:
            # Sort by date
            messages.sort(key=lambda x: x.get('date', 0))
            
            # Save as JSON
            json_file = save_path / "messages.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            # Save as CSV
            csv_file = save_path / "messages.csv"
            self._save_as_csv(messages, csv_file)
            
            # Save as HTML for easy viewing
            html_file = save_path / "messages.html"
            self._save_as_html(messages, html_file)
            
            print(f"  ✓ Extracted {len(messages)} messages")
            return {
                'count': len(messages),
                'json_file': str(json_file),
                'csv_file': str(csv_file),
                'html_file': str(html_file)
            }
        else:
            print("  ✗ No messages found")
            return {'count': 0}
    
    def extract_photos(self, save_path=None):
        """Extract photos and videos"""
        if save_path is None:
            save_path = self.extraction_dir / "media"
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        print("Extracting photos and videos...")
        
        # Common media directories
        media_dirs = [
            '/sdcard/DCIM/Camera',
            '/sdcard/DCIM',
            '/sdcard/Pictures',
            '/sdcard/Download',
            '/sdcard/Movies',
            '/storage/emulated/0/DCIM',
        ]
        
        extracted_files = []
        
        for media_dir in media_dirs:
            print(f"  Checking {media_dir}...")
            
            # List media files
            result = self.adb.execute_command([
                'shell', 'find', media_dir,
                '-type', 'f',
                '-name', '*.jpg', '-o',
                '-name', '*.jpeg', '-o',
                '-name', '*.png', '-o',
                '-name', '*.gif', '-o',
                '-name', '*.mp4', '-o',
                '-name', '*.mov', '-o',
                '-name', '*.avi', '-o',
                '-name', '*.mkv'
            ])
            
            if result['success'] and result['output']:
                files = result['output'].strip().split('\n')
                
                for file_path in files:
                    if file_path.strip():
                        try:
                            # Create local path
                            rel_path = file_path.replace('/sdcard/', '').replace('/storage/emulated/0/', '')
                            local_path = save_path / rel_path
                            local_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Pull file
                            print(f"    Downloading: {rel_path[:50]}...")
                            if self.adb.pull_file(file_path, str(local_path)):
                                extracted_files.append({
                                    'original_path': file_path,
                                    'local_path': str(local_path),
                                    'size': os.path.getsize(local_path)
                                })
                        except Exception as e:
                            print(f"    Error downloading {file_path}: {e}")
        
        # Create thumbnail gallery
        if extracted_files:
            self._create_media_gallery(extracted_files, save_path)
            
            print(f"  ✓ Extracted {len(extracted_files)} media files")
            return {
                'count': len(extracted_files),
                'directory': str(save_path),
                'sample_files': extracted_files[:10]
            }
        else:
            print("  ✗ No media files found")
            return {'count': 0}
    
    def extract_whatsapp(self, save_path=None):
        """Extract WhatsApp data"""
        if save_path is None:
            save_path = self.extraction_dir / "whatsapp"
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        print("Extracting WhatsApp data...")
        
        whatsapp_paths = [
            '/sdcard/WhatsApp/Databases',
            '/sdcard/WhatsApp/Media',
            '/sdcard/WhatsApp/.Shared',
            '/data/data/com.whatsapp',
        ]
        
        extracted = []
        
        for wa_path in whatsapp_paths:
            local_path = save_path / wa_path.split('/')[-1]
            print(f"  Extracting {wa_path}...")
            
            if self.adb.pull_file(wa_path, str(local_path)):
                extracted.append({
                    'source': wa_path,
                    'local': str(local_path)
                })
        
        # Try to decrypt message databases if key is available
        if (save_path / "Databases").exists():
            print("  Attempting to decrypt WhatsApp databases...")
            decrypted = self._decrypt_whatsapp_db(save_path)
            if decrypted:
                extracted.append({'decrypted': decrypted})
        
        if extracted:
            print(f"  ✓ WhatsApp data extracted")
            return {'extracted_items': extracted}
        else:
            print("  ✗ No WhatsApp data found")
            return {'count': 0}
    
    def _extract_from_locked_device(self):
        """Try to extract data from locked device"""
        print("\n🔐 ATTEMPTING LOCKED DEVICE EXTRACTION")
        
        methods = [
            self._locked_adb_backup,
            self._locked_mtp_access,
            self._locked_recovery_mode,
            self._locked_emergency_call,
        ]
        
        for i, method in enumerate(methods, 1):
            print(f"\n[{i}/{len(methods)}] Trying locked extraction method...")
            result = method()
            if result:
                return result
        
        print("\n❌ Could not extract from locked device")
        return False
    
    def _locked_adb_backup(self):
        """Try ADB backup on locked device"""
        print("Method: ADB backup (may work on some devices)")
        
        print("  ADB backup sometimes works without unlock")
        print("  Try: adb backup -apk -shared -all -system")
        
        backup_file = self.extraction_dir / "locked_backup.ab"
        
        result = self.adb.execute_command([
            'backup', '-apk', '-shared', '-all',
            '-f', str(backup_file)
        ])
        
        if result['success']:
            print(f"  ✓ Backup created: {backup_file}")
            print("  Check device screen for approval")
            return str(backup_file)
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
            return False
    
    def create_extraction_report(self):
        """Create comprehensive extraction report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'device_info': self.adb.get_device_info() if self.adb.check_adb_installed() else {},
            'extractions': []
        }
        
        # Scan for previous extractions
        for item in self.extraction_dir.iterdir():
            if item.is_dir():
                report_file = item / "extraction_report.json"
                if report_file.exists():
                    with open(report_file, 'r') as f:
                        extraction_data = json.load(f)
                        report['extractions'].append(extraction_data)
        
        # Save master report
        master_report = self.extraction_dir / "master_report.json"
        with open(master_report, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Master report created: {master_report}")
        return master_report