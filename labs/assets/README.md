# Module B Evidence Templates

These audit-ready templates support the 1-day Train-the-Trainer MicroHack for
the "AI Platform on Microsoft Azure" Specialization checklist V1.8.1. Pupils
complete the forms using fictional Contoso customer scenarios anonymized as
Customer A, Customer B, and Customer C.

## Evidence Naming Convention

Use `[ControlRef]_[DocumentType]_v[N]` in titles, file exports, screenshots, and
handoff notes.

Examples:

- `B11_PortfolioAssessment_v1`
- `B21_HLD_CustomerA_v1`
- `B23_FoundryEvaluationResults_CustomerA_v1`
- `B42_Runbook_IncidentResponse_CustomerA_v1`

## Template Index

| Template | Module B control | Lab |
| --- | --- | --- |
| [B11_PortfolioAssessment.md](B11_PortfolioAssessment.md) | B.1.1 Portfolio assessment | Lab 1 |
| [B21_SolutionDesign.md](B21_SolutionDesign.md) | B.2.1 Solution design | Lab 2 |
| [B22_WellArchitectedReview.md](B22_WellArchitectedReview.md) | B.2.2 Azure Well-Architected Review | Lab 3 |
| [B23_PoCPilot.md](B23_PoCPilot.md) | B.2.3 PoC or pilot | Lab 4 |
| [B31_DeploymentPlan.md](B31_DeploymentPlan.md) | B.3.1 Deployment plan | Lab 5 |
| [B41_ValidationTesting.md](B41_ValidationTesting.md) | B.4.1 Validation testing | Lab 6 |
| [B42_PostDeploymentDocs.md](B42_PostDeploymentDocs.md) | B.4.2 Post-deployment documentation | Lab 7 |

## How Trainers Re-Skin Contoso

1. Keep the fictional source documents in `labs/data/contoso` license-free.
2. Replace company labels with workshop-safe names only, such as Customer A,
   Customer B, and Customer C.
3. Do not insert real tenant IDs, secrets, customer names, contracts, or
   production screenshots.
4. Update scenario facts consistently across the portfolio, design, pilot,
   deployment, validation, and BAU documentation templates.
5. If using different fictional data, update
   `labs/data/eval/golden_qa.jsonl` so evaluation answers remain grounded.

## Trainer Notes

- Each template contains a header table, fill-in fields, guidance notes, and an
  Acceptance / Definition of Done checklist.
- The templates mirror specialization deliverable vocabulary: HLD, LLD,
  runbook scenarios, KT plan audiences, 4-week hypercare, and Definition of
  Done.
- Markdown linting is expected to run in CI.
