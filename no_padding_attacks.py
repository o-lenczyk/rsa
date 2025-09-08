import random
import math
import time
from rsa_from_scratch import getUnsafePrime, generate_keypair, encrypt, decrypt, gcd, mod_inverse

def textbook_encrypt(pk, plaintext):
    """Textbook RSA encryption - no padding"""
    e, n = pk
    # Convert each letter to its ASCII value and encrypt
    cipher = [pow(ord(char), e, n) for char in plaintext]
    return cipher

def textbook_decrypt(pk, ciphertext):
    """Textbook RSA decryption - no padding"""
    d, n = pk
    plain = [chr(pow(char, d, n)) for char in ciphertext]
    return ''.join(plain)

def attack_low_exponent(ciphertext, e, n):
    """
    Low exponent attack: If e=3 and message is small, recover m = c^(1/3)
    """
    if e != 3:
        return None

    for c in ciphertext:
        m = round(c ** (1/3))
        if m ** 3 == c:
            return chr(m)
    return None

def attack_homomorphic(c1, c2, e, n):
    """
    Homomorphic attack: If you have Enc(m1) and Enc(m2),
    then Enc(m1*m2) = Enc(m1) * Enc(m2) mod n
    """
    c_combined = (c1 * c2) % n

    return c_combined

def attack_short_message(ciphertext, n, max_range=10000):
    """
    Short message attack: For very short messages, brute force is feasible
    """
    for possible_m in range(max_range):
        c_test = pow(possible_m, 3, n)  # Assuming e=3
        if c_test in ciphertext:
            return possible_m  # Return numeric value
    return None

def demonstrate_vulnerabilities_for_bits(bits):
    """Run attack demonstration for a specific key size"""
    print(f"\n{'='*60}")
    print(f"TESTING {bits}-bit primes → {bits*2}-bit RSA key")
    print(f"{'='*60}")

    demo_start_time = time.time()

    # Generate vulnerable keypair
    print("1. Generating vulnerable RSA keypair (e=3 for low exponent attack)...")
    print(f"Using {bits}-bit primes (creates {bits*2}-bit RSA key)")
    print(f"Even {bits*2}-bit 'secure' keys don't protect textbook RSA!")

    keygen_start = time.time()
    p = getUnsafePrime(bits)
    q = getUnsafePrime(bits)
    public, private = generate_keypair(p, q)
    keygen_time = time.time() - keygen_start

    e, n = public
    d, _ = private

    # Force e=3 for demonstration
    e = 3
    public = (e, n)
    print(f"Public key: (e={e}, n={n})")
    print(f"Private key: (d={d}, n={n})")
    print(f"Key generation time: {keygen_time:.4f} seconds")
    print()

    # Test messages (bank account example)
    m1, m2 = 500, 300  # Two bank balances
    print(f"2. Original messages: Bank balances ${m1} and ${m2}")
    print(f"   Combined balance: ${m1 + m2}")
    print(f"   Product: ${m1 * m2}")
    print()

    # Encrypt the numeric values directly
    encrypt_start = time.time()
    c1 = pow(m1, e, n)  # Encrypt $500
    c2 = pow(m2, e, n)  # Encrypt $300
    ciphertext = [c1, c2]
    encrypt_time = time.time() - encrypt_start
    print(f"3. Encrypted messages: {ciphertext}")
    print(f"Encryption time: {encrypt_time:.6f} seconds")
    print()

    # Demonstrate low exponent attack
    print("4. LOW EXPONENT ATTACK (e=3):")
    attack1_start = time.time()
    recovered_values = []
    for i, c in enumerate(ciphertext):
        # Try to recover the original value
        m_recovered = round(c ** (1/3))
        if m_recovered ** 3 == c:
            recovered_values.append(m_recovered)
            print(f"   Recovered value from C{i+1}: ${m_recovered}")
        else:
            print(f"   Could not recover from C{i+1} (value too large)")

    # Check if we recovered the correct values
    attack1_success = (len(recovered_values) == 2 and
                      recovered_values[0] == m1 and
                      recovered_values[1] == m2)
    attack1_time = time.time() - attack1_start
    print(f"   Expected: ${m1} and ${m2}")
    print(f"   Attack successful: {attack1_success}")
    print(f"   Low exponent attack time: {attack1_time:.6f} seconds")
    print()

    print("5. HOMOMORPHIC ATTACK:")
    attack2_start = time.time()
    homomorphic_demo = False
    if len(ciphertext) >= 2:
        c1, c2 = ciphertext[0], ciphertext[1]
        c_combined = attack_homomorphic(c1, c2, e, n)
        print(f"   C1 = {c1} (encrypts ${m1})")
        print(f"   C2 = {c2} (encrypts ${m2})")
        print(f"   C1 * C2 mod n = {c_combined}")
        print("   This encrypts the product of the original messages!")
        print(f"   If decrypted with private key, would get: ${m1 * m2}")
        print(f"   (Individual values remain unknown)")
        homomorphic_demo = True
    attack2_time = time.time() - attack2_start
    print(f"   Homomorphic attack time: {attack2_time:.6f} seconds")
    print()

    print("6. SHORT MESSAGE ATTACK:")
    attack3_start = time.time()
    recovered_count = 0
    for i, c in enumerate(ciphertext):
        recovered = attack_short_message([c], n)
        if recovered is not None:
            expected = [m1, m2][i]
            print(f"   Brute force recovered: ${recovered} from {c}")
            if recovered == expected:
                recovered_count += 1
        else:
            print(f"   Could not brute force {c}")
    attack3_success = recovered_count == len(ciphertext)
    attack3_time = time.time() - attack3_start
    print(f"   Short message attack time: {attack3_time:.6f} seconds")
    print()

    total_time = time.time() - demo_start_time

    print("=== PERFORMANCE SUMMARY ===")
    print(f"Total demonstration time: {total_time:.4f} seconds")
    print(f"Key generation: {keygen_time:.6f} seconds ({keygen_time/total_time*100:.1f}%)")
    print(f"Encryption: {encrypt_time:.6f} seconds ({encrypt_time/total_time*100:.1f}%)")
    print(f"Low exponent attack: {attack1_time:.6f} seconds ({attack1_time/total_time*100:.1f}%)")
    print(f"Homomorphic attack: {attack2_time:.6f} seconds ({attack2_time/total_time*100:.1f}%)")
    print(f"Short message attack: {attack3_time:.6f} seconds ({attack3_time/total_time*100:.1f}%)")
    print()

    print("=== CONCLUSION ===")
    print(f"Textbook RSA with {bits*2}-bit keys is vulnerable to:")
    print("- Low exponent attacks (when e is small)")
    print("- Homomorphic attacks (mathematical relationships preserved)")
    print("- Brute force attacks (for short messages)")
    print("- Deterministic encryption (same message = same ciphertext)")
    print("\nThese vulnerabilities are prevented by proper padding schemes")

    # Return results for summary table
    return {
        'bits': bits,
        'rsa_bits': bits * 2,
        'keygen_time': keygen_time,
        'encrypt_time': encrypt_time,
        'attack1_time': attack1_time,
        'attack1_success': attack1_success,
        'attack2_time': attack2_time,
        'attack2_demo': homomorphic_demo,
        'attack3_time': attack3_time,
        'attack3_success': attack3_success,
        'total_time': total_time
    }

