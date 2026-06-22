# DGB Sentinel AI Shield v4 Test Matrix

Author attribution: DarekDGB

## Scope

This matrix covers the V4.5C DGB Sentinel AI pilot component-verdict contract.

The goal is to prove one Shield component can produce a signed v4 verdict envelope after the QWG pilot pattern has been proven.

## Positive Tests

| Test | Expected result |
|---|---|
| build unsigned DGB Sentinel AI v4 payload | deterministic payload with `contract_version: 4` |
| add required classical + ML-DSA test signatures | signed envelope validates |
| validate with matching context hash | verification summary returned |
| verify required role | `shield_component_sentinel_ai` only |

## Negative Tests

| Test | Expected result |
|---|---|
| tampered signature | fail closed |
| changed context hash after signing | fail closed |
| missing ML-DSA required signature | fail closed |
| duplicate algorithm entry | fail closed |
| unsupported algorithm | fail closed |
| wrong domain tag | fail closed |
| wrong signed payload hash | fail closed |
| revoked key | fail closed |
| artifact outside key validity window | fail closed |
| forbidden authority metadata | fail closed |
| null in signed payload | fail closed |
| float in signed payload | fail closed |
| duplicate JSON key while parsing | fail closed |

## Required CI Gate

```text
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
```

## Authority Boundary

Passing these tests proves only the DGB Sentinel AI v4 component-verdict contract shape.

It does not grant transaction-signing authority, broadcast authority, DigiByte consensus authority, or AdamantineOS final authority.
