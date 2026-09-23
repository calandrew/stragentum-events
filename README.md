# Stragentum Event Scout

Fortnightly automated scan of Auckland business events for Stragentum networking.

- `calendar.ics`: subscribed Outlook feed ("Stragentum Prospect Events"). Raw URL: https://raw.githubusercontent.com/calandrew/stragentum-events/main/calendar.ics
- `events.json`: event store, source of truth for the feed
- `SPEC.md`: research brief each run follows (edit to change sources, filters or scoring)
- `scout.py`: merge and ICS renderer
