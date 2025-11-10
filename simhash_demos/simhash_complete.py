import argparse, sys, os, re, hashlib, math, json
from pathlib import Path
import gzip, bz2, lzma
from collections import deque

# ---------- hashing core ----------
def hash_feature_bytes(b: bytes, bitlen=64) -> int:
    h = hashlib.blake2b(b, digest_size=bitlen // 8).digest()
    return int.from_bytes(h, "big")

def hamming_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()

# ---------- I/O helpers ----------
def open_maybe_compressed(path: str, mode: str):
    """
    path: file path or '-' for stdin
    mode: 'rb' or 'rt'
    """
    if path == "-":
        return sys.stdin.buffer if "b" in mode else sys.stdin
    p = Path(path)
    suffix = "".join(p.suffixes).lower()
    if suffix.endswith(".gz"):
        return gzip.open(p, mode)  # auto text/binary based on mode
    if suffix.endswith(".bz2") or suffix.endswith(".bzip2"):
        return bz2.open(p, mode)
    if suffix.endswith(".xz") or suffix.endswith(".lzma"):
        return lzma.open(p, mode)
    if "b" in mode:
        return open(p, "rb")
    return open(p, "rt", encoding="utf-8", errors="ignore")

def sign_from_vec(vec):
    out = 0
    for i, s in enumerate(vec):
        if s > 0:
            out |= (1 << i)
    return out

# ---------- TEXT MODE (token or n-gram tokens) ----------
WORD_RE = re.compile(r"\w+", re.UNICODE)

def stream_word_tokens_fh(fh, lowercase=True):
    for line in fh:
        if lowercase:
            line = line.lower()
        yield from WORD_RE.findall(line)

def stream_token_ngrams(tokens, n=3):
    if n <= 1:
        yield from tokens
        return
    window = deque(maxlen=n-1)
    for t in tokens:
        if len(window) == n - 1:
            yield " ".join([*window, t])
        window.append(t)

def simhash_text(path, bitlen=64, ngram=3, weight_fn=None, chunk_size=None):
    vec = [0] * bitlen
    with open_maybe_compressed(path, "rt") as fh:
        tokens = stream_word_tokens_fh(fh)
        feats = stream_token_ngrams(tokens, n=ngram)
        for feat in feats:
            w = 1 if weight_fn is None else weight_fn(feat)
            if not w:
                continue
            h = hash_feature_bytes(feat.encode("utf-8", "ignore"), bitlen=bitlen)
            for i in range(bitlen):
                vec[i] += w if (h >> i) & 1 else -w # if the i-th bit is 1 add weight else subtract
    out = sign_from_vec(vec)
    return out

# ---------- BYTES MODE (byte n-grams) ----------
def stream_byte_ngrams_fh(fh, n=7, step=1, chunk_size=1<<20):
    assert n >= 1 and step >= 1
    window = deque(maxlen=n)
    since = 0
    while True:
        data = fh.read(chunk_size)
        if not data:
            break
        for b in data:
            window.append(b)
            if len(window) == n:
                if since == 0:
                    yield bytes(window)
                since = (since + 1) % step

def simhash_bytes(path, bitlen=64, n=7, step=1, chunk_size=1<<20, weight_fn=None):
    vec = [0] * bitlen
    with open_maybe_compressed(path, "rb") as fh:
        for gram in stream_byte_ngrams_fh(fh, n=n, step=step, chunk_size=chunk_size):
            w = 1 if weight_fn is None else weight_fn(gram)
            if not w:
                continue
            h = hash_feature_bytes(gram, bitlen=bitlen)
            for i in range(bitlen):
                vec[i] += w if (h >> i) & 1 else -w
    out = sign_from_vec(vec)
    return out

# ---------- CLI ----------
def iter_input_paths(paths, recursive=False):
    for p in paths:
        if p == "-":
            yield p
            continue
        p = Path(p)
        if p.is_dir():
            if recursive:
                for q in p.rglob("*"):
                    if q.is_file():
                        yield str(q)
            else:
                for q in p.iterdir():
                    if q.is_file():
                        yield str(q)
        elif p.exists():
            yield str(p)
        else:
            # allow globs passed unexpanded on Windows/powershell
            for q in Path().glob(str(p)):
                if q.is_file():
                    yield str(q)

def to_fixed_hex(h: int, bitlen: int) -> str:
    width = (bitlen + 3) // 4
    return f"{h:0{width}x}"

def main():
    ap = argparse.ArgumentParser(description="Streamed SimHash for files, stdin, and directories.")
    ap.add_argument("paths", nargs="+", help="Files/dirs/globs or '-' for stdin")
    ap.add_argument("--mode", choices=["text", "bytes"], default="bytes",
                    help="Feature mode: text tokens or byte n-grams (default: bytes)")
    ap.add_argument("--bitlen", type=int, default=128, help="Output hash bit length (64/128)")
    ap.add_argument("--ngram", type=int, default=7, help="[text/bytes] token/byte n-gram size")
    ap.add_argument("--step", type=int, default=1, help="[bytes] slide step in bytes")
    ap.add_argument("--chunk-size", type=int, default=1<<20, help="Read size per chunk (bytes)")
    ap.add_argument("--recursive", action="store_true", help="Recurse into directories")
    ap.add_argument("--json", action="store_true", help="Emit JSON lines instead of TSV")
    args = ap.parse_args()

    for path in iter_input_paths(args.paths, recursive=args.recursive): # todo: add multiple iterations, with a CLI flag
        if args.mode == "text":
            h = simhash_text(path, bitlen=args.bitlen, ngram=args.ngram)
        else:
            h = simhash_bytes(path, bitlen=args.bitlen, n=args.ngram,
                              step=args.step, chunk_size=args.chunk_size)

        if args.json:
            rec = {"path": path, "simhash_hex": to_fixed_hex(h, args.bitlen),
                   "bitlen": args.bitlen, "mode": args.mode}
            print(json.dumps(rec, ensure_ascii=False))
        else:
            print(f"{to_fixed_hex(h, args.bitlen)}\t{args.bitlen}\t{args.mode}\t{path}")

if __name__ == "__main__":
    main()