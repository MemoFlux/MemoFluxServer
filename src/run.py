#!/usr/bin/env python
import uvicorn
from dotenv import load_dotenv
from pathlib import Path

if __name__ == "__main__":
    load_dotenv(Path.cwd() / ".env")

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        # reload=True,
        log_level="info",
    )
