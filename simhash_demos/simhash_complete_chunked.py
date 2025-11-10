#!/usr/bin/env python3
import argparse, sys, os, re, hashlib, json
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
        return gzip.open(p, mode)   # auto text/binary based on mode
    if suffix.endswith(".bz2") or suffix.endswith(".bzip2"):
        return bz2.open(p, mode)
    if suffix.endswith(".xz") or suffix.endswith(".lzma"):
        return lzma.open(p, mode)
    if "b" in mode:
        return open(p, "rb")
    return open(p, "rt", encoding="utf-8", errors="ignore")

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

def simhash_text(path, bitlen=64, ngram=3, weight_fn=None):
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
                vec[i] += w if (h >> i) & 1 else -w
    return sign_from_vec(vec)

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
    return sign_from_vec(vec)
# ---------- helpers for block mode ----------
def sign_from_vec(vec):
    out = 0
    for i, s in enumerate(vec):
        if s > 0:
            out |= (1 << i)
    return out

_SIZE_RE = re.compile(r"\s*(\d+(?:\.\d+)?)\s*([kmgt]?i?b?|)\s*$", re.I)
_MULT = {
    "": 1, "b": 1,
    "k": 1<<10, "kb": 1<<10, "kib": 1<<10,
    "m": 1<<20, "mb": 1<<20, "mib": 1<<20,
    "g": 1<<30, "gb": 1<<30, "gib": 1<<30,
    "t": 1<<40, "tb": 1<<40, "tib": 1<<40,
}
def parse_size(s: str) -> int:
    """
    Parse sizes like 64K, 1M, 4MiB, 2G, 1.5MB → bytes (powers of two).
    """
    m = _SIZE_RE.fullmatch(s or "")
    if not m:
        raise ValueError(f"invalid size: {s!r}")
    num = float(m.group(1))
    unit = (m.group(2) or "").lower()
    mult = _MULT.get(unit)
    if mult is None:
        raise ValueError(f"invalid size unit in {s!r}")
    return int(num * mult)

# ---------- per-block SimHash (bytes mode) ----------
def simhash_bytes_blocks(path, bitlen=128, n=7, step=1, block_size=1<<20, chunk_size=1<<20, weight_fn=None):
    """
    Yield per-block SimHashes for binary data in bytes mode.
    Each n-gram contributes to the block where the window *ends*.
    Yields dicts: {"block": idx, "start": start_byte, "end": end_byte_exclusive, "hash": int}
    """
    with open_maybe_compressed(path, "rb") as fh:
        vec = [0] * bitlen
        window = deque(maxlen=n)
        since = 0
        byte_idx = 0                # total bytes consumed so far
        current_block = 0
        touched = False             # whether the current block got any contributions

        def finalize(block_idx, upto_byte):
            nonlocal vec, touched
            if not touched:
                return None
            h = sign_from_vec(vec)
            start = block_idx * block_size
            end = min(upto_byte, (block_idx + 1) * block_size)
            rec = {"block": block_idx, "start": start, "end": end, "hash": h}
            vec = [0] * bitlen
            touched = False
            return rec

        while True:
            data = fh.read(chunk_size)
            if not data:
                break
            for b in data:
                window.append(b)
                byte_idx += 1
                if len(window) == n:
                    if since == 0:
                        # this window ends at byte (byte_idx-1)
                        end_pos = byte_idx - 1
                        block_idx = end_pos // block_size

                        # finalize fully completed blocks
                        while block_idx > current_block:
                            rec = finalize(current_block, byte_idx - 1)
                            if rec is not None:
                                yield rec
                            current_block += 1

                        # contribute this window to the current block
                        w = 1 if weight_fn is None else weight_fn(bytes(window))
                        if w:
                            h = hash_feature_bytes(bytes(window), bitlen=bitlen)
                            for i in range(bitlen):
                                vec[i] += w if (h >> i) & 1 else -w
                            touched = True
                    since = (since + 1) % step

        # finalize last block
        rec = finalize(current_block, byte_idx)
        if rec is not None:
            yield rec

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
    ap.add_argument("--bitlen", type=int, default=128, help="Output hash bit length (64/128/256...)")
    ap.add_argument("--ngram", type=int, default=7, help="[text/bytes] token/byte n-gram size")
    ap.add_argument("--step", type=int, default=1, help="[bytes] slide step in bytes")
    ap.add_argument("--chunk-size", type=int, default=1<<20, help="Read size per chunk (bytes)")
    ap.add_argument("--recursive", action="store_true", help="Recurse into directories")
    ap.add_argument("--json", action="store_true", help="Emit JSON lines instead of TSV")
    ap.add_argument("--block-size", type=str, default=None,
                    help="If set (e.g. 64K, 1M, 256KiB), emit one SimHash per block of this size.")
    args = ap.parse_args()

    block_bytes = parse_size(args.block_size) if args.block_size else None

    for path in iter_input_paths(args.paths, recursive=args.recursive):
        # Per-block output
        if block_bytes:
            if args.mode == "text":
                # Text chunked at byte boundaries (simple). If you need token-aware chunking, ask and we can add it.
                it = simhash_bytes_blocks(path, bitlen=args.bitlen, n=args.ngram,
                                          step=args.step, block_size=block_bytes,
                                          chunk_size=args.chunk_size)
            else:  # bytes
                it = simhash_bytes_blocks(path, bitlen=args.bitlen, n=args.ngram,
                                          step=args.step, block_size=block_bytes,
                                          chunk_size=args.chunk_size)

            for rec in it:
                hx = to_fixed_hex(rec["hash"], args.bitlen)
                if args.json:
                    print(json.dumps({
                        "path": path, "block": rec["block"],
                        "start": rec["start"], "end": rec["end"],
                        "bitlen": args.bitlen, "mode": args.mode,
                        "simhash_hex": hx
                    }, ensure_ascii=False))
                else:
                    print(f"{hx}\t{args.bitlen}\t{args.mode}\t{path}\tblock={rec['block']}\t[{rec['start']},{rec['end']})")
            continue  # next path

        # Whole-file (original behavior)
        if args.mode == "text":
            h = simhash_text(path, bitlen=args.bitlen, ngram=args.ngram)
        else:
            h = simhash_bytes(path, bitlen=args.bitlen, n=args.ngram,
                              step=args.step, chunk_size=args.chunk_size)

        hx = to_fixed_hex(h, args.bitlen)
        if args.json:
            rec = {"path": path, "simhash_hex": hx, "bitlen": args.bitlen, "mode": args.mode}
            print(json.dumps(rec, ensure_ascii=False))
        else:
            print(f"{hx}\t{args.bitlen}\t{args.mode}\t{path}")

if __name__ == "__main__":
    main()
