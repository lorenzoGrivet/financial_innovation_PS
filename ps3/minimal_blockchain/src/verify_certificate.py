import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

from config import CERTS_DIR
from utils import load_json, encode_for_hashing


def verify_certificate(cert_path: Path) -> bool:
    """
    Verifies the signature of a certificate.

    The certificate is valid if the signature matches the deterministically
    encoded payload under the public key included in the certificate itself.
    """
    cert = load_json(cert_path)

    payload = cert["payload"]
    signature_b64 = cert["signature"]

    public_key = serialization.load_pem_public_key(
        payload["pk_bytes"].encode("utf-8")
    )

    signature = base64.b64decode(signature_b64)
    message = encode_for_hashing(payload)

    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def verify_all_certificates():
    cert_files = sorted(CERTS_DIR.glob("*.json"))

    if not cert_files:
        print("No certificates found in data/certs/")
        return

    valid_count = 0

    for cert_path in cert_files:
        is_valid = verify_certificate(cert_path)
        print(f"{cert_path.name}: {is_valid}")
        if is_valid:
            valid_count += 1

    print(f"\nValid certificates: {valid_count}/{len(cert_files)}")


if __name__ == "__main__":
    verify_all_certificates()