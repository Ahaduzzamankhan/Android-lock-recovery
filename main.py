#!/usr/bin/env python3
"""
AndroidLockRecovery - Main Entry Point
Professional toolkit for Android lock screen recovery
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║      ANDROID LOCK RECOVERY TOOLKIT v2.0           ║
    ║     Professional Unlock Solution                  ║
    ╚═══════════════════════════════════════════════════╝
    
    ⚠️  LEGAL DISCLAIMER:
    This tool is for RECOVERING ACCESS TO YOUR OWN DEVICES ONLY.
    Use on devices you own or have explicit permission to access.
    Misuse of this tool is illegal and unethical.
    """)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required!")
        sys.exit(1)
    
    # Check for ADB
    try:
        from adb_manager import ADBManager
        adb = ADBManager()
        if not adb.check_adb_installed():
            print("ADB not found. Please install Android Platform Tools.")
            sys.exit(1)
    except ImportError:
        print("Error: Required modules not found.")
        sys.exit(1)
    
    # Show main menu
    show_main_menu()

def show_main_menu():
    """Display main menu and handle user choice"""
    from cli_interface import CLInterface
    
    interface = CLInterface()
    
    while True:
        choice = interface.show_main_menu()
        
        if choice == '1':
            device_info_flow()
        elif choice == '2':
            backup_flow()
        elif choice == '3':
            bypass_flow()
        elif choice == '4':
            factory_reset_flow()
        elif choice == '5':
            data_recovery_flow()
        elif choice == '6':
            firmware_flow()
        elif choice == '7':
            settings_flow()
        elif choice == '8':
            print("\n👋 Thank you for using AndroidLockRecovery!")
            print("Remember: Only use on devices you own!")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")

def device_info_flow():
    """Get device information"""
    from device_scanner import DeviceScanner
    from cli_interface import CLInterface
    
    interface = CLInterface()
    scanner = DeviceScanner()
    
    print("\n📱 DEVICE INFORMATION")
    print("=" * 50)
    
    devices = scanner.scan_devices()
    if not devices:
        interface.show_error("No devices found!")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"\nDevice {i}:")
        print(f"  Serial: {device.get('serial', 'Unknown')}")
        print(f"  Model: {device.get('model', 'Unknown')}")
        print(f"  Android: {device.get('android_version', 'Unknown')}")
        print(f"  Security: {device.get('security_patch', 'Unknown')}")
        print(f"  Lock Type: {device.get('lock_type', 'Unknown')}")

def backup_flow():
    """Backup device data"""
    from backup_tool import BackupTool
    from cli_interface import CLInterface
    
    interface = CLInterface()
    backup = BackupTool()
    
    print("\n💾 DATA BACKUP")
    print("=" * 50)
    
    # Ask for backup type
    backup_type = interface.ask_backup_type()
    
    if backup_type == '1':
        backup.create_full_backup()
    elif backup_type == '2':
        backup.create_selective_backup()
    elif backup_type == '3':
        backup.create_adb_backup()

def bypass_flow():
    """Lock screen bypass flow"""
    from cli_interface import CLInterface
    from pattern_bypass import PatternBypass
    from pin_reset import PINReset
    from password_cracker import PasswordCracker
    from biometric_bypass import BiometricBypass
    from frp_bypass import FRPBypass
    
    interface = CLInterface()
    
    print("\n🔓 LOCK BYPASS METHODS")
    print("=" * 50)
    
    lock_type = interface.ask_lock_type()
    
    if lock_type == '1':  # Pattern
        tool = PatternBypass()
        tool.attempt_bypass()
    elif lock_type == '2':  # PIN
        tool = PINReset()
        tool.attempt_bypass()
    elif lock_type == '3':  # Password
        tool = PasswordCracker()
        tool.attempt_bypass()
    elif lock_type == '4':  # Biometric
        tool = BiometricBypass()
        tool.attempt_bypass()
    elif lock_type == '5':  # FRP
        tool = FRPBypass()
        tool.attempt_bypass()

def factory_reset_flow():
    """Factory reset flow"""
    from factory_reset import FactoryResetTool
    from cli_interface import CLInterface
    
    interface = CLInterface()
    reset = FactoryResetTool()
    
    print("\n⚠️  FACTORY RESET")
    print("=" * 50)
    print("WARNING: This will erase ALL data on the device!")
    print("Use only as last resort!")
    
    if interface.confirm_destructive_action("factory reset"):
        method = interface.ask_reset_method()
        reset.perform_reset(method)

def data_recovery_flow():
    """Data recovery flow"""
    from data_extractor import DataExtractor
    from cli_interface import CLInterface
    
    interface = CLInterface()
    extractor = DataExtractor()
    
    print("\n🔍 DATA RECOVERY")
    print("=" * 50)
    
    recovery_type = interface.ask_recovery_type()
    
    if recovery_type == '1':
        extractor.extract_contacts()
    elif recovery_type == '2':
        extractor.extract_messages()
    elif recovery_type == '3':
        extractor.extract_photos()
    elif recovery_type == '4':
        extractor.extract_app_data()

def firmware_flow():
    """Firmware tools flow"""
    from firmware_tool import FirmwareTool
    from cli_interface import CLInterface
    
    interface = CLInterface()
    firmware = FirmwareTool()
    
    print("\n⚙️  FIRMWARE TOOLS")
    print("=" * 50)
    
    action = interface.ask_firmware_action()
    
    if action == '1':
        firmware.download_firmware()
    elif action == '2':
        firmware.flash_firmware()
    elif action == '3':
        firmware.check_updates()

def settings_flow():
    """Settings and configuration"""
    from config_manager import ConfigManager
    from cli_interface import CLInterface
    
    interface = CLInterface()
    config = ConfigManager()
    
    print("\n⚙️  SETTINGS")
    print("=" * 50)
    
    setting = interface.ask_setting()
    
    if setting == '1':
        config.change_adb_path()
    elif setting == '2':
        config.change_backup_location()
    elif setting == '3':
        config.toggle_logging()
    elif setting == '4':
        config.reset_settings()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue on GitHub.")
        sys.exit(1)