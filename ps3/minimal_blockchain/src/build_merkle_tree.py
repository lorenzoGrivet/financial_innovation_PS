from pathlib import Path

from config import CERTS_DIR, PROOFS_DIR
from utils import load_json, save_json, ensure_dir, encode_for_hashing, sha256_bytes

def find_certificate_index(leaves_info, target_cert_name):
    """
    Returns the position of a certificate inside the leaf list.

    The proof depends on the position of the leaf in the ordered certificate set,
    so we need this index before generating the path.
    """
    for i, item in enumerate(leaves_info):
        if item["cert_name"] == target_cert_name:
            return i
    raise ValueError(f"Certificate not found: {target_cert_name}")

def hash_certificate(cert: dict) -> str:
    """
    Computes the Merkle leaf associated with one certificate.

    The full certificate object is hashed, not only the payload, so the leaf
    commits both to the notarized information and to its signature.
    """
    return sha256_bytes(encode_for_hashing(cert))


def hash_pair(left_hash: str, right_hash: str) -> str:
    """
    Parent hash = SHA256((left_hash + right_hash).encode('utf-8'))
    """
    return sha256_bytes((left_hash + right_hash).encode("utf-8"))


def get_certificate_files():
    return sorted(CERTS_DIR.glob("*.json"))


def build_leaf_nodes():
    """
    Loads certificates and prepares the list of leaves used to build the tree.

    Along with the hash, we also keep the file name and path so that proofs can
    later be associated with the corresponding certificate.
    """
    cert_files = get_certificate_files()
    leaves = []

    for cert_path in cert_files:
        cert = load_json(cert_path)
        leaf_hash = hash_certificate(cert)
        leaves.append({
            "cert_path": str(cert_path),
            "cert_name": cert_path.name,
            "leaf_hash": leaf_hash
        })

    return leaves


def build_merkle_tree_from_leaves(leaf_hashes):
    """
    Builds the Merkle tree level by level.

    levels[0] contains the leaves.
    levels[-1][0] is the Merkle root.

    When a level has an odd number of nodes, the last hash is duplicated.
    """
    if not leaf_hashes:
        raise ValueError("No leaf hashes provided.")

    levels = [leaf_hashes]

    current_level = leaf_hashes

    while len(current_level) > 1:
        next_level = []

        if len(current_level) % 2 == 1:
            current_level = current_level + [current_level[-1]]

        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1]
            parent = hash_pair(left, right)
            next_level.append(parent)

        levels.append(next_level)
        current_level = next_level

    return levels


def get_merkle_root(levels):
    return levels[-1][0]


def generate_merkle_proof(levels, target_index):
    """
    Generates a Merkle proof for the leaf at target_index.
    Proof format:
    [
      {"position": "right", "hash": "..."},
      {"position": "left", "hash": "..."},
      ...
    ]
    """
    proof = []
    index = target_index

    for level in levels[:-1]:
        working_level = level[:]

        if len(working_level) % 2 == 1:
            working_level.append(working_level[-1])

        if index % 2 == 0:
            sibling_index = index + 1
            sibling_position = "right"
        else:
            sibling_index = index - 1
            sibling_position = "left"

        proof.append({
            "position": sibling_position,
            "hash": working_level[sibling_index]
        })

        index = index // 2

    return proof


def main(target_cert_name=None):
    ensure_dir(PROOFS_DIR)

    leaves_info = build_leaf_nodes()

    if not leaves_info:
        print("No certificates found in data/certs/")
        return

    leaf_hashes = [item["leaf_hash"] for item in leaves_info]
    levels = build_merkle_tree_from_leaves(leaf_hashes)
    root = get_merkle_root(levels)

    print("Leaf nodes:")
    for i, item in enumerate(leaves_info):
        print(f"{i}: {item['cert_name']} -> {item['leaf_hash']}")

    print("\nMerkle Root:")
    print(root)

    # If no certificate name is provided, use the first one by default
    if target_cert_name is None:
        target_index = 0
    else:
        target_index = find_certificate_index(leaves_info, target_cert_name)

    target_cert = leaves_info[target_index]
    proof = generate_merkle_proof(levels, target_index)

    proof_data = {
        "target_cert_name": target_cert["cert_name"],
        "target_leaf_hash": target_cert["leaf_hash"],
        "target_index": target_index,
        "merkle_root": root,
        "proof": proof
    }

    proof_path = PROOFS_DIR / f"merkle_proof_{Path(target_cert['cert_name']).stem}.json"
    save_json(proof_path, proof_data)

    print(f"\nProof saved to: {proof_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage: python src/build_merkle_tree.py [certificate_name]")