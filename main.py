"""
main.py — Application entry point for WeekPlate.
Combines the FastAPI HTML web frontend, the SQLite database initialization,
and the FastMCP server with TokenAuth ASGI middleware.
Zero AI inside: pure web app + MCP protocol transport.
"""

import contextlib
from fastapi import FastAPI
import db
from web import router
from mcp_server import mcp, TokenAuth


@contextlib.asynccontextmanager
async def lifespan(app):
    """Initialize database tables and run the MCP session manager."""
    db.init()
    async with mcp.session_manager.run():
        yield


# FastAPI web app
web = FastAPI(
    title="WeekPlate",
    description="Plan meals with Claude. Shop smarter together.",
    lifespan=lifespan,
)

# Include the HTML web routes (Home, Dashboard, Meal Editor, Grocery Checklist, Share)
web.include_router(router)

# Mount the MCP server (serves /mcp)
web.mount("/", mcp.streamable_http_app())

# Wrap with TokenAuth middleware so /u/<token>/mcp automatically authenticates the user
app = TokenAuth(web)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
