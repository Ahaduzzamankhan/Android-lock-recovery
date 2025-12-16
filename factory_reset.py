"""
Factory Reset - Safe factory reset methods with data protection
"""

import time
import os
from pathlib import Path
from adb_manager import ADBManager

class FactoryResetTool:
    def __init__(self):
        self.adb = ADBManager()
        self.warning_shown = False
    
    def perform_reset(self, method='safe'):
        """Perform factory reset with selected method"""
        if not self.warning_shown:
            self._show_warning()
            self.warning_shown = True
        
        methods = {
            'safe': self._safe_reset,
            'recovery': self._recovery_reset,
            'fastboot': self._fastboot_reset,
            'frp': self._frp_reset,
            'hard': self._hard_reset,
        }
        
        if method in methods:
            return methods[method]()
        else:
            print(f"Unknown method: {method}")
            return False
    
    def _show_warning(self):
        """Show factory reset warnings"""
        print("\n" + "!" * 70)
        print("⚠️  CRITICAL WARNING: FACTORY RESET")
        print("!" * 70)
        print("\nThis will:")
        print("  ❌ ERASE ALL USER DATA")
        print("  ❌ Remove accounts and settings")
        print("  ❌ Delete apps and app data")
        print("  ❌ Wipe internal storage")
        print("  ❌ Restore to factory state")
        
        print("\nData that will be LOST FOREVER:")
        print("  - Photos and videos")
        print("  - Contacts and messages")
        print("  - Documents and downloads")
        print("  - App data and settings")
        print("  - Accounts and passwords")
        
        print("\n⚠️  CANNOT BE UNDONE!")
        print("Ensure you have BACKED UP everything important!")
        
        response = input("\nType 'I UNDERSTAND' to continue: ")
        if response != 'I UNDERSTAND':
            print("Reset cancelled.")
            return False
        
        # Double check
        print("\nLAST CHANCE: This is irreversible!")
        response = input("Type 'CONFIRM RESET' to proceed: ")
        if response != 'CONFIRM RESET':
            print("Reset cancelled.")
            return False
        
        return True
    
    def _safe_reset(self):
        """Safe reset with maximum data protection"""
        print("\n🛡️  SAFE FACTORY RESET")
        print("Trying to preserve data where possible")
        
        # Step 1: Backup suggestions
        print("\n📦 RECOMMENDED BACKUPS:")
        print("1. Google Photos backup (if enabled)")
        print("2. Google Drive backup")
        print("3. Samsung Cloud (Samsung devices)")
        print("4. Manufacturer cloud services")
        print("5. Manual transfer to computer")
        
        input("\nPress Enter after backing up...")
        
        # Step 2: Account removal
        print("\n👤 REMOVING ACCOUNTS:")
        print("Important: Remove accounts to avoid FRP lock")
        
        if self.adb.check_adb_installed():
            print("Checking for accounts...")
            result = self.adb.execute_command(['shell', 'cmd', 'account', 'list'])
            if result['success']:
                print(f"Accounts found:\n{result['output']}")
        
        print("\nManual steps required:")
        print("1. Go to Settings > Accounts")
        print("2. Remove Google account")
        print("3. Remove other accounts")
        print("4. Turn off 'Find My Device'")
        
        input("\nPress Enter after removing accounts...")
        
        # Step 3: Perform reset
        print("\n🔄 PERFORMING SAFE RESET")
        
        print("Method 1: Settings reset (recommended)")
        print("  Go to: Settings > System > Reset options")
        print("  Select: Erase all data (factory reset)")
        
        print("\nMethod 2: Recovery mode (alternative)")
        print("  Power off device")
        print("  Boot to recovery (Volume Up + Power)")
        print("  Select: Wipe data/factory reset")
        
        print("\n⚠️  DO NOT REBOOT until reset completes!")
        
        result = input("\nHas reset completed? (y/n): ").lower()
        if result == 'y':
            print("\n✅ Safe reset performed!")
            print("Device should now be at setup screen.")
            return True
        
        return False
    
    def _recovery_reset(self):
        """Recovery mode factory reset"""
        print("\n⚙️  RECOVERY MODE FACTORY RESET")
        
        print("Steps:")
        print("1. Power off the device completely")
        print("2. Press and hold recovery combo:")
        print("   - Most devices: Volume UP + Power")
        print("   - Samsung: Volume UP + Home + Power")
        print("   - Some: Volume DOWN + Power")
        print("3. Release when logo appears")
        
        print("\nIn recovery menu:")
        print("1. Use volume keys to navigate")
        print("2. Power button to select")
        print("3. Select 'Wipe data/factory reset'")
        print("4. Confirm 'Yes'")
        print("5. Select 'Wipe cache partition' (optional)")
        print("6. Select 'Reboot system now'")
        
        print("\n⚠️  Some recoveries have different options!")
        
        result = input("\nPerform recovery reset? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\nManually perform steps above...")
        result = input("\nDid recovery reset succeed? (y/n): ").lower()
        return result == 'y'
    
    def _fastboot_reset(self):
        """Fastboot mode factory reset (for unlocked bootloaders)"""
        print("\n⚡ FASTBOOT FACTORY RESET")
        print("For devices with unlocked bootloaders")
        
        # Check for fastboot
        try:
            result = subprocess.run(['fastboot', 'devices'], 
                                  capture_output=True, text=True)
            if 'fastboot' not in result.stdout:
                print("No device in fastboot mode")
                print("\nTo enter fastboot:")
                print("1. Power off device")
                print("2. Press Volume DOWN + Power")
                print("3. Or: adb reboot bootloader")
                return False
        except FileNotFoundError:
            print("Fastboot not installed")
            return False
        
        print("\n⚠️  WARNING: Fastboot commands are powerful!")
        print("Incorrect commands can brick device!")
        
        commands = [
            ("fastboot erase userdata", "Erase user data partition"),
            ("fastboot erase cache", "Erase cache partition"),
            ("fastboot format userdata", "Format user data"),
            ("fastboot -w", "Wipe userdata and cache"),
        ]
        
        print("\nAvailable fastboot wipe commands:")
        for cmd, desc in commands:
            print(f"  {cmd} - {desc}")
        
        print("\n⚠️  RECOMMENDED: Use recovery mode instead!")
        print("Fastboot is for advanced users only")
        
        result = input("\nUse fastboot? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\nSelect command to run (1-4): ", end='')
        choice = input().strip()
        
        if choice in ['1', '2', '3', '4']:
            cmd_index = int(choice) - 1
            cmd, desc = commands[cmd_index]
            
            print(f"\nExecuting: {cmd}")
            print(f"Description: {desc}")
            
            confirm = input("Type 'EXECUTE' to run: ")
            if confirm == 'EXECUTE':
                try:
                    subprocess.run(cmd.split(), timeout=30)
                    print("Command executed.")
                    
                    # Reboot
                    subprocess.run(['fastboot', 'reboot'], timeout=10)
                    print("Device rebooting...")
                    return True
                except Exception as e:
                    print(f"Error: {e}")
                    return False
        
        return False
    
    def _frp_reset(self):
        """FRP-aware factory reset"""
        print("\n🔐 FRP-AWARE FACTORY RESET")
        print("To avoid Factory Reset Protection lock")
        
        print("\nBEFORE RESET:")
        print("1. MUST remove Google account:")
        print("   Settings > Accounts > Google > Remove account")
        
        print("\n2. MUST remove other accounts:")
        print("   Samsung, Xiaomi, Huawei, etc.")
        
        print("\n3. MUST disable 'Find My Device':")
        print("   Settings > Security > Find My Device")
        
        print("\n4. Verify accounts are removed:")
        print("   Settings should show 'No accounts'")
        
        print("\n5. THEN perform factory reset")
        
        result = input("\nHave you removed ALL accounts? (y/n): ").lower()
        if result != 'y':
            print("\n❌ DO NOT RESET without removing accounts!")
            print("You will get FRP locked!")
            return False
        
        print("\n✅ Accounts removed. Proceed with reset.")
        return self._safe_reset()
    
    def _hard_reset(self):
        """Hard reset - last resort"""
        print("\n💀 HARD FACTORY RESET")
        print("LAST RESORT - When nothing else works")
        
        print("\n⚠️  EXTREME WARNING:")
        print("This may:")
        print("  - Brick device if done wrong")
        print("  - Void warranty")
        print("  - Cause permanent damage")
        
        print("\nMethods (varies by device):")
        print("1. Test Point method (hardware)")
        print("2. EDL mode flash")
        print("3. Bootloader reflash")
        print("4. JTAG/Sampling method")
        
        print("\n⚠️  REQUIRES:")
        print("  - Technical expertise")
        print("  - Special tools/cables")
        print("  - Risk of permanent damage")
        
        print("\n✅ RECOMMENDED:")
        print("Take to authorized service center")
        print("Provide proof of purchase")
        
        result = input("\nContinue with hard reset? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\nSelect device brand for specific instructions:")
        print("1. Samsung")
        print("2. Xiaomi")
        print("3. Huawei")
        print("4. Other")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            self._samsung_hard_reset()
        elif choice == '2':
            self._xiaomi_hard_reset()
        elif choice == '3':
            self._huawei_hard_reset()
        else:
            print("\nGeneral hard reset steps:")
            print("1. Find device-specific guide online")
            print("2. Look for 'test point' or 'EDL mode'")
            print("3. Use manufacturer flash tools")
            print("4. Follow instructions precisely")
        
        return False
    
    def _samsung_hard_reset(self):
        """Samsung-specific hard reset methods"""
        print("\n📱 SAMSUNG HARD RESET")
        
        print("Common methods:")
        print("1. Combination firmware flash")
        print("2. SamFirm tool (requires paid account)")
        print("3. Octoplus/Octopus box (paid)")
        print("4. Test Point for specific models")
        
        print("\n⚠️  Samsung protection:")
        print("- Knox warranty bit (trips permanently)")
        print("- RMM lock (region lock)")
        print("- Recent models very secure")
        
        print("\n✅ Recommendation:")
        print("Use Samsung authorized service")
        print("Provide proof of purchase")
    
    def post_reset_setup(self):
        """Guide for setup after factory reset"""
        print("\n🔄 POST-RESET SETUP GUIDE")
        
        print("After factory reset:")
        print("\n1. Initial setup:")
        print("   - Select language")
        print("   - Connect to WiFi")
        print("   - Accept terms")
        
        print("\n2. Google account:")
        print("   - Sign in with ORIGINAL account")
        print("   - For FRP bypass, may need different account")
        
        print("\n3. Restore options:")
        print("   - Restore from Google backup")
        print("   - Restore from manufacturer backup")
        print("   - Set up as new device")
        
        print("\n4. Security setup:")
        print("   - Set new screen lock")
        print("   - Enable Find My Device")
        print("   - Configure fingerprint/face")
        
        print("\n5. App restoration:")
        print("   - Install essential apps")
        print("   - Restore app data if backed up")
        print("   - Configure settings")
        
        print("\n⚠️  IMPORTANT:")
        print("If FRP locked, you need original account")
        print("Otherwise, contact manufacturer with proof")