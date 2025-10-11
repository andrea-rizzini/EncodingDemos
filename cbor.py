import hashlib
import cbor2  # pip install cbor2

arch = {
    "family": "MyAgent",
    "version_major": 3,
    "num_layers": 48,
    "d_model": 4096,
    "ffn": 11008,
    "attn_heads": 32,
    "rope_base": 10000,
}

# cbor2 usa encoding canonico con sort_keys=True in dumps
cbor_bytes = cbor2.dumps(arch, canonical=True)  # chiavi in ordine canonico, interi shortest
arch_fp = hashlib.sha256(cbor_bytes).digest()   # 32 byte

print(arch_fp.hex())