def demonstrate_vulnerabilities():
    print("=== RSA Textbook Vulnerabilities Demonstration ===\n")

    total_start_time = time.time()

    # Generate vulnerable keypair (large to prove key size doesn't help)
    print("1. Generating vulnerable RSA keypair (e=3 for low exponent attack)...")
    bits = 1024  # 1024-bit primes → 2048-bit RSA key
    print(f"Using {bits}-bit primes (creates {bits*2}-bit RSA key)")
    print(f"Even {bits*2}-bit 'secure' keys don't protect textbook RSA")

    keygen_start = time.time()
    p = getUnsafePrime(bits)
    q = getUnsafePrime(bits)
    public, private = generate_keypair(p, q)
    keygen_time = time.time() - keygen_start

    e, n = public
    d, _ = private

    # Force e=3 for demonstration
    e = 3
    public = (e, n)
    print(f"Public key: (e={e}, n={n})")
    print(f"Private key: (d={d}, n={n})")
    print(f"Key generation time: {keygen_time:.4f} seconds")
    print()

    # Test message
    message = "hi"
    print(f"2. Original message: '{message}'")
    print(f"   ASCII values: {[ord(c) for c in message]}")
    print()

    # Encrypt
    encrypt_start = time.time()
    ciphertext = textbook_encrypt(public, message)
    encrypt_time = time.time() - encrypt_start
    print(f"3. Encrypted message: {ciphertext}")
    print(f"Encryption time: {encrypt_time:.6f} seconds")
    print()

    # Demonstrate low exponent attack
    print("4. LOW EXPONENT ATTACK (e=3):")
    attack1_start = time.time()
    recovered_chars = []
    for c in ciphertext:
        recovered = attack_low_exponent([c], e, n)
        if recovered:
            recovered_chars.append(recovered)
            print(f"   Recovered character from {c}: '{recovered}'")
        else:
            print(f"   Could not recover from {c}")

    recovered_message = ''.join(recovered_chars)
    attack1_time = time.time() - attack1_start
    print(f"   Recovered message: '{recovered_message}'")
    print(f"   Attack successful: {recovered_message == message}")
    print(f"   Low exponent attack time: {attack1_time:.6f} seconds")
    print()

    # Demonstrate homomorphic properties
    print("5. HOMOMORPHIC ATTACK:")
    attack2_start = time.time()
    if len(ciphertext) >= 2:
        c1, c2 = ciphertext[0], ciphertext[1]
        c_combined = attack_homomorphic(c1, c2, e, n)
        print(f"   C1 = {c1} (encrypts '{message[0]}')")
        print(f"   C2 = {c2} (encrypts '{message[1]}')")
        print(f"   C1 * C2 mod n = {c_combined}")
        print("   This encrypts the product of the original messages!")
        print("   If decrypted with private key, would get:", ord(message[0]) * ord(message[1]))
    attack2_time = time.time() - attack2_start
    print(f"   Homomorphic attack time: {attack2_time:.6f} seconds")
    print()

    # Demonstrate short message attack
    print("6. SHORT MESSAGE ATTACK:")
    attack3_start = time.time()
    recovered_chars = []
    for i, c in enumerate(ciphertext):
        recovered = attack_short_message([c], n)
        if recovered is not None:
            char = chr(recovered)
            expected = message[i]
            print(f"   Brute force recovered: '{char}' from {c}")
            if char == expected:
                recovered_chars.append(char)
        else:
            print(f"   Could not brute force {c}")
    recovered_message_brute = ''.join(recovered_chars)
    attack3_success = recovered_message_brute == message
    attack3_time = time.time() - attack3_start
    print(f"   Recovered message: '{recovered_message_brute}'")
    print(f"   Attack successful: {attack3_success}")
    print(f"   Short message attack time: {attack3_time:.6f} seconds")
    print()

    total_time = time.time() - total_start_time

    print("=== PERFORMANCE SUMMARY ===")
    print(f"Total demonstration time: {total_time:.4f} seconds")
    print(f"Key generation: {keygen_time:.6f} seconds ({keygen_time/total_time*100:.1f}%)")
    print(f"Encryption: {encrypt_time:.6f} seconds ({encrypt_time/total_time*100:.1f}%)")
    print(f"Low exponent attack: {attack1_time:.6f} seconds ({attack1_time/total_time*100:.1f}%)")
    print(f"Homomorphic attack: {attack2_time:.6f} seconds ({attack2_time/total_time*100:.1f}%)")
    print(f"Short message attack: {attack3_time:.6f} seconds ({attack3_time/total_time*100:.1f}%)")
    print()

    print("=== CONCLUSION ===")
    print("Textbook RSA is vulnerable to:")
    print("- Low exponent attacks (when e is small)")
    print("- Homomorphic attacks (mathematical relationships preserved)")
    print("- Brute force attacks (for short messages)")
    print("- Deterministic encryption (same message = same ciphertext)")
    print("\nThese vulnerabilities are prevented by proper padding schemes!")

