# Getting a Google Places API key

The bundled fallback script and Google's official Maps Platform MCP server both authenticate against the same product — **Google Maps Platform** — using the same kind of key. One-time setup:

## Steps

1. **Sign in** to the [Google Cloud Console](https://console.cloud.google.com/).

2. **Create or pick a project.** Top-left project selector → **New Project**. Any name works.

3. **Enable billing.** Nav menu → **Billing** → link a payment method to the project. This is required to create a Maps Platform key. See [Google's billing & pricing docs](https://developers.google.com/maps/billing-and-pricing/overview) for what's free, what isn't, and the current monthly credit.

4. **Enable the Places API (New).** Nav menu → **APIs & Services** → **Library**. Search for **Places API (New)** and click **Enable**.

   > ⚠ There are two: "Places API" (legacy) and "Places API (New)". The bundled script uses the **New** one — enable that, not the legacy.

5. **Create the key.** **APIs & Services** → **Credentials** → **Create credentials** → **API key**. Copy the value somewhere safe (1Password, etc.).

6. **Restrict the key (strongly recommended).** Click **Edit** on the newly created key:
   - **API restrictions** → **Restrict key** → tick only **Places API (New)**. If the key ever leaks, this caps the blast radius — it can't be used against other Google APIs on your bill.
   - **Application restrictions** → leave as **None** for personal CLI use. Set **IP addresses** if you have a stable one.

7. **Set a budget alert (recommended).** Nav menu → **Billing** → **Budgets & alerts**. Pick a threshold you're comfortable with — it's a cheap safety net regardless of expected usage.

## Pricing and free credit

Pricing and free-credit terms change. Rather than mirror them here (and risk going stale), check Google's own pages:

- [Maps Platform billing & pricing overview](https://developers.google.com/maps/billing-and-pricing/overview) — explains the monthly credit and which calls count against it
- [Maps Platform pricing sheet](https://mapsplatform.google.com/pricing/) — current per-call prices, including Places API (New) Text Search

The bundled script calls the **Places API (New) Text Search** endpoint with the Pro field set (it requests rating, opening hours, price level, etc.), so look up that specific row.

## Where to put the key

Once you have it, see the [Search backends section of the README](../README.md#search-backends) for how to wire it into the local install, the claude.ai zip, or a secret manager.
