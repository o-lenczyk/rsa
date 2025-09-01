import time
import subprocess
import re
from factordb.factordb import FactorDB
from rsa_from_scratch import generate_keypair, encrypt, decrypt
from Crypto.Util.number import getPrime
from sympy.ntheory import factorint
import gmpy2
import requests
import json
from config import WOLFRAM_ALPHA_APP_ID

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

def break_rsa_sage(n):
    try:
        from sage.all import factor
    except ImportError:
        print("SageMath is not installed or not available in this environment.")
        return None
    print("Factoring with SageMath...")
    factors = factor(n)
    primes = [int(f[0]) for f in factors]
    if len(primes) == 2:
        return primes[0], primes[1]
    elif len(primes) > 2:
        # Try to find two factors that multiply to n
        for i in range(len(primes)):
            for j in range(i+1, len(primes)):
                if primes[i] * primes[j] == n:
                    return primes[i], primes[j]
    print("Failed to factor n with SageMath.")
    return None

def break_rsa_cypari2(n):
    try:
        import cypari2
    except ImportError:
        print("cypari2 is not installed. Please install it with 'pip install cypari2'.")
        return None
    pari = cypari2.Pari()

    new_stack_size_bytes = 100 * 1024 * 1024
    pari.allocatemem(new_stack_size_bytes)

    print("Factoring with cypari2...")
    factors = pari.factor(n)
    # factors is a Gen object behaving like a list of [prime, exponent] pairs
    if not factors:
        print("cypari2 failed to find any factors.")
        return None
    # Take the first prime factor found
    p = int(factors[0][0])
    if n % p == 0:
        q = n // p
        # Sanity check to ensure we have two distinct factors other than 1
        if p * q == n and p != 1 and q != 1:
            return p, q
    print("Failed to factor n with cypari2.")
    return None

def break_rsa_flint(n):
    try:
        from flint import fmpz
    except ImportError:
        print("python-flint is not installed. Please install it with 'pip install python-flint'.")
        return None
    print("Factoring with python-flint...")
    factors = fmpz(n).factor()
    # factors is a list of (prime, exponent) tuples
    if not factors:
        print("python-flint failed to find any factors.")
        return None
    p = factors[0][0]
    if n % p == 0:
        q = n // p
        if p * q == n and p != 1 and q != 1:
            return int(p), int(q)
    print("Failed to factor n with python-flint.")
    return None

def break_rsa_cado_nfs(n):
    print("Factoring with CADO-NFS...")
    # CADO-NFS is optimized for large numbers and may fail on small inputs.
    # We'll set a minimum bit length for the number to be factored.
    if n.bit_length() < 200:
        print("Number is too small for CADO-NFS, skipping.")
        return None
    cado_path = '/home/orest/repos/cado-nfs'
    try:
        command = f'./cado-nfs.py {n}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cado_path)

        if result.returncode != 0:
            print(f"CADO-NFS exited with an error: {result.stderr}")
            return None

        # CADO-NFS prints the factors on separate lines.
        lines = result.stdout.strip().split('\n')
        factors = [int(line) for line in lines if line.isdigit()]
        
        if len(factors) == 2:
            p = factors[0]
            q = factors[1]
            if p * q == n:
                return p, q
        elif len(factors) > 2:
             for i in range(len(factors)):
                for j in range(i + 1, len(factors)):
                    if factors[i] * factors[j] == n:
                        return factors[i], factors[j]

        print(f"Failed to parse factors from CADO-NFS output.")
        print("CADO-NFS stdout:", result.stdout)
        return None

    except FileNotFoundError:
        print(f"cado-nfs.py not found in {cado_path}. Please check the path.")
        return None
    except subprocess.TimeoutExpired:
        print("CADO-NFS took too long to execute and was terminated.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running CADO-NFS: {e}")
        return None

def break_rsa_factordb(n):
    print("Factoring with factordb...")
    try:
        f = FactorDB(n)
        f.connect()
        factors = f.get_factor_list()
        if len(factors) == 2:
            p = factors[0]
            q = factors[1]
            if p * q == n:
                return p, q
        elif len(factors) > 2:
             for i in range(len(factors)):
                for j in range(i + 1, len(factors)):
                    if factors[i] * factors[j] == n:
                        return factors[i], factors[j]
        print(f"Failed to parse factors from factordb output.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running factordb: {e}")
        return None

