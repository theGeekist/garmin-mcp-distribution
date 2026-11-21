# Reading Garmin data

Choose the smallest appropriate set of tools for the user's question. Use tool discovery and schemas from the actual connection rather than relying on names remembered from an older release.

| User request | Tool selection and interpretation |
| --- | --- |
| Recent runs, activities or comparisons | Start with `garmin_list_activities` for bounded date and sport filters. For advanced text or performance filters use `garmin_search_activities`. Follow pagination where required. Compare equal-length, complete periods unless the user asks otherwise. |
| One activity | Resolve the activity ID from the list or search, then use `garmin_get_activity` for current totals. Use `garmin_get_activity_details` only when its additional fields are relevant. If several records match, identify the candidates rather than picking one arbitrarily. |
| Lap timing, effort, heart rate or other sensors | Use `garmin_get_activity_laps` for laps, `garmin_get_activity_effort` for perceived effort and `garmin_get_activity_samples` for recorded time-series data. Follow `nextOffset` for the necessary range. Prefer corrected Garmin Connect totals to recorded file values for final distance, duration and derived pace. |
| Original exercise file | Use `garmin_get_activity_fit_file` for original FIT/ZIP file data when an export or file-level investigation is requested, respecting paging and checksum continuity. |
| Personal bests or running progress | Use `garmin_get_personal_records` for Garmin's recognised records and `garmin_get_running_trends` for supported 28–90-day periods. For other windows use appropriately bounded activity history. Clearly distinguish Garmin-held records from bests calculated over a retrieved subset, and mark incomplete analyses. |
| Daily recovery or activity metrics | Use `garmin_get_daily_health` for one date and metric and `garmin_get_daily_summaries` for a supported cross-metric period. Use a dedicated metric history tool for a deeper trend in sleep, heart rate, HRV, Body Battery, stress, steps, hydration or weight. |
| Daily or historical wellness | Use `garmin_get_wellness_summary` for a native daily wellness response and `garmin_get_wellness_history` for its historical equivalent; do not assume these are identical to convenience summaries. |
| Weight | Use `garmin_get_weight_history` for progression, `garmin_get_weight_measurements` for individual readings and `garmin_get_weight_goals` when goals matter. |
| Heart-rate training zones or fitness age | Use `garmin_get_heart_rate_zones` or `garmin_get_fitness_age`, respectively, if the question requires Garmin's configured zones or estimate. |
| Saved workouts | Use `garmin_list_workouts` to find saved sessions and `garmin_get_workout` to inspect one. For the workout linked to a completed activity, use `garmin_get_activity_workouts`. |
| Other documented data | Use `garmin_data_catalog` to discover available endpoints and dedicated tools. Prefer the dedicated tool. Use `garmin_read_data` only if it remains exposed and needed for data not supported by the dedicated interface. Do not invent endpoint paths or parameters. |
| Account and connection | Use `garmin_account_status` for relevant connection capabilities. Use `garmin_get_profile_settings` when units or account preferences matter. If the connection itself is unavailable, direct the user to its host's reconnect flow and Geekist support. |

Align time zones, calendar dates, measurements and units across combined results. Report which period and data support calculations; do not silently treat a partial or missing record as a complete zero. For charts or exports, include the fields necessary for the request and confirm before external sharing.


Retrieved FIT files may contain GPS and device details; request them only when relevant to the user’s intended analysis.
