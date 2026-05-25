---
name: restaurant-finder
description: Find restaurants matching user criteria, whether the criteria are explicit (vegan, no spice, has coffee, open late, under £30/head) or implicit/vibes-based ("good for a summer day", "somewhere to impress a date", "a place to read alone"). Use this skill whenever the user asks for a restaurant, café, bar, or place to eat or drink — even casually phrased ("where should I go for dinner", "anywhere nice nearby", "I want noodles"). Especially important when the request contains vibes, moods, occasions, or weather references rather than concrete filters, because those need interpretation before searching.
---

# Restaurant finder

Help the user find a restaurant that actually matches what they want, including when what they want isn't literally what they said.

## Core workflow

1. **Resolve location.** If the user named a place ("in Soho", "near King's Cross"), use that. Otherwise default to their known location from context. If the request looks travel-related ("when I'm in Lisbon next week", "for my Tokyo trip"), confirm the location before searching rather than assuming home.

2. **Classify the criteria.** Read what they asked for and separate it into:
   - **Explicit constraints** — concrete filters: cuisine, price, dietary needs, "has X", "open late", "outdoor seating", "good for groups". Use these directly.
   - **Implicit / vibes criteria** — moods, occasions, weather, feelings: "summer day", "cosy", "date night", "post-work", "rainy afternoon", "I need cheering up". These map to multiple plausible interpretations.

3. **Handle implicit criteria with interpretation branches.** Do not silently pick one reading and search for it — the user usually has a specific picture in mind and a single guess is likely wrong. Instead, identify 2–3 plausible directions the phrase could go and present them to the user before searching. Examples:

   - *"Good for a summer day"* → (a) outdoor seating / terrace / garden, (b) air-conditioned and cool inside, (c) light summery food (salads, seafood, cold noodles, gelato).
   - *"Somewhere to impress a date"* → (a) elegant fine-dining, (b) intimate / candlelit / small-plates, (c) interesting or unusual concept that gives you something to talk about.
   - *"Cosy autumn evening"* → (a) warm interior with fireplace / wood, (b) hearty comfort food (stews, pasta, ramen), (c) wine bar or pub with character.
   - *"Working from a café"* → (a) wifi + power + table space (laptop-friendly), (b) quiet and calm, (c) good coffee specifically.

   Present these as a short choice — "I read this a few ways: A, B, or C — which fits, or shall I do a mix?" — then search.

   If the criteria are explicit and clear, skip this step and search directly.

4. **Search.** Pick the best available backend in this order — A, then B, then C.

   **A. Google Maps MCP server.** Check your available tool list for an MCP places-search tool — anything matching `mcp__*maps*` or `mcp__*places*` (e.g. `mcp__google_maps__search_places`). If one is present, use it. This is the preferred path: structured JSON, no script execution, no fragile parsing.

   **B. Bundled fallback script.** Otherwise, run the bundled script via Bash:
   ```
   python3 "$SKILL_DIR/scripts/places_search.py" "<query1>" ["<query2>" ...]
   ```
   `$SKILL_DIR` is the directory containing this SKILL.md (typically `~/.claude/skills/restaurant-finder`). Pass each interpretation as a separate argument — the script runs them in parallel and returns one JSON object keyed by query.

   - **Exit 0:** parse and use the JSON.
   - **Exit 3 with stderr `GOOGLE_PLACES_API_KEY not set`:** fall through to (C).
   - **Any other non-zero exit:** also fall through to (C).

   **C. Web search fallback.** Use `web_search`. When you fall back to (C), **the response to the user MUST begin with this exact warning** (verbatim, on its own line at the top):

   > ⚠ No Places API available — using web search. Results are paraphrased from articles and may be outdated, incomplete, or inaccurate. See the README for setup.

   Do NOT include the warning when (A) or (B) succeeded.

   **Query construction (all tiers):** combine resolved criteria with the location. "restaurants with terrace Soho London" beats "summery restaurants Soho" — concrete attributes outrank mood words. For multi-interpretation searches the user wants a mix of, fire parallel queries: multiple args to the script in (B), or multiple `web_search` / MCP calls in a single message.

5. **Filter and rank.** Skim results for fit. Drop obvious mismatches (chain when they wanted independent, wrong cuisine, closed permanently, very low rating with few reviews). Rank by how well each matches the *actual* criteria, not just by Google rating.

