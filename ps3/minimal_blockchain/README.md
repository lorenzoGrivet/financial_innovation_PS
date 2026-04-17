# Minimal Blockchain: Decentralized Document Notary (PoA)

## 1. Overview

This project implements a minimal blockchain-based system for decentralized document notarization. The goal is to prove that a user possessed a document at a given time without relying on a central authority.

The system combines cryptographic signatures, Merkle trees, and a Proof of Authority (PoA) blockchain.

---

## 2. Methodology

The system follows this pipeline:

```
Documents → Certificates → Merkle Tree → Blocks → Blockchain
```

### Certificates

Each user generates an ECC key pair and signs a certificate:

[
c_i = (\text{user_id}, \text{public_key}, \text{document_hash}, \text{timestamp})
]

The document is represented by its SHA-256 hash. The certificate is signed using the user’s private key, ensuring authenticity.

---

### Merkle Tree

Certificates are aggregated into a Merkle tree:

[
\ell_i = \text{SHA256}(\text{encode}(cert_i))
]

[
h = \text{SHA256}(h_{\text{left}} | h_{\text{right}})
]

The root hash provides a compact commitment to all certificates. Merkle proofs allow efficient verification of membership.

---

### Block Structure

Each block contains:

* Header:
  [
  B_h = (\text{prev_hash}, \text{merkle_root}, \text{timestamp}, \text{proposer_id})
  ]

* Body: list of certificates

* Signature:
  [
  \sigma_B = \text{Sign}_{sk}(\text{SHA256}(\text{encode}(B_h)))
  ]

---

### Proof of Authority (PoA)

Time is divided into slots:

[
\text{slot_index} = \left\lfloor \frac{T - \text{GENESIS_TIME}}{\text{SLOT_DURATION}} \right\rfloor
]

Only one proposer can create a block per slot:

[
\text{slot_index} \bmod \text{GROUP_SIZE} = \text{proposer_id}
]

---

## 3. Multi-User Simulation

The system simulates four participants:

| proposer_id | User    |
| ----------- | ------- |
| 0           | Daniela |
| 1           | Andrea  |
| 2           | Brian   |
| 3           | Gri     |

Each participant has independent keys and signs their own certificates. Block creation follows the PoA slot rule.

---

## 4. Verification

The blockchain is validated by checking:

* Correct block linking (`prev_hash`)
* Merkle root consistency
* Valid block signatures
* PoA rules (correct proposer and slot)
* No blocks from the future

Merkle proofs are also verified for multiple certificates, showing that the method generalizes beyond a single case.

---

## 5. Execution

```bash
python src/generate_keys.py
python src/create_certificate.py
python src/verify_certificate.py
python src/build_merkle_tree.py <certificate_name>
python src/verify_merkle_proof.py <proof_filename>
python src/create_block.py <proposer_id>
python src/verify_chain.py
```

---

## 6. Economic Perspective

The system is permissioned (PoA). To make it permissionless, it would require:

* PoW or PoS instead of PoA
* Incentive mechanisms
* Protection against Sybil attacks

This introduces trade-offs between security, cost, and decentralization.

---

## 7. Conclusion

The project demonstrates a complete minimal blockchain pipeline, combining cryptographic identity, Merkle aggregation, and PoA consensus to build a verifiable decentralized notary system.
