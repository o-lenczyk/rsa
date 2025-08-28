import time
from rsa_from_scratch import generate_keypair, encrypt, decrypt
from Crypto.Util.number import getPrime
from sympy.ntheory import factorint
import gmpy2

def pollards_rho(n):
    # Simple Pollard's Rho implementation for factoring n
    if n % 2 == 0:
        return 2
    x = 2
    y = 2
    d = 1
    f = lambda x: (x*x + 1) % n
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
    if d == n:
        return None
    return d

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def break_rsa_pollards_rho(n):
    # Factor n to get p and q using Pollard's Rho
    p = pollards_rho(n)
    if p is None or n % p != 0:
        print("Failed to factor n with Pollard's Rho.")
        return None
    q = n // p
    return p, q

def break_rsa_sympy(n):
    print("SymPy's factorint will automatically choose the factoring algorithm (could be trial division, Pollard's Rho, ECM, etc.)")
    factors = factorint(n) 
    keys = list(factors.keys())
    print(f"SymPy factorint found factors: {keys}")
    if len(keys) == 2:
        return keys[0], keys[1]
    print("Failed to factor n with SymPy's factorint.")
    return None

def break_rsa_sympy_custom(n, trial=False, rho=False, pm1=False, ecm=False):
    print(f"SymPy factorint with options: use_trial={trial}, use_rho={rho}, use_pm1={pm1}, use_ecm={ecm}")
    factors = factorint(n, use_trial=trial, use_rho=rho, use_pm1=pm1, use_ecm=ecm, verbose=True)
    keys = list(factors.keys())
    print(f"SymPy factorint found factors: {keys}")
    if len(keys) == 2:
        return keys[0], keys[1]
    print("Failed to factor n with SymPy's factorint (custom options).")
    return None

def break_rsa_trial_division(n):
    print("Factoring with trial division only...")
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return i, n // i
    print("Failed to factor n with trial division.")
    return None

def break_rsa_gmpy2(n):
    print("Factoring with gmpy2 (trial division using primes)...")
    factor = gmpy2.next_prime(1)
    while factor * factor <= n:
        if n % factor == 0:
            return int(factor), int(n // factor)
        factor = gmpy2.next_prime(factor)
    print("Failed to factor n with gmpy2.")
    return None

# Update main algorithm selection
if __name__ == "__main__":
    print("Choose factoring algorithm:")
    print("1. Trial division (pure Python, slow for large numbers)")
    print("2. gmpy2 (trial division using primes)")
    print("3. Pollard's Rho (custom implementation)")
    print("4. SymPy factorint (auto algorithm selection)")
    print("5. SymPy factorint (trial division only)")
    print("6. SymPy factorint (Pollard's Rho only)")
    print("7. SymPy factorint (Pollard's p-1 only)")
    print("8. SymPy factorint (ECM only)")
    algo_choice = input("Enter 1-8: ").strip()

    if algo_choice == "1":
        break_rsa = break_rsa_trial_division
        algo_name = "Trial division (pure Python)"
    elif algo_choice == "2":
        break_rsa = break_rsa_gmpy2
        algo_name = "gmpy2 (trial division using primes)"
    elif algo_choice == "3":
        break_rsa = break_rsa_pollards_rho
        algo_name = "Pollard's Rho"
    elif algo_choice == "4":
        break_rsa = break_rsa_sympy
        algo_name = "SymPy factorint (auto)"
    elif algo_choice == "5":
        break_rsa = lambda n: break_rsa_sympy_custom(n, trial=True)
        algo_name = "SymPy factorint (trial division only)"
    elif algo_choice == "6":
        break_rsa = lambda n: break_rsa_sympy_custom(n, rho=True)
        algo_name = "SymPy factorint (Pollard's Rho only)"
    elif algo_choice == "7":
        break_rsa = lambda n: break_rsa_sympy_custom(n, pm1=True)
        algo_name = "SymPy factorint (Pollard's p-1 only)"
    elif algo_choice == "8":
        break_rsa = lambda n: break_rsa_sympy_custom(n, ecm=True)
        algo_name = "SymPy factorint (ECM only)"
    else:
        print("Invalid choice. Defaulting to trial division.")
        break_rsa = break_rsa_trial_division
        algo_name = "Trial division (pure Python)"

    for bits in [8, 16, 32, 64, 128]:
        print(f"\n--- Testing RSA with {bits}-bit primes ---")
        p = getPrime(bits)
        q = getPrime(bits)
        public, private = generate_keypair(p, q)
        e, n = public
        d, _ = private
        print(f"Public key: (encryption exponent e={e}, modulus n={n})")
        print(f"Private key: (decryption exponent d={d}, modulus n={n})")
        print(f"Prime factors: p={p}, q={q}")

        message = "hello"
        encrypted = encrypt(public, message)
        print("Encrypted message:", encrypted)

        print(f"Attempting to break RSA using {algo_name}...")
        start = time.time()
        cracked_pq = break_rsa(n)
        end = time.time()
        if cracked_pq:
            cracked_p, cracked_q = cracked_pq
            print(f"Cracked p: {cracked_p}, q: {cracked_q}")
            phi = (cracked_p - 1) * (cracked_q - 1)
            d_cracked = pow(e, -1, phi)
            cracked_private = (d_cracked, n)
            decrypted = decrypt(cracked_private, encrypted)
            print(f"Decrypted message with cracked key: {decrypted}")
            print(f"Cracked decryption exponent d={d_cracked}")
            print(f"Time to break: {end - start:.4f} seconds")
        else:
            print("Failed to break RSA.")