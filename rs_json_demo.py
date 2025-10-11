
import sys, json, hashlib, random
from reedsolo import RSCodec, ReedSolomonError

def canonicalize_json(obj) -> bytes:

    return json.dumps(
        obj,
        ensure_ascii=False,    
        sort_keys=True,         
        separators=(",", ":")   
    ).encode("utf-8")

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) != 2:
        print("Usage: python rs_json_demo.py data.json")
        sys.exit(1)

    path = sys.argv[1]

    # 1) Read JSON
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2) Canonicalize -> bytes
    canon = canonicalize_json(data)
    print("Canonical JSON bytes:", canon)
    print("Canonical JSON bytes length:", len(canon))

    # 3) exact ID (content-addressed)
    exact_id = sha256(canon)
    print("Exact ID (SHA-256):", exact_id)

    # 4) Reed–Solomon encode
    rsc = RSCodec(nsym=4)

    codeword = rsc.encode(canon)
    print("Codeword length:", len(codeword), "(= data + 4 parity bytes)")

    # # 5a) Simulate corruption: 2 random byte errors
    corrupted = bytearray(codeword)
    # choose two random positions to corrupt
    idxs = random.sample(range(len(corrupted)), k=2)
    for i in idxs:
        corrupted[i] ^= 0xA5  # flip some bits

    print("\n--- Decode with 2 unknown errors ---")
    try:
        dec, _, _ = rsc.decode(bytes(corrupted))
        print("Decoding OK (errors corrected). Equal to original:",
              dec == canon)
        print("Reconstructed ID:", sha256(dec))
    except ReedSolomonError as e:
        print("Decoding failed:", e)

    # 5b) Same corruption but treating it as ERASURE (known positions)
    print("\n--- Decode as 2 erasures (known positions) ---")
    try:
        dec2, _, _ = rsc.decode(bytes(corrupted), erase_pos=idxs)
        print("Decoding OK (erasures). Equal to original:",
              dec2 == canon)
        print("Reconstructed ID:", sha256(dec2))
    except ReedSolomonError as e:
        print("Decoding failed:", e)

    # 6) Final identity verification
    # (the ID must be identical if the original data is recovered)
    if 'dec' in locals() and dec == canon:
        assert sha256(dec) == exact_id
    if 'dec2' in locals() and dec2 == canon:
        assert sha256(dec2) == exact_id

if __name__ == "__main__":
    main()
