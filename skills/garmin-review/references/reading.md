# Reading Garmin data

| Request | Tool and approach |
| --- | --- |
| Find or compare activities | Start with `garmin_list_activities` using the requested dates and sport. Follow pagination within the requested period. Use equal-length comparison windows by default, name the dates and flag a partial current period. Use the account's calendar dates where available and state a meaningful date or time-zone assumption. |
| Inspect an activity | Resolve its ID with the list, then call `garmin_get_activity`. If several records match, show the identifying details needed to pick one. Use the current Garmin Connect summary for distance, duration and derived pace where it differs from device samples. |
| Review laps, sensors or effort | Use `garmin_get_activity_laps`, `garmin_get_activity_samples` or `garmin_get_activity_effort` only when relevant. Follow `nextOffset` for the sample range needed. Distinguish laps and samples from corrected activity totals and flag missing effort or feeling. |
| Running trends and records | Use `garmin_get_running_trends` for supported 28–90-day running windows and `garmin_get_personal_records` for Garmin's recorded personal bests. For a different comparison window, use bounded activity reads. Label incomplete trends and distinguish tool-provided records from bests derived from the retrieved subset. |
| Daily metrics | Use `garmin_get_daily_health` for a date and metric such as sleep, heart rate, HRV, Body Battery, stress, steps or weight. Use `garmin_get_daily_summaries` for a supported date range. Label the metric, units and calendar dates. |
| Menstrual cycle tracking | Use `garmin_get_menstrual_cycle_summary` for a summary or `garmin_get_menstrual_cycle_day` for details on a specific date. See [Menstrual cycle records](#menstrual-cycle-records) for dates, estimates and missing data. |
| Saved workouts | Use `garmin_list_workouts` to locate records and `garmin_get_workout` with the selected workout ID to inspect one. |
| Other Garmin data | Use `garmin_data_catalog` to discover supported queries before calling `garmin_read_data`. Use the catalog's argument definitions and never invent upstream paths. |
| Connection status | Use `garmin_account_status` if exposed and relevant. If the MCP connection itself is unavailable, direct the user to their host's connection setup or work with data they choose to supply. |

When combining Garmin results with another user-authorized source, label each source and align dates and units before calculating. Link to the activity if the tool supplied a link. For a chart or export, use only the necessary fields and avoid sharing it externally without explicit authorization.

## Menstrual cycle records

Read cycle data when the user asks for it. Use their Garmin calendar date as `calendarDate` in `YYYY-MM-DD` format. For the day view, pass the current date in the user’s time zone as `todayDate`, including when looking up an earlier day. Use `includeAnalysis: true` when the user asks for Garmin’s analysis. If only the generic tool is available, look up the supported cycle endpoints and arguments with `garmin_data_catalog`. [Garmin Personal API reference client](https://github.com/garmin/connect-personal-api-python)

Identify logged records and Garmin estimates separately. When a successful response is empty or lacks a requested value, say what Garmin did not return for that date. If the call fails, report the failed read separately. Use the returned records to answer the request and keep clinical conclusions, pregnancy inferences and fertility advice out of the cycle review.
