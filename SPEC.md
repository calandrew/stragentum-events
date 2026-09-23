# Stragentum Event Scout: research spec

Purpose: surface Auckland business events where Callum Andrew (Founder, Stragentum; strategy consultancy for consumer goods, PE and board clients) can meet decision-makers. Output feeds the "Stragentum Prospect Events" subscribed calendar in Outlook. Every event is UNCONFIRMED until Callum registers.

## 1. Window
Run date (NZ time) to run date + 42 days. Events already in the repo's events.json are re-checked only if they fall inside the window.

## 2. Sources (MECE: work through every tier, in order)
Tier A, anchor chambers (always open the events page directly, never rely on search snippets):
- American Chamber of Commerce in NZ (AmCham NZ)
- Auckland Business Chamber

Tier B, industry and trade associations with Auckland events (locate each official events page):
- Governance and capital: Institute of Directors (Auckland branch), NZ Private Capital, Chapter Zero NZ
- Employers and exporters: EMA (Employers and Manufacturers Association), ExportNZ, BusinessNZ
- Bilateral chambers: British Chamber (BritCham NZ), Europe NZ / EU chambers, Australia NZ business councils, NZ China Council, Asia NZ Foundation, NZ India business bodies
- Consumer goods and marketing: NZ Food & Grocery Council, Retail NZ, FoodHQ / NZ Food Innovation network, Marketing Association NZ, Brands / Advertising bodies
- Innovation and growth: Tātaki Auckland Unlimited, The Icehouse, NZTech / Techweek, NZ Growth Capital Partners, Sustainable Business Network
- Professional bodies: CA ANZ, CPA Australia, Global Women, Deloitte / PwC / KPMG / EY / Bell Gully / Chapman Tripp / Russell McVeagh public client events
Add any other Auckland body discovered during research that clearly hosts senior-audience events.

Tier C, aggregators and news (supplementary, to catch what A and B miss):
- Eventbrite and Humanitix (Auckland, business / networking / leadership)
- NZ Herald Business, BusinessDesk, NBR (incl. NBR and Herald events), Idealog, Stuff Business

Always follow through to the organiser's own booking page. Never use an aggregator URL as `url` when an organiser page exists.

## 3. Filter
Include only: in-person (or hybrid with in-person option) in the Auckland region; open to external registration (or member events Callum could attend as a guest/member); inside the window.
Exclude: online-only webinars, multi-day paid training courses, student/career events, purely technical/product events, events already sold out with no waitlist.

## 4. Score (1 to 5), include if score >= 3
Score = rounded mean of four criteria, each 1 to 5:
1. Audience seniority: share of CEO/CFO/director/owner/PE partner attendees.
2. Theme fit: corporate strategy, growth, M&A/capital, innovation, management, consumer goods/FMCG/retail, trade and export.
3. Networking density: dedicated networking segment, drinks, roundtable format, audience size 40 to 300.
4. Access economics: cost relative to expected senior contacts; free or member-rate is a 5, > NZD 1,000 per head is a 1 unless audience seniority is 5.
Score 3 events are prefixed "[?]" in the calendar automatically. Score 4 to 5 are unprefixed.

## 5. Fields per event (JSON)
Write all shortlisted events to `new.json` as an array. Times are Auckland local, ISO 8601 without offset.

```json
{
  "title": "AmCham Business Breakfast: Trade Outlook 2027",
  "start": "2026-10-14T07:00",
  "end": "2026-10-14T09:00",
  "time_text": "7:00am registration, 7:30am start, 9:00am close",
  "venue": "Cordis Auckland",
  "address": "83 Symonds Street, Grafton",
  "organiser": "AmCham NZ",
  "url": "https://organiser-booking-page",
  "source_url": "https://where-it-was-found",
  "cost": "Members NZD 95, non-members NZD 140 (+GST)",
  "registration": "Online via organiser page; closes 10 Oct",
  "audience": "Exporters, C-suite, trade policy; approx 150",
  "networking": "30 min networking breakfast before programme",
  "speakers": "Names and titles",
  "agenda": "One-line agenda",
  "fit_score": 4,
  "fit_rationale": "One sentence: why this room is worth Callum's time",
  "unverified": "List any field inferred rather than read from the organiser page, else omit"
}
```
Rules: `title`, `start`, `url` are mandatory. If the time is unknown use a date-only `start` ("2026-10-14") and say so in `unverified`. Never invent speakers, prices or times; write "TBC" instead.

## 6. Publish
`python3 scout.py merge --repo . --new new.json`, then `git add -A && git commit -m "Scout run <date>" && git push`
The script upserts by a stable UID (title + date), bumps SEQUENCE when time/venue/cost/url changes, and prunes events more than 14 days past.

## 7. Report (the run's final message, sent via SendUserMessage)
One-line verdict (e.g. "7 new events, 2 worth booking this week"), then a table: date, event, fit score, cost, registration deadline. Flag any event whose registration closes within 7 days. List sources that failed to load so coverage gaps are visible.
