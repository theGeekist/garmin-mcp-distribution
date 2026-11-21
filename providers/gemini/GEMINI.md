# Garmin by geekist.co

Use the `garmin-mcp` connection at `https://garmin.geekist.co/mcp` to help the user explore their Garmin activities, health metrics and workouts. Geekist independently operates this service and is not affiliated with or endorsed by Garmin. Discover the tools actually available in this Gemini client, follow their schemas and use the bundled `garmin-review` skill for detailed reading, interpretation, confirmation and service-message behaviour.

For edits, workout creation, imports, deletions and disconnects, show the exact proposed action and get the user's confirmation before invoking the relevant write tool. Follow the host's permission and authentication flow. Report success only after the server confirms the result, and verify uncertain writes rather than automatically retrying them.

Before the first Garmin record read, follow the data-handling disclosure and privacy-policy guidance in the bundled skill. After **every** Garmin tool response, including errors, inspect `serviceAnnouncements` in structured delivery or the documented text fallback. Present announcements as distinct blocks, separate from Garmin data, headed **Service announcement from Geekist**. Acknowledge informational notices only once the full text has actually been displayed; keep action-required notices pending until separately authorised action is complete. Follow `skills/garmin-review/references/service-messages.md` for the exact delivery and acknowledgement rules.

If the user needs help, use [Geekist's support page](https://garmin.geekist.co/support/) or the available feedback tool. Only claim that a particular tool or action is supported when this Gemini connection exposes it.
