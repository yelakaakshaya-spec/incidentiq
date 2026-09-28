import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "incidentiq")
HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
)
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


# =========================
# OPTIONAL DEMO FALLBACK
# =========================

demo_memories = []


# =========================
# IMPORT HINDSIGHT
# =========================

try:
    from hindsight_client import Hindsight
except ImportError:
    Hindsight = None


# =========================
# IMPORT GROQ
# =========================

try:
    from groq import Groq
except ImportError:
    Groq = None


# =========================
# HINDSIGHT CLIENT
# =========================

def hindsight_client():
    if not Hindsight or not HINDSIGHT_API_KEY:
        return None

    return Hindsight(
        base_url=HINDSIGHT_BASE_URL,
        api_key=HINDSIGHT_API_KEY,
        timeout=30.0
    )


# =========================
# CREATE BANK IF NEEDED
# =========================

def ensure_bank():
    client = hindsight_client()

    if not client:
        return False

    try:
        client.create_bank(
            bank_id=BANK_ID,
            name="IncidentIQ Memory",
            mission=(
                "Remember production incidents, root causes, "
                "resolutions and lessons so engineers can resolve "
                "future incidents faster."
            )
        )
    except Exception:
        # Bank may already exist.
        pass

    return True


# =========================
# RECALL MEMORY
# =========================

def recall_memories(query, limit=5):

    client = hindsight_client()

    if client:

        try:
            result = client.recall(
                bank_id=BANK_ID,
                query=query,
                types=[
                    "world",
                    "experience",
                    "observation"
                ],
                budget="high",
                max_tokens=8192
            )

            memories = []

            for r in result.results[:limit]:

                memories.append({
                    "text": r.text,
                    "type": getattr(r, "type", "memory")
                })

            return memories

        except Exception as e:

            return [{
                "text": f"Hindsight error: {e}",
                "type": "error"
            }]

    # =========================
    # LOCAL FALLBACK
    # =========================

    q = query.lower()

    scored = []

    for item in demo_memories:

        text = item["text"]

        score = sum(
            1
            for word in q.split()
            if len(word) > 3 and word in text.lower()
        )

        if score:
            scored.append((score, item))

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        x[1]
        for x in scored[:limit]
    ]


# =========================
# SAVE MEMORY
# =========================

def retain_memory(content):

    client = hindsight_client()

    if client:

        ensure_bank()

        client.retain(
            bank_id=BANK_ID,
            content=content,
            context="IncidentIQ production incident memory"
        )

        return True

    # Local fallback
    demo_memories.append({
        "text": content,
        "type": "experience"
    })

    return True


# =========================
# AI RESPONSE
# =========================

def generate_agent_response(incident, memories):

    memory_text = "\n\n".join(
        f"- {m['text']}"
        for m in memories
        if m.get("type") != "error"
    )

    # =========================
    # GROQ AI
    # =========================

    if GROQ_API_KEY and Groq:

        try:

            client = Groq(
                api_key=GROQ_API_KEY
            )

            prompt = f"""
You are IncidentIQ, an AI incident response agent for software engineering and DevOps teams.

CURRENT INCIDENT:
{incident}

HISTORICAL MEMORY FROM HINDSIGHT:
{memory_text if memory_text else "No relevant historical incident found."}

Your job is to help an engineer investigate the current production incident.

IMPORTANT RULES:

1. Treat information from Hindsight as historical evidence, not absolute truth.

2. NEVER invent or add facts that are not present in:
   - the current incident, or
   - the historical memory.

3. If a possible cause is not confirmed by the memory, clearly label it as a
   "possible cause" or "hypothesis".

4. If historical memory contains a confirmed root cause, you may mention it,
   but clearly say that the engineer must verify whether the same condition
   exists in the current incident.

5. If historical memory contains a previous resolution, mention it accurately.
   Do not add extra details that are not present in the memory.

6. Clearly distinguish between:
   - Current incident facts
   - Historical memory
   - Possible causes
   - Recommended investigation steps

7. If relevant historical memory exists:
   - Clearly mention the previous incident.
   - Mention its root cause only if it is explicitly present in the memory.
   - Mention its resolution only if it is explicitly present in the memory.
   - Explain why the memory may be relevant.
   - Tell the engineer to verify the current evidence.

8. If no historical memory exists:
   - Clearly say this is a first-time or unseen incident.
   - Suggest investigation steps based only on the current incident.
   - Do not claim certainty about the root cause.

Respond using exactly this structure:

STATUS:

MEMORY:

LIKELY CAUSES:

RECOMMENDED NEXT STEPS:

WHY THESE STEPS:

SAFETY NOTE:

Do not invent missing information.
"""

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful DevOps incident "
                            "response assistant. Accuracy is more "
                            "important than guessing."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_completion_tokens=700
            )

            return response.choices[0].message.content

        except Exception as e:

            return fallback_response(
                incident,
                memories,
                f"Groq unavailable: {e}"
            )

    # =========================
    # FALLBACK RESPONSE
    # =========================

    return fallback_response(
        incident,
        memories
    )


