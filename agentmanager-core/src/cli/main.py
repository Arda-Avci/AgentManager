from __future__ import annotations

import asyncio
import sys

import click

from src.database.engine import init_db


@click.group()
def cli():
    pass


@cli.command()
def start():
    click.echo("Starting AgentManager Core...")
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=3010, reload=True)


@cli.command()
def init():
    click.echo("Initializing database...")
    asyncio.run(init_db())
    click.echo("Database initialized.")


@cli.command()
@click.argument("name")
@click.option("--role", default="assistant", help="Agent role")
@click.option("--provider", default="openai", help="LLM provider")
@click.option("--model", default="gpt-4o", help="Model name")
def create(name, role, provider, model):
    click.echo(f"Creating agent: {name} ({role}, {provider}/{model})")
    from httpx import AsyncClient

    async def _call():
        async with AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:3010/api/v1/agents",
                json={"name": name, "role": role, "provider": provider, "model": model},
            )
            click.echo(resp.json())

    asyncio.run(_call())


@cli.command()
def status():
    click.echo("Fetching agent status...")
    from httpx import AsyncClient

    async def _call():
        async with AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:3010/api/v1/agents")
            agents = resp.json()
            if not agents:
                click.echo("No agents found.")
                return
            for a in agents:
                click.echo(
                    f"  [{a['status']:>8}] {a['name']:20} {a['provider']}/{a['model']}"
                )

    asyncio.run(_call())


def main():
    if len(sys.argv) < 2:
        sys.argv.append("--help")
    cli()
