# restaurant-finder

A Claude skill for finding restaurants that match what you actually want — whether you ask in explicit terms ("vegan lunch near Liverpool Street under £20") or in vibes ("somewhere good for a summer day", "a place to impress a date").

## What it does

- Resolves location from context or asks when the request looks travel-related.
- For explicit criteria, searches directly.
- For implicit / mood-based criteria, identifies 2–3 plausible interpretations and asks which one fits before searching — so you don't get a list built on a guess about what you meant.
- Returns a ranked text list of 3–5 picks, each with a one-line rationale tied to your actual criteria (not generic praise).

## Install

### Claude.ai / Claude apps

1. Download the `restaurant-finder.skill` file from the releases page (or build it yourself, see below).
2. Upload it via **Settings → Capabilities → Skills → Upload skill**.

### Claude Code

```bash
npx skills add https://github.com/<your-username>/restaurant-finder
```

Or clone into your skills directory:

```bash
git clone https://github.com/<your-username>/restaurant-finder ~/.claude/skills/restaurant-finder
```

## Build the `.skill` file yourself

The `.skill` file is just a zip of this folder. From the parent directory:

```bash
cd restaurant-finder && zip -r ../restaurant-finder.skill . -x "*.DS_Store" && cd ..
```

## Examples

**Explicit:**
> "Vegan lunch near Liverpool Street, under £20"
→ Direct search, ranked list.

**Implicit:**
> "Somewhere good for a summer day in Soho"
→ Branches first: outdoor seating? air-conditioned? summery food? — then searches based on your pick.

## License

MIT

