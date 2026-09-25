# Homework 3: AI-assisted Real Estate CRM

This homework is a real estate CRM with a conversational AI agent. The CRM stores brokerages, contacts, property deals, and activities. A user can give the agent a natural-language brief; the agent chooses CRM tools and performs the requested workflow through the API.

## What I built

- **CRM API:** TypeScript, Express, Prisma, and PostgreSQL. It exposes authenticated REST endpoints for CRM operations and a GraphQL endpoint for structured queries.
- **Data model:** Companies, buyer/seller contacts, deals with pipeline stages, activities, and users. Prisma migrations define the database schema.
- **AI agent:** A Python command-line chat/brief interface using Gemini. Its tool executor can operate in mock mode or call the CRM API. The loop has step and time limits, and tracing records agent activity.

The repository contains an API and a command-line agent; it does not contain a browser frontend.

## Project map

| Path | Purpose |
| --- | --- |
| [`api/src/`](api/src/) | REST routes, GraphQL schema and resolvers, authentication, validation |
| [`api/prisma/`](api/prisma/) | Database schema, migrations, and sample-data seed |
| [`agent/`](agent/) | Gemini agent loop, CRM tools, guardrails, and tracing |
| [`docker-compose.yaml`](docker-compose.yaml) | Local PostgreSQL service on port 5433 |

## Run locally

You need Docker, Node.js, Python 3, and a Gemini API key.

1. Start PostgreSQL from this directory: `docker compose up -d`.
2. In `api/`, install packages with `npm install`, copy `.env.example` to `.env`, and set `DATABASE_URL`, `JWT_SECRET`, and `AGENT_PASSWORD`. Run `npm run migrate`, `npm run seed`, then `npm run dev`.
3. In `agent/`, create a Python environment and run `pip install -r requirements.txt`. Copy `.env.example` to `.env`; set `GEMINI_API_KEY`, `CRM_API_URL`, `CRM_AGENT_EMAIL`, and `CRM_AGENT_PASSWORD`. The agent password must match the API seed user's password.
4. Run a brief from `agent/`:

```bash
python main.py --use-api "Find a company and create a new buyer lead"
```

The API listens on `http://localhost:3000` by default, with GraphQL at `/graphql` and a health check at `/health`. To explore the agent's workflow without changing CRM records, use `--mock` in place of `--use-api`; a Gemini key is still required.

The example environment files contain placeholder credentials. Replace them before running the project.
