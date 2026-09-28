# IncidentIQ — AI Incident Response Agent

IncidentIQ is a hackathon prototype that uses **Hindsight persistent memory** to help engineering teams respond to production incidents.

## Core learning loop

1. Engineer reports an incident.
2. Agent searches Hindsight for similar incidents.
3. If no relevant memory exists, the agent starts a new investigation.
4. Engineer confirms the root cause and resolution.
5. IncidentIQ stores the experience in Hindsight.
6. A future similar incident can recall the previous experience.

## Official technology

- Hindsight Python client: `hindsight-client`
- Hindsight Cloud API
- Groq for LLM reasoning
- Flask for the web application

Hindsight is the required memory layer for the hackathon.

## Run locally

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Hindsight and Groq keys.

Then:

```powershell
python app.py
```

Open:

`http://127.0.0.1:5000`

## Demo flow

### Demo 1 — first-time incident

Use:

> Payment API is returning 503 errors after deployment v2.4. Customers cannot complete payments.

The agent should show that no relevant memory exists.

### Demo 2 — teach the agent

Enter:

Root cause:
> Database connection pool exhausted.

Resolution:
> Increased connection pool from 50 to 100.

Runbook:
> Database Connection Troubleshooting.

Click **Save Experience to Memory**.

### Demo 3 — recall

Run the same or a similar incident again.

The agent should retrieve the stored experience from Hindsight and show it under **Hindsight Memory**.

## Important

Never commit `.env` or API keys to GitHub.
