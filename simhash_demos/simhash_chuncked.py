import re
from simhash import Simhash, SimhashIndex

F = 128

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

sentence_1 = 'Hello, I\'m Andrea, I\'m 26 and I live in Milan. I love cryptography and AI.'
sentence_2 = 'Hello, I\'m Andrew, I\'m 26 and I live in Milan. I like cryptography and AI.'

print("Sentence 1: ", sentence_1)
print("Sentence 2: ", sentence_2)

# Whithout chunking
simhash_1 = Simhash(get_features(sentence_1), f=F)
simhash_2 = Simhash(get_features(sentence_2), f=F)

print ('%x' % simhash_1.value)
print ('%x' % simhash_2.value)

print (simhash_1.distance(simhash_1))
print (simhash_1.distance(simhash_2))
print ("")

# With chunking