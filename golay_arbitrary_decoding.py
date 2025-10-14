from sage.all import *

# Binary Golay G23
C = codes.GolayCode(GF(2), extended=False)  # [23,12,7]

# Encode a 12-bit message
E = C.encoder()

m1 = vector(GF(2), [1,0,1,1, 0,0,1,0, 1,0,0,1, 1,0,0,1, 0,0,1,1, 0,1,1])
print("Message 1:")
print(m1)

m2 = vector(GF(2), [1,0,1,1, 0,0,1,0, 1,0,1,1, 1,0,0,1, 0,0,1,1, 0,1,1])
print("Message 2:")
print(m2)

# Decode
D = C.decoder()  # default decoder (metric: Hamming)

m1_hat = D.decode_to_message(m1)
m2_hat = D.decode_to_message(m2)

c1_hat = D.decode_to_code(m1)
c2_hat = D.decode_to_code(m2)

print("\nNearest codeword from message 1:")
print(c1_hat)
print("Decoded message from first received word:")
print(m1_hat)          # [23, 12, 7] Golay code

print("\nNearest codeword from message 2:")
print(c2_hat)
print("Decoded message from second received word:")
print(m2_hat)          # [23, 12, 7] Golay code