import re
from simhash import Simhash, SimhashIndex
def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

sentence_1 = 'How are you? I am fine. Thanks.'
sentence_2 = 'How are yuu? I am fine. Thanks.'

simhash_1 = Simhash(get_features(sentence_1))
simhash_2 = Simhash(get_features(sentence_2))

print ('%x' % simhash_1.value)
print ('%x' % simhash_2.value)

print (simhash_1.distance(simhash_1))
print (simhash_1.distance(simhash_2))
print ("")
