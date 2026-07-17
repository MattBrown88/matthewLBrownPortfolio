Reddit post

Want to get some perspective on using a Python (FastAPI, Flask, etc) backend with Supabase. 

I'm comparing two options:

### Option 1: Python backend only: 

**Frontend -> FastAPI -> Supabase**

Pros:

- Python ecosystem
- No Supabase runtime constraints (400s, 256mb memory, etc.)
- Single backend deployment

Cons:

- Verify Supabase JWT in Python
- Frontend talks to separate API instead of Supabase Edge Functions

### Option 2: Edge Function as a gateway to Python: 

**Frontend -> Supabase Edge Function -> Python -> Supabase**

Pros:

- Supabase Edge Functions are the public API layer
- Built-in JWT verification
- Python ecosystem

Cons: 

- Multiple deployments
- Additional network hop
- Edge Function still has runtime limits for the gateway request
- Distributed debugging / observability. Errors, logs, and tracing now span two runtimes.

I'm leaning towards not calling Python from an Edge Function. It seems cleaner to use Edge Functions until they become insufficient, then add separate Python services to handle relevant workflows.

Curious about others experience using a Python backend with Supabase. Has anyone adopted Edge Functions as the gateway layer, and if so, what benefits did it provide?



1. Only Edge functions:
   1. Pros
      1.  Auth included, no separate deployment necessary
      2. Can handle background processes up to 400s
   2. Cons
      1. You must write code in Deno
      2. Runtime limits: memory 256MB, wallclock 400s, cpu time 2s, Idle timeout 150s
2. Only Python (FastAPI, Flask, etc.)
   1. Pros
      1. No supabase runtime limits. 
         1. Cloud Run, Railway, Lambdas have higher limits
      2. Python libraries
   2. Cons
      1. Authenticate manually
      2.  requires separate deployment
3. Edge Function called from Python
   1. Pros
      1. Python libraries
      2. No Supabase runtime limits.
         1. Can return long-running Python immediately
   2. Cons
      1. Multiple deployments

This tutorial will demonstrate how to use a python backend in conjunction with Supabase Edge Functions. I like this structure because we keep everything in the Supabase platform except the business logic of the backend functions. The benefits of this are:

- Edge Functions have a fixed runtime (60 seconds?) and so not designed for long-running background tasks.
- Authentication is built into the edge functions. No need to implement yourself in Python. Then you'd have two separate auth systems.
- You get to develop in the Python ecosystem. Much more mature tooling, especially for AI applications.
- More developer support. There are a lot more  Python developers than deno developers.

### How does this differ from not using Supabase Edge Functions and just having Python backend

No config.yml to handle verify_jwt. No supabase.functions.invoke, manually set the jwt each time there's a frontend call to the edge function.

We will create two Edge Functions to handle the calls to python:

-  `call_python`: called by frontend users with `verify_jwt=true` and uses RLS.

  - To authenticate, this uses a secret shared (`PYTHON_API_KEY`) between the python backend and the edge functions. Because they are both backend code, this secret is never exposed to the frontend. In addition, the user jwt key is passed in the request. This way RLS can be utilized in Python. Here is example code from an edge function. You can see how `PYTHON_API_KEY` is an env var that is sent to the python route in the request. Then on the backend it is evaluated against the PYTHON_API_KEY in the Python code

  - ```
    // Supabase Edge Function
    const PYTHON_API_KEY = Deno.env.get("PYTHON_API_KEY")!;
    
     const res = await fetch(`127.0.0.1:8000/${route}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": PYTHON_API_KEY,
          // Forward the caller's JWT so the Python backend can query as the user.
          Authorization: req.headers.get("Authorization") ?? "",
        },
        body,
      });
      
    # Python service
    
    ```

  - 

-  `call_python_jobs`: called by the system with `verify_jwt=false` and uses the service role key. 

In this first part of this tutorial we will show how to setup locally. At the end we will show how to deploy to railway. 

### Setting Local Environment Variables

python env. Run `supabase status` to get the SUPABASE vars.

```
PYTHON_API_KEY=test
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_PUBLISHABLE_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
SUPABASE_SECRET_KEY=sb_secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Supabase env

