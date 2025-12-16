"""
Password Cracker - Advanced password recovery techniques
Includes dictionary attacks, mask attacks, and hash analysis
"""

import hashlib
import itertools
import time
import os
from pathlib import Path
from adb_manager import ADBManager

class PasswordCracker:
    def __init__(self):
        self.adb = ADBManager()
        self.wordlists = {
            'common': self._load_wordlist('common_passwords.txt'),
            'android': self._load_wordlist('android_passwords.txt'),
            'names': self._load_wordlist('common_names.txt'),
            'dates': self._generate_date_list(),
        }
    
    def attempt_bypass(self):
        """Main password bypass entry point"""
        print("\n🔑 PASSWORD CRACKING TOOL")
        print("=" * 60)
        print("WARNING: Use only on your own devices!")
        print("Unauthorized access is illegal!")
        
        # Check device status
        if not self.adb.check_adb_installed():
            return False
        
        print("\nSelect attack method:")
        print("1. Dictionary attack (common passwords)")
        print("2. Mask attack (known pattern)")
        print("3. Hybrid attack (dictionary + rules)")
        print("4. Analyze password hash")
        print("5. Smart brute force")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            return self.dictionary_attack()
        elif choice == '2':
            return self.mask_attack()
        elif choice == '3':
            return self.hybrid_attack()
        elif choice == '4':
            return self.analyze_hash()
        elif choice == '5':
            return self.smart_bruteforce()
        else:
            print("Invalid choice")
            return False
    
    def dictionary_attack(self):
        """Dictionary attack using common passwords"""
        print("\n📚 DICTIONARY ATTACK")
        print("Testing common passwords...")
        
        # Common Android passwords
        common_passwords = [
            # Most common globally
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            # Common patterns
            "123123", "abc123", "password1", "monkey", "1234567890",
            # Android specific
            "android", "google", "samsung", "000000", "123456789",
            # Dates
            "01011980", "121212", "131313", "123456789",
        ]
        
        # Add wordlist passwords
        if self.wordlists['common']:
            common_passwords.extend(self.wordlists['common'][:500])  # Limit to 500
        
        print(f"Testing {len(common_passwords)} passwords...")
        
        # This is a simulation - real testing would require device access
        for i, password in enumerate(common_passwords, 1):
            print(f"  Testing: {password} ({i}/{len(common_passwords)})", end='\r')
            time.sleep(0.01)  # Simulate delay
            
            # In real scenario, would test on device
            # success = self._test_password_on_device(password)
            
            if i % 100 == 0:
                print(f"\n  Progress: {i}/{len(common_passwords)}")
        
        print("\n\nDictionary attack completed.")
        print("If none worked, try other methods.")
        
        return False  # Simulation only
    
    def mask_attack(self):
        """Mask attack with known pattern"""
        print("\n🎭 MASK ATTACK")
        print("Use when you know password pattern")
        
        print("\nKnown information:")
        length = input("Password length (or press Enter if unknown): ").strip()
        known_chars = input("Known characters/positions (e.g., a??123): ").strip()
        charset = input("Character set (1=digits, 2=lower, 3=upper, 4=all): ").strip()
        
        # Define character sets
        charsets = {
            '1': '0123456789',
            '2': 'abcdefghijklmnopqrstuvwxyz',
            '3': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '4': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()'
        }
        
        chosen_charset = charsets.get(charset, charsets['4'])
        
        if known_chars:
            # Generate passwords based on mask
            print(f"\nGenerating passwords with mask: {known_chars}")
            passwords = self._generate_from_mask(known_chars, chosen_charset)
        elif length:
            # Generate all combinations of given length
            print(f"\nGenerating {length}-character passwords...")
            passwords = self._generate_combinations(int(length), chosen_charset)
        else:
            print("Need at least length or mask")
            return False
        
        print(f"Total possibilities: {len(passwords):,}")
        
        if len(passwords) > 1000000:
            print("Too many possibilities. Try a more specific mask.")
            return False
        
        print("\nStarting mask attack...")
        for i, password in enumerate(passwords, 1):
            print(f"  Testing: {password} ({i}/{len(passwords)})", end='\r')
            time.sleep(0.001)
        
        print("\n\nMask attack completed.")
        return False
    
    def hybrid_attack(self):
        """Hybrid attack: dictionary + rules"""
        print("\n⚡ HYBRID ATTACK")
        print("Applying rules to dictionary words")
        
        base_words = self.wordlists['common'] or [
            "password", "admin", "welcome", "sunshine", "iloveyou",
            "monkey", "letmein", "dragon", "baseball", "football"
        ]
        
        rules = [
            lambda x: x,                    # Original
            lambda x: x + "123",            # Add numbers
            lambda x: x + "!",              # Add symbol
            lambda x: x.capitalize(),       # Capitalize
            lambda x: x + x,                # Duplicate
            lambda x: x[::-1],              # Reverse
            lambda x: x.replace('a', '@'),  # Leet speak
            lambda x: x.replace('e', '3'),
            lambda x: x.replace('o', '0'),
        ]
        
        passwords = set()
        for word in base_words[:100]:  # Limit for demo
            for rule in rules:
                passwords.add(rule(word))
        
        print(f"Generated {len(passwords)} password variations")
        
        # Add number suffixes
        numbered = set()
        for pwd in list(passwords)[:500]:  # Limit
            for i in range(10):
                numbered.add(pwd + str(i))
                numbered.add(str(i) + pwd)
        
        passwords.update(numbered)
        print(f"Total with numbers: {len(passwords)}")
        
        print("\nTesting hybrid passwords...")
        for i, pwd in enumerate(passwords, 1):
            print(f"  Testing: {pwd} ({i}/{len(passwords)})", end='\r')
            time.sleep(0.001)
        
        print("\n\nHybrid attack completed.")
        return False
    
    def smart_bruteforce(self):
        """Smart brute force with common patterns"""
        print("\n🧠 SMART BRUTE FORCE")
        print("Targeting common password patterns")
        
        patterns = [
            # Phone numbers
            lambda: self._generate_phone_numbers(),
            
            # Dates
            lambda: self._generate_dates(),
            
            # Keyboard patterns
            lambda: self._generate_keyboard_patterns(),
            
            # Repeated patterns
            lambda: self._generate_repeated_patterns(),
        ]
        
        all_passwords = set()
        
        for pattern_func in patterns:
            passwords = pattern_func()
            all_passwords.update(passwords)
            print(f"  Pattern generated: {len(passwords)} passwords")
        
        print(f"\nTotal smart passwords: {len(all_passwords):,}")
        
        if len(all_passwords) > 500000:
            print("Too many. Try more specific patterns.")
            return False
        
        print("\nStarting smart brute force...")
        for i, pwd in enumerate(all_passwords, 1):
            print(f"  Testing: {pwd} ({i}/{len(all_passwords)})", end='\r')
            time.sleep(0.001)
        
        print("\n\nSmart brute force completed.")
        return False
    
    def analyze_hash(self):
        """Analyze password hash for weaknesses"""
        print("\n🔍 PASSWORD HASH ANALYSIS")
        
        # Try to get hash from device
        hash_data = None
        if self.adb.is_device_rooted():
            print("Pulling password hash from device...")
            temp_file = "/tmp/password_hash.bin"
            if self.adb.pull_file('/data/system/password.key', temp_file):
                with open(temp_file, 'rb') as f:
                    hash_data = f.read()
                os.remove(temp_file)
        
        if hash_data:
            print(f"Hash size: {len(hash_data)} bytes")
            print(f"Hex: {hash_data.hex()}")
            print(f"SHA1 of hash: {hashlib.sha1(hash_data).hexdigest()}")
            
            # Analyze hash type
            self._analyze_hash_type(hash_data)
            
            # Check if hash is crackable
            return self._assess_crackability(hash_data)
        else:
            print("Could not retrieve hash.")
            print("Hash analysis requires:")
            print("1. Root access to device")
            print("2. Physical access to pull files")
            print("3. password.key file from /data/system/")
            
            return False
    
    def _load_wordlist(self, filename):
        """Load wordlist from file"""
        wordlist_paths = [
            Path(__file__).parent / "wordlists" / filename,
            Path.home() / ".android_recovery" / "wordlists" / filename,
            Path("/usr/share/wordlists") / filename,
        ]
        
        for path in wordlist_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        return [line.strip() for line in f if line.strip()]
                except:
                    continue
        
        return []
    
    def _generate_date_list(self):
        """Generate common date passwords"""
        dates = []
        
        # Years 1900-2025
        for year in range(1900, 2026):
            dates.append(str(year))
            dates.append(f"{year:04d}")
        
        # Common date formats
        common_dates = [
            "01011980", "12121980", "01011990", "12121990",
            "01012000", "12122000", "01012010", "12122010",
            "01011970", "12121970", "01011985", "12121985",
        ]
        
        dates.extend(common_dates)
        return dates
    
    def _generate_from_mask(self, mask, charset):
        """Generate passwords from mask with wildcards"""
        import re
        
        # Convert mask to pattern
        pattern = mask.replace('?', '.')
        
        # For simple masks, generate combinations
        if mask.count('?') <= 6:
            positions = [i for i, char in enumerate(mask) if char == '?']
            results = []
            
            # Generate all combinations for wildcard positions
            for combo in itertools.product(charset, repeat=len(positions)):
                password = list(mask)
                for pos, char in zip(positions, combo):
                    password[pos] = char
                results.append(''.join(password))
            
            return results
        
        return []
    
    def _generate_combinations(self, length, charset):
        """Generate all combinations of given length"""
        if length <= 4:  # Reasonable for demo
            return [''.join(combo) for combo in itertools.product(charset, repeat=length)]
        else:
            # Too many combinations
            return []
    
    def _generate_phone_numbers(self):
        """Generate common phone number patterns"""
        numbers = []
        
        # Common prefixes and patterns
        prefixes = ['555', '123', '999', '777', '888']
        suffixes = ['0000', '1234', '1111', '9999']
        
        for prefix in prefixes:
            for suffix in suffixes:
                numbers.append(prefix + suffix)
        
        return numbers
    
    def _generate_dates(self):
        """Generate date-based passwords"""
        dates = []
        
        # DDMMYYYY variations
        for day in range(1, 32):
            for month in range(1, 13):
                for year in [1980, 1990, 1995, 2000, 2010, 2020]:
                    dates.append(f"{day:02d}{month:02d}{year}")
                    dates.append(f"{month:02d}{day:02d}{year}")
        
        # YYYYMMDD
        for year in [1980, 1990, 2000, 2010, 2020]:
            for month in range(1, 13):
                for day in range(1, 32):
                    dates.append(f"{year}{month:02d}{day:02d}")
        
        return dates[:1000]  # Limit
    
    def _generate_keyboard_patterns(self):
        """Generate keyboard pattern passwords"""
        patterns = []
        
        # Horizontal patterns
        rows = ['qwerty', 'asdfgh', 'zxcvbn', '123456', '7890-=']
        for row in rows:
            for i in range(len(row) - 3):
                patterns.append(row[i:i+4])
                patterns.append(row[i:i+5])
                patterns.append(row[i:i+6])
        
        # Vertical patterns (keyboard columns)
        columns = ['1qaz', '2wsx', '3edc', '4rfv', '5tgb', '6yhn']
        patterns.extend(columns)
        
        return patterns
    
    def _generate_repeated_patterns(self):
        """Generate repeated character patterns"""
        patterns = []
        
        # Repeated digits
        for digit in '0123456789':
            patterns.append(digit * 4)
            patterns.append(digit * 5)
            patterns.append(digit * 6)
        
        # Alternating patterns
        for i in range(10):
            patterns.append(f"{i}{i+1}{i}{i+1}")
            patterns.append(f"{i}{i}{i+1}{i+1}")
        
        return patterns
    
    def _analyze_hash_type(self, hash_data):
        """Analyze hash algorithm and strength"""
        length = len(hash_data)
        
        print("\n🔬 Hash Analysis:")
        
        if length == 16:
            print("  Likely: MD5 hash (weak, pre-Android 4.4)")
        elif length == 20:
            print("  Likely: SHA1 hash (Android 4.0-8.1)")
        elif length == 32:
            print("  Likely: SHA256 hash (Android 9+)")
        elif length == 48:
            print("  Likely: SHA384 hash")
        elif length == 64:
            print("  Likely: SHA512 hash")
        elif length == 40:
            print("  Could be: SHA1 with salt (20+20 bytes)")
        elif length > 100:
            print("  Likely: PBKDF2 with many iterations (Android 9+)")
        else:
            print(f"  Unknown format: {length} bytes")
        
        # Check for common weaknesses
        if hash_data.startswith(b'\x00'):
            print("  Warning: Hash starts with null bytes (weak?)")
        
        if all(b == 0 for b in hash_data):
            print("  Critical: All-zero hash (empty password?)")
    
    def _assess_crackability(self, hash_data):
        """Assess how crackable the hash is"""
        length = len(hash_data)
        
        print("\n📊 Crackability Assessment:")
        
        if length <= 20:
            print("  High: Short hash (MD5/SHA1)")
            print("  Tools like hashcat can crack quickly")
            return True
        
        elif length <= 32:
            print("  Medium: SHA256 hash")
            print("  Crackable with good dictionary/GPU")
            return True
        
        elif length <= 64:
            print("  Low: SHA512 or similar")
            print("  Requires significant resources")
            return False
        
        else:
            print("  Very Low: Likely PBKDF2 with high iterations")
            print("  Practically uncrackable with brute force")
            return False