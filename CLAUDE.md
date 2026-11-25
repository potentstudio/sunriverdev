# SunRiver website

This repository is the SunRiver website. It replaces the Squarespace site at sunriver.com. `README.md` explains how the
build works (forms, tracking, images, search tags). This file is the rules.

## Who it is for

- **Company:** SunRiver Firelight, a 55+ active adult home builder, operated by SunRiver (SunRiver Communities).
- **Where:** the Firelight master-planned community in Toquerville, Utah, near St. George.
- **Owner:** Clark. He owns the GitHub repository, the Vercel team and the Sanity project. Ask him before anything that
  changes who has access, costs money, or creates something new (see "Never create infrastructure").

## Content rules (non-negotiable)

1. **Never invent facts.** No made-up statistics, dates, addresses, prices, amenity claims, phone numbers or company
   facts. Use only what the owner provided or what is already in this repository or in Sanity.
2. **A gap gets a placeholder, not a guess.** Insert a clearly marked `[PENDING]` and flag it to the owner.
3. **Terminology**
   - Say **"members"**, never "residents".
   - The community facility is **"the Clubhouse"** (capitalized, with "the").
   - **No em dashes** in customer-facing copy. `add()` in `sitegen/lib.py` fails the build if a page contains one.
   - **"Firelight" alone means the master-planned development.** For the community, the builder or this website, say
     **"SunRiver Firelight"**.
4. **Future amenities stay in the future tense.** Anything not built yet, including the Clubhouse, is written as
   "will" everywhere on the site.
5. **"Founders Club" language is approved** (cleared by the owner in July 2026).
6. **Private data stays private.** Buyer names, lenders, trust IDs and anything else from internal sales or jobsite
   sheets never go on the site, into this repository, or into Sanity.
7. **Drive times from SunRiver Firelight, confirmed by the owner (Nov 2026):** Zion National Park (Springdale entrance)
   31 minutes, St. George 24 minutes, Cedar City 35 minutes. Use these everywhere. Any other drive time needs a source.
8. **No golf at SunRiver Firelight, and no interest rates or percentages** in copy.

## Where each kind of content lives

One home for each kind of content. Do not add a second source for something that already has one.

| Content | Lives in | How to change it |
|---|---|---|
| Blog posts (Bucketlist Living) | Sanity, type `post` | Create or edit the post in Sanity. Photos are uploaded to Sanity. `data/local_posts.json` stays empty. |
| Floor plans | Sanity, type `floorPlan` | Edit in Sanity. `data/overrides.json` is only for a correction that cannot be made in Sanity yet; remove the entry once Sanity is right. |
| SunRiver Firelight homes for sale and prices | `data/inventory.json` (the sales team's Move-In Ready sheet) | The owner sends a screenshot of the latest sheet; rewrite `asOf` and `homes` to match it exactly. A home that also has a Sanity `homeListing` at the same street address keeps that listing's photos, videos and page address; price, status and specs always come from the sheet. |
| Homes in other communities | `data/mls_listings.json` | Same idea: this file sets price, status and specs. |
| Page text, layout, forms, design | The code in `sitegen/` and `assets/` | Edit the code. |
| Clubs and calendar on Live On | `data/live_on.json` | Edit the file. |

Sanity project: `ib6s13lu`, dataset `production` (public read). The site reads it at build time.

## Workflow and deployment

- **A push to `main` goes live.** Vercel project `sunriverdev` in the SunRiver Communities team builds every push.
  Build locally first: `OFFLINE=1 python3 build.py` (snapshots) or `python3 build.py` (live Sanity content).
- **Never create infrastructure:** no new Vercel projects, Sanity projects or datasets, domains, or hosting accounts
  without the owner's say-so.
- **Do not change** `framework`, `installCommand`, `buildCommand` or `outputDirectory` in `vercel.json`, and do not
  convert the site to another framework.
- **Hidden pages** (drafts, ad landing pages) are listed in `NOINDEX` in `sitegen/seo.py`.
- **Forms** post to HubSpot. Never send test submissions to HubSpot without the owner's go-ahead: every one creates a
  contact, pings Slack and assigns a lead owner.
