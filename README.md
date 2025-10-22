## Prerequisites

- Python 3.13 or newer.

## Installing uv and running the agent

To check if `uv` is installed, run:

```bash
uv --version
```

## Environment variables

```
# .env.local example
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
LIVEKIT_URL=your_livekit_url
NEXT_PUBLIC_LIVEKIT_URL=your_livekit_url
# any other vars your environment needs
```

Adjust names and values according to your runtime configuration.

## How to run the agent

Install library:
```bash
uv sync
```

Run the agent script:

```bash
uv run src/agent.py dev
```
