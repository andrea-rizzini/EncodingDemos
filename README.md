## In this project you can find demos for different encoding algorithms

### 1) Reed–Solomon encoding
- `rs_demo.py`: Reed–Solomon encoding demo using the `reedsolo` Python library.
- `rs_json_demo.py`: Same as `rs_demo.py`, but encodes a JSON file.
- `rs_demo.go` and `rs_demo_2.go`: Reed–Solomon demos using the `klauspost/reedsolomon` Go library.

### 2) Binary Golay Code
- ```golay_demo.py```: Binay Golay Code encoding demo
- ```golay_distance_test.py```: Binary Golay code demo showing that, starting from a codeword ```c```, two different perturbations of at most three bits both decode to the same codeword in the code space using the decode_to_code method, and ultimately to the same original message using the decode_to_message method.
- ```golay_arbitrary_decoding.py```: Binary Golay code demo showing that, starting from arbitrary 23-bit vectors, two inputs that differ by only one bit can decode to different codewords in the code space and therefore to completely different messages.

Note:  
The (23,12,7) binary Golay code is a perfect t=3 code that partitions the 23-bit space into disjoint Hamming spheres of radius 3 around each codeword. Two neighboring vectors (even 1-bit apart) can lie in different spheres, so a bounded-distance decoder maps them to different codewords, and thus different decoded messages.