# =========================
# FALLBACK RESPONSE
# =========================

def fallback_response(
    incident,
    memories,
    note=""
):

    if memories:

        return f"""STATUS:
Similar historical incidents found.

MEMORY:
{memories[0]['text']}

LIKELY CAUSES:
The historical incident is a useful lead, but the current incident must be verified.

RECOMMENDED NEXT STEPS:
1. Check current service and error logs.
2. Compare recent deployments or configuration changes.
3. Verify the root cause described in the historical memory.
4. Follow the relevant runbook before making production changes.

WHY THESE STEPS:
The recommendation is based on previous incident experience stored in Hindsight.

SAFETY NOTE:
Do not apply a previous fix blindly. Verify the current evidence first.

{note}"""

    return f"""STATUS:
No relevant historical incident found.

MEMORY:
Hindsight has no matching experience for this incident yet.

LIKELY CAUSES:
The agent cannot determine the root cause from the description alone.

RECOMMENDED NEXT STEPS:
1. Check service health and application logs.
2. Check recent deployments and configuration changes.
3. Check database and dependency connectivity.
4. Follow the service's troubleshooting runbook.
5. Record the confirmed root cause and resolution after recovery.

WHY THESE STEPS:
This appears to be a first-time or unseen incident, so the agent starts with evidence-based investigation.

SAFETY NOTE:
Do not make destructive production changes without verification.

{note}"""


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================
# ANALYZE INCIDENT
# =========================

@app.post("/api/analyze")
def analyze():

    data = request.get_json() or {}

    incident = (
        data.get("incident") or ""
    ).strip()

    if not incident:

        return jsonify({
            "error": "Please describe the incident."
        }), 400

    # Focused Hindsight search
    query = f"""
Previous production incidents involving:

Payment API
503 errors
deployment
database connection pool
customer payment failures

Current incident:

{incident}

Find relevant previous incidents,
root causes, resolutions and runbooks.
"""

    memories = recall_memories(
        query,
        limit=5
    )

    # Remove error messages
    memories = [
        m
        for m in memories
        if m.get("type") != "error"
    ]

    answer = generate_agent_response(
        incident,
        memories
    )

    return jsonify({

        "answer": answer,

        "memories": memories,

        "memory_count": len(memories),

        "mode": (
            "Hindsight Cloud"
            if HINDSIGHT_API_KEY
            else "Local Demo Mode"
        )
    })


# =========================
# CLOSE INCIDENT + LEARN
# =========================

@app.post("/api/resolve")
def resolve():

    data = request.get_json() or {}

    incident = (
        data.get("incident") or ""
    ).strip()

    root_cause = (
        data.get("root_cause") or ""
    ).strip()

    resolution = (
        data.get("resolution") or ""
    ).strip()

    runbook = (
        data.get("runbook") or ""
    ).strip()

    if not incident or not root_cause or not resolution:

        return jsonify({
            "error": (
                "Incident, root cause and "
                "resolution are required."
            )
        }), 400

    memory = f"""IncidentIQ experience recorded on {datetime.now().isoformat(timespec='minutes')}:

Incident:
{incident}

Confirmed root cause:
{root_cause}

Resolution that worked:
{resolution}

Runbook used:
{runbook or 'Not specified'}

Lesson:
This experience should be recalled when future incidents have similar symptoms.
"""

    try:

        retain_memory(
            memory
        )

        return jsonify({

            "success": True,

            "message": (
                "Incident experience saved "
                "to Hindsight memory."
            ),

            "mode": (
                "Hindsight Cloud"
                if HINDSIGHT_API_KEY
                else "Local Demo Mode"
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# VIEW MEMORIES
# =========================

@app.get("/api/memories")
def memories():

    result = recall_memories(
        "production incidents root causes resolutions runbooks",
        limit=20
    )

    return jsonify({
        "memories": result
    })


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )

