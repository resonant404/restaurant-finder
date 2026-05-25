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