6. **Present as a ranked text list with reasoning per pick.** For each restaurant, give:
   - **Name** — neighbourhood
   - One sentence on why it fits *their* criteria (not generic praise)
   - Practical detail that matters for the request: price band, whether to book, opening hours if relevant, the specific dish or feature that justifies the pick

   Aim for 3–5 picks. More than that is noise; fewer feels thin unless the brief is very narrow.

## Verifying attributes Places can't confirm

Places data does not expose many attributes users care about — aircon, noise level, laptop-friendliness, dish availability. How you handle this depends on *how the attribute entered the conversation*.

**A. User explicitly insists on the attribute** (e.g. "must have aircon", "needs to be quiet enough to talk", "definitely has high chairs"). Don't just hedge — actually try to verify. In rough order of effort:

1. **Check Places fields you might have skipped.** `accessibilityOptions` is a real field — use it directly for wheelchair access rather than inferring. Same for `outdoor_seating` types, `reservable`, etc.
2. **Restaurant website.** `WebFetch` the `websiteUri` from the Places result and search for the attribute (e.g. "air con", "climate control", "fully air conditioned"). Newer venues often advertise these.
3. **Review text mining.** The Places result returns a handful of reviews. Skim them for keywords:
   - AC: `"stuffy"`/`"hot inside"`/`"sweltering"` → likely no AC; `"freezing"`/`"too cold"`/`"bring a jacket"` → AC present.
   - Noise: `"loud"`/`"noisy"`/`"can't hear"` → loud; `"quiet"`/`"intimate"` → quiet.
   - Work-friendly: `"wifi"`/`"plug"`/`"laptop"`/`"worked here"` → yes.
   - Family-friendly: `"high chair"`/`"kids menu"`/`"family"` → yes.
   - Reviews written during heatwaves (UK Jul/Aug) are particularly load-bearing for AC questions.
4. **Strong proxies when direct evidence is thin** — use as *signal, not proof*, and mark inferred picks as such ("modern fit-out so likely AC, not confirmed"):
   - Modern build / shopping centre / hotel / basement venue → AC near-certain.
   - Listed building / Victorian pub / old converted warehouse → often no AC.
   - Chain / fine-dining / modern Asian / sushi → AC near-certain.
   - Sports bar → loud; omakase counter / tasting menu → quiet.

Show the evidence trail briefly so the user can judge ("website mentions AC", "two reviews complain about heat", "inferred from building type").

**B. The attribute came from a vibe direction *you* proposed** (e.g. user said "good for a summer day", you offered "air-conditioned" as one branch, they picked it). Don't escalate to website/review mining by default — that's expensive for what's still a guess at their preference. Instead, after the Places search, **flag in the response that the attribute isn't directly confirmable from the data**, and let them decide whether to enforce it. Example:

> Heads-up: Places doesn't expose aircon as a field, so I've ranked by likely-AC proxies (modern build, indoor-focused). Want me to verify by checking websites/reviews?

This keeps the default response tight while making the gap visible.

## Things to get right

**Don't invent details.** Only state facts that came from the search results (rating, address, hours, listed features). Do not claim "great wine list" or "famous for X" unless the result data actually supports it. If the user wants a specific guarantee ("definitely has outdoor seating"), say where you got that — and if it's not in the data, say so and suggest they check the restaurant directly. **When using the (C) web_search fallback, this rule binds especially hard: snippets are paraphrased third-party prose, not authoritative facts. Hedge claims that aren't directly quoted in the snippet.**

**Match the register.** A "where should I grab a quick lunch" query gets a tighter, more casual answer than "anniversary dinner". Don't over-engineer.

**Respect what they said no to.** If they said "not Italian", don't include Italian even if it's the highest-rated nearby. Negative constraints are usually the strongest signal.

**One follow-up max.** If after interpretation and searching the result still feels off (e.g. nothing in their price range), say so and ask one focused question rather than firing off a second round of clarifications.

**Edge cases.**
- Very small town or rural area with few options: present what exists honestly, don't pad the list.
- User wants something the location famously lacks ("authentic ramen in [small town]"): say so directly and offer the closest alternative.
- Time-sensitive ("open right now"): factor opening hours into ranking, not just into the description.

## Example

**User:** "I want somewhere good for a summer day in Soho"

**Response shape:**

> A few ways to read "summer day" — which fits?
> - **Outdoor seating** — terrace, garden, or pavement tables
> - **Cool & air-conditioned** — escape the heat, light interior
> - **Summery food** — seafood, salads, cold dishes, frozen drinks
>
> Or I can give you a mix.

Then on their reply, search and return a ranked list with one-line rationales.

