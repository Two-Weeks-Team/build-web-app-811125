from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import Base, engine, seed_demo_data
from routes import router

app = FastAPI(title="Build Web App API", version="1.0.0")

Base.metadata.create_all(bind=engine)
seed_demo_data()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Build Web App API</title>
  <style>
    body { font-family: Inter, Arial, sans-serif; background: #0b1020; color: #e6edf7; margin: 0; padding: 24px; }
    .card { max-width: 980px; margin: 0 auto; background: #121a33; border: 1px solid #2a355f; border-radius: 14px; padding: 24px; }
    h1 { margin: 0 0 6px; font-size: 30px; }
    p { color: #b8c3df; }
    code { color: #93c5fd; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .endpoint { background: #0f1730; border: 1px solid #26335e; border-radius: 10px; padding: 10px 12px; }
    .method { font-weight: 700; color: #fbbf24; margin-right: 8px; }
    a { color: #60a5fa; text-decoration: none; }
  </style>
</head>
<body>
  <div class='card'>
    <h1>Build Web App — API</h1>
    <p>Turn rough project notes into a traceable, presentation-ready product brief.</p>
    <p><strong>Tech Stack:</strong> FastAPI 0.115.0, SQLAlchemy 2.0.35, PostgreSQL-ready models, DO Serverless Inference (Claude 4.6 Sonnet).</p>
    <div class='grid'>
      <div class='endpoint'><span class='method'>GET</span><code>/health</code></div>
      <div class='endpoint'><span class='method'>GET</span><code>/seeds</code> and <code>/api/seeds</code></div>
      <div class='endpoint'><span class='method'>POST</span><code>/plan</code> and <code>/api/plan</code></div>
      <div class='endpoint'><span class='method'>POST</span><code>/insights</code> and <code>/api/insights</code></div>
      <div class='endpoint'><span class='method'>POST</span><code>/dossiers/save</code> and <code>/api/dossiers/save</code></div>
      <div class='endpoint'><span class='method'>GET</span><code>/dossiers</code> and <code>/api/dossiers</code></div>
    </div>
    <p style='margin-top:18px;'>Docs: <a href='/docs'>/docs</a> · Redoc: <a href='/redoc'>/redoc</a></p>
  </div>
</body>
</html>
"""