if __name__ == '__main__':
    print("=== MULTI-KEY-SIZE RSA VULNERABILITY TEST ===")
    print("Testing textbook RSA attacks across different key sizes\n")

    key_sizes = [512, 1024, 2048]  # Test different key sizes
    results = []

    for bits in key_sizes:
        try:
            result = demonstrate_vulnerabilities_for_bits(bits)
            results.append(result)
        except KeyboardInterrupt:
            print(f"\nSkipping {bits}-bit test due to timeout...")
            continue
        except Exception as e:
            print(f"\nError testing {bits}-bit keys: {e}")
            continue

    # Display summary table
    print("\n" + "="*120)
    print("SUMMARY TABLE: RSA Textbook Vulnerabilities Across Key Sizes")
    print("="*120)
    print(f"{'Key Size':<12} {'RSA Bits':<10} {'Key Gen':<10} {'Encrypt':<10} {'Low Exp':<10} {'Success':<8} {'Homom':<8} {'Success':<8} {'Brute':<8} {'Success':<8} {'Total':<10}")
    print(f"{'(primes)':<12} {'(modulus)':<10} {'Time':<10} {'Time':<10} {'Attack':<10} {'(Low)':<8} {'Attack':<8} {'(Homom)':<8} {'Attack':<8} {'(Brute)':<8} {'Time':<10}")
    print("-" * 120)

    for result in results:
        print(f"{result['bits']:<12} {result['rsa_bits']:<10} "
              f"{result['keygen_time']:<10.4f} {result['encrypt_time']:<10.6f} "
              f"{result['attack1_time']:<10.6f} {str(result['attack1_success']):<8} "
              f"{result['attack2_time']:<8.6f} {str(result['attack2_demo']):<8} "
              f"{result['attack3_time']:<8.6f} {str(result['attack3_success']):<8} "
              f"{result['total_time']:<10.4f}")

    print("-" * 120)
    print(f"{'TOTALS':<12} {'':<10} "
          f"{sum(r['keygen_time'] for r in results):<10.4f} "
          f"{sum(r['encrypt_time'] for r in results):<10.6f} "
          f"{sum(r['attack1_time'] for r in results):<10.6f} {'':<8} "
          f"{sum(r['attack2_time'] for r in results):<8.6f} {'':<8} "
          f"{sum(r['attack3_time'] for r in results):<8.6f} {'':<8} "
          f"{sum(r['total_time'] for r in results):<10.4f}")

    print("\n" + "="*120)
    print("FINAL CONCLUSION:")
    print("Regardless of key size (512, 1024, or 2048-bit RSA keys),")
    print("textbook RSA remains vulnerable to the demonstrated attacks.")
    print("This proves that PROPER PADDING is essential for RSA security,")
    print("not just larger key sizes!")
    print("="*120)