def break_rsa_yafu(n):
    print("Factoring with YAFU...")
    try:
        command = f'yafu "factor({n})"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"YAFU exited with an error: {result.stderr}")
            return None

        # YAFU prints factors in the format PXX = ...
        # We look for these lines to extract the prime factors.
        factors = re.findall(r'P\d+ = (\d+)', result.stdout)
        
        if len(factors) == 2:
            p = int(factors[0])
            q = int(factors[1])
            if p * q == n:
                return p, q
        # Handle cases where n is a product of more than two primes, find a valid pair.
        elif len(factors) > 2:
            primes = [int(f) for f in factors]
            for i in range(len(primes)):
                for j in range(i + 1, len(primes)):
                    if primes[i] * primes[j] == n:
                        return primes[i], primes[j]

        print(f"Failed to parse factors from YAFU output.")
        print("YAFU stdout:", result.stdout)
        return None

    except FileNotFoundError:
        print("YAFU command not found. Please ensure it is installed and in your system's PATH.")
        return None
    except subprocess.TimeoutExpired:
        print("YAFU took too long to execute and was terminated.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running YAFU: {e}")
        return None

def break_rsa_wolframalpha(n):
    print("Factoring with Wolfram Alpha...")
    app_id = WOLFRAM_ALPHA_APP_ID
    if not app_id or app_id == 'YOUR_WOLFRAM_ALPHA_APP_ID':
        print("Wolfram Alpha App ID not configured.")
        return None

    url = "https://api.wolframalpha.com/v2/query"
    params = {
        "input": f"FactorInteger[{n}]",
        "appid": app_id,
        "output": "JSON",
        "format": "plaintext",
    }

    try:
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()

        qres = data.get("queryresult", {})
        if not qres.get("success", False):
            # Sometimes WA succeeds but 'success' is False; keep going to parse pods anyway
            if not qres.get("pods"):
                print("Wolfram Alpha did not return pods.")
                return None

        # Prefer 'Prime factorization' or 'Result' pods; fall back to any pod with 'factor'
        pods = qres.get("pods", [])
        candidate_pods = []
        for pod in pods:
            title = (pod.get("title") or "").lower()
            if "prime factorization" in title or title == "result" or "factor" in title:
                candidate_pods.append(pod)

        factors = []
        for pod in candidate_pods:
            for sub in pod.get("subpods", []):
                text = sub.get("plaintext")
                factors = _parse_walpha_factor_text(text)
                if factors:
                    # Try to find p,q with product n (RSA)
                    for i in range(len(factors)):
                        for j in range(i + 1, len(factors)):
                            if factors[i] * factors[j] == n:
                                return factors[i], factors[j]
                    # If exactly two factors and they multiply to n, return them
                    if len(factors) == 2 and factors[0] * factors[1] == n:
                        return factors[0], factors[1]
        print("Failed to parse factors from Wolfram Alpha output.")
        return None

    except Exception as e:
        print(f"Wolfram Alpha API error: {e}")
        return None

def _parse_walpha_factor_text(s: str):
    """Parse plaintext like '181 × 227' or '3^2 * 5 * 7' (optionally 'n = ...')."""
    if not s:
        return []
    # Keep only the RHS if an '=' appears
    if '=' in s:
        s = s.split('=', 1)[1]
    # Normalize separators
    s = s.replace('×', '*').replace('·', '*').replace(' ', '')
    # Extract tokens like 123 or 123^4
    tokens = re.findall(r'\d+(?:\^\d+)?', s)
    factors = []
    for tok in tokens:
        if '^' in tok:
            base, exp = tok.split('^', 1)
            factors.extend([int(base)] * int(exp))
        else:
            factors.append(int(tok))
    return factors

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
    print("9. SageMath (factorization using Sage)")
    print("10. cypari2 (Pari/GP)")
    print("11. python-flint")
    print("12. YAFU (standalone tool)")
    print("13. CADO-NFS (standalone tool)")
    print("14. FactorDB (online database)")
    print("15. Wolfram Alpha (online API)")
    algo_choice = input("Enter 1-15: ").strip()

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
    elif algo_choice == "9":
        break_rsa = break_rsa_sage
        algo_name = "SageMath (factorization using Sage)"
    elif algo_choice == "10":
        break_rsa = break_rsa_cypari2
        algo_name = "cypari2 (Pari/GP)"
    elif algo_choice == "11":
        break_rsa = break_rsa_flint
        algo_name = "python-flint"
    elif algo_choice == "12":
        break_rsa = break_rsa_yafu
        algo_name = "YAFU"
    elif algo_choice == "13":
        break_rsa = break_rsa_cado_nfs
        algo_name = "CADO-NFS"
    elif algo_choice == "14":
        break_rsa = break_rsa_factordb
        algo_name = "FactorDB"
    elif algo_choice == "15":
        break_rsa = break_rsa_wolframalpha
        algo_name = "Wolfram Alpha"
    else:
        print("Invalid choice. Defaulting to trial division.")
        break_rsa = break_rsa_trial_division
        algo_name = "Trial division (pure Python)"

    for bits in [8, 16, 32, 34,36,38,40,64, 128, 130, 132, 256]:
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
