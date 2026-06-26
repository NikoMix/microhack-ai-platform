# Evidence Filename Check

## Description

Validate evidence filenames against the `[ControlRef]_[DocumentType]_v[N]` convention used in the MicroHack.

## Inputs

- `name`: Candidate filename, for example `B.2.1_SolutionDesign_v1.pdf`.

## Steps

1. Use the custom MCP tool `validate_evidence_filename(name)` when available.
2. Confirm the control reference is a known Module B control.
3. Confirm document type is descriptive and the version is a positive integer.
4. Recommend a corrected filename when invalid.
5. Remind pupils to keep customer names anonymized in evidence.
