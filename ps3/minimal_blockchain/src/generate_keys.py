from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from config import KEYS_DIR
from utils import ensure_dir


USERS = ["Daniela", "Andrea", "Brian", "Gri"]


def generate_ecc_keypair(user_id: str):
    """
    Generates one ECC key pair for a participant and stores it in PEM format.

    The private key is used for signing certificates and blocks.
    The public key is later used by other participants to verify signatures.
    """
    ensure_dir(KEYS_DIR)

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    sk_path = KEYS_DIR / f"{user_id}_sk.pem"
    pk_path = KEYS_DIR / f"{user_id}_pk.pem"

    with open(sk_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(pk_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print(f"Generated keys for {user_id}")


if __name__ == "__main__":
    for user in USERS:
        generate_ecc_keypair(user)