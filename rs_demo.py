from reedsolo import RSCodec, ReedSolomonError

# First case, without specifying corrupted positions can correct 1 error
print("Case 1: Correcting 1 error without specifying positions")
rsc = RSCodec(nsym=2) # change this value to test more/less parity symbols
msg = b"HELLO_RS"
codeword = rsc.encode(msg)
print("codeword:", codeword)

corrupted = bytearray(codeword)
corrupted[1] ^= 0x55 
print("corrupted:", corrupted)

try:
    dec, _, _ = rsc.decode(bytes(corrupted))
    print("OK:", dec == msg, dec)
except ReedSolomonError as e:
    print("Decoding failed:", e)

# Second case, specifying corrupted positions can correct 2 errors
print("\nCase 2: Correcting 2 errors by specifying positions")
rsc = RSCodec(nsym=2)
msg = b"HELLO_RS"
codeword = rsc.encode(msg)
print("codeword:", codeword)

corrupted = bytearray(codeword)
corrupted[1] ^= 0x55
corrupted[7] ^= 0x99
print("corrupted:", corrupted)

try:
    dec, _, _ = rsc.decode(bytes(corrupted), erase_pos=[1, 7])
    print("OK:", dec == msg, dec)
except ReedSolomonError as e:
    print("Decoding failed:", e)

# Third case, with more parity symbols can correct 2 errors without specifying positions
print("\nCase 3: Correcting 2 errors without specifying positions")
rsc = RSCodec(nsym=4) 
msg = b"HELLO_RS"
codeword = rsc.encode(msg)
print("codeword:", codeword)

corrupted = bytearray(codeword)
corrupted[1] ^= 0x55
corrupted[7] ^= 0x99
print("corrupted:", corrupted)

try:    
    dec, _, _ = rsc.decode(bytes(corrupted))
    print("OK:", dec == msg, dec)
except ReedSolomonError as e:
    print("Decoding failed:", e)

# trying to decode a chunk without doing the encoding first
print("\nCase 4: Decoding without prior encoding")
rsc = RSCodec(nsym=2)
corrupted = bytearray(b"HELLO_RS")

try:
    dec, _, _ = rsc.decode(bytes(corrupted))
    print("OK:", dec == msg, dec)
except ReedSolomonError as e:
    print("Decoding failed:", e)