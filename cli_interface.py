"""
CLI Interface - Command line interface for AndroidLockRecovery
"""

import os
import sys
from datetime import datetime

class CLInterface:
    def __init__(self):
        self.width = 80
        self.colors = self._init_colors()
    
    def _init_colors(self):
        """Initialize color codes for terminal"""
        colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
        }
        
        # Check if terminal supports colors
        try:
            import curses
            curses.setupterm()
            if curses.tigetnum('colors') < 8:
                # No color support, return empty strings
                return {k: '' for k in colors}
        except:
            pass
        
        return colors
    
    def show_main_menu(self):
        """Display main menu"""
        self.clear_screen()
        
        print(self.colors['cyan'] + "=" * self.width)
        print("      ANDROID LOCK RECOVERY TOOLKIT v2.0")
        print("=" * self.width + self.colors['reset'])
        
        print(f"\n{self.colors['yellow']}⚠️  LEGAL DISCLAIMER:{self.colors['reset']}")
        print("Use only on devices you own or have permission to access.")
        print("Unauthorized access is illegal and unethical.")
        
        print(f"\n{self.colors['green']}📱 MAIN MENU{self.colors['reset']}")
        print("-" * 40)
        
        menu_items = [
            ("1", "Device Information", "Scan and display device details"),
            ("2", "Data Backup", "Backup data before any operations"),
            ("3", "Lock Bypass", "Bypass pattern/PIN/password/FRP"),
            ("4", "Factory Reset", "Last resort - erases everything"),
            ("5", "Data Recovery", "Extract data from locked device"),
            ("6", "Firmware Tools", "Download and flash firmware"),
            ("7", "Security Audit", "Check device security status"),
            ("8", "Exit", "Exit the toolkit"),
        ]
        
        for num, title, description in menu_items:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {self.colors['bold']}{title:<20}{self.colors['reset']} {description}")
        
        print(f"\n{self.colors['cyan']}─" * 40 + self.colors['reset'])
        
        while True:
            choice = input(f"\n{self.colors['green']}Select option (1-8): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice. Please enter 1-8.{self.colors['reset']}")
    
    def ask_backup_type(self):
        """Ask for backup type"""
        print(f"\n{self.colors['cyan']}📦 BACKUP TYPE{self.colors['reset']}")
        print("-" * 40)
        
        options = [
            ("1", "Full Backup", "Backup everything (takes time & space)"),
            ("2", "Selective Backup", "Choose what to backup"),
            ("3", "ADB Backup", "Use Android's built-in backup system"),
            ("4", "Cancel", "Return to main menu"),
        ]
        
        for num, title, description in options:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<20} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select backup type (1-4): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def ask_lock_type(self):
        """Ask what type of lock to bypass"""
        print(f"\n{self.colors['cyan']}🔓 LOCK TYPE{self.colors['reset']}")
        print("-" * 40)
        
        print("What type of lock is on the device?")
        
        options = [
            ("1", "Pattern", "Dot-to-dot pattern"),
            ("2", "PIN", "4-6 digit PIN"),
            ("3", "Password", "Text password"),
            ("4", "Biometric", "Fingerprint/Face"),
            ("5", "FRP", "Factory Reset Protection"),
            ("6", "Don't Know", "Let tool detect"),
        ]
        
        for num, title, description in options:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<15} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select lock type (1-6): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def confirm_destructive_action(self, action_name):
        """Confirm destructive actions like factory reset"""
        print(f"\n{self.colors['red']}⚠️  CRITICAL WARNING{self.colors['reset']}")
        print("-" * 40)
        
        print(f"This will perform: {self.colors['bold']}{action_name.upper()}{self.colors['reset']}")
        print(f"{self.colors['red']}This action:{self.colors['reset']}")
        print("  • CANNOT be undone")
        print("  • Will ERASE data")
        print("  • May BRICK device if done wrong")
        
        print(f"\n{self.colors['yellow']}Before continuing:{self.colors['reset']}")
        print("  1. Backup all important data")
        print("  2. Ensure device is charged (>50%)")
        print("  3. Have proof of ownership ready")
        
        response = input(f"\n{self.colors['green']}Type 'I UNDERSTAND' to continue: {self.colors['reset']}")
        return response == 'I UNDERSTAND'
    
    def ask_reset_method(self):
        """Ask for factory reset method"""
        print(f"\n{self.colors['cyan']}🔄 RESET METHOD{self.colors['reset']}")
        print("-" * 40)
        
        print("Select reset method:")
        
        methods = [
            ("1", "Safe Reset", "Try to preserve data if possible"),
            ("2", "Recovery Mode", "Standard recovery mode reset"),
            ("3", "Fastboot", "For unlocked bootloaders (advanced)"),
            ("4", "FRP-aware", "Avoid FRP lock (remove accounts first)"),
            ("5", "Hard Reset", "Last resort (risky)"),
        ]
        
        for num, title, description in methods:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<15} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select method (1-5): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return ['safe', 'recovery', 'fastboot', 'frp', 'hard'][int(choice) - 1]
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def ask_recovery_type(self):
        """Ask for data recovery type"""
        print(f"\n{self.colors['cyan']}🔍 DATA RECOVERY{self.colors['reset']}")
        print("-" * 40)
        
        print("What data do you want to recover?")
        
        options = [
            ("1", "Contacts", "Phone contacts and call logs"),
            ("2", "Messages", "SMS and MMS messages"),
            ("3", "Photos/Videos", "Media files"),
            ("4", "App Data", "Application data and settings"),
            ("5", "Everything", "All recoverable data"),
        ]
        
        for num, title, description in options:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<15} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select recovery type (1-5): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def ask_firmware_action(self):
        """Ask for firmware action"""
        print(f"\n{self.colors['cyan']}⚙️  FIRMWARE TOOLS{self.colors['reset']}")
        print("-" * 40)
        
        print("Firmware operations:")
        
        options = [
            ("1", "Download Firmware", "Download stock firmware"),
            ("2", "Flash Firmware", "Flash firmware to device"),
            ("3", "Check Updates", "Check for firmware updates"),
            ("4", "Emergency Recovery", "Recover bricked device"),
        ]
        
        for num, title, description in options:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<20} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select action (1-4): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def ask_setting(self):
        """Ask for setting to change"""
        print(f"\n{self.colors['cyan']}⚙️  SETTINGS{self.colors['reset']}")
        print("-" * 40)
        
        print("Toolkit settings:")
        
        options = [
            ("1", "ADB Path", "Change ADB executable path"),
            ("2", "Backup Location", "Change backup save location"),
            ("3", "Logging", "Enable/disable logging"),
            ("4", "Reset Settings", "Reset to defaults"),
            ("5", "Back", "Return to main menu"),
        ]
        
        for num, title, description in options:
            print(f"{self.colors['blue']}{num}.{self.colors['reset']} {title:<20} {description}")
        
        while True:
            choice = input(f"\n{self.colors['green']}Select setting (1-5): {self.colors['reset']}").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print(f"{self.colors['red']}Invalid choice.{self.colors['reset']}")
    
    def show_progress(self, current, total, message=""):
        """Show progress bar"""
        bar_width = 40
        percent = current / total if total > 0 else 0
        filled = int(bar_width * percent)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        sys.stdout.write(f"\r{self.colors['cyan']}[{bar}] {percent:.1%} {message}{self.colors['reset']}")
        sys.stdout.flush()
        
        if current >= total:
            print()  # New line when complete
    
    def show_success(self, message):
        """Show success message"""
        print(f"\n{self.colors['green']}✅ {message}{self.colors['reset']}")
    
    def show_error(self, message):
        """Show error message"""
        print(f"\n{self.colors['red']}❌ {message}{self.colors['reset']}")
    
    def show_warning(self, message):
        """Show warning message"""
        print(f"\n{self.colors['yellow']}⚠️  {message}{self.colors['reset']}")
    
    def show_info(self, message):
        """Show info message"""
        print(f"\n{self.colors['blue']}ℹ️  {message}{self.colors['reset']}")
    
    def show_device_info(self, device_info):
        """Show device information in formatted way"""
        print(f"\n{self.colors['cyan']}📱 DEVICE INFORMATION{self.colors['reset']}")
        print("-" * 40)
        
        info_map = {
            'Model': device_info.get('Model', 'Unknown'),
            'Android Version': device_info.get('Android Version', 'Unknown'),
            'Serial Number': device_info.get('Serial Number', 'Unknown'),
            'Manufacturer': device_info.get('Manufacturer', 'Unknown'),
            'Security Patch': device_info.get('Security Patch', 'Unknown'),
            'Bootloader': device_info.get('Bootloader', 'Unknown'),
            'Hardware': device_info.get('Hardware', 'Unknown'),
        }
        
        for key, value in info_map.items():
            print(f"{self.colors['blue']}{key:<20}{self.colors['reset']}: {value}")
    
    def show_security_report(self, report):
        """Show security report"""
        print(f"\n{self.colors['cyan']}🔒 SECURITY REPORT{self.colors['reset']}")
        print("-" * 40)
        
        score = report.get('security_score', 0)
        
        # Color code based on score
        if score >= 80:
            score_color = self.colors['green']
            rating = "GOOD"
        elif score >= 60:
            score_color = self.colors['yellow']
            rating = "FAIR"
        elif score >= 40:
            score_color = self.colors['red']
            rating = "POOR"
        else:
            score_color = self.colors['red'] + self.colors['bold']
            rating = "CRITICAL"
        
        print(f"{self.colors['blue']}Security Score:{self.colors['reset']} {score_color}{score}/100 ({rating}){self.colors['reset']}")
        print(f"{self.colors['blue']}Total Risks:{self.colors['reset']} {report.get('total_risks', 0)}")
        
        if report.get('risks_found'):
            print(f"\n{self.colors['yellow']}⚠️  IDENTIFIED RISKS:{self.colors['reset']}")
            for i, risk in enumerate(report['risks_found'][:5], 1):
                print(f"  {i}. {risk}")
            
            if len(report['risks_found']) > 5:
                print(f"  ... and {len(report['risks_found']) - 5} more")
        
        if report.get('recommendations'):
            print(f"\n{self.colors['green']}💡 RECOMMENDATIONS:{self.colors['reset']}")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"  {i}. {rec}")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wait_for_user(self, message="Press Enter to continue..."):
        """Wait for user to press Enter"""
        input(f"\n{self.colors['dim']}{message}{self.colors['reset']}")
    
    def ask_yes_no(self, question, default=True):
        """Ask yes/no question"""
        choices = "Y/n" if default else "y/N"
        prompt = f"{question} [{choices}]: "
        
        while True:
            response = input(f"{self.colors['green']}{prompt}{self.colors['reset']}").strip().lower()
            
            if response == '':
                return default
            elif response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print(f"{self.colors['red']}Please enter y/n or press Enter for default.{self.colors['reset']}")
    
    def show_banner(self):
        """Show toolkit banner"""
        banner = f"""
{self.colors['cyan']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║      █████╗ ███╗   ██╗██████╗ ██████╗  ██████╗ ██╗██████╗           ║
║     ██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██║██╔══██╗          ║
║     ███████║██╔██╗ ██║██║  ██║██████╔╝██║   ██║██║██║  ██║          ║
║     ██╔══██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██║██║  ██║          ║
║     ██║  ██║██║ ╚████║██████╔╝██║  ██║╚██████╔╝██║██████╔╝          ║
║     ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝           ║
║                                                                      ║
║                  L O C K   R E C O V E R Y   T O O L K I T           ║
║                                                                      ║
║              Version 2.0 • For Educational Purposes Only             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{self.colors['reset']}
        """
        
        print(banner)
    
    def show_legal_warning(self):
        """Show legal warning"""
        warning = f"""
{self.colors['red']}
╔══════════════════════════════════════════════════════════════════════╗
║                     ⚠️   LEGAL WARNING  ⚠️                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  This tool is for RECOVERING ACCESS TO YOUR OWN DEVICES ONLY.        ║
║                                                                      ║
║  By using this tool, you agree that:                                 ║
║                                                                      ║
║  1. You will ONLY use it on devices you own                         ║
║  2. You have explicit permission for any other devices               ║
║  3. You understand unauthorized access is ILLEGAL                    ║
║  4. You accept ALL responsibility for your actions                   ║
║                                                                      ║
║  The developers are NOT responsible for misuse of this tool.         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{self.colors['reset']}
        """
        
        print(warning)
        
        response = input(f"\n{self.colors['green']}Type 'I AGREE' to continue: {self.colors['reset']}")
        return response == 'I AGREE'