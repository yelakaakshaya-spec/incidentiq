# 🚨 IncidentIQ — AI Incident Response Agent

> **Turn every production incident into future experience.**

IncidentIQ is an AI-powered incident response agent for software engineering and DevOps teams.

It uses **Hindsight persistent memory** to remember previous production incidents, confirmed root causes, resolutions, runbooks, and lessons learned.

When a similar incident happens again, IncidentIQ recalls relevant past experience and helps engineers investigate the current incident.

### Core Learning Loop

**Incident → Recall → Reason → Resolve → Learn → Improve**

---

## 🌐 Live Demo

🚀 **Live Application:**  
https://incidentiq-b0o6.onrender.com

💻 **GitHub Repository:**  
https://github.com/yelakaakshaya-spec/incidentiq

---

## 🎯 Problem

Production incidents are time-sensitive and often require engineers to search through:

- Previous incident reports
- Post-mortems
- Troubleshooting notes
- Runbooks
- Previous resolutions
- Historical operational knowledge

Important knowledge can be difficult to retrieve when an incident is happening.

### The Problem

> **How can an AI incident-response agent remember previous incidents and use that experience during future incidents?**

---

## 💡 Solution

IncidentIQ combines:

- 🧠 **Hindsight** — persistent AI memory
- 🤖 **Groq** — LLM reasoning
- 🌐 **Flask** — backend application
- 🎨 **HTML/CSS/JavaScript** — interactive dashboard
- ☁️ **Render** — deployment

When an incident is reported, IncidentIQ:

1. Understands the current incident.
2. Searches Hindsight for relevant historical experience.
3. Retrieves previous incidents and resolutions.
4. Uses historical information as evidence.
5. Helps the engineer investigate the current incident.
6. Allows the engineer to record the confirmed resolution.
7. Stores the new experience in Hindsight.
8. Uses that experience during future incidents.

---

# 🧠 Hindsight Memory

Memory is the central feature of IncidentIQ.

The agent does not rely only on the current prompt.

It can recall persistent information from previous incidents.

### Example

### First Incident

```text
Payment API is returning 503 errors after deployment.
Customers cannot complete payments.
