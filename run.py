"""
run.py — Production-grade launcher for the Industrial Knowledge Platform API.

This module is intentionally limited to:
  1. Configuration loading   — via core.settings.Settings (single source of truth)
  2. CLI argument parsing    — overrides for Settings values, no new defaults
  3. Pre-flight validation   — lightweight checks before Uvicorn starts
  4. Startup banner          — human-readable summary of active configuration
  5. uvicorn.run()           — hand off to Uvicorn with the resolved config

Nothing from app/ is imported or modified here.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Guard: import Settings early so pydantic-settings can parse .env.
# A ValidationError here means required config (secret_key, database_url, …)
# is missing and the server cannot start.
# ---------------------------------------------------------------------------
try:
    from core.settings import Settings
except Exception as exc:  # pragma: no cover
    sys.exit(f"[FATAL] Could not import Settings: {exc}")

import uvicorn


# ---------------------------------------------------------------------------
# Internal types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResolvedConfig:
    """Fully-resolved, immutable launch configuration."""
    host: str
    port: int
    workers: int
    reload: bool
    log_level: str
    settings: Settings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser(settings: Settings) -> argparse.ArgumentParser:
    """
    Build the argument parser.  All defaults come from Settings so that
    .env is the single source of truth; CLI flags are explicit overrides only.
    """
    parser = argparse.ArgumentParser(
        prog="python run.py",
        description="Launch the Industrial Knowledge Platform API server.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default=settings.server_host,
        metavar="HOST",
        help="Bind address",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.server_port,
        metavar="PORT",
        help="Port to listen on",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=settings.server_workers,
        metavar="N",
        help="Number of Uvicorn worker processes (production only; forces --no-reload)",
    )

    reload_group = parser.add_mutually_exclusive_group()
    reload_group.add_argument(
        "--reload",
        dest="reload",
        action="store_true",
        default=None,
        help="Enable auto-reload (default: on when DEBUG=true, single worker)",
    )
    reload_group.add_argument(
        "--no-reload",
        dest="reload",
        action="store_false",
        help="Disable auto-reload",
    )

    parser.add_argument(
        "--log-level",
        default=settings.log_level.lower(),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        metavar="LEVEL",
        help="Uvicorn log level",
    )
    return parser


def _resolve_config(settings: Settings, args: argparse.Namespace) -> ResolvedConfig:
    """
    Merge Settings + CLI args into a single immutable ResolvedConfig.
    CLI values win over Settings values.
    """
    host: str = args.host
    port: int = args.port
    workers: int = args.workers
    log_level: str = args.log_level

    # Reload: explicit CLI flag > DEBUG setting
    if args.reload is None:
        # Neither --reload nor --no-reload was passed; derive from DEBUG
        reload: bool = settings.debug
    else:
        reload = args.reload

    return ResolvedConfig(
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level=log_level,
        settings=settings,
    )


# ---------------------------------------------------------------------------
# Pre-flight validation
# ---------------------------------------------------------------------------

def _validate(cfg: ResolvedConfig) -> Tuple[List[str], List[str]]:
    """
    Perform lightweight pre-flight checks.

    Returns (errors, warnings).
    Errors prevent startup; warnings are printed and ignored.
    No database connections or heavy I/O are performed here.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # --- Worker count --------------------------------------------------
    if cfg.workers < 1:
        errors.append(
            f"server_workers must be >= 1, got {cfg.workers}. "
            "Set SERVER_WORKERS in .env or use --workers."
        )

    # --- Reload + multi-worker conflict --------------------------------
    if cfg.reload and cfg.workers > 1:
        errors.append(
            f"reload=True is incompatible with workers={cfg.workers}. "
            "Use --no-reload for multi-worker deployments, or --workers 1 "
            "for development with auto-reload."
        )

    # --- Upload directory ----------------------------------------------
    # LocalStorageProvider already calls os.makedirs on first use, which
    # is the established project convention.  We replicate the same call
    # here so a misconfigured path is caught before Uvicorn starts.
    upload_dir = os.path.abspath(cfg.settings.upload_directory)
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except OSError as exc:
        errors.append(
            f"Could not create upload directory '{upload_dir}': {exc}. "
            "Check UPLOAD_DIRECTORY and file-system permissions."
        )

    # --- LLM provider API keys (warnings only) -------------------------
    provider = cfg.settings.llm_provider.lower()
    key_map = {
        "groq": ("groq_api_key", "GROQ_API_KEY"),
        "openai": ("openai_api_key", "OPENAI_API_KEY"),
        "gemini": ("gemini_api_key", "GEMINI_API_KEY"),
        "anthropic": ("anthropic_api_key", "ANTHROPIC_API_KEY"),
    }
    if provider in key_map:
        attr, env_var = key_map[provider]
        if not getattr(cfg.settings, attr, None):
            warnings.append(
                f"LLM provider is '{provider}' but {env_var} is not set. "
                "AI-powered features will be unavailable at runtime."
            )

    # --- Neo4j (warning if enabled but credentials are defaults) -------
    if cfg.settings.enable_knowledge_graph:
        if cfg.settings.neo4j_password == "neo4j_password":
            warnings.append(
                "enable_knowledge_graph=True but NEO4J_PASSWORD appears to be "
                "the default value. Verify your Neo4j credentials in .env."
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _print_banner(cfg: ResolvedConfig) -> None:
    environment = "Development" if cfg.settings.debug else "Production"
    env_color = _YELLOW if cfg.settings.debug else _GREEN
    reload_label = f"{_GREEN}enabled{_RESET}" if cfg.reload else f"{_DIM}disabled{_RESET}"
    api_base = f"http://{cfg.host}:{cfg.port}"

    lines = [
        "",
        f"{_BOLD}{_CYAN}  ╔══════════════════════════════════════════════╗{_RESET}",
        f"{_BOLD}{_CYAN}  ║  Industrial Knowledge Platform API            ║{_RESET}",
        f"{_BOLD}{_CYAN}  ╚══════════════════════════════════════════════╝{_RESET}",
        "",
        f"  {_BOLD}Environment{_RESET}   {env_color}{environment}{_RESET}",
        f"  {_BOLD}API URL{_RESET}       {api_base}/api/v1",
        f"  {_BOLD}Swagger UI{_RESET}    {api_base}/docs",
        f"  {_BOLD}ReDoc{_RESET}         {api_base}/redoc",
        "",
        f"  {_BOLD}Host{_RESET}          {cfg.host}",
        f"  {_BOLD}Port{_RESET}          {cfg.port}",
        f"  {_BOLD}Workers{_RESET}       {cfg.workers}",
        f"  {_BOLD}Auto-reload{_RESET}   {reload_label}",
        f"  {_BOLD}Log level{_RESET}     {cfg.log_level}",
        f"  {_BOLD}App version{_RESET}   {cfg.settings.app_version}",
        "",
    ]
    print("\n".join(lines))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    # 1. Load configuration — single source of truth
    try:
        settings = Settings()
    except Exception as exc:
        print(f"{_RED}[FATAL] Configuration error: {exc}{_RESET}", file=sys.stderr)
        print(
            "       Ensure all required variables are set in .env "
            "(see .env.example for reference).",
            file=sys.stderr,
        )
        return 1

    # 2. Parse CLI — overrides only, all defaults come from Settings
    parser = _build_parser(settings)
    args = parser.parse_args()

    # 3. Resolve unified config
    cfg = _resolve_config(settings, args)

    # 4. Pre-flight validation
    errors, warnings = _validate(cfg)

    for warning in warnings:
        print(f"{_YELLOW}[WARNING] {warning}{_RESET}", file=sys.stderr)

    if errors:
        for error in errors:
            print(f"{_RED}[ERROR] {error}{_RESET}", file=sys.stderr)
        print(
            f"\n{_RED}Server startup aborted due to configuration errors above.{_RESET}",
            file=sys.stderr,
        )
        return 1

    # 5. Startup banner (no secrets printed)
    _print_banner(cfg)

    # 6. Hand off to Uvicorn
    uvicorn.run(
        "app.main:app",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.reload,
        workers=cfg.workers,
        log_level=cfg.log_level,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
