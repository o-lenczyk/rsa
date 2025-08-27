import random

def is_prime(n, k=128):
    """
    Test if a number is prime using the Miller-Rabin primality test.
    k is the number of rounds of testing to perform.
    """
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    
    # Find odd_part and power_of_two such that n - 1 = odd_part * 2^power_of_two
    power_of_two = 0
    odd_part = n - 1
    while odd_part & 1 == 0:
        power_of_two += 1
        odd_part //= 2
    
    # Perform k rounds of testing
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, odd_part, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < power_of_two and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def generate_prime_candidate(length):
    """
    Generate an odd integer randomly.
    """
    p = random.getrandbits(length)
    # Apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=1024):
    """
    Generate a prime number of a given bit length.
    """
    p = 4
    # Keep generating while the primality test fails
    while not is_prime(p):
        p = generate_prime_candidate(length)
    return p

def gcd(a, b):
    """
    Euclidean algorithm to find the greatest common divisor of a and b.
    """
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """
    Extended Euclidean algorithm to find the modular inverse of a under m.
    """
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def generate_keypair(p, q):
    """
    Generate a public/private key pair from primes p and q.
    """
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
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
    key, n = pk
    # Convert each letter in the plaintext to numbers based on the character using a^b mod m
    cipher = [pow(ord(char), key, n) for char in plaintext]
    # Return the array of bytes
    return cipher

def decrypt(pk, ciphertext):
    # Unpack the key into its components
    key, n = pk
    # Generate the plaintext based on the ciphertext and key using a^b mod m
    plain = [chr(pow(char, key, n)) for char in ciphertext]
    # Return the array of bytes as a string
    return ''.join(plain)

if __name__ == '__main__':
    '''
    Detect if the script is being run directly by the user
    '''
    print("RSA Encrypter/ Decrypter")

    choice = input("Choose an option: (1) Encrypt/Decrypt a new message or (2) Decrypt a message with a key: ")

    if choice == '1':
        p = generate_prime_number(64)
        q = generate_prime_number(64)
        
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
            # This assumes the numbers are separated by some non-digit character, 
            # or are otherwise parsable. For this simple case, let's assume they are just concatenated.
            # A better implementation would require a separator.
            # We will assume the user copies the full string of numbers.
            # This part is tricky without a defined format for the encrypted message.
            # Let's ask the user to provide the numbers separated by spaces.
            encrypted_msg_str = input("Enter the encrypted message (numbers separated by spaces): ")
            encrypted_msg = [int(x) for x in encrypted_msg_str.split()]
        except ValueError:
            print("Invalid encrypted message format. Please enter numbers separated by spaces.")
            exit()

        print("Decrypting message...")
        decrypted_msg = decrypt(private, encrypted_msg)
        print("Your decrypted message is:")
        print(decrypted_msg)
    else:
        print("Invalid choice.")
