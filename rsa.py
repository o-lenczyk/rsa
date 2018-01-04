import random
import time
import base64

def miller_rabin(n, k=10):
	if n == 2:
		return True
	if not n & 1:
		return False

	def check(a, s, d, n):
		x = pow(a, d, n)
		if x == 1:
			return True
		for i in xrange(s - 1):
			if x == n - 1:
				return True
			x = pow(x, 2, n)
		return x == n - 1

	s = 0
	d = n - 1

	while d % 2 == 0:
		d >>= 1
		s += 1

	for i in xrange(k):
		a = random.randrange(2, n - 1)
		if not check(a, s, d, n):
			return False
        return True
def rollPrime(k=512):
    fail = False
    tested = set([])
    n = random.getrandbits(k)
    while not miller_rabin(n):
        tested.add(n)
        print "failed"
        while n in tested:
            n = random.getrandbits(k)
        return n
def rollPrimeRange(p,q):
    fail = False
    tested = set([])
    n = random.randint(p,q)
    while not miller_rabin(n):
        tested.add(n)
        while n in tested:
            n = random.randint(p,q)
        return n

start_time = time.time()
p,q = rollPrime(), rollPrime()
smartTime=(time.time() - start_time)
print "finished in: '%f'" % smartTime

totient=(p-1)*(q-1)
e = rollPrimeRange(p,q)
print base64.b64encode(str(p))
print base64.b64encode(str(q))
print base64.b64encode(str(totient))
print base64.b64encode(str(e))
