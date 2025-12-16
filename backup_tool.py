"""
Backup Tool - Creates backups of device data before reset
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
from adb_manager import ADBManager

class BackupTool:
    def __init__(self):
        self.adb = ADBManager()
        self.backup_dir = Path.home() / "AndroidBackups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_full_backup(self):
        """Create a full backup of the device"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"full_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print(f"\n📦 Creating FULL backup: {backup_path}")
        print("This may take several minutes...")
        
        # Create backup directory structure
        (backup_path / "apps").mkdir(parents=True, exist_ok=True)
        (backup_path / "media").mkdir(parents=True, exist_ok=True)
        (backup_path / "data").mkdir(parents=True, exist_ok=True)
        
        backup_info = {
            'backup_type': 'full',
            'timestamp': datetime.now().isoformat(),
            'device_info': self.adb.get_device_info(),
            'sections': []
        }
        
        # Backup sections
        sections = [
            ('Contacts & Call Logs', self._backup_contacts),
            ('SMS Messages', self._backup_sms),
            ('Photos & Videos', self._backup_media),
            ('Documents', self._backup_documents),
            ('App Data', self._backup_app_data),
            ('System Settings', self._backup_settings),
        ]
        
        for section_name, backup_func in sections:
            print(f"\nBacking up {section_name}...")
            try:
                section_info = backup_func(backup_path)
                backup_info['sections'].append({
                    'name': section_name,
                    'status': 'success',
                    'info': section_info
                })
                print(f"  ✓ {section_name} backed up successfully")
            except Exception as e:
                backup_info['sections'].append({
                    'name': section_name,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"  ✗ Failed to backup {section_name}: {e}")
        
        # Save backup metadata
        with open(backup_path / "backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        # Compress backup
        print("\nCompressing backup...")
        self._compress_backup(backup_path)
        
        print(f"\n✅ Full backup completed!")
        print(f"Location: {backup_path}.zip")
        print(f"Size: {self._get_folder_size(backup_path)}")
        
        return backup_path
    
    def create_selective_backup(self):
        """Create selective backup of chosen data types"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"selective_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print("\n📋 SELECTIVE BACKUP")
        print("=" * 50)
        print("Choose what to backup:")
        print("1. Contacts and Call Logs")
        print("2. SMS/MMS Messages")
        print("3. Photos and Videos")
        print("4. Music and Audio")
        print("5. Documents and Downloads")
        print("6. WhatsApp Data")
        print("7. App Data (non-system apps)")
        print("8. System Settings")
        print("9. All of the above")
        
        choices = input("\nEnter choices (comma-separated, e.g., 1,3,5): ").strip()
        
        if not choices:
            print("No selections made. Cancelling backup.")
            return
        
        selected = [c.strip() for c in choices.split(',')]
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_info = {
            'backup_type': 'selective',
            'timestamp': datetime.now().isoformat(),
            'selected_options': selected,
            'sections': []
        }
        
        # Map choices to backup functions
        option_map = {
            '1': ('Contacts', self._backup_contacts),
            '2': ('SMS', self._backup_sms),
            '3': ('Media', self._backup_media),
            '4': ('Audio', self._backup_audio),
            '5': ('Documents', self._backup_documents),
            '6': ('WhatsApp', self._backup_whatsapp),
            '7': ('App Data', self._backup_app_data),
            '8': ('Settings', self._backup_settings),
        }
        
        if '9' in selected:
            # Backup everything
            selected = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        for choice in selected:
            if choice in option_map:
                section_name, backup_func = option_map[choice]
                print(f"\nBacking up {section_name}...")
                try:
                    section_info = backup_func(backup_path)
                    backup_info['sections'].append({
                        'name': section_name,
                        'status': 'success',
                        'info': section_info
                    })
                    print(f"  ✓ {section_name} backed up successfully")
                except Exception as e:
                    backup_info['sections'].append({
                        'name': section_name,
                        'status': 'failed',
                        'error': str(e)
                    })
                    print(f"  ✗ Failed to backup {section_name}: {e}")
        
        # Save metadata
        with open(backup_path / "backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"\n✅ Selective backup completed!")
        print(f"Location: {backup_path}")
        
        return backup_path
    
    def create_adb_backup(self):
        """Create backup using ADB backup command"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"adb_backup_{timestamp}.ab"
        
        print("\n🔧 ADB BACKUP")
        print("=" * 50)
        print("This uses the built-in Android backup system.")
        print("You need to accept the backup on your device screen.")
        
        print(f"\nBackup file will be saved as: {backup_file}")
        print("\nStarting ADB backup...")
        print("Check your device screen and accept the backup!")
        
        # ADB backup command
        result = self.adb.execute_command(['backup', '-apk', '-shared', '-all', '-system', 
                                          '-f', str(backup_file)])
        
        if result['success']:
            print(f"\n✅ ADB backup completed!")
            print(f"File: {backup_file}")
            print(f"Size: {self._get_file_size(backup_file)}")
            
            # Convert to tar if needed
            if input("\nConvert to tar format for easier access? (y/n): ").lower() == 'y':
                self._convert_ab_to_tar(backup_file)
        else:
            print(f"\n❌ ADB backup failed: {result['error']}")
        
        return backup_file if result['success'] else None
    
    def _backup_contacts(self, backup_path):
        """Backup contacts and call logs"""
        contacts_dir = backup_path / "contacts"
        contacts_dir.mkdir(exist_ok=True)
        
        # Backup contacts
        result = self.adb.execute_command(['shell', 'content', 'query', 
                                          '--uri', 'content://contacts/phones', 
                                          '--projection', 'display_name:number'])
        
        if result['success'] and result['output']:
            contacts_file = contacts_dir / "contacts.txt"
            with open(contacts_file, 'w', encoding='utf-8') as f:
                f.write(result['output'])
        
        # Backup call log
        result = self.adb.execute_command(['shell', 'content', 'query', 
                                          '--uri', 'content://call_log/calls'])
        
        if result['success'] and result['output']:
            calls_file = contacts_dir / "call_log.txt"
            with open(calls_file, 'w', encoding='utf-8') as f:
                f.write(result['output'])
        
        return {
            'contacts_file': str(contacts_dir / "contacts.txt"),
            'call_log_file': str(contacts_dir / "call_log.txt")
        }
    
    def _backup_sms(self, backup_path):
        """Backup SMS messages"""
        sms_dir = backup_path / "sms"
        sms_dir.mkdir(exist_ok=True)
        
        result = self.adb.execute_command(['shell', 'content', 'query', 
                                          '--uri', 'content://sms', 
                                          '--projection', '_id:address:date:body'])
        
        if result['success'] and result['output']:
            sms_file = sms_dir / "sms.txt"
            with open(sms_file, 'w', encoding='utf-8') as f:
                f.write(result['output'])
            
            return {'sms_file': str(sms_file), 'message_count': len(result['output'].split('\n'))}
        
        return {'sms_file': None, 'message_count': 0}
    
    def _backup_media(self, backup_path):
        """Backup photos and videos"""
        media_dir = backup_path / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Common media directories
        media_folders = [
            '/sdcard/DCIM',
            '/sdcard/Pictures',
            '/sdcard/Movies',
            '/sdcard/Download',
            '/sdcard/WhatsApp/Media'
        ]
        
        copied_files = []
        
        for folder in media_folders:
            print(f"  Copying from {folder}...", end='', flush=True)
            
            # List files
            result = self.adb.execute_command(['shell', 'find', folder, 
                                              '-type', 'f', '-name', '*.jpg', 
                                              '-o', '-name', '*.png', '-o', 
                                              '-name', '*.mp4', '-o', 
                                              '-name', '*.mov'])
            
            if result['success'] and result['output']:
                files = result['output'].strip().split('\n')
                count = 0
                
                for file in files:
                    if file.strip():
                        try:
                            # Create relative path
                            rel_path = file.replace('/sdcard/', '')
                            dest_path = media_dir / rel_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Pull file
                            self.adb.pull_file(file, str(dest_path))
                            copied_files.append(rel_path)
                            count += 1
                        except:
                            continue
                
                print(f" {count} files")
        
        return {
            'media_directory': str(media_dir),
            'total_files': len(copied_files),
            'sample_files': copied_files[:10]  # First 10 files
        }
    
    def _backup_whatsapp(self, backup_path):
        """Backup WhatsApp data"""
        whatsapp_dir = backup_path / "whatsapp"
        whatsapp_dir.mkdir(parents=True, exist_ok=True)
        
        # WhatsApp directories
        wa_paths = [
            '/sdcard/WhatsApp/Databases',
            '/sdcard/WhatsApp/Media',
            '/sdcard/WhatsApp/.Shared'
        ]
        
        for wa_path in wa_paths:
            local_path = whatsapp_dir / wa_path.split('/')[-1]
            print(f"  Copying {wa_path}...")
            self.adb.pull_file(wa_path, str(local_path))
        
        return {'whatsapp_directory': str(whatsapp_dir)}
    
    def _backup_app_data(self, backup_path):
        """Backup non-system app data"""
        apps_dir = backup_path / "apps"
        apps_dir.mkdir(exist_ok=True)
        
        # Get list of user apps
        result = self.adb.execute_command(['shell', 'pm', 'list', 'packages', '-3'])
        
        if result['success']:
            packages = [pkg.replace('package:', '').strip() 
                       for pkg in result['output'].split('\n') if pkg]
            
            backed_up = []
            
            for package in packages[:10]:  # Limit to 10 apps to avoid timeout
                print(f"  Backing up {package}...", end='', flush=True)
                
                # Backup APK
                apk_result = self.adb.execute_command(['shell', 'pm', 'path', package])
                if apk_result['success']:
                    apk_path = apk_result['output'].replace('package:', '').strip()
                    if apk_path:
                        apk_file = apps_dir / f"{package}.apk"
                        self.adb.pull_file(apk_path, str(apk_file))
                
                # Backup data (requires root)
                if self.adb.is_device_rooted():
                    data_dir = f"/data/data/{package}"
                    local_data_dir = apps_dir / package
                    self.adb.pull_file(data_dir, str(local_data_dir))
                
                backed_up.append(package)
                print(" ✓")
            
            return {
                'apps_directory': str(apps_dir),
                'backed_up_apps': backed_up,
                'total_apps': len(packages)
            }
        
        return {'apps_directory': str(apps_dir), 'backed_up_apps': []}
    
    def _backup_settings(self, backup_path):
        """Backup system settings"""
        settings_dir = backup_path / "settings"
        settings_dir.mkdir(exist_ok=True)
        
        # Backup various settings
        settings_commands = [
            ('global_settings.txt', 'shell settings list global'),
            ('system_settings.txt', 'shell settings list system'),
            ('secure_settings.txt', 'shell settings list secure'),
        ]
        
        for filename, command in settings_commands:
            result = self.adb.execute_command(command.split())
            if result['success']:
                filepath = settings_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result['output'])
        
        return {'settings_directory': str(settings_dir)}
    
    def _compress_backup(self, backup_path):
        """Compress backup directory to zip"""
        zip_path = backup_path.parent / f"{backup_path.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path.parent)
                    zipf.write(file_path, arcname)
        
        # Remove original directory
        shutil.rmtree(backup_path)
        
        return zip_path
    
    def _convert_ab_to_tar(self, ab_file):
        """Convert ADB backup (.ab) to tar format"""
        try:
            import zlib
            import struct
            
            print("Converting .ab to .tar...")
            
            with open(ab_file, 'rb') as f:
                data = f.read()
            
            # Remove Android backup header
            if data.startswith(b'ANDROID BACKUP'):
                # Find end of header
                header_end = data.find(b'\n', 14) + 1
                tar_data = data[header_end:]
                
                # Write tar file
                tar_file = ab_file.with_suffix('.tar')
                with open(tar_file, 'wb') as f:
                    f.write(tar_data)
                
                print(f"✅ Converted to: {tar_file}")
                return tar_file
            
        except Exception as e:
            print(f"Failed to convert: {e}")
            return None
    
    def _get_folder_size(self, path):
        """Get size of folder in human readable format"""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        
        return self._human_readable_size(total)
    
    def _get_file_size(self, filepath):
        """Get file size in human readable format"""
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            return self._human_readable_size(size)
        return "0 B"
    
    def _human_readable_size(self, size):
        """Convert bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir() or item.suffix in ['.zip', '.ab', '.tar']:
                backups.append({
                    'name': item.name,
                    'path': str(item),
                    'size': self._get_file_size(item) if item.is_file() 
                           else self._get_folder_size(item),
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return backups
    
    def restore_backup(self, backup_name):
        """Restore from a backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"Backup not found: {backup_name}")
            return False
        
        print(f"\n🔄 Restoring from backup: {backup_name}")
        print("WARNING: This may overwrite existing data!")
        
        confirm = input("Type 'RESTORE' to continue: ")
        if confirm != 'RESTORE':
            print("Restore cancelled.")
            return False
        
        # TODO: Implement restore logic
        print("Restore functionality coming soon!")
        
        return True