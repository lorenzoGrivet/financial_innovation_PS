from config import CERTS_DIR, PROOFS_DIR
from utils import load_json, encode_for_hashing, sha256_bytes


def hash_certificate(cert: dict) -> str:
    return sha256_bytes(encode_for_hashing(cert))


def hash_pair(left_hash: str, right_hash: str) -> str:
    return sha256_bytes((left_hash + right_hash).encode("utf-8"))


def verify_merkle_proof(cert: dict, proof: list, expected_root: str) -> bool:
    """
    Verifies that a certificate belongs to a Merkle tree with a given root.

    Starting from the leaf corresponding to the certificate, the proof
    reconstructs the path up to the root by iteratively combining sibling
    hashes. The result must match the expected Merkle root.
    """
    current_hash = hash_certificate(cert)

    for step in proof:
        sibling_hash = step["hash"]
        position = step["position"]

        if position == "right":
            current_hash = hash_pair(current_hash, sibling_hash)
        elif position == "left":
            current_hash = hash_pair(sibling_hash, current_hash)
        else:
            raise ValueError(f"Invalid proof position: {position}")

    return current_hash == expected_root


def main(proof_filename=None):
    if proof_filename is None:
        proof_files = sorted(PROOFS_DIR.glob("*.json"))

        if not proof_files:
            print("No proof files found in data/proofs/")
            return

        proof_path = proof_files[0]
    else:
        proof_path = PROOFS_DIR / proof_filename

        if not proof_path.exists():
            print(f"Proof file not found: {proof_path}")
            return

    proof_data = load_json(proof_path)

    cert_name = proof_data["target_cert_name"]
    expected_root = proof_data["merkle_root"]
    proof = proof_data["proof"]

    cert_path = CERTS_DIR / cert_name
    cert = load_json(cert_path)

    is_valid = verify_merkle_proof(cert, proof, expected_root)

    print(f"Proof file: {proof_path.name}")
    print(f"Certificate: {cert_name}")
    print(f"Expected root: {expected_root}")
    print(f"Merkle proof valid: {is_valid}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage: python src/verify_merkle_proof.py [proof_filename]")