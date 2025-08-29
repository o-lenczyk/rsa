# Primality Test Library Comparison

| Prime Size (bits)  | Sympy isprime                         | PyCryptodome.isPrime                | gmpy2.is_prime                             | Typical RSA Prime (bits) |
|--------------------|---------------------------------------|--------------------------------------|---------------------------------------------|--------------------------|
| 0–64 bits          | Instant (deterministic small bases)   | Instant (fixed small bases)          | Instant (deterministic small bases)         | N/A                      |
| 65–512 bits        | <1 ms (Baillie–PSW)                   | <1 ms (MR rounds, error bound)       | <1 ms (configurable MR rounds)              | 256–512 bits (32–64 bytes) – deprecated |
| 513–1024 bits      | 10–50 ms                              | 1–10 ms (default error <2⁻⁸⁰)        | 1–20 ms (error ≤4^–k configurable)          | 1024 bits (128 bytes)    |
| 1025–1536 bits     | 50–200 ms                             | 5–30 ms                              | 5–30 ms                                     | 1536 bits (192 bytes)    |
| 1537–2048 bits     | 100–500 ms                            | 10–50 ms                             | 5–30 ms                                     | 2048 bits (256 bytes)    |
| >2048 bits         | >500 ms (not recommended)             | 20–100 ms                            | <50 ms (preferred for >2048 bits)           | 4096 bits (512 bytes)    |

Legend:
- Bits indicate the size of the prime input to the primality test.  
- MR: Miller–Rabin with configurable rounds.  

## Ease-of-Use Comparison

| Library      | Pros                                                       | Cons                                        |
|--------------|------------------------------------------------------------|---------------------------------------------|
| Sympy        | Very readable API; no external dependencies; extensive docs | Slower on very large (>1024-bit) primes     |
| PyCryptodome | Integrates seamlessly with RSA workflows; secure defaults; fast up to 2048 bits | Requires importing from `Crypto.Util.number`; fewer tutorials |
| gmpy2        | Blazing performance on large primes; configurable error probability; GMP optimized | External GMP dependency; installation complexity |


I will use PyCryptodome’s `isPrime` rather than gmpy2. PyCryptodome offers:

- Easy installation with a single `pip install pycryptodome` command.
- Seamless integration into RSA workflows via `from Crypto.Util.number import isPrime`.
- Secure default error bounds (error < 2⁻⁸⁰) and excellent performance up to 2048-bit primes.
- gmpy2 requires build tools and GMP headers in path
