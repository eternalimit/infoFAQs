# Research Preprint: Reversible Mapping of 8-Bit Octets to Twelve Ternary Digits

**Version:** 1.0 — 2026-11-08  
**Author/attribution:** Richard Stein / Your Company Incorporated (proposed research record)  
**Status:** Computationally tested encoding proposal; NOT a published standards specification or peer-reviewed paper.  
**Scope:** Standard ASCII, 8-bit octets, and fixed-width 12-trit encoding.  
**Repository publication:** This Markdown preprint is not authorization to deploy a website, mint a token, or change private archives.

## Abstract
We specify and exhaustively test a lossless, fixed-width mapping from an 8-bit octet to twelve ternary digits (trits). The mapping encodes an unsigned byte integer in base 3, padded with leading zero trits to exactly twelve positions. Standard ASCII is a 7-bit character repertoire encoded here as byte values 0–127 with a zero high bit. All 256 byte values round-trip without collision. The scheme is mathematically valid but inefficient in capacity: twelve trits allow 531,441 values, whereas an octet has 256. It is not standard ASCII, nor evidence of blockchain minting, cryptographic security, or deployment.

## 1. Definitions and hypotheses
ASCII, per ANSI X3.4 / RFC 20, defines 128 code positions, 0 through 127. An octet holds 8 binary digits and has 256 values. A trit is one ternary digit in {0,1,2}. Twelve trits have 3^12 = 531441 possible sequences.

H1: Every octet b in [0,255] maps to a unique 12-trit sequence.  
H2: Decoding the sequence returns the original octet.  
H3: ASCII input bytes in [0,127] retain their original ASCII code positions.  
H4: Arbitrary twelve-trit sequences are not necessarily valid encoded octets; decoding MUST reject values above 255.

## 2. Proposed encoding and decoding
**Encode:** For integer b in [0,255], let E(b) be the base-3 representation of b, left-padded with '0' to length 12.  
**Decode:** For a 12-character string t consisting only of 0,1,2, compute D(t) = sum(t[i] * 3^(11-i)) for i=0..11. Reject if D(t) > 255. Reject malformed lengths or digits.

Pseudocode:
```python
def encode_octet(b):
    assert isinstance(b, int) and 0 <= b <= 255
    digits = ""
    for _ in range(12):
        digits = str(b % 3) + digits
        b //= 3
    return digits

def decode_octet(t):
    if len(t) != 12 or any(c not in "012" for c in t):
        raise ValueError("invalid trit string")
    n = int(t, 3)
    if n > 255:
        raise ValueError("outside octet domain")
    return n
```

## 3. Reproducible exhaustive test
Test all 256 integers b = 0..255: verify E(b) has length 12, contains only digits 0/1/2, D(E(b)) == b, and the 256 encodings are distinct. Verify ASCII examples and boundary values. This test was independently executed in a JavaScript runtime for this preprint; 256/256 round trips passed, 256 unique encodings. This is a mathematical unit test, not a network or GitHub CI run.

| Byte decimal | 8-bit binary | 12-trit encoding |
|---:|---|---|
| 0 | 00000000 | 000000000000 |
| 32 (space) | 00100000 | 000000001012 |
| 48 ('0') | 00110000 | 000000001210 |
| 65 ('A') | 01000001 | 000000002102 |
| 80 ('P') | 01010000 | 000000002222 |
| 127 | 01111111 | 000000011201 |
| 128 | 10000000 | 000000011202 |
| 255 | 11111111 | 000000100110 |

The string `PUBLIC BCC` is 10 ASCII bytes and therefore becomes 120 trits under this scheme. The strings `0120`, `1201`, and `2012` are valid ternary digit strings but are **not** valid single-octet encodings under this specification because they are not 12 trits long. No specific semantics are assigned to these motifs without a separate documented protocol.

## 4. Results and limitations
**PASS (unit tests):** 256/256 byte round trips, uniqueness 256/256, valid fixed-width output.  
**Capacity:** 3^12 = 531441 possible 12-trit strings; only 256 are assigned byte encodings.  
**Minimum trits:** 6, because 3^5 = 243 < 256 <= 3^6 = 729. Twelve trits are a deliberate padding choice, not the minimum.  
**ASCII:** ASCII is 7-bit; 8-bit storage is a byte representation, not an 8-bit ASCII standard.  
**Security:** This mapping is encoding only; it does not encrypt, authenticate, hash, or provide integrity protection.  
**Deployment:** No live website, GitHub workflow, ledger, token, or mint is validated by the unit test.  
**External review:** No independent peer review has been performed.

## 5. Conclusion
A fixed 8-bit-to-12-trit mapping is mathematically valid and lossless when decoding enforces the byte domain. It can be used as an experimental data representation but must not be conflated with standard ASCII, security, or financial transaction validation.

## References
- ANSI X3.4, *American National Standard Code for Information Interchange (ASCII)*.
- RFC 20, *ASCII format for Network Interchange*, https://www.rfc-editor.org/rfc/rfc20
- RFC 3629, *UTF-8, a transformation format of ISO 10646*, https://www.rfc-editor.org/rfc/rfc3629

© 2026 Your Company Incorporated. All rights reserved. Research attribution supplied by project owner; no claim of peer-review acceptance.
