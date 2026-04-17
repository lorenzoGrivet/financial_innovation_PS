import time
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from config import KEYS_DIR, CERTS_DIR, DOCUMENTS_DIR
from utils import ensure_dir, sha256_file, encode_for_hashing, save_json


DOCUMENT_ASSIGNMENTS = {
    "Daniela": ["doc1.txt", "doc2.txt"],
    "Andrea": ["doc3.txt", "doc4.txt"],
    "Brian": ["doc5.txt", "doc6.txt"],
    "Gri": ["doc7.txt", "doc8.txt"],
}


def load_private_key(path: Path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def sign_payload(private_key, payload: dict) -> str:
    message = encode_for_hashing(payload)
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode("utf-8")


def create_certificate(user_id: str, document_filename: str, cert_name: str = None):
    ensure_dir(CERTS_DIR)

    sk_path = KEYS_DIR / f"{user_id}_sk.pem"
    pk_path = KEYS_DIR / f"{user_id}_pk.pem"
    doc_path = DOCUMENTS_DIR / document_filename

    private_key = load_private_key(sk_path)
    public_key_bytes = load_public_key_bytes(pk_path)

    payload = {
        "user_id": user_id,
        "pk_bytes": public_key_bytes.decode("utf-8"),
        "document_hash": sha256_file(doc_path),
        "timestamp": int(time.time())
    }

    signature_b64 = sign_payload(private_key, payload)

    cert = {
        "payload": payload,
        "signature": signature_b64
    }

    if cert_name is None:
        doc_stem = Path(document_filename).stem
        cert_name = f"cert_{user_id}_{doc_stem}.json"

    cert_path = CERTS_DIR / cert_name
    save_json(cert_path, cert)

    print(f"Certificate saved to: {cert_path}")


def create_all_certificates():
    for user_id, documents in DOCUMENT_ASSIGNMENTS.items():
        for document_filename in documents:
            create_certificate(user_id=user_id, document_filename=document_filename)


if __name__ == "__main__":
    create_all_certificates()