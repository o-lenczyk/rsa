import time
from rsa_from_scratch import getPrimeSmooth, generate_keypair, encrypt, decrypt
# Import all cracking algorithms from crack_rsa.py
# Import all cracking algorithms from crack_rsa.py
# We will only use our custom implementation for now.
# from crack_rsa import (
#     break_rsa_trial_division,
#     break_rsa_gmpy2,
#     break_rsa_pollards_rho,
#     break_rsa_sympy,
#     break_rsa_sympy_custom,
#     break_rsa_sage,
#     break_rsa_cypari2,
#     break_rsa_flint,
#     break_rsa_yafu,
#     break_rsa_cado_nfs,
#     break_rsa_factordb,
#     break_rsa_wolframalpha
# )

def get_small_primes(limit):
    primes = []
    sieve = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if sieve[p]:
            primes.append(p)
            for i in range(p * p, limit + 1, p):
                sieve[i] = False
    return primes

def break_rsa_pollards_p1_iterative(n):
    """
    Tries Pollard's p-1 with increasing smoothness bounds to find the 'sweet spot'.
    """
    bound = 200  # Start with a reasonable bound
    max_bound = 200000 # Don't search forever

    # Need a gcd function, let's define a simple one here
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    while bound <= max_bound:
        print(f"Attempting Pollard's p-1 with bound B={bound}")
        a = 2
        primes = get_small_primes(bound)
        
        for p_prime in primes:
            p_power = p_prime
            while p_power * p_prime <= bound:
                p_power *= p_prime
            a = pow(a, p_power, n)

        g = gcd(a - 1, n)
        
        if 1 < g < n:
            print(f"Success! Found a factor with bound B={bound}")
            return g, n // g
        elif g == n:
            print(f"Bound B={bound} was too high (g=n). Both p-1 and q-1 are smooth to this bound. Stopping.")
            return None
        
        # If g == 1, the bound was too small. Increase it and try again.
        print(f"Bound B={bound} was too small (g=1). Increasing bound.")
        bound *= 2
        
    print(f"Failed to find a factor even after increasing bound to {max_bound}.")
    return None


if __name__ == "__main__":
    algorithms = {
        "Custom Pollard's p-1 (Iterative)": break_rsa_pollards_p1_iterative,
    }

    # Test various key lengths
    for bits in [64, 128, 256, 512, 1024, 2048]:
        print(f"\n\n--- Testing RSA with {bits}-bit SMOOTH primes (vulnerable to Pollard's p-1) ---")
        
        print("Generating p (this might take a while)...")
        p = getPrimeSmooth(bits)
        print("Generating q (this might take a while)...")
        q = getPrimeSmooth(bits)
        
        while p == q:
            print("p and q were the same, regenerating q...")
            q = getPrimeSmooth(bits)
            
        public, private = generate_keypair(p, q)
        e, n = public
        d, _ = private
        
        print(f"\nGenerated Public Key (e, n): ({e}, {n})")
        print(f"Original primes: p={p}, q={q}")
        
        message = "test"
        encrypted_msg = encrypt(public, message)
        print(f"Encrypted message: {encrypted_msg}")
        
        print("\n--- Attempting to crack the modulus n using various algorithms ---")

        for name, func in algorithms.items():
            print(f"\n--- Testing {name} ---")
            start_time = time.time()
            cracked_pq = func(n)
            end_time = time.time()
            
            if cracked_pq:
                cracked_p, cracked_q = cracked_pq
                print(f"Success! Factors found: p={cracked_p}, q={cracked_q}")
                
                # Verify factors are correct
                if (cracked_p == p and cracked_q == q) or \
                   (cracked_p == q and cracked_q == p):
                    print("Factors match the original primes.")
                else:
                    print("Warning: Factors do not match original primes, but their product is n.")

                phi = (cracked_p - 1) * (cracked_q - 1)
                d_cracked = pow(e, -1, phi)
                cracked_private = (d_cracked, n)
                decrypted = decrypt(cracked_private, encrypted_msg)
                print(f"Decrypted message with cracked key: {decrypted}")
                print(f"Time to break: {end_time - start_time:.6f} seconds")
            else:
                print(f"Failed to factor n with {name}.")
                print(f"Time elapsed: {end_time - start_time:.6f} seconds")
