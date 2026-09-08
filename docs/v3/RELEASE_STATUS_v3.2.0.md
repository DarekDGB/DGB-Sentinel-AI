# Sentinel AI - Historical Shield v3.2.0 Release Status

Author attribution: DarekDGB
Status: Historical compatibility record

## Retained scope

The v3.2.0 series established manifest, reason-ID, evidence-family, and
canonical-verdict locks. The frozen v3 manifest retains package_version
3.2.0 and contract_version 3 inside the current distribution.

This record is not a pending instruction to create or move a v3.2.0 tag.
Current candidate status and gates are recorded in
[the v4.0.0 release status](../v4/RELEASE_STATUS_v4.0.0.md).

## Historical verification requirements

The v3 checklist required green CI, its coverage gate, complete registries,
negative verdict tests, documentation agreement, a fresh-ZIP review, and
authorized bypass review. Those requirements and any historical review
results do not establish v4 release readiness or a new security audit.

## Authority boundary

The retained v3 output is evidence only. It cannot sign or broadcast
transactions, hold wallet keys, change DigiByte consensus, override the Shield
Orchestrator, or approve AdamantineOS execution directly.

AdamantineOS consumes Shield through the deterministic Orchestrator receipt.
A Shield ALLOW is not final signing or execution approval.

## Independent release lines

AdamantineOS has its own release line and authorization gates. Historical
references to its v2.2.0 WSQK v2 upgrade do not prescribe its current version
or authorize any tag. Use the current living roadmap for release decisions.
