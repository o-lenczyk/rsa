import random
import subprocess
import re
from Crypto.Util.number import getPrime as crypto_getPrime, isPrime

def isPrime(n):
    """
    Custom primality test using trial division with small primes.
    For larger numbers, this is probabilistic but good enough for our purposes.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Use small primes for trial division
    small_primes = get_small_primes(min(10000, int(n**0.5) + 1))
    for prime in small_primes:
        if prime * prime > n:
            break
        if n % prime == 0:
            return False

    # For larger numbers, do additional checks
    i = small_primes[-1] + 2 if small_primes else 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True

def crypto_getPrime(bits):
    """
    Custom prime generation - generates a random prime of specified bit length.
    """
    while True:
        # Generate random odd number of correct bit length
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1  # Ensure correct bit length and odd

        if isPrime(candidate):
            return candidate

def get_small_primes(limit):
    primes = []
    sieve = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if sieve[p]:
            primes.append(p)
            for i in range(p * p, limit + 1, p):
                sieve[i] = False
    return primes

def factor_with_yafu(n):
    """
    Factors a number n using the YAFU command-line tool.
    Returns a dictionary of prime factors and their exponents, similar to sympy.factorint.
    """
    try:
        command = f'yafu "factor({n})"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"YAFU exited with an error: {result.stderr}")
            return None

        # YAFU prints factors in the format PXX = ...
        # We look for these lines to extract the prime factors.
        # It also prints factors in the format C = p1 * p2 * ...
        factors_raw = re.findall(r'(?:P\d+|C) = (\d+)', result.stdout)
        
        factors_dict = {}
        for f_str in factors_raw:
            factor = int(f_str)
            # YAFU might return composite factors if it can't fully factor.
            # For our purpose, we need prime factors.
            # We'll assume YAFU returns prime factors for smooth numbers.
            # If n is large and YAFU returns a composite, this logic might need refinement.
            if factor > 1:
                factors_dict[factor] = factors_dict.get(factor, 0) + 1
        
        # If YAFU returns a single factor that is n itself, it means it couldn't factor it.
        if len(factors_dict) == 1 and list(factors_dict.keys())[0] == n:
            return {} # Return empty dict if not factored
            
        return factors_dict

    except FileNotFoundError:
        print("YAFU command not found. Please ensure it is installed and in your system's PATH.")
        return None
    except subprocess.TimeoutExpired:
        print("YAFU took too long to execute and was terminated.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running YAFU: {e}")
        return None

def getPrime(bits):
    """
    Generates a safe prime p of 'bits' length.
    A safe prime is a prime p where (p-1)/2 is also prime.
    This makes p-1 have a large prime factor, protecting against Pollard's p-1 attack.
    """
    while True:
        # Generate a random prime q of (bits-1) length
        q = crypto_getPrime(bits - 1)
        # Compute p = 2*q + 1
        p = 2 * q + 1
        # Check if p is prime and has correct bit length
        if isPrime(p) and p.bit_length() == bits:
            print(f"Generated safe prime p = {p}")
            print(f"(p-1)/2 = {q} (also prime)")
            return p

def getUnsafePrime(bits):
    """
    Generates a regular prime p of 'bits' length (not necessarily safe).
    This is vulnerable to Pollard's p-1 attack if p-1 is smooth.
    """
    return crypto_getPrime(bits)

def getPrimeSmooth(bits, max_attempts_per_bound=10000):
    """
    Generates a prime p of 'bits' length, such that p-1 is B-smooth.
    Starts with a dynamic smoothness bound based on bit size and increases it if it fails to find a prime.
    """
    # Dynamically calculate a reasonable starting bound.
    # This is a heuristic; a larger bit size needs a larger pool of small primes to succeed in a reasonable time.
    initial_smoothness_bound = bits * 4
    print(f"Dynamically setting initial smoothness bound to {initial_smoothness_bound} for {bits}-bit prime.")
    
    smoothness_bound = initial_smoothness_bound
    while True:
        small_primes = get_small_primes(smoothness_bound)
        
        for _ in range(max_attempts_per_bound):
            p_minus_1 = 2
            
            target_lower = 1 << (bits - 1)
            
            # Build p-1 by multiplying random small primes
            while p_minus_1.bit_length() < bits:
                p_minus_1 *= random.choice(small_primes)
                
            # We might have overshot the bit length, so we can try to adjust
            # This part is tricky, a simpler way is just to check if p is of the right bit length
            
            p = p_minus_1 + 1
            
            if p.bit_length() == bits and isPrime(p):
                print(f"Found prime with smoothness bound: {smoothness_bound}")
                
                # Use YAFU for factorization
                factors = factor_with_yafu(p-1)
                if not factors: # YAFU failed to factor or returned empty
                    print(f"  --- YAFU failed to factor p-1. Retrying...")
                    continue

                print(f"  p = {p}")
                print(f"  Factors of p-1: {factors}")
                
                # Ensure factors.keys() is not empty before calling max()
                if not factors.keys():
                    print(f"  --- Prime rejected: No prime factors found for p-1. Retrying...")
                    continue

                max_factor = max(factors.keys())
                print(f"  Max prime factor of p-1 is: {max_factor}")
                
                # This is the crucial fix: check the largest prime POWER, not just the largest prime.
                max_prime_power = max(q**k for q, k in factors.items())
                print(f"  Max prime POWER of p-1 is: {max_prime_power}")

                # We need the max prime power to be crackable by our iterative attack.
                # The attack stops at 200000, so we must generate a prime that respects this.
                # Increasing this threshold to speed up prime generation for larger bit sizes.
                if max_prime_power > 20000000: # Increased from 200,000 to 20,000,000
                    print(f"  --- Prime rejected: Max prime power {max_prime_power} is too large to be cracked quickly. Retrying...")
                    continue # Reject this prime and try to generate another one.

                if max_factor > smoothness_bound:
                    print(f"  *** WARNING: Max factor {max_factor} > smoothness bound {smoothness_bound}. This is a bug!")
                return p
        
        # If we failed to find a prime, increase the smoothness bound and try again.
        smoothness_bound *= 2
        print(f"Could not find prime with bound {smoothness_bound//2}, increasing smoothness bound to {smoothness_bound}")

def gcd(candidate_exponent, totient_phi):
    """
    Euclidean algorithm to find the greatest common divisor of candidate_exponent and totient_phi.
    """
    while totient_phi != 0:
        candidate_exponent, totient_phi = totient_phi, candidate_exponent % totient_phi
    return candidate_exponent

def mod_inverse(encryption_exponent_e, totient_phi):
    """
    Extended Euclidean algorithm to find the modular inverse of encryption_exponent_e under totient_phi.
    """
    m0, x0, x1 = totient_phi, 0, 1
    if totient_phi == 1:
        return 0
    while encryption_exponent_e > 1:
        q = encryption_exponent_e // totient_phi
        totient_phi, encryption_exponent_e = encryption_exponent_e % totient_phi, totient_phi
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def generate_keypair(p, q):
    """
    Generate a public/private key pair from primes p and q.
    """
    if p == q:
        raise ValueError('p and q cannot be equal.')
    
    n = p * q
    phi = (p-1) * (q-1)
    
    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)
    
    # Use Euclid's Algorithm to verify that e and phi(n) are coprime
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)
        
    # Use Extended Euclidean Algorithm to generate the private key
    d = mod_inverse(e, phi)
    
    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))

def encrypt(pk, plaintext):
    # Unpack the key into it's components
    e, n = pk
    # Convert each letter in the plaintext to numbers based on the character using a^b mod m
    cipher = [pow(ord(char), e, n) for char in plaintext]
    # Return the array of bytes
    return cipher

def decrypt(pk, ciphertext):
    # Unpack the key into its components
    d, n = pk
    # Generate the plaintext based on the ciphertext and key using a^b mod m
    plain = [chr(pow(char, d, n)) for char in ciphertext]
    # Return the array of bytes as a string
    return ''.join(plain)

if __name__ == '__main__':
    print("RSA Encrypter/ Decrypter")

    choice = input("Choose an option: (1) Encrypt/Decrypt a new message (secure with safe primes), (2) Decrypt a message with a key, or (3) Generate keys with smooth primes for testing Pollard's p-1: ")

    if choice == '1':
        try:
            bits = int(input("Enter bit size for p and q (e.g., 8, 16, 32, 64): "))
        except ValueError:
            print("Invalid bit size. Using default 64 bits.")
            bits = 64

        print("Generating secure primes (this might take a while)...")
        p = getPrime(bits)
        q = getPrime(bits)
        
        public, private = generate_keypair(p, q)
        
        print("Your public key is ", public ," and your private key is ", private)
        
        message = input("Enter a message to encrypt with your public key: ")
        encrypted_msg = encrypt(public, message)
        
        print("Your encrypted message is: ")
        print(' '.join(map(str, encrypted_msg)))
        
        print("Decrypting message with private key ", private ," . . .")
        print("Your message is:")
        print(decrypt(private, encrypted_msg))

    elif choice == '2':
        private_key_str = input("Enter your private key (d, n): ")
        try:
            private = eval(private_key_str)
            if not (isinstance(private, tuple) and len(private) == 2 and all(isinstance(i, int) for i in private)):
                raise ValueError
        except (ValueError, SyntaxError):
            print("Invalid private key format. Please enter as a tuple, e.g., (123, 456)")
            exit()

        try:
            encrypted_msg_str = input("Enter the encrypted message (numbers separated by spaces): ")
            encrypted_msg = [int(x) for x in encrypted_msg_str.split()]
        except ValueError:
            print("Invalid encrypted message format. Please enter numbers separated by spaces.")
            exit()

        print("Decrypting message...")
        decrypted_msg = decrypt(private, encrypted_msg)
        print("Your decrypted message is:")
        print(decrypted_msg)

    elif choice == '3':
        try:
            bits = int(input("Enter bit size for p and q (e.g., 8, 16, 32, 64): "))
        except ValueError:
            print("Invalid bit size. Using default 64 bits.")
            bits = 64
            
        print("Generating p (this might take a while)...")
        p = getPrimeSmooth(bits)
        print("Generating q (this might take a while)...")
        q = getPrimeSmooth(bits)
        
        # Ensure p and q are not the same
        while p == q:
            print("p and q were the same, regenerating q...")
            q = getPrimeSmooth(bits)

        print(f"\nGenerated Primes (vulnerable to Pollard's p-1):")
        print(f"p = {p}")
        print(f"q = {q}")
        
        public, private = generate_keypair(p, q)
        
        print("\nYour public key is ", public ," and your private key is ", private)
        
        message = input("Enter a message to encrypt with your public key: ")
        encrypted_msg = encrypt(public, message)
        
        print("Your encrypted message is: ")
        print(' '.join(map(str, encrypted_msg)))
        
        print("\nDecrypting message with private key ", private ," . . .")
        print("Your message is:")
        print(decrypt(private, encrypted_msg))

    else:
        print("Invalid choice.")