```
PYTHON_BASE_URL=http://host.docker.internal:8000
PYTHON_API_KEY=test
JOBS_SECRET_KEY=jobs-super-secret-key
```

You can see we set `PYTHON_API_KEY` in both Python and Supabase. This value is never exposed to the frontend and validates calls between Edge Functions and Python. The `SUPABASE_` vars are automatically set in Edge Functions. We have to set them in the Python backend to have access to the Supabase Postgres instance. `JOBS_SECRET_KEY` is the shared secret between Edge Functions and backend Supabase instance (what exactly is this? cron, db, what else?)

`PYTHON_BASE_URL`: Locally Supabase is run from Docker so this means the host machine.

SHOW DIAGRAM OF HOW THE AUTH WORKS.

## Architecture Overview

Client → Supabase Edge Function (Deno/TS) → Python FastAPI (Railway) → Response

The Edge Function acts as a secure proxy: it adds an API key before forwarding to Python, so the Python backend is never directly exposed.

## Project Structure

supabase-python-backend/
├── supabase/
│   ├── config.toml
│   ├── functions/
│   │   ├── .env.example
│   │   └── call-python/
│   │       └── index.ts
└── python-backend/
    ├── main.py
    ├── requirements.txt
    ├── Dockerfile
    └── railway.toml

---

Prerequisites

npm install -g @railway/cli
brew install supabase/tap/supabase

railway login
supabase login

---
Step 1: Project structure

supabase-python-backend/
├── supabase/
│   ├── config.toml
│   └── functions/
│       ├── .env.example
│       └── call-python/
│           ├── index.ts
│           └── services.json
└── python-backends/
    ├── Dockerfile
    ├── requirements.txt
    ├── service1/
    │   └── main.py
    └── service2/
        └── main.py

---
Step 2: Python services

shared/auth.py

import os
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY = os.environ["API_KEY"]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

python-backends/service1/main.py
from fastapi import FastAPI, Security
from shared.auth import verify_api_key

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(_=Security(verify_api_key)):
    print("service 1 called")
    return {"service": "text-analysis", "status": "ok"}

Python-backend/service2/main.py

import asyncio
from fastapi import FastAPI, Security
from shared.auth import verify_api_key

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/keywords")
async def keywords(_=Security(verify_api_key)):
    await asyncio.sleep(1)
    print("service 2 called")
    return {"service": "keyword-extractor", "status": "ok"}

Step 4: Python requirements

cd python-backend
uv venv
source .venv/bin/activate
uv pip install fastapi "uvicorn[standard]" pydantic
uv pip freeze > requirements.txt

Step 5: Dockerfile

python-backend/Dockerfile
ARG SERVICE_DIR=service1

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt
COPY shared/ ./shared/
COPY ${SERVICE_DIR}/main.py .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

---
### Create new Edge Function

We are going to use just one edge function to call python. We may want at least two in production. One for background jobs and one that returns right away. But for demonstration purposes this should be good.

Step 2: Add the services config

Create supabase/functions/call-python/services.json and fill in your Railway URLs once deployed:

{
  "analyze": "https://text-analysis.railway.app",
  "keywords": "https://keyword-extractor.railway.app"
}

supabase functions new call-python

Supabase/functions/call-python

import services from "./services.json" with { type: "json" };

const PYTHON_API_KEY = Deno.env.get("PYTHON_API_KEY")!;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

