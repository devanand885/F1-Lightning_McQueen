# F1 Lightning McQueen Frontend

The Next.js frontend for F1 Lightning McQueen. It's a read-only client over the FastAPI
backend in `../backend` — see the root [`README.md`](../README.md) for the
full architecture and how to run the backend + Postgres it depends on.

## Design system

- **Font**: Titillium Web (all weights 200–900)
- **Primary**: `#ff6548` (accent)
- **Base bg**: `#0a0a0a` / **Surface bg**: `#111111`
- Dark, data-dense, Bloomberg-terminal-inspired aesthetic

## Routes

| Route | Status |
|---|---|
| `/dashboard` | Season overview, standings, calendar - real backend data |
| `/drivers`, `/drivers/[driverNumber]` | Real backend data; Compare wired |
| `/constructors`, `/constructors/[constructorId]` | Real backend data; Compare + Export wired |
| `/circuits`, `/circuits/[circuitId]` | Real backend data |
| `/compare?type=driver\|constructor&ids=1,2` | Driver-vs-driver / constructor-vs-constructor comparison |
| `/archetypes`, `/simulator`, `/search`, `/settings` | Placeholder stubs - not built yet |

Cards with no legitimate backend data source (aero efficiency, performance
radar, upgrade tracking, wind tunnel, pace-vs-field trends) render an honest
"Not yet available" placeholder (`PlaceholderPanel`) instead of a fabricated
number - this is intentional, not missing work.

## Getting started

```bash
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to http://localhost:8000/api/v1
npm run dev
```

The backend (`../backend`) and Postgres need to be running for any page to
show real data - see the root README.

## Tests

```bash
npm test          # vitest run, single pass
npm run test:watch
```

Component tests cover loading/empty/error states and real interactive
behavior (sorting, filtering, search navigation, export/compare flows) -
they mock the API layer, not the backend itself.

## Other checks

```bash
npm run lint
npx tsc --noEmit
```
