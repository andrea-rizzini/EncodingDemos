from sage.all import *

# Binary Golay G23
C = codes.GolayCode(GF(2), extended=False)  # [23,12,7]

# Encode a 12-bit message
E = C.encoder()

m = random_vector(GF(2), C.dimension())
print("Message:")
print(m)

c = E.encode(m)
print("Codeword:")
print(c)

# Create an error vector with 3 errors (bits to be flipped)
e = vector(GF(2), [1 if i in {0,5,9} else 0 for i in range(C.length())])
print("Error vector:")
print(e)

r = c + e
print("Received word:")
print(r)

# Decode
D = C.decoder()  # default decoder (metric: Hamming)
m_hat = D.decode_to_message(r)

print("Decoded message:")
print(m_hat)          # [23, 12, 7] Golay code over GF(2)
print(m == m_hat) # True