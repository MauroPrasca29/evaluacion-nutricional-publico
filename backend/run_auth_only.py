from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import importlib.util
from pathlib import Path

# Load src/api/auth.py as a module without importing the whole package to avoid
# pulling in heavy optional dependencies from other routers.
src_dir = Path(__file__).parent / "src"
# Ensure package imports like `core` and `src.*` resolve
import sys
sys.path.insert(0, str(src_dir))

auth_path = src_dir / "api" / "auth.py"
spec = importlib.util.spec_from_file_location("auth_module", str(auth_path))
auth_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth_module)  # type: ignore
auth_router = getattr(auth_module, "router")

app = FastAPI(title="Auth Test App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/api/auth")

@app.get("/")
def root():
    return {"ok": True, "service": "auth-only"}
