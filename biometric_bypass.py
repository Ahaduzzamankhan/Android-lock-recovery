"""
Biometric Bypass - Methods to bypass fingerprint/face unlock
"""

import time
import subprocess
from adb_manager import ADBManager

class BiometricBypass:
    def __init__(self):
        self.adb = ADBManager()
        self.methods = [
            self._method_safe_mode,
            self._method_alternative_auth,
            self._method_emergency_call,
            self._method_reboot_trick,
            self._method_adb_fingerprint,
        ]
    
    def attempt_bypass(self):
        """Try biometric bypass methods"""
        print("\n👆 BIOMETRIC BYPASS")
        print("=" * 60)
        
        if not self.adb.check_adb_installed():
            return False
        
        print("Biometric locks include:")
        print("  - Fingerprint")
        print("  - Face Unlock")
        print("  - Iris Scanner")
        print("  - Voice Match")
        
        bio_type = input("\nWhat type of biometric lock? (1=fingerprint, 2=face, 3=both): ").strip()
        
        print("\n⚠️  Note: Biometric bypass is difficult")
        print("Android has strong biometric protection")
        
        # Try methods
        success = False
        for i, method in enumerate(self.methods, 1):
            print(f"\n[{i}/{len(self.methods)}] Trying method...")
            if method(bio_type):
                success = True
                break
        
        if success:
            print("\n✅ Biometric bypass successful!")
        else:
            print("\n❌ All biometric bypass methods failed")
            print("\nConsider:")
            print("1. Using backup PIN/password")
            print("2. Factory reset (erases data)")
            print("3. Contact manufacturer")
        
        return success
    
    def _method_safe_mode(self, bio_type):
        """Method 1: Safe mode disable"""
        print("Method 1: Safe mode")
        
        print("  Some devices disable biometrics in safe mode")
        print("  Steps:")
        print("  1. Power off device")
        print("  2. Press and hold power button")
        print("  3. When logo appears, press and hold volume down")
        print("  4. Keep holding until boot completes")
        print("  5. Check if PIN/password is required instead")
        
        result = input("\n  Try safe mode? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\n  Manually boot to safe mode as described")
        result = input("  Did safe mode disable biometrics? (y/n): ").lower()
        return result == 'y'
    
    def _method_alternative_auth(self, bio_type):
        """Method 2: Alternative authentication"""
        print("Method 2: Alternative authentication")
        
        print("  After multiple failed biometric attempts:")
        print("  1. Android may ask for PIN/password")
        print("  2. Try 5-10 failed fingerprint/face attempts")
        print("  3. Look for 'Use PIN' or 'Use Password' option")
        
        print("\n  For fingerprint:")
        print("  - Try different fingers (including opposite hand)")
        print("  - Try wiping sensor")
        print("  - Try warmer/cooler fingers")
        
        print("\n  For face unlock:")
        print("  - Try with/without glasses")
        print("  - Try different lighting")
        print("  - Try different angles")
        
        result = input("\n  Can you see alternative auth option? (y/n): ").lower()
        return result == 'y'
    
    def _method_emergency_call(self, bio_type):
        """Method 3: Emergency call crash"""
        print("Method 3: Emergency call trick")
        
        print("  Old method for some devices:")
        print("  1. On lock screen, tap Emergency Call")
        print("  2. Dial *#*#... service codes")
        print("  3. Try: *#*#7378423#*#* (Service menu)")
        print("  4. Try: *#0*# (Test menu)")
        print("  5. Quick back/exit may crash lock screen")
        
        result = input("\n  Try emergency call method? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\n  Manually try on device")
        result = input("  Did it work? (y/n): ").lower()
        return result == 'y'
    
    def _method_reboot_trick(self, bio_type):
        """Method 4: Reboot timing attack"""
        print("Method 4: Reboot timing")
        
        print("  Some devices have timing vulnerability:")
        print("  1. Reboot device")
        print("  2. Immediately after boot, quickly:")
        print("     - Swipe up/enter PIN quickly")
        print("     - Try emergency call trick")
        print("  3. Biometric service may not be loaded yet")
        
        if self.adb.is_device_rooted():
            print("\n  With root access:")
            print("  1. Reboot to recovery")
            print("  2. Delete biometric data files")
            print("  3. Reboot to system")
        
        result = input("\n  Try reboot timing? (y/n): ").lower()
        if result != 'y':
            return False
        
        print("\n  Manually reboot and try quick unlock")
        result = input("  Did timing attack work? (y/n): ").lower()
        return result == 'y'
    
    def _method_adb_fingerprint(self, bio_type):
        """Method 5: ADB fingerprint simulation (requires root)"""
        print("Method 5: ADB fingerprint simulation")
        
        if not self.adb.is_device_rooted():
            print("  ✗ Requires root access")
            return False
        
        print("  Attempting to simulate fingerprint via ADB...")
        
        # Try to find fingerprint service
        result = self.adb.execute_command(['shell', 'dumpsys', 'fingerprint'])
        
        if result['success']:
            print("  ✓ Fingerprint service found")
            
            # Try to get enrolled fingerprints
            result = self.adb.execute_command(['shell', 'cmd', 'fingerprint', 'list'])
            if result['success']:
                print(f"  Enrolled fingerprints: {result['output']}")
            
            # WARNING: Actually bypassing fingerprint requires deep system access
            # This is just for demonstration
            
            print("\n  ⚠️  Advanced method (theoretical):")
            print("  Could attempt to:")
            print("  1. Disable fingerprint service")
            print("  2. Remove fingerprint data")
            print("  3. Spoof fingerprint authentication")
            
            print("\n  This requires:")
            print("  - Deep system knowledge")
            print("  - Specific device vulnerabilities")
            print("  - Risk of bricking device")
        
        else:
            print("  ✗ Could not access fingerprint service")
        
        return False
    
    def analyze_biometric_security(self):
        """Analyze biometric security level"""
        print("\n🔒 BIOMETRIC SECURITY ANALYSIS")
        
        if not self.adb.check_adb_installed():
            return
        
        # Check fingerprint hardware
        result = self.adb.execute_command(['shell', 'getprop', 'ro.hardware.fingerprint'])
        if result['success'] and result['output']:
            print(f"Fingerprint hardware: {result['output']}")
        
        # Check biometric strength
        result = self.adb.execute_command(['shell', 'dumpsys', 'device_policy'])
        if result['success'] and 'biometric' in result['output']:
            print("\nBiometric policy found")
            
            # Parse for security levels
            lines = result['output'].split('\n')
            for line in lines:
                if 'BIOMETRIC' in line or 'FINGERPRINT' in line:
                    print(f"  {line.strip()}")
        
        # Check Android version
        result = self.adb.execute_command(['shell', 'getprop', 'ro.build.version.sdk'])
        if result['success']:
            sdk = result['output'].strip()
            print(f"\nAndroid SDK: {sdk}")
            
            # Biometric improvements by version
            biometric_versions = {
                '23': 'Android 6.0 - Basic fingerprint API',
                '24': 'Android 7.0 - Improved fingerprint',
                '28': 'Android 9.0 - BiometricPrompt API',
                '29': 'Android 10 - Strong biometrics required',
                '30': 'Android 11 - Enhanced biometrics',
                '31': 'Android 12 - More secure',
            }
            
            if sdk in biometric_versions:
                print(f"Biometric features: {biometric_versions[sdk]}")
        
        print("\n📊 Security Assessment:")
        print("  High: Android 9.0+ with BiometricPrompt")
        print("  Medium: Android 7.0-8.1")
        print("  Low: Android 6.0 or custom ROMs")
    
    def create_fake_fingerprint(self):
        """Demonstration of fingerprint spoofing concepts"""
        print("\n⚠️  FINGERPRINT SPOOFING (EDUCATIONAL)")
        print("This demonstrates concepts only!")
        
        print("\nHow fingerprint systems work:")
        print("1. Sensor captures fingerprint image")
        print("2. Extracts minutiae points (ridges/valleys)")
        print("3. Creates mathematical template")
        print("4. Compares with stored templates")
        
        print("\nPotential vulnerabilities:")
        print("1. Fake fingerprints (gelatin, latex)")
        print("2. Latent fingerprints (on screen)")
        print("3. Sensor spoofing (electrical signals)")
        print("4. Template database access")
        
        print("\n⚠️  LEGAL NOTE:")
        print("Creating fake fingerprints without authorization is:")
        print("- Illegal in most countries")
        print("- Considered identity theft")
        print("- Can carry severe penalties")
        
        print("\n✅ LEGAL alternatives:")
        print("1. Use backup PIN/password")
        print("2. Factory reset with proof of ownership")
        print("3. Manufacturer service center")
        
        return False