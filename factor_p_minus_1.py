import subprocess
import re

def factor_with_yafu(n):
    """
    Factors a number n using the YAFU command-line tool.
    Returns a dictionary of prime factors and their exponents.
    """
    try:
        command = f'yafu "factor({n})"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"YAFU exited with an error: {result.stderr}")
            return None

        factors_raw = re.findall(r'(?:P\d+|C) = (\d+)', result.stdout)
        
        factors_dict = {}
        for f_str in factors_raw:
            factor = int(f_str)
            if factor > 1:
                factors_dict[factor] = factors_dict.get(factor, 0) + 1
        
        if len(factors_dict) == 1 and list(factors_dict.keys())[0] == n:
            return {}
            
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

def parse_smooth_keys_file(filepath):
    """
    Parses the smooth-keys2.txt file and extracts p and q values.
    Assumes a single 2048-bit key pair in the file.
    """
    keys_data = []
    p_val = None
    q_val = None
    bits_val = 2048 # Assuming 2048-bit as per the user's request

    with open(filepath, 'r') as f:
        content = f.read()
        
        p_match = re.search(r'p=(\d+)', content)
        if p_match:
            p_val = int(p_match.group(1))
        
        q_match = re.search(r'q=(\d+)', content)
        if q_match:
            q_val = int(q_match.group(1))
        
        if p_val and q_val:
            keys_data.append({'bits': bits_val, 'p': p_val, 'q': q_val})
            
    return keys_data

if __name__ == "__main__":
    filepath = "smooth-keys2.txt"
    keys = parse_smooth_keys_file(filepath)

    if not keys:
        print(f"No keys found in {filepath}. Please ensure the file exists and is correctly formatted.")
    else:
        for key_pair in keys:
            bits = key_pair['bits']
            p = key_pair['p']
            q = key_pair['q']

            if bits == 2048: # Only process 2048-bit keys
                print(f"\n--- Analyzing {bits}-bit Primes ---")
                print(f"p = {p}")
                print(f"q = {q}")

            print(f"\nFactoring p-1 ({p-1})...")
            factors_p_minus_1 = factor_with_yafu(p - 1)
            if factors_p_minus_1:
                sorted_factors_p = dict(sorted(factors_p_minus_1.items()))
                print(f"  Factors of p-1: {sorted_factors_p}")
                max_prime_factor_p = max(factors_p_minus_1.keys())
                max_prime_power_p = max(f**e for f, e in factors_p_minus_1.items())
                print(f"  Max prime factor of p-1: { {max_prime_factor_p} }")
                print(f"  Max prime power of p-1: { {max_prime_power_p} }")
            else:
                print("  Failed to factor p-1 with YAFU.")

            print(f"\nFactoring q-1 ({q-1})...")
            factors_q_minus_1 = factor_with_yafu(q - 1)
            if factors_q_minus_1:
                sorted_factors_q = dict(sorted(factors_q_minus_1.items()))
                print(f"  Factors of q-1: {sorted_factors_q}")
                max_prime_factor_q = max(factors_q_minus_1.keys())
                max_prime_power_q = max(f**e for f, e in factors_q_minus_1.items())
                print(f"  Max prime factor of q-1: { {max_prime_factor_q} }")
                print(f"  Max prime power of q-1: { {max_prime_power_q} }")
            else:
                print("  Failed to factor q-1 with YAFU.")
