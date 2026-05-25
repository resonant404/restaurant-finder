# restaurant-finder

A Claude skill for finding restaurants that match what you actually want — whether you ask in explicit terms ("vegan lunch near Liverpool Street under £20") or in vibes ("somewhere good for a summer day", "a place to impress a date").

## What it does

- Resolves location from context or asks when the request looks travel-related.
- For explicit criteria, searches directly.
- For implicit / mood-based criteria, identifies 2–3 plausible interpretations and asks which one fits before searching — so you don't get a list built on a guess about what you meant.
- Returns a ranked text list of 3–5 picks, each with a one-line rationale tied to your actual criteria (not generic praise).

## Install

Clone the repo and run the build script:

```bash
git clone https://github.com/<your-username>/restaurant-finder
cd restaurant-finder
./build.sh
```

`build.sh` does two things:

- **Installs into Claude Code** at `~/.claude/skills/restaurant-finder/`. Restart Claude Code and the skill is live.
- **Builds an upload bundle** at `dist/restaurant-finder.zip`. Drag this into **Settings → Capabilities → Skills → Upload skill** on claude.ai.

To pick up upstream changes later, just re-run it:

```bash
git pull && ./build.sh
```

If you only want one target, set `SKIP_LOCAL_INSTALL=1` or `SKIP_ZIP=1` in the environment.

## Search backends

The skill tries three sources in order — pick whichever you're willing to set up:

**1. Google Maps MCP server (preferred).** Structured Places data, no script in the loop. Install Google's official Maps Platform MCP server (or any community one), register it in Claude Code, and the skill auto-detects it. You'll need a Google Cloud project with the Places API (New) enabled and a key — the $200/month free tier covers normal personal use.

**2. Bundled fallback script.** If no MCP server is found, the skill runs `scripts/places_search.py` (stdlib Python, ships with the install). Same Google Places API under the hood — set the key in your shell:

```bash
export GOOGLE_PLACES_API_KEY=...
```

Add it to your `.zshrc` / `.bashrc` so Claude Code inherits it. If you keep secrets in a manager like 1Password / Bitwarden / `pass`, export the key the same way you do for any other CLI — e.g. `export GOOGLE_PLACES_API_KEY="$(op read 'op://...')"` or run Claude via `op run --env-file=... --`. The script just reads `$GOOGLE_PLACES_API_KEY`; it doesn't care how the variable got populated.

For the claude.ai upload zip, set the key before running `build.sh` and it'll be baked into the zip's `scripts/.env` (zip only — never the repo, never the local install).

**3. Web search.** If neither (1) nor (2) is configured, the skill falls back to web search and prepends a warning to its response. Results work but lose structured fields (price level, current open status, etc.) and lean on paraphrased article snippets.

## Examples

**Explicit:**
> "Vegan lunch near Liverpool Street, under £20"
→ Direct search, ranked list.

**Implicit:**
> "Somewhere good for a summer day in Soho"
→ Branches first: outdoor seating? air-conditioned? summery food? — then searches based on your pick.

*If none of the above are available, we offer a fallback:*

![](assets/dyson.jpg)

## License

MIT

