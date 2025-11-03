import re
from simhash import Simhash, SimhashIndex

F = 128

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

sentence_1 = 'How are you? I am fine. Thanks.'
sentence_2 = 'How are yuu? I am fine. Thanks.'

# First iteration
simhash_1 = Simhash(get_features(sentence_1), f=F)
simhash_2 = Simhash(get_features(sentence_2), f=F)

print ('%x' % simhash_1.value)
print ('%x' % simhash_2.value)

print (simhash_1.distance(simhash_1))
print (simhash_1.distance(simhash_2))
print ("")

# Second iteration

hex_1 = f'{simhash_1.value:0{F//4}x}'   # 32 hex se F=128 (16 se F=64)
hex_2 = f'{simhash_2.value:0{F//4}x}'

simhash_1_1 = Simhash(get_features(hex_1), f=F)
simhash_2_1 = Simhash(get_features(hex_2), f=F)

print ('%x' % simhash_1_1.value)
print ('%x' % simhash_2_1.value)

print(simhash_1_1.distance(simhash_1_1))
print(simhash_1_1.distance(simhash_2_1))