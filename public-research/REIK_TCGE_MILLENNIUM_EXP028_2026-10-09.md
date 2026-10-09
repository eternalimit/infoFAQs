# REIK/TCGE Millennium Research — Experiment 028

**Public research evidence notice — 2026-10-09**  
**Status: verified finite experiment; P versus NP HOLD.**  
**Scope: local research and checks, not an external solver benchmark or Millennium Prize solution.**

This is a sanitized public record of Experiment 028 in the preserved REIK/TCGE research sequence. It is mirrored to public repositories to make the claim and its limitations discoverable. It is **not** a new GitHub-backed copy of the full evidence archive, an external audit, or a signature.

## Immutable lineage

- Original unchanged `0/U/1` CNF kernel `kernel001.py`, SHA-256: `03a38cf8aa32b49e6dcdd8c22e900d4172827af7c59402490dce5439bdfb9402`
- Verified Experiment 027 parent manifest SHA-256: `46a9a7ec8a6c3fdcffaae43ced90d726de8cc4d0832af8b08f67603689080810`
- Verified Experiment 027 258-event receipt tip: `d7cfa6376acde51f2c3bbc97cd01b6aa12cd22ce684cdb8aef625420ac4626e4`
- Experiment 028 sealed evidence manifest SHA-256: `fd140b98467001f01967dd9c470325a5aa7d57a2adbb26d102632ab933e29789`
- Experiment 028 chronological successor tip SHA-256: `a452640c04c91322ede44cc0e3374ff427fb7f1ee5b4d10252047f269ce7632e`
- 258 inherited + 16 successor = **274** locally verified receipt links. The hashes refer to exact separately preserved artifact bytes, not to this explanatory Markdown file.

## Formal object and finite verified results

Under a partial Boolean assignment, the original CNF evaluator returns:

- `0`: at least one CNF clause is falsified;
- `1`: all clauses are already satisfied;
- `U`: unresolved, neither terminal condition has been demonstrated.

`U` does not assert a satisfying completion; `0` and `1` persist under consistent extension. This is a partial-assignment state machine, **not** a general algorithmic complexity result.

The new independent verification program checked four **inherited, locally constructed** UNSAT derivations by (i) reconstructing each resolution step and (ii) independently confirming reverse unit propagation (RUP) against the **entire accumulated clause database**:

| Local UNSAT input | Verified resolution and RUP additions |
|---|---:|
| 256-variable inconsistent XOR cycle | 1,023 |
| Deterministically permuted XOR cycle | 1,023 |
| Sign-flipped XOR cycle | 1,023 |
| Seeded contradictory CNF | 7 |
| **Total** | **3,076** |

Further *local finite* checks: three SAT models (2,095 clause evaluations), exact comparison of 1,065 original SATLIB clauses, 729 partial assignments over a six-variable example, 1,040 terminal-state extensions, 12 falsification controls, and 33 evidence-file SHA-256 checks.

## Explicit HOLD boundaries

- **HOLD:** independently sourced, original-byte, fully active 256-variable SAT **and** UNSAT benchmark pair, with independently certified answers.
- **HOLD:** locally downloaded, independently SHA-256-verified, actually executed dedicated Kissat/CaDiCaL/MiniSat binary.
- **HOLD:** independent third-party DRAT/LRAT proof-checker execution on a proof emitted by that dedicated solver.
- **NOT PERFORMED:** any new qualifying head-to-head solver-performance comparison in Experiment 028.
- **HOLD:** universal polynomial-time SAT algorithm, P = NP, P ≠ NP, or any Millennium Prize solution.

The original-byte external SATLIB specimen has **250 variables**, not 256. Public metadata for a 256-variable candidate and a checksum published for a Kissat executable were identified, but the required local acquisition and verification were **not** completed. Local transformations are not independent held-out data. Z3 was not substituted for the unavailable dedicated solver.

## Research controls and reproducibility

Preserve all eight existing FIDELITY principles: Identity, Provenance, Chronology, Independence, Method/Object Separation, Non-Expansion, Falsification Persistence, and Uncertainty.

Given the separately sealed original Experiment 028 evidence bundle, reproduce using `python integrity028.py`, `python verify_receipts028.py`, and `python verify028.py`. The full bundle and checker source have **not** been attached to this public repository merely by committing this notice. A GitHub commit makes this *public account of evidence* visible; it does not re-run or independently validate the tests, prove authorship of third-party material, create an external signature, or establish on-chain anchoring.

**Public communication rule:** repeat verified evidence faithfully; keep unverifiable extensions at HOLD; exclude private credentials and unrelated personal information. Additional publication requires actual writes and commit receipts—there is no autonomous background public sync.

*Recorded for public inspection as a bounded REIK/TCGE research handoff. The preserved finite conclusions are reproducible from the sealed evidence artifact; the universal mathematical claim remains HOLD.*
