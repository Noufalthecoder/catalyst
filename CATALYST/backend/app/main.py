import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure app package is discoverable
sys.path.append(str(Path(__file__).parent.parent))

from app.api.stats import router as stats_router
from app.api.catalog import router as catalog_router
from app.api.review import router as review_router
from app.api.enrichment import router as enrichment_router
from app.api.sources import router as sources_router
from app.api.exports import router as exports_router

app = FastAPI(
    title="CATALYST — Industrial Product Intelligence API",
    description="AI-powered Product Intelligence, Verification, and Enrichment Engine",
    version="1.0.0"
)

# Enable CORS for Next.js development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(stats_router)
app.include_router(catalog_router)
app.include_router(review_router)
app.include_router(enrichment_router)
app.include_router(sources_router)
app.include_router(exports_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "engine": "CATALYST Product Intelligence",
        "version": "1.0.0",
        "source_provider": "live",
        "ready": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
