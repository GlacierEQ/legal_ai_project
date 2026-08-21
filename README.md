# Legal AI Project

## Layer 1 — Recruiter: what this is and why it matters

Legal AI Project is an application workspace for a legal-AI system with frontend, backend, deployment, documentation, testing, and project-planning surfaces. It is meant to turn a difficult class of legal-information workflows into something inspectable, buildable, and maintainable rather than a one-off demonstration.

It matters because legal-AI work is most useful when product experience, system design, environment configuration, and testable implementation are available in the same repository. The project is a platform for building and evaluating those capabilities; it does not itself establish legal advice, a legal conclusion, or the truth of any case record.

## Layer 2 — Master: architecture and distinctive method

The repository combines application code, a frontend, Docker Compose configuration, environment templates, specifications, scripts, tests, and architecture/project documentation. The distinctive method is not that it uses AI in isolation. It gives the system surrounding structure: deployment, documentation, testing, and configuration sit beside the application layers so the implementation can be understood as a complete technical workflow.

| Checked-in surface | Role in the system |
|---|---|
| `app/`, `frontend/` | Application and client implementation areas. |
| `docker-compose.yml` | Local multi-service composition surface. |
| `requirements.txt` | Python dependency declaration. |
| `docs/`, `architecture_technique.md` | System and technical documentation. |
| `tests/`, `scripts/` | Validation and operational support. |
| `.env.example` and related templates | Environment configuration references. |

An ordinary legal-information prototype can hide its assumptions in a notebook or single UI. This project is stronger when its architecture, runtime configuration, tests, and application surfaces stay visible and mutually consistent.

## Layer 3 — Machine: current integration surface

| Surface | Kind | Machine-use guidance |
|---|---|---|
| `docker-compose.yml` | Service composition | Use the checked-in file as the local deployment entry point after reviewing environment requirements. |
| `requirements.txt` | Python dependency declaration | Install in an isolated environment appropriate to the project. |
| `app/`, `frontend/` | Application interfaces | Inspect local docs and tests for actual start commands and integration paths. |
| `.env.example`, `.env.auth`, `.env.llm`, `.env.pinecone` | Configuration references | Treat as templates; never commit live credentials or personal data. |
| `tests/` | Verification surface | Run and extend tests before relying on a changed behavior. |

No OpenAPI, protobuf, or stable public external API is declared in the root README material inspected here. Machine clients should follow the checked-in application and deployment documentation instead of assuming a contract.

## Layer 4 — Mesh: family and integration map

**Monolith route:** [GlacierEQ/monolith](https://github.com/GlacierEQ/monolith) maps the repository estate and routes discovery across domains.

**Legal mesh position:** This repository is entered through the **Legal Details** branch, in **Evidence-ledger, case-specific context, and detailed working surfaces**. The branch is a navigation lens; it does not replace this repository’s local history, files, or responsibilities.

| Mesh relationship | This repository’s role | Boundary |
|---|---|---|
| Legal Data | may consume clearly attributed legal-information inputs and retrieval results | Source references and provenance stay attributable to their record-bearing owner. |
| Legal Tech | contains application, frontend, deployment, and test surfaces | Tools and derived outputs do not replace native records or source context. |
| Legal Details | may present derived legal workflows without elevating output into a source record | Matter-specific context and work product stay distinguishable from source material. |

**Entry and peer links:** [Legal Powerhouse](https://github.com/GlacierEQ/legal-powerhouse) is the legal-engineering gateway; [DOCKETS](https://github.com/GlacierEQ/DOCKETS) is a source-first docket routing surface; and [SUPERLUMINAL_CASE_MATRIX](https://github.com/GlacierEQ/SUPERLUMINAL_CASE_MATRIX) is a case-model foundation candidate. These are useful mesh entry points, not exclusive or authority-transferring heads.
