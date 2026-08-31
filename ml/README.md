# ML layer (boundary only)

This directory is a placeholder for the data science / machine learning work
that consumes F1 Lightning McQueen's backend data. It is intentionally empty of any actual
modeling code - that's a separate, deliberate phase of the project, owned
outside of the engineering foundation built in `backend/`.

```
ml/
  models/     trained model artifacts / definitions
  features/   feature engineering pipelines built on top of backend data
  inference/  code that serves model output back through the FastAPI backend
```

## How this is expected to connect to the rest of the system

```
OpenF1 -> backend/ingestion -> PostgreSQL -> FastAPI -> Next.js frontend
                                    |
                                    v
                              ml/ (this directory)
                       features -> models -> inference
```

The backend's job is to provide clean, reliable, queryable source data
(seasons, meetings, sessions, laps, positions, pit stops, intervals, stints,
weather, race control, session results) and clean read endpoints/exports for
it - see the root `README.md`. Nothing in `backend/` invents analytical
metrics (reliability scores, aero efficiency, driver archetypes, etc.) on
the frontend's behalf; those are expected to be produced here, once real
methodology exists, and then integrated back into the API/frontend.
