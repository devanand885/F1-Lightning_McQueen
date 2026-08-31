# F1 Lightning McQueen

An F1 data platform: a Next.js frontend backed by a FastAPI service and a
normalized PostgreSQL database populated from the [OpenF1](https://openf1.org)
API.

```
OpenF1 -> backend/ingestion -> PostgreSQL -> backend/app (FastAPI) -> frontend (Next.js)
```

The frontend has been fully migrated off mock data and its old browser-side
OpenF1 call onto this backend. A data science / ML layer sits on top of the
same database: driver archetypes (clustering), a championship simulator
(Monte Carlo), real driver/circuit analytics, and historical strategy
insights. See "Project status" below for what's done.

## Layout

```
frontend/
  src/features/{drivers,constructors,circuits,dashboard,compare,archetypes,simulator}/
               api/, types/, hooks/, components/, pages/ per feature
  src/features/shared/   layout (search, nav), reusable UI (Panel, PlaceholderPanel,
                          InsufficientDataPanel), filters
  src/lib/     API client, download helper, debounce hook
backend/
  app/         FastAPI app: config, DB session, ORM models, OpenF1 client, API routes
  app/services/ orchestrates repositories + ml/ for the DS/ML endpoints (keeps routers thin)
  ingestion/   CLI + services that pull OpenF1 data into PostgreSQL
  alembic/     database migrations
  tests/       pytest suite (OpenF1 client, upsert/idempotency, model constraints, API,
               ml feature-engineering units, DS/ML API smoke tests)
ml/          data science / ML layer - installable package (`pip install -e ./ml`)
  features/    pure pandas/numpy feature engineering (driver + circuit), no DB/HTTP
  models/      train_archetypes.py + versioned artifacts under models/artifacts/<date>/
  inference/   loads artifacts / runs the simulator and strategy analysis at request time
docker-compose.yml   Postgres (+ backend) for local dev
```

Layering for every DS/ML feature is **router -> service -> ml/ (features or
inference) -> repository -> DB** - routers never touch pandas/numpy/sklearn
directly, and `ml/` never touches the database directly (it takes plain
rows the repository layer already pulled).

## Prerequisites

- Docker Desktop (for Postgres)
- Python 3.12+
- Node.js (for the frontend, see `frontend/README.md`)

## Local setup

**1. Start Postgres**

```
docker compose up -d postgres
```

This maps Postgres to **host port 5433**, not 5432 - chosen to avoid
clashing with a Postgres instance you may already have installed natively.
Check `docker-compose.yml`/`backend/.env.example` if you need to change it.

**2. Set up the backend**

```
cd backend
python -m venv venv
./venv/Scripts/activate        # venv\Scripts\activate on Windows cmd
pip install -r requirements-dev.txt
cp .env.example .env
```

**3. Run migrations**

```
alembic upgrade head
```

**4. Ingest some data**

```
python -m ingestion.cli ingest-season --year 2025
python -m ingestion.cli ingest-meeting --meeting-key 1254
python -m ingestion.cli ingest-session --session-key 9693
```

Each level cascades down (season -> meetings -> sessions -> lap/position/pit
stop/interval/stint/weather/race control/result data) and is safe to re-run:
every write is an upsert keyed on OpenF1's natural identifiers, so re-running
updates rows instead of duplicating them. OpenF1's free tier is rate-limited
(3 req/s, 30 req/min) and the client throttles to stay under that, so a full
season takes a while - expect on the order of 30-60+ minutes.

**5. Install the ML package and train the archetype model**

```
pip install -e ../ml
python ../ml/models/train_archetypes.py
```

Installs `ml/` editable into the backend venv (it's a sibling package, not
a subpackage of `backend/`) and writes a versioned artifact - scaler,
k-means model, PCA projection, and metadata (silhouette score, cluster
sizes, feature list) - to `ml/models/artifacts/<date>/`. The `/archetypes`
and `/simulator` API endpoints read whatever the *latest* artifact
directory is; re-run this any time the underlying data changes materially.
Needs at least a season or two of race data ingested first (archetype
eligibility requires 15+ completed race sessions per driver).

**6. Run the backend**

```
uvicorn app.main:app --reload
```

`GET /health` checks the app can reach the database.

**7. Run the frontend**

```
cd ../frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to http://localhost:8000/api/v1
npm run dev
```

See `frontend/README.md` for frontend-specific details (routes, design
system, tests).

## Tests

```
cd backend
# create a test database once:
docker compose exec postgres psql -U F1 Lightning McQueen -d F1 Lightning McQueen -c "CREATE DATABASE F1 Lightning McQueen_test;"
pytest

cd ../frontend
npm test
```

## Project status

**Done:**
- Normalized Postgres schema (seasons, meetings, sessions, circuits,
  drivers, constructors, session entries, laps, positions, pit stops,
  intervals, stints, weather, race control, session results), populated by
  an idempotent, failure-tolerant ingestion CLI.
- A centralized, resilient OpenF1 integration layer (retries, rate
  limiting, response validation, logging) - the *only* place in the system
  that knows OpenF1's base URL.
- A full FastAPI read API: drivers, constructors, circuits, dashboard
  aggregation, search, compare, export, seasons, plus the DS/ML endpoints
  below.
- The frontend is fully wired to that API - Drivers, Constructors,
  Circuits, and Dashboard all show real data; the global ⌘K search, list
  filtering/sorting, driver/constructor Compare, and CSV/JSON Export all
  work end to end.
- **Driver Archetypes** (`/archetypes`): K-means clustering on
  teammate-relative pace/degradation/consistency/start-performance
  (controls for car performance - validated against a cluster×constructor
  cross-tab). PCA scatter, cluster cards, excluded-driver list with
  reasons.
- **Championship Simulator** (`/simulator`): seeded 10,000-run Monte Carlo
  over the season's remaining races, on top of each driver's real
  already-accumulated points. Win/podium probabilities, expected points,
  a documented "this is a simulation, not a prediction" disclaimer.
- **Driver Analytics** (`/drivers/[driverNumber]`): real pace (field- and
  teammate-relative), tyre degradation (fuel-corrected, outlier-lap
  filtered), consistency, start performance, wet/dry, a pace-over-time
  trend, and a circuit-type performance radar - replacing every previously
  mocked chart on this page.
- **Circuit Capability** (`/circuits/[circuitId]`): circuits classified
  into Low/Medium/High-Speed from real speed-trap and pace-spread data,
  not an invented multi-axis profile.
- **Compare** (`/compare`): a new "Analytical" section (teammate-relative
  pace, degradation, consistency, archetype) alongside the original raw
  aggregates section.
- **Strategy Insights** (dashboard): real, sourced, sample-sized sentences
  (stop-count distribution, compound transitions, pit timing, an undercut
  heuristic) - explicitly historical/post-race, not live or predictive.
- Tests: backend (pytest - client, ingestion, API, ml feature-engineering
  units, DS/ML API smoke tests) and frontend (vitest + React Testing
  Library - loading/empty/error/insufficient-data states, sort/filter
  interaction, search, compare/export flows).

**Not built:** `/search` (page) and `/settings` are still placeholder
stubs. Full telemetry/`car_data` aero modeling and the two constructor
placeholder cards (`PerformanceEfficiencyScatter`,
`DevelopmentProgressCard`) are intentionally out of scope - that data
either isn't ingested or isn't measurable from what OpenF1 provides.

No analytical metric is invented anywhere in the app. Where a real
methodology exists, it's disclosed (see each feature's docstrings in
`ml/`); where a specific driver/circuit doesn't have enough data for it,
the UI shows an honest "Insufficient data" state instead of a fabricated
number.
