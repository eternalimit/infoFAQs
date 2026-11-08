# InfoFAQs GENESIS — Carry-forward and emergency-path control
Status: STAGING ONLY. No production DNS, TLS, hosting, repository visibility, or endpoint changes authorized by this commit.
Target: eternalimit/infoFAQs
Branch: consolidation/public-gateway-20261108
Entry: gateway/genesis/index.html

## Carry forward
- InfoFAQs / THE CUBE brand, Know More. Have Fun., YCI copyright, META METAL.
- Preserve original homepage, CATBOT 100, 10 FAQs, Marketplace, MINE.UNI, and all source histories unchanged.
- Preserve all private archives and repository access controls.
- Existing /mine/uni/ page is linked; no provider integration is asserted live.

## Cutoff rule
Legacy public endpoints and routes may be retired ONLY after an independently tested production cutover and a dependency inventory, with explicit endpoint-by-endpoint confirmation.
Do not sever emergency administrative access, rollback deployment, DNS recovery, backup storage, or incident response access.
Never point public traffic to a private archive. Never publish secrets.

## Release gates
1. Inventory active DNS/Cloudflare rules, host origin, redirects, integrations, and external links.
2. Compare source and deployed artifact SHA-256 computed from exact bytes.
3. Verify www and apex TLS, certificate chain, redirects, mobile and desktop navigation.
4. Execute and record 80 matrix checks (PASS / FAIL / UNVERIFIED).
5. Test rollback and emergency recovery paths independently.
6. Promote only with verified production target and explicit release approval.
7. After cutover, retire only superseded public endpoints, retaining recovery controls.
8. Record exact commits, observed results, timestamps, and receipt hashes.

## Provider boundaries
GitHub is verified as source provider. Cloudflare authoritative nameservers were identified; authenticated zone ownership, origin and TLS remain unverified. Other providers remain experimental, isolated under the private one.uni branch.

## Failure behavior
If any mandatory release check fails, leave existing public service intact; investigate and correct. No destructive cutoffs.
