from sage.all import *

# Binary Golay G23
C = codes.GolayCode(GF(2), extended=False)  # [23,12,7]

# Encode a 12-bit message
E = C.encoder()

m = vector(GF(2), [1,0,1,1, 0,0,1,0, 1,0,0,1])
print("Message:")
print(m)

c = E.encode(m)
print("Encoded codeword:")
print(c)

# Create a first error vector with 3 errors (bits to be flipped)
e1 = vector(GF(2), [1 if i in {0,5,9} else 0 for i in range(C.length())])
print("Error vector 1:")
print(e1)

# Create a second error vector with 3 errors (bits to be flipped)
e2 = vector(GF(2), [1 if i in {1,5,10} else 0 for i in range(C.length())])
print("Error vector 2:")
print(e2)

r1 = c + e1
print("Received word with first error vector:")
print(r1)

r2 = c + e2
print("Received word with second error vector:")
print(r2)

# Decode
D = C.decoder()  # default decoder (metric: Hamming)

m1_hat = D.decode_to_message(r1)
m2_hat = D.decode_to_message(r2)
c1_hat = D.decode_to_code(r1)
c2_hat = D.decode_to_code(r2)

print("\nNearest codeword from message 1:")
print(c1_hat)
print("Decoded message from first received word:")
print(m1_hat)          # [23, 12, 7] Golay code
print("\nNearest codeword from message 2:")
print(c2_hat)
print("Decoded message from second received word:")
print(m2_hat)          # [23, 12, 7] Golay code