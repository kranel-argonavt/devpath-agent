# Architecture

The planned architecture centers on a future root agent in `devpath/agent.py` that coordinates specialized sub-agents:

- job analyzer;
- portfolio evidence extractor;
- profile matcher;
- gap planner;
- application writer;
- interview coach;
- privacy guard.

Deterministic helpers will live in `devpath/core/`, shared schemas in `devpath/schemas/`, and optional external integrations in `devpath/services/`. A future `mcp_server/` package will expose selected capabilities to compatible clients.