async function callService(serviceUrl: string, path: string, req: Request): Promise<Response> {
  const res = await fetch(`${serviceUrl}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": PYTHON_API_KEY,
    },
    body: req.body,
  });
  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const url = new URL(req.url);
  const route = url.pathname.split("/").pop() as keyof typeof services;

  if (!services[route]) {
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  return callService(services[route], `/${route}`, req);
});

---


---
Step 3: Set up local secrets

cp supabase/functions/.env.example supabase/functions/.env

Fill in supabase/functions/.env:
PYTHON_API_KEY=your-shared-secret-key

Add to .gitignore:
supabase/functions/.env

Step  Deploy railway

# Initialize the Railway project (one time)
railway init

Create railway.toml file

python-backends/service1/railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "../Dockerfile"
buildArgs = { SERVICE_DIR = "service1" }

[deploy]
healthcheckPath = "/health"

python-backends/service2/railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "../Dockerfile"
buildArgs = { SERVICE_DIR = "service2" }

[deploy]
healthcheckPath = "/health"

---
Step 4: Test locally

supabase start
supabase functions serve call-python --env-file .env

curl -X POST http://localhost:54321/functions/v1/call-python/analyze \
  -H "Authorization: Bearer <local-anon-key>" \
  -H "Content-Type: application/json" \
  -d '{}'

---
Step 5: Set production secrets and deploy

supabase secrets set PYTHON_API_KEY=<your-shared-key>

supabase functions deploy call-python

---
Step 6: Test production

curl -X POST https://<project-ref>.supabase.co/functions/v1/call-python/analyze \
  -H "Authorization: Bearer <anon-key>" \
  -H "Content-Type: application/json" \
  -d '{}'

curl -X POST https://<project-ref>.supabase.co/functions/v1/call-python/keywords \
  -H "Authorization: Bearer <anon-key>" \
  -H "Content-Type: application/json" \
  -d '{}'







Step 6: Edge Function

supabase/functions/call-python/services.json
{
  "analyze": "https://text-analysis.railway.app",
  "keywords": "https://keyword-extractor.railway.app"
}

supabase/functions/call-python/index.ts
import services from "./services.json" with { type: "json" };

const PYTHON_API_KEY = Deno.env.get("PYTHON_API_KEY")!;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

async function callService(serviceUrl: string, path: string, req: Request): Promise<Response> {
  const res = await fetch(`${serviceUrl}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": PYTHON_API_KEY,
    },
    body: req.body,
  });
  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const url = new URL(req.url);
  const route = url.pathname.split("/").pop() as keyof typeof services;

  if (!services[route]) {
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  return callService(services[route], `/${route}`, req);
});

---
Step 7: Secrets template

supabase/functions/.env.example
PYTHON_API_KEY=your-shared-secret-key

Copy to supabase/functions/.env for local dev. Add .env to .gitignore.

---
Step 8: Deploy Python services to Railway

cd python-backends

# Initialize Railway project
railway init

# --- Service 1 ---
railway add                        # name it "text-analysis"
railway service                    # select text-analysis
railway variable set SERVICE_DIR=service1
railway variable set API_KEY=<strong-random-key>
railway up

# --- Service 2 ---
railway add                        # name it "keyword-extractor"
railway service                    # select keyword-extractor
railway variable set SERVICE_DIR=service2
railway variable set API_KEY=<same-key-as-above>
railway up

Once both are deployed, go to the Railway dashboard for each service and generate a public domain under Settings → Networking → Generate Domain. Update services.json with those URLs.

---
Step 8: Set Supabase secrets

# From repo root
supabase link --project-ref <your-project-ref>

supabase secrets set PYTHON_API_KEY=<same-key-you-set-in-railway>

---
Step 9: Deploy the Edge Function

supabase functions deploy call-python

---
Step 10: Test

# Service 1
curl -X POST https://<project-ref>.supabase.co/functions/v1/call-python/analyze \
  -H "Authorization: Bearer <anon-key>" \
  -H "Content-Type: application/json" \
  -d '{}'

# Service 2
curl -X POST https://<project-ref>.supabase.co/functions/v1/call-python/keywords \
  -H "Authorization: Bearer <anon-key>" \
  -H "Content-Type: application/json" \
  -d '{}'

Expected responses:
// /analyze
{"service": "text-analysis", "status": "ok"}

// /keywords
{"service": "keyword-extractor", "status": "ok"}