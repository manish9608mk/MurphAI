# MurphAI --- Project History & Current State

> Master handoff document for continuing MurphAI in a new chat.

## 1. Product Vision

MurphAI is being built as a serious startup/product, not merely a demo
or interview project.

Core positioning:

**Portable Proof-of-Work & Professional Reputation Infrastructure**

Long-term flow:

``` text
Worker → Job → Customer → Assignment → Work → Evidence
→ Customer Confirmation → Payment / Invoice
→ Verified Reputation → Portable Professional History
→ ML Feedback Loop
```

Initial market direction: electricians first, then plumbers, mechanics,
technicians, construction/home-service workers, and other gig/workforce
categories.

MurphAI should not become a generic chatbot, LinkedIn clone, generic job
portal, generic AI wrapper, or generic freelancer marketplace.

The defensibility direction is first-party verified work data, evidence,
feedback loops, worker-owned history, trust, integrations, distribution,
and accumulated data.

------------------------------------------------------------------------

## 2. V1 Product Flow

``` text
Customer creates job
        ↓
AI understands job
        ↓
AI helps match workers
        ↓
Worker accepts assignment
        ↓
Work is performed
        ↓
Evidence is submitted
        ↓
Customer confirms completion
        ↓
Payment / invoice
        ↓
Verified reputation
        ↓
ML learns from real outcomes
```

ML is intended to solve real product problems rather than being added
just to make the project look like an AI project.

Future ML areas discussed:

-   worker-job matching
-   success prediction
-   skills/experience intelligence
-   reputation intelligence
-   pricing intelligence
-   anomaly/fraud detection
-   recommendations

------------------------------------------------------------------------

## 3. Original Learning Roadmap

``` text
Phase 0  — Python Foundation
Phase 1  — DSA
Phase 2  — Linux
Phase 3  — Networking
Phase 4  — Git & GitHub
Phase 5  — Docker
Phase 6  — AWS
Phase 7  — Kubernetes
Phase 8  — Terraform
Phase 9  — CI/CD
Phase 10 — Monitoring
Phase 11 — Projects
Phase 12 — Resume
Phase 13 — Placements & Interviews
```

MurphAI became the main practical project for applying these concepts.

------------------------------------------------------------------------

## 4. Backend Foundation

Main stack:

-   Python
-   FastAPI
-   Uvicorn
-   SQLAlchemy
-   PostgreSQL
-   Alembic
-   Pydantic
-   JWT authentication
-   pytest

The initial milestone was a working FastAPI application with a root
endpoint. The backend was then hardened systematically.

------------------------------------------------------------------------

## 5. Security & Authentication

Completed:

``` text
Authentication                 ✅
JWT security                  ✅
Secret-key validation         ✅
```

Security decisions:

-   JWT secret is loaded from environment configuration.
-   Secret has a minimum length requirement.
-   JWT algorithm is restricted to `HS256`.
-   Real secrets stay in `.env`.
-   `.env` is ignored by Git.
-   An earlier exposed development secret was rotated.
-   Production secrets are planned for AWS Secrets Manager.
-   GitHub Actions production AWS access should use OIDC instead of
    long-lived access keys.

------------------------------------------------------------------------

## 6. Authorization / IDOR Review

Authorization was reviewed across the API/service layer.

Important ownership rules:

-   User update/delete → authenticated owner
-   Job create → authenticated customer
-   Job update/delete/status → job owner
-   Worker create → authenticated user
-   Worker update/delete → authorized owner
-   Skills modification → worker owner
-   Assignment create → job owner
-   Assignment view → job owner or assigned worker
-   Assignment accept/reject → assigned worker
-   Assignment cancel → job owner
-   Work create → assigned worker + accepted assignment
-   Work read → customer or worker
-   Work update/status → assigned worker
-   Evidence create → assigned worker + valid work state
-   Evidence read → customer or worker
-   Confirmation create → customer + completed work
-   Confirmation read → customer or assigned worker
-   Payment create → customer + completed/confirmed work
-   Payment action → customer
-   Payment read → customer or assigned worker
-   Reputation create → customer + valid completed/confirmed/paid work
-   Reputation read → reviewer/recipient

The authorization design was considered sound and was not unnecessarily
redesigned.

------------------------------------------------------------------------

## 7. Error Handling & Logging

Completed:

``` text
Global unexpected-error handling       ✅
Application logging                   ✅
Request IDs                            ✅
```

Unexpected exceptions are logged internally and return a generic
response:

``` json
{"detail": "Internal server error"}
```

Every request receives:

``` text
X-Request-ID
```

Request logging records:

-   request ID
-   method
-   path
-   status code
-   duration

Logs go to stdout so Docker/cloud logging systems can collect them.

Minor future refinement identified: middleware and the global exception
handler can currently produce two logs for the same unexpected
exception.

------------------------------------------------------------------------

## 8. Database

PostgreSQL became the application database.

SQLAlchemy engine uses:

``` python
pool_pre_ping=True
```

The request database dependency:

1.  creates a session
2.  yields it
3.  rolls back on exceptions
4.  closes the session

The correct dependency is in:

``` text
backend/app/core/dependencies.py
```

An unused duplicate database dependency was removed.

Alembic is used for migrations.

------------------------------------------------------------------------

## 9. Database Integrity

Database-level constraints were added:

``` text
Job budget:
budget > 0
constraint: ck_jobs_budget_positive

Worker experience:
experience_years >= 0
constraint: ck_workers_experience_non_negative
```

These were tested directly against PostgreSQL.

Important interview concept:

> API validation protects normal requests; database constraints protect
> the data even if another code path bypasses the API.

------------------------------------------------------------------------

## 10. Concurrency Hardening

MurphAI was hardened beyond simple CRUD.

### Assignment

Critical flows use row locking with `with_for_update()`.

Covered:

-   create assignment
-   accept assignment
-   reject assignment
-   cancel assignment

The accept flow locks relevant records and performs the state transition
transactionally.

Assignment tests reached:

``` text
20 passed
```

### Payment

Important decisions:

-   payment amount is derived from the job budget
-   `work_id` is unique
-   creating a payment locks Work
-   marking a payment as paid locks Payment

Future improvement identified:

``` text
Float money values
      ↓
Decimal / fixed precision
      ↓
Payment provider / ledger
```

SQLite tests do not prove PostgreSQL contention behavior.

### Work / Confirmation / Reputation

Critical flows were also protected:

-   Work creation locks Assignment.
-   Confirmation creation locks Work.
-   Reputation creation locks Work.
-   Duplicate records are prevented.
-   State conditions are rechecked while locked.

------------------------------------------------------------------------

## 11. Health & Readiness

The API has:

``` text
/health
/ready
```

`/health` confirms the application is running.

`/ready` executes a real database query:

``` sql
SELECT 1
```

If the database is unavailable, readiness returns a not-ready response.

Docker uses `/ready` for its healthcheck.

------------------------------------------------------------------------

## 12. Docker

MurphAI was containerized.

The Docker image:

-   uses Python 3.12 slim
-   contains backend and ML code
-   contains Alembic configuration
-   installs runtime dependencies
-   runs as a non-root `murphai` user
-   exposes port 8000
-   uses `/ready` as a healthcheck

Local Compose services:

``` text
postgres
backend
```

Named volumes:

``` text
postgres_data
mlflow_data
mlruns_data
```

This removed machine-specific Mac filesystem mounts.

------------------------------------------------------------------------

## 13. Docker Security Review

The image was checked for accidental inclusion of:

-   `.env`
-   database files
-   `.git`
-   `.DS_Store`

`.dockerignore` excludes development-only and sensitive files.

The rebuilt image contained no `.DS_Store`.

Approximate image size:

``` text
240,887,562 bytes
≈ 230 MB
```

This was considered acceptable for the current stage.

------------------------------------------------------------------------

## 14. ML System

The ML project structure includes:

``` text
ml/
├── data
├── features
├── models
├── evaluation
├── inference
├── registry
├── tracking
└── tests
```

Current model:

``` text
Random Forest
```

Purpose:

``` text
worker-job success prediction
```

------------------------------------------------------------------------

## 15. Feature Engineering

Features include:

``` text
worker_experience_years
worker_completed_jobs
worker_success_rate
worker_rating
required_skill_count
matched_skill_count
skill_match_ratio
location_match
distance_km
job_complexity
job_budget
skill_gap
worker_reliability_score
budget_per_complexity
```

Derived features include:

-   skill match ratio
-   skill gap
-   worker reliability score
-   budget per complexity

Inference returns features in the same order expected by training.

------------------------------------------------------------------------

## 16. MLflow

MLflow is used for:

-   experiment tracking
-   parameters
-   metrics
-   artifacts
-   model registration
-   model versioning
-   champion model selection

### Current development architecture

``` text
MurphAI
   │
   └── MLflow SDK
          ├── SQLite
          └── local mlruns
```

### Agreed production architecture

``` text
MurphAI
   │
   ▼
MLflow Tracking Server
   │
   ├── RDS PostgreSQL
   │      └── metadata / registry
   │
   └── S3
          └── model artifacts
```

This architecture was intentionally selected and should not be casually
redesigned.

------------------------------------------------------------------------

## 17. MLflow Portability

The MLflow configuration was changed so storage paths are
environment-configurable.

Development defaults:

``` text
project/mlflow.db
project/mlruns
```

Docker overrides:

``` text
MLFLOW_DB_PATH=/app/.mlflow/mlflow.db
MLFLOW_ARTIFACT_ROOT=/app/mlruns
```

The code no longer depends on a developer-specific Mac absolute path.

The same application can therefore run in:

``` text
Developer machine
Docker
CI
Production
```

with environment-specific storage.

------------------------------------------------------------------------

## 18. MLflow Model Registry

Registered model:

``` text
murphai-worker-job-matching
```

Active alias:

``` text
champion
```

The application resolves the champion model through MLflow rather than
using a hardcoded local model filename.

Conceptually:

``` text
champion alias
      ↓
MLflow Registry
      ↓
current model version
      ↓
inference
```

------------------------------------------------------------------------

## 19. Champion Model Inference

Main file:

``` text
ml/src/inference/champion_predict.py
```

Responsibilities:

1.  validate input
2.  preserve training feature order
3.  load champion model
4.  generate binary prediction
5.  generate probability
6.  return standardized output

Response:

``` text
predicted_success
success_probability
model_name
```

Current model name:

``` text
RandomForest
```

------------------------------------------------------------------------

## 20. Champion Model Caching

Champion inference was optimized with in-memory model caching so the
MLflow model does not need to be loaded from storage for every
prediction.

Explicit cache clearing is supported.

Dedicated champion inference tests reached:

``` text
10 passed
```

Backend ML tests reached:

``` text
13 passed
```

------------------------------------------------------------------------

## 21. Backend ML API

Endpoint:

``` text
POST /ml/predict
```

The endpoint:

-   requires authentication
-   validates input through Pydantic
-   delegates to the ML service
-   keeps ML implementation details outside the route

Architecture:

``` text
FastAPI route
      ↓
ML service
      ↓
Feature preparation
      ↓
Champion model
      ↓
JSON response
```

------------------------------------------------------------------------

## 22. ML Service

File:

``` text
backend/app/services/ml_service.py
```

Flow:

``` text
API request
   ↓
request.model_dump()
   ↓
prepare_inference_features()
   ↓
predict_with_champion()
   ↓
WorkerJobPredictionResponse
```

The API route should remain thin; ML logic belongs in the ML/service
layers.

------------------------------------------------------------------------

## 23. MLflow Tests

MLflow tests use isolated temporary storage.

Each test gets:

``` text
temporary SQLite tracking database
temporary artifact directory
```

Tests cover:

-   tracking URI
-   experiment creation
-   artifact location
-   run creation
-   parameter logging
-   metric logging
-   model logging

Latest focused result:

``` text
9 passed
```

------------------------------------------------------------------------

## 24. Docker MLflow Problem and Fix

Docker initially failed with:

``` text
sqlite3.OperationalError:
unable to open database file
```

Cause:

-   MLflow storage directories
-   named volume ownership
-   non-root runtime user

Fix:

1.  create `/app/.mlflow`
2.  create `/app/mlruns`
3.  create `murphai` user
4.  `chown` application/storage paths
5.  run as `murphai`

After the fix:

-   Docker training succeeded
-   model registration succeeded
-   champion alias worked
-   champion tests passed
-   full Docker tests passed

------------------------------------------------------------------------

## 25. ML Training Verification

A Docker training run produced:

``` text
Accuracy  = 0.6922
Precision = 0.7358
Recall    = 0.8314
F1        = 0.7807
ROC-AUC   = 0.7264
```

These are metrics from that specific development/training run, not a
claim about production performance.

------------------------------------------------------------------------

## 26. MLflow Persistence Verification

The champion model survived:

``` text
docker compose down
        ↓
containers removed
        ↓
named volumes preserved
        ↓
docker compose up -d
        ↓
same champion version/source run
```

This proved local Docker recreation did not lose MLflow state stored in
named volumes.

------------------------------------------------------------------------

## 27. GitHub Actions CI

CI was added at:

``` text
.github/workflows/ci.yml
```

Flow:

``` text
Checkout
   ↓
Python 3.12
   ↓
Install dependencies
   ↓
Prepare MLflow champion model
   ↓
Run tests
   ↓
Build Docker image
```

Triggers:

``` text
push → main
pull request → main
```

The workflow initially had two problems:

1.  missing CI application configuration
2.  missing MLflow champion registration

Both were fixed.

The final CI prepares/trains/registers a model before running
registry-dependent tests.

------------------------------------------------------------------------

## 28. Dependency Review

A temporary dependency-tree tool was used.

Result:

``` text
No dependency conflicts detected.
```

The tool was not added to project dependencies.

Requirements were not unnecessarily regenerated.

------------------------------------------------------------------------

## 29. Frontend

Frontend development also started.

Direction:

``` text
React
```

Architecture:

``` text
React frontend
      │
      │ HTTP / JSON
      ▼
FastAPI backend
      │
      ├── PostgreSQL
      └── ML pipeline
```

The browser should never directly connect to PostgreSQL.

For ML:

``` text
React
  ↓
POST /ml/predict
  ↓
FastAPI
  ↓
ML service
  ↓
Champion model
  ↓
JSON
  ↓
React UI
```

The landing page was being developed toward a real product interface.

------------------------------------------------------------------------

## 30. Production Configuration

Development:

``` text
.env
 ↓
local PostgreSQL
 ↓
MLflow SQLite
 ↓
local mlruns
```

Production target:

``` text
AWS Secrets Manager
        ↓
production environment
        ↓
RDS PostgreSQL
        ↓
MLflow Tracking Server
        ↓
S3 artifacts
```

Production should not depend on:

-   developer Mac paths
-   MLflow local SQLite
-   local artifact directories
-   long-lived AWS credentials

------------------------------------------------------------------------

## 31. Agreed AWS Architecture

Target:

``` text
                         Internet
                            │
                            ▼
                     Route 53 / DNS
                            │
                            ▼
                    HTTPS / ALB
                            │
                            ▼
                     ECS Fargate
                     MurphAI API
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
          RDS           MLflow Server   Secrets
       PostgreSQL            │          Manager
             │              │
             │       ┌──────┴──────┐
             │       ▼             ▼
             │   RDS PostgreSQL    S3
             │   MLflow metadata   artifacts
             │
             └──────────────┐
                            ▼
                       CloudWatch
```

CI/CD:

``` text
GitHub
   ↓
GitHub Actions
   ↓
Tests
   ↓
Docker build
   ↓
ECR
   ↓
ECS deployment
```

GitHub Actions should eventually authenticate to AWS with OIDC.

------------------------------------------------------------------------

## 32. Production Migration Sequence

The agreed sequence is:

``` text
1. Docker review
        ↓
2. Production config separation
        ↓
3. MLflow SQLite → PostgreSQL
        ↓
4. MLflow artifacts → S3
        ↓
5. AWS architecture
        ↓
6. Create RDS / S3 / Secrets etc.
        ↓
7. Deploy MLflow + MurphAI
        ↓
8. ECS Fargate
```

The purpose is to understand and prepare the system before creating
production infrastructure.

------------------------------------------------------------------------

## 33. AWS Work Started

AWS Console was opened.

The console showed AWS credits at the time:

``` text
US$120.00
120 days remaining
```

The console was displaying:

``` text
US East (N. Virginia)
```

The preferred deployment region discussed for MurphAI was:

``` text
ap-south-1
Mumbai
```

No production RDS/ECS/MLflow infrastructure had been created at the
stopping point.

------------------------------------------------------------------------

## 34. AWS CLI

AWS CLI was installed successfully:

``` text
AWS CLI 2.36.46
```

Installed under:

``` text
/Users/manishkumar/.local/share/aws-cli
```

The installer reported that this directory needs to be on PATH:

``` text
/Users/manishkumar/.local/bin
```

At the stopping point:

``` bash
aws --version
```

still returned:

``` text
zsh: command not found: aws
```

because PATH had not yet been updated.

Next commands:

``` bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
which aws
aws --version
```

After that, AWS identity should be checked before creating anything.

Do not blindly run `aws configure`; production authentication should
avoid long-lived access keys.

------------------------------------------------------------------------

## 35. Important Verified Test Checkpoints

The full regression suite progressed through:

``` text
238 passed
247 passed
248 passed
251 passed
253 passed
```

Latest confirmed full suite:

``` text
253 passed in 35.61s
```

Latest Docker full suite:

``` text
253 passed in 57.84s
```

------------------------------------------------------------------------

## 36. Important Git Commits

Important commits recorded:

``` text
285831b  add application logging
3d5b36e  harden database connection handling
0c6e91b  harden database transaction rollback
7fb1579  fix database transaction dependency
1f147a9  add database integrity constraints
263d212  add GitHub Actions CI
8d5ff87  fix CI test environment
8027e9a  fix CI MLflow champion setup
d224908  make MLflow storage portable across environments
abf3a8a  document production application configuration
bd1741f  cache champion model for inference
65dcfe1  make MLflow tracking environment configurable
```

Latest known clean Git checkpoint:

``` text
65dcfe1
make MLflow tracking environment configurable
```

The working tree was clean at the latest verified checkpoint.

------------------------------------------------------------------------

## 37. Interview-Level Explanation

A concise explanation:

> MurphAI is a production-oriented AI-enabled work platform that
> connects customers with skilled workers while building a verified
> proof-of-work and reputation graph. The backend uses FastAPI and
> PostgreSQL, with JWT authentication, authorization, transactional
> workflows, database constraints, concurrency controls, Docker, and
> automated tests. The ML pipeline uses feature engineering and a Random
> Forest model, with MLflow handling experiments, artifacts, model
> registration, and a champion alias. Development uses local MLflow
> SQLite and filesystem artifacts, while the production target uses an
> MLflow Tracking Server backed by PostgreSQL and S3, deployed as part
> of an AWS architecture using ECS Fargate and supporting services.

------------------------------------------------------------------------

## 38. Engineering Principles Established

For every major change:

``` text
1. Understand why
2. Inspect existing code
3. Avoid duplicate functionality
4. Make the smallest correct architectural change
5. Add/update tests
6. Run focused tests
7. Run full regression suite
8. Verify Docker when relevant
9. Check git diff/status
10. Make one logical commit
11. Push
12. Record checkpoint
```

Avoid:

-   random architecture redesign
-   unnecessary dependencies
-   hardcoded machine-specific paths
-   secrets in Git
-   business logic inside API routes
-   trusting client-supplied financial values
-   exposing internal exceptions
-   assuming SQLite proves PostgreSQL concurrency
-   deploying production infrastructure before configuration is ready

------------------------------------------------------------------------

## 39. Exact Next Step

Continue from:

``` text
AWS CLI 2.36.46 installed
        ↓
~/.local/bin not on PATH
        ↓
Fix PATH
        ↓
Verify aws --version
        ↓
Verify AWS identity
        ↓
Read-only AWS account/region checks
        ↓
Production configuration separation
        ↓
MLflow SQLite → PostgreSQL
        ↓
MLflow artifacts → S3
        ↓
AWS infrastructure
```

Do not redesign the agreed production architecture unless a concrete
technical or cost constraint requires it.

------------------------------------------------------------------------

# Current Status Snapshot

``` text
Backend                         ✅
PostgreSQL                      ✅
Authentication                 ✅
Authorization                  ✅
JWT security                   ✅
Global error handling          ✅
Application logging            ✅
Request IDs                    ✅
Health/readiness               ✅
Transaction rollback           ✅
DB constraints                 ✅
Concurrency hardening          ✅
Docker                         ✅
Non-root container             ✅
Docker persistence             ✅
ML pipeline                    ✅
Feature engineering            ✅
MLflow tracking                ✅
MLflow registry                ✅
Champion alias                 ✅
Champion model caching         ✅
ML API                         ✅
ML tests                       ✅
GitHub Actions CI              ✅
Frontend foundation            🔄
AWS CLI installation           ✅
AWS CLI PATH                   ⏳ NEXT
Production MLflow              ⏳
RDS                            ⏳
S3                             ⏳
Secrets Manager                ⏳
MLflow Tracking Server         ⏳
ECR                            ⏳
ECS Fargate                    ⏳
ALB / HTTPS                    ⏳
CloudWatch                     ⏳
Production CD                  ⏳
```
