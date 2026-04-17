import time
import math
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from config import CERTS_DIR, CHAIN_DIR, KEYS_DIR, GENESIS_TIME, SLOT_DURATION, GROUP_SIZE
from utils import (
    ensure_dir,
    load_json,
    save_json,
    encode_for_hashing,
    sha256_bytes,
    sha256_of_json,
)


PROPOSERS = {
    0: "Daniela",
    1: "Andrea",
    2: "Brian",
    3: "Gri",
}


def load_private_key(path: Path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def sign_header_hash(private_key, header_hash: str) -> str:
    """
    Signs the block header hash with the proposer private key.

    The signature is stored in base64 so it can be written directly in JSON.
    """
    signature = private_key.sign(
        header_hash.encode("utf-8"),
        ec.ECDSA(hashes.SHA256())
    )
    return base64.b64encode(signature).decode("utf-8")


def hash_certificate(cert: dict) -> str:
    return sha256_bytes(encode_for_hashing(cert))


def hash_pair(left_hash: str, right_hash: str) -> str:
    return sha256_bytes((left_hash + right_hash).encode("utf-8"))


def compute_merkle_root_from_certs(certificates: list) -> str:
    """
    Rebuilds the Merkle root directly from the certificates included in the block body.

    This ensures that the header commitment can always be recomputed from the data
    stored inside the same block.
    """
    if not certificates:
        raise ValueError("Cannot compute Merkle root from an empty certificate list.")

    current_level = [hash_certificate(cert) for cert in certificates]

    while len(current_level) > 1:
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        next_level = []
        for i in range(0, len(current_level), 2):
            parent = hash_pair(current_level[i], current_level[i + 1])
            next_level.append(parent)

        current_level = next_level

    return current_level[0]


def get_certificates_from_folder():
    cert_files = sorted(CERTS_DIR.glob("*.json"))
    certificates = [load_json(path) for path in cert_files]
    return certificates, cert_files


def get_previous_block_hash():
    ensure_dir(CHAIN_DIR)
    block_files = sorted(CHAIN_DIR.glob("block_*.json"))

    if not block_files:
        return "GENESIS"

    last_block_path = block_files[-1]
    last_block = load_json(last_block_path)
    return sha256_of_json(last_block)


def get_current_slot_index(current_time: int) -> int:
    if current_time < GENESIS_TIME:
        raise ValueError("Current time is before Genesis Time.")
    return (current_time - GENESIS_TIME) // SLOT_DURATION


def get_slot_owner(slot_index: int) -> int:
    return slot_index % GROUP_SIZE


def is_my_turn(proposer_id: int, current_time: int) -> bool:
    slot_index = get_current_slot_index(current_time)
    return get_slot_owner(slot_index) == proposer_id


def get_slot_start_end(slot_index: int):
    slot_start = GENESIS_TIME + slot_index * SLOT_DURATION
    slot_end = slot_start + SLOT_DURATION
    return slot_start, slot_end


def create_block(proposer_id: int):
    """
    Creates a new block if the proposer is authorized in the current slot.

    The block contains:
    - a header with chain linkage and timing information,
    - a body with the certificates,
    - a signature over the header hash.
    """
    ensure_dir(CHAIN_DIR)

    if proposer_id not in PROPOSERS:
        raise ValueError(f"Unknown proposer_id: {proposer_id}")

    proposer_name = PROPOSERS[proposer_id]
    sk_path = KEYS_DIR / f"{proposer_name}_sk.pem"

    if not sk_path.exists():
        raise FileNotFoundError(f"Private key not found for proposer {proposer_name}: {sk_path}")

    current_time = int(time.time())

    if current_time < GENESIS_TIME:
        raise ValueError("Cannot create block before Genesis Time.")

    slot_index = get_current_slot_index(current_time)
    expected_proposer = get_slot_owner(slot_index)
    slot_start, slot_end = get_slot_start_end(slot_index)

    print(f"Current time: {current_time}")
    print(f"Slot index: {slot_index}")
    print(f"Slot interval: [{slot_start}, {slot_end})")
    print(f"Expected proposer for this slot: {expected_proposer}")
    print(f"Your proposer_id: {proposer_id}")

    if expected_proposer != proposer_id:
        print("It is NOT your turn to create a block in this slot.")
        return

    certificates, cert_files = get_certificates_from_folder()

    if not certificates:
        raise ValueError("No certificates found in data/certs/")

    merkle_root = compute_merkle_root_from_certs(certificates)
    prev_hash = get_previous_block_hash()

    header = {
        "prev_hash": prev_hash,
        "merkle_root": merkle_root,
        "timestamp": current_time,
        "proposer_id": proposer_id
    }

    header_hash = sha256_of_json(header)

    private_key = load_private_key(sk_path)
    block_signature = sign_header_hash(private_key, header_hash)

    block = {
        "header": header,
        "body": certificates,
        "block_signature": block_signature
    }

    existing_blocks = sorted(CHAIN_DIR.glob("block_*.json"))
    block_index = len(existing_blocks)
    block_path = CHAIN_DIR / f"block_{block_index}.json"
    save_json(block_path, block)

    print(f"\nBlock created: {block_path}")
    print(f"Included certificates: {len(certificates)}")
    print(f"Merkle root: {merkle_root}")
    print(f"Previous hash: {prev_hash}")
    print(f"Header hash: {header_hash}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) !=2:
        print("Usage: python src/create_block.py <proposer_id>")
    else: 
        proposer_id = int(sys.argv[1])
        create_block(proposer_id=proposer_id)