"""
Command-line interface for Telos-Scale.
"""

import argparse
import sys
import os
import logging
from typing import Optional
import yaml
from dotenv import load_dotenv
from telos_scale import TelosScale

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from .env and config.yml."""
    load_dotenv()
    config = {}
    if os.path.exists("config.yml"):
        with open("config.yml", "r") as f:
            try:
                config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to parse config.yml: {e}")
    return config


def setup_logging(verbose: bool):
    """Configure logging level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
    )


def run_command(args):
    """Execute the main run loop."""
    setup_logging(args.verbose)
    logger.info(f"Starting Telos-Scale v0.1 with {args.loops} loops, workers={args.workers}")
    agent = TelosScale(
        shared_url=args.shared_url if args.share else None,
        model=args.model,
        sandbox_image=args.sandbox_image,
        sandbox_memory_limit=args.sandbox_memory,
    )
    agent.run(loops=args.loops, workers=args.workers)
    logger.info("Run completed.")


def status_command(args):
    """Show current status."""
    setup_logging(args.verbose)
    # Placeholder: show some stats
    print("Telos-Scale v0.1")
    print("No active runs.")
    print("Use 'telos-scale run' to start.")


def list_command(args):
    """List past trials."""
    setup_logging(args.verbose)
    # For v0.1, just show placeholder
    print("Past trials functionality not yet implemented.")


def export_command(args):
    """Export results to JSON."""
    setup_logging(args.verbose)
    print(f"Exporting results to {args.output} (not implemented)")


def dashboard_command(args):
    """Start web dashboard."""
    setup_logging(args.verbose)
    print("Dashboard not yet implemented. Use 'telos-scale demo' for simple demo.")


def demo_command(args):
    """Run a simple demo."""
    setup_logging(args.verbose)
    from telos_scale import TelosScale
    print("=== Telos-Scale Demo ===")
    agent = TelosScale()
    print("Running a single autonomous loop...")
    result = agent.run_loop()
    print(f"Goal: {result['goal']}")
    print(f"Result: {result['result'][:200]}...")
    print("Demo completed.")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="telos-scale",
        description="Autonomous AI agent platform for massive parallel experimentation.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    config = load_config()

    # run command
    run_parser = subparsers.add_parser("run", help="Run autonomous loops")
    run_parser.add_argument("--loops", type=int, default=config.get("loops", 10), help="Number of loops to execute")
    run_parser.add_argument("--workers", type=int, default=config.get("workers", 1), help="Number of parallel workers")
    run_parser.add_argument("--model", type=str, default=config.get("model", "gemini/gemini-flash-latest"),
                          help="LLM model to use")
    
    # Enable sharing if explicitly set in cli, or if set to true in config
    run_parser.add_argument("--share", action="store_true", default=config.get("share", False), help="Enable sharing")
    run_parser.add_argument("--shared-url", type=str,
                          default=config.get("shared_url", "https://api.telos.scale"),
                          help="Shared server URL")
    run_parser.add_argument("--sandbox-image", type=str,
                          default=config.get("sandbox_image", "python:3.11-slim"),
                          help="Docker image for sandbox")
    run_parser.add_argument("--sandbox-memory", type=str,
                          default=config.get("sandbox_memory", "512m"),
                          help="Memory limit for sandbox container")
    run_parser.add_argument("--verbose", "-v", action="store_true",
                          help="Enable verbose logging")
    run_parser.set_defaults(func=run_command)

    # status command
    status_parser = subparsers.add_parser("status", help="Show current status")
    status_parser.add_argument("--verbose", "-v", action="store_true")
    status_parser.set_defaults(func=status_command)

    # list command
    list_parser = subparsers.add_parser("list", help="List past trials")
    list_parser.add_argument("--verbose", "-v", action="store_true")
    list_parser.set_defaults(func=list_command)

    # export command
    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument("--output", "-o", default="results.json",
                             help="Output file")
    export_parser.add_argument("--verbose", "-v", action="store_true")
    export_parser.set_defaults(func=export_command)

    # dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    dashboard_parser.add_argument("--port", type=int, default=8050,
                                help="Port for dashboard")
    dashboard_parser.add_argument("--verbose", "-v", action="store_true")
    dashboard_parser.set_defaults(func=dashboard_command)

    # demo command (extra)
    demo_parser = subparsers.add_parser("demo", help="Run a simple demo")
    demo_parser.add_argument("--verbose", "-v", action="store_true")
    demo_parser.set_defaults(func=demo_command)

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()