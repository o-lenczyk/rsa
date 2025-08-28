import random
from Crypto.Util.number import getPrime

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

    choice = input("Choose an option: (1) Encrypt/Decrypt a new message or (2) Decrypt a message with a key: ")

    if choice == '1':
        try:
            bits = int(input("Enter bit size for p and q (e.g., 8, 16, 32, 64): "))
        except ValueError:
            print("Invalid bit size. Using default 64 bits.")
            bits = 64

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
    else:
        print("Invalid choice.")
