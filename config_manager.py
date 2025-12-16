"""
Config Manager - Manage toolkit configuration and settings
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".androidlockrecovery"
        self.config_file = self.config_dir / "config.json"
        self.default_config = self._get_default_config()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create config
        self.config = self.load_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'version': '2.0',
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            
            'adb': {
                'path': self._find_adb_path(),
                'timeout': 30,
                'auto_connect': True,
            },
            
            'backup': {
                'location': str(Path.home() / "AndroidBackups"),
                'compress': True,
                'keep_versions': 5,
                'auto_backup': True,
            },
            
            'security': {
                'log_operations': True,
                'prompt_destructive': True,
                'legal_warning': True,
                'encrypt_backups': False,
            },
            
            'ui': {
                'colors': True,
                'progress_bars': True,
                'detailed_output': True,
                'language': 'en',
            },
            
            'advanced': {
                'auto_update': True,
                'debug_mode': False,
                'log_level': 'INFO',
                'max_log_size': '10MB',
            },
        }
    
    def _find_adb_path(self):
        """Find ADB executable path"""
        possible_paths = [
            "adb",  # In PATH
            "/usr/bin/adb",
            "/usr/local/bin/adb",
            "C:\\Android\\platform-tools\\adb.exe",
            str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe"),
            str(Path.home() / "Library/Android/sdk/platform-tools/adb"),
        ]
        
        for path in possible_paths:
            if self._check_executable(path):
                return path
        
        return "adb"  # Assume it's in PATH
    
    def _check_executable(self, path):
        """Check if executable exists and works"""
        try:
            import subprocess
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults for missing keys
                config = self._merge_configs(self.default_config, loaded_config)
                config['updated'] = datetime.now().isoformat()
                
                return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config
        else:
            # Create default config
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        config['updated'] = datetime.now().isoformat()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_configs(self, default, loaded):
        """Merge default and loaded configurations"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_configs(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save changes
        return self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.config['updated'] = datetime.now().isoformat()
        return self.save_config()
    
    def change_adb_path(self):
        """Change ADB path interactively"""
        from cli_interface import CLInterface
        cli = CLInterface()
        
        current_path = self.get('adb.path', 'adb')
        print(f"\nCurrent ADB path: {current_path}")
        
        print("\nCommon ADB locations:")
        print("1. In PATH (just 'adb')")
        print("2. Custom path")
        print("3. Auto-detect")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            new_path = "adb"
        elif choice == '2':
            new_path = input("Enter full path to ADB: ").strip()
        elif choice == '3':
            new_path = self._find_adb_path()
            print(f"Auto-detected: {new_path}")
        else:
            print("Invalid choice")
            return False
        
        # Test the new path
        if self._check_executable(new_path):
            self.set('adb.path', new_path)
            print(f"{cli.colors['green']}✓ ADB path updated{cli.colors['reset']}")
            return True
        else:
            print(f"{cli.colors['red']}✗ ADB not found at: {new_path}{cli.colors['reset']}")
            return False
    
    def change_backup_location(self):
        """Change backup location"""
        from cli_interface import CLInterface
        cli = CLInterface()
        
        current = self.get('backup.location')
        print(f"\nCurrent backup location: {current}")
        
        new_location = input("\nEnter new backup location: ").strip()
        
        if not new_location:
            print("No location provided")
            return False
        
        # Create directory if it doesn't exist
        try:
            Path(new_location).mkdir(parents=True, exist_ok=True)
            
            # Test write permission
            test_file = Path(new_location) / "write_test.txt"
            test_file.write_text("test")
            test_file.unlink()
            
            self.set('backup.location', new_location)
            print(f"{cli.colors['green']}✓ Backup location updated{cli.colors['reset']}")
            return True
            
        except Exception as e:
            print(f"{cli.colors['red']}✗ Cannot use location: {e}{cli.colors['reset']}")
            return False
    
    def toggle_logging(self):
        """Toggle operation logging"""
        from cli_interface import CLInterface
        cli = CLInterface()
        
        current = self.get('security.log_operations', True)
        new_value = not current
        
        self.set('security.log_operations', new_value)
        
        status = "enabled" if new_value else "disabled"
        print(f"{cli.colors['green']}✓ Operation logging {status}{cli.colors['reset']}")
        
        return True
    
    def show_config(self):
        """Show current configuration"""
        from cli_interface import CLInterface
        cli = CLInterface()
        
        print(f"\n{cli.colors['cyan']}⚙️  CURRENT CONFIGURATION{cli.colors['reset']}")
        print("-" * 40)
        
        categories = {
            'ADB Settings': self.config.get('adb', {}),
            'Backup Settings': self.config.get('backup', {}),
            'Security Settings': self.config.get('security', {}),
            'UI Settings': self.config.get('ui', {}),
            'Advanced Settings': self.config.get('advanced', {}),
        }
        
        for category, settings in categories.items():
            print(f"\n{cli.colors['yellow']}{category}{cli.colors['reset']}")
            for key, value in settings.items():
                if key not in ['updated', 'created']:
                    print(f"  {key:<20}: {value}")
        
        print(f"\n{cli.colors['dim']}Config file: {self.config_file}{cli.colors['reset']}")
        print(f"{cli.colors['dim']}Last updated: {self.config.get('updated', 'Unknown')}{cli.colors['reset']}")
    
    def export_config(self, filepath=None):
        """Export configuration to file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"androidlockrecovery_config_{timestamp}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✓ Configuration exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"✗ Error exporting config: {e}")
            return None
    
    def import_config(self, filepath):
        """Import configuration from file"""
        if not os.path.exists(filepath):
            print(f"Config file not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'r') as f:
                imported_config = json.load(f)
            
            # Validate version
            if imported_config.get('version') != self.config.get('version'):
                print(f"Warning: Config version mismatch. Current: {self.config.get('version')}, Imported: {imported_config.get('version')}")
            
            # Merge with current config
            self.config = self._merge_configs(self.config, imported_config)
            self.save_config()
            
            print(f"✓ Configuration imported from: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ Error importing config: {e}")
            return False
    
    def setup_wizard(self):
        """Initial setup wizard for first-time users"""
        from cli_interface import CLInterface
        cli = CLInterface()
        
        cli.clear_screen()
        cli.show_banner()
        
        print(f"\n{cli.colors['cyan']}⚙️  INITIAL SETUP WIZARD{cli.colors['reset']}")
        print("-" * 40)
        print("\nLet's configure the toolkit for first use.")
        
        # ADB setup
        print(f"\n{cli.colors['yellow']}Step 1: ADB Configuration{cli.colors['reset']}")
        print("ADB (Android Debug Bridge) is required for device communication.")
        
        adb_path = self._find_adb_path()
        print(f"\nAuto-detected ADB: {adb_path}")
        
        if input(f"\nUse this ADB path? (y/n): ").lower() != 'y':
            custom_path = input("Enter custom ADB path: ").strip()
            if self._check_executable(custom_path):
                adb_path = custom_path
            else:
                print(f"{cli.colors['red']}ADB not found at: {custom_path}{cli.colors['reset']}")
                print("Will use auto-detected path.")
        
        self.set('adb.path', adb_path)
        
        # Backup location
        print(f"\n{cli.colors['yellow']}Step 2: Backup Location{cli.colors['reset']}")
        default_backup = str(Path.home() / "AndroidBackups")
        print(f"\nDefault backup location: {default_backup}")
        
        if input(f"\nUse default location? (y/n): ").lower() != 'y':
            custom_location = input("Enter custom backup location: ").strip()
            try:
                Path(custom_location).mkdir(parents=True, exist_ok=True)
                default_backup = custom_location
            except Exception as e:
                print(f"{cli.colors['red']}Error: {e}{cli.colors['reset']}")
                print("Using default location.")
        
        self.set('backup.location', default_backup)
        
        # Security settings
        print(f"\n{cli.colors['yellow']}Step 3: Security Settings{cli.colors['reset']}")
        
        log_ops = cli.ask_yes_no("Log all operations for audit trail?", True)
        self.set('security.log_operations', log_ops)
        
        prompt_destructive = cli.ask_yes_no("Prompt before destructive actions?", True)
        self.set('security.prompt_destructive', prompt_destructive)
        
        # UI settings
        print(f"\n{cli.colors['yellow']}Step 4: UI Preferences{cli.colors['reset']}")
        
        use_colors = cli.ask_yes_no("Use colored output?", True)
        self.set('ui.colors', use_colors)
        
        progress_bars = cli.ask_yes_no("Show progress bars?", True)
        self.set('ui.progress_bars', progress_bars)
        
        # Save configuration
        self.save_config()
        
        print(f"\n{cli.colors['green']}✅ Setup complete!{cli.colors['reset']}")
        print(f"Configuration saved to: {self.config_file}")
        
        cli.wait_for_user()
        
        return True
    
    def create_shortcut(self):
        """Create desktop shortcut (platform-specific)"""
        import platform
        system = platform.system()
        
        print(f"\nCreating shortcut for {system}...")
        
        if system == "Windows":
            return self._create_windows_shortcut()
        elif system == "Linux":
            return self._create_linux_shortcut()
        elif system == "Darwin":  # macOS
            return self._create_macos_shortcut()
        else:
            print(f"Unsupported system: {system}")
            return False
    
    def _create_windows_shortcut(self):
        """Create Windows shortcut"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "AndroidLockRecovery.lnk")
            
            target = sys.executable
            wDir = os.path.dirname(sys.executable)
            icon = sys.executable
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.Arguments = "-m androidlockrecovery"
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print(f"✓ Shortcut created on desktop: {shortcut_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error creating shortcut: {e}")
            return False
    
    def cleanup_old_files(self, days_old=30):
        """Clean up old backup and log files"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Cleanup old backups
        backup_dir = Path(self.get('backup.location'))
        if backup_dir.exists():
            backup_files = list(backup_dir.rglob("*"))
            deleted = 0
            
            for file_path in backup_files:
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        try:
                            file_path.unlink()
                            deleted += 1
                        except:
                            pass
            
            if deleted > 0:
                print(f"Cleaned up {deleted} old backup files")
        
        # Cleanup old logs
        log_dir = self.config_dir / "logs"
        if log_dir.exists():
            log_files = list(log_dir.rglob("*.log"))
            deleted_logs = 0
            
            for log_file in log_files:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    try:
                        log_file.unlink()
                        deleted_logs += 1
                    except:
                        pass
            
            if deleted_logs > 0:
                print(f"Cleaned up {deleted_logs} old log files")
        
        return True