from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
KEYS_DIR = DATA_DIR / "keys"
CERTS_DIR = DATA_DIR / "certs"
PROOFS_DIR = DATA_DIR / "proofs"
CHAIN_DIR = DATA_DIR / "chain"

HASH_ENCODING_SORT_KEYS = True
HASH_ENCODING_SEPARATORS = (",", ":")
HASH_ENCODING_UTF = "utf-8"

GENESIS_TIME = 1710000000   
SLOT_DURATION = 300         # 5 minutes
GROUP_SIZE = 4