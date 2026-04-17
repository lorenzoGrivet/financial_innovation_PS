import time
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

from config import CHAIN_DIR, KEYS_DIR, GENESIS_TIME, SLOT_DURATION, GROUP_SIZE
from utils import load_json, encode_for_hashing, sha256_bytes, sha256_of_json


PROPOSERS = {
    0: "Daniela",
    1: "Andrea",
    2: "Brian",
    3: "Gri",
}


def hash_certificate(cert: dict) -> str:
    return sha256_bytes(encode_for_hashing(cert))


def hash_pair(left_hash: str, right_hash: str) -> str:
    return sha256_bytes((left_hash + right_hash).encode("utf-8"))


def compute_merkle_root_from_certs(certificates: list) -> str:
    """
    Recomputes the Merkle root from the certificates stored in a block body.

    This is one of the key integrity checks of the blockchain: the header
    claims a Merkle root, and the verifier must be able to reconstruct the
    same root directly from the certificates included in the block.
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


def get_current_slot_index(block_timestamp: int) -> int:
    if block_timestamp < GENESIS_TIME:
        raise ValueError("Block timestamp is before Genesis Time.")
    return (block_timestamp - GENESIS_TIME) // SLOT_DURATION


def get_slot_owner(slot_index: int) -> int:
    return slot_index % GROUP_SIZE


def get_slot_start_end(slot_index: int):
    slot_start = GENESIS_TIME + slot_index * SLOT_DURATION
    slot_end = slot_start + SLOT_DURATION
    return slot_start, slot_end


def load_public_key_for_proposer(proposer_id: int):
    if proposer_id not in PROPOSERS:
        raise ValueError(f"Unknown proposer_id: {proposer_id}")

    proposer_name = PROPOSERS[proposer_id]
    pk_path = KEYS_DIR / f"{proposer_name}_pk.pem"

    if not pk_path.exists():
        raise FileNotFoundError(f"Public key not found for proposer {proposer_name}: {pk_path}")

    with open(pk_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def verify_block_signature(header: dict, block_signature_b64: str) -> bool:
    """
    Verifies that the block signature was produced by the proposer declared
    in the block header.

    The signature is checked against the hash of the header, not the whole
    block. This is enough to protect the block’s essential metadata:
    chain linkage, Merkle commitment, timestamp, and proposer identity.
    """
    proposer_id = header["proposer_id"]
    public_key = load_public_key_for_proposer(proposer_id)

    header_hash = sha256_of_json(header)
    signature = base64.b64decode(block_signature_b64)

    try:
        public_key.verify(
            signature,
            header_hash.encode("utf-8"),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False


def verify_block(block: dict, previous_block_hash: str = None, block_index: int = None) -> bool:
    """
    Verifies all validity conditions for a single block.

    A block is accepted only if:
    - it links correctly to the previous block,
    - its Merkle root matches its body,
    - its proposer is the correct authority for the corresponding slot,
    - its signature is valid,
    - and its timestamp is not in the future.
    """
    header = block["header"]
    body = block["body"]
    block_signature = block["block_signature"]

    prev_hash = header["prev_hash"]
    merkle_root = header["merkle_root"]
    timestamp = header["timestamp"]
    proposer_id = header["proposer_id"]

    # 1. Check future block
    current_time = int(time.time())
    if timestamp > current_time:
        print(f"[Block {block_index}] Invalid: block timestamp is in the future.")
        return False

    # 2. Check prev_hash link
    if previous_block_hash is None:
        if prev_hash != "GENESIS":
            print(f"[Block {block_index}] Invalid: first block must have prev_hash = 'GENESIS'.")
            return False
    else:
        if prev_hash != previous_block_hash:
            print(f"[Block {block_index}] Invalid: prev_hash does not match previous block hash.")
            return False

    # 3. Check Merkle root from body
    recomputed_merkle_root = compute_merkle_root_from_certs(body)
    if recomputed_merkle_root != merkle_root:
        print(f"[Block {block_index}] Invalid: Merkle root does not match body.")
        return False

    # 4. Check PoA slot rule
    try:
        slot_index = get_current_slot_index(timestamp)
    except ValueError as e:
        print(f"[Block {block_index}] Invalid: {e}")
        return False

    expected_proposer = get_slot_owner(slot_index)
    slot_start, slot_end = get_slot_start_end(slot_index)

    if proposer_id != expected_proposer:
        print(
            f"[Block {block_index}] Invalid: proposer_id {proposer_id} "
            f"is not the expected proposer {expected_proposer} for slot {slot_index}."
        )
        return False

    if not (slot_start <= timestamp < slot_end):
        print(
            f"[Block {block_index}] Invalid: timestamp {timestamp} is outside "
            f"slot interval [{slot_start}, {slot_end})."
        )
        return False

    # 5. Check block signature
    if not verify_block_signature(header, block_signature):
        print(f"[Block {block_index}] Invalid: block signature is not valid.")
        return False

    print(f"[Block {block_index}] Valid.")
    return True


def verify_chain() -> bool:
    block_files = sorted(CHAIN_DIR.glob("block_*.json"))

    if not block_files:
        print("No blocks found in data/chain/")
        return False

    previous_block_hash = None

    for i, block_path in enumerate(block_files):
        block = load_json(block_path)

        is_valid = verify_block(
            block=block,
            previous_block_hash=previous_block_hash,
            block_index=i
        )

        if not is_valid:
            print("\nChain verification failed.")
            return False

        previous_block_hash = sha256_of_json(block)

    print("\nChain verification successful: all blocks are valid.")
    return True


if __name__ == "__main__":
    verify_chain()