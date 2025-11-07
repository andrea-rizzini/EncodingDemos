import re
from simhash import Simhash, SimhashIndex

F = 64

def get_features(s):
    width = 2
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def get_chunks(s, chunk_size=10):
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    chunks = [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]
    return chunks

sentence_1 = 'Hello, I\'m Andrea, I\'m 26 and I live in Milan. I love cryptography and AI.'
sentence_2 = 'Hello, I\'m Andrea, I\'m 26 and I live in Milan. I like cryptography and AI.'

print("Sentence 1: ", sentence_1)
print("Sentence 2: ", sentence_2)

# Whithout chunking
simhash_1 = Simhash(get_features(sentence_1), f=F)
simhash_2 = Simhash(get_features(sentence_2), f=F)

print ('\nSimhash 1: %x' % simhash_1.value)
print ('Simhash 2: %x' % simhash_2.value)


print ("\nSimhash 1 distance to Simhash 2: ", simhash_1.distance(simhash_2))

# With chunking
chunks_1 = get_chunks(sentence_1, chunk_size=15)
chunks_2 = get_chunks(sentence_2, chunk_size=15)

print("\nChunks Sentence 1:", chunks_1)
print("Chunks Sentence 2:", chunks_2)

simhashes_1 = [Simhash(get_features(chunk), f=F) for chunk in chunks_1]
simhashes_2 = [Simhash(get_features(chunk), f=F) for chunk in chunks_2]

print("\nSimhashes for Sentence 1 chunks:")
for i, sh in enumerate(simhashes_1):
    print(f"Chunk {i + 1}: {sh.value:x}")

print("\nSimhashes for Sentence 2 chunks:")
for i, sh in enumerate(simhashes_2):
    print(f"Chunk {i + 1}: {sh.value:x}")

# Compare per-chunk distances between corresponding Simhashes
print("\nPer-chunk Simhash distances (Sentence 1 vs Sentence 2):")
pair_count = min(len(simhashes_1), len(simhashes_2))
for i in range(pair_count):
    d = simhashes_1[i].distance(simhashes_2[i])
    print(f"Chunk {i + 1} distance: {d}")

if len(simhashes_1) != len(simhashes_2):
    print("\nNote: Unequal number of chunks; compared only overlapping pairs.")
