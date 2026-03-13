# Dashboard Logic (v1.0)

## Sheets
- Raw Data: direct form responses
- Per Student: aggregation by student_id_hash
- Alerts: inactivity and risk flags
- GPS Tracker: daily G/P/S distribution

## Suggested Columns (Per Student)
- student_id_hash
- total_entries
- last_entry_date
- g_count
- p_count
- s_count
- avg_satisfaction
- avg_difficulty

## Example Formulas (Google Sheets)
- total_entries: `=COUNTIF(Raw!B:B, A2)`
- last_entry_date: `=MAX(FILTER(Raw!A:A, Raw!B:B=A2))`
- g_count: `=COUNTIFS(Raw!B:B, A2, Raw!E:E, "G")`
- p_count: `=COUNTIFS(Raw!B:B, A2, Raw!E:E, "P")`
- s_count: `=COUNTIFS(Raw!B:B, A2, Raw!E:E, "S")`
- avg_satisfaction: `=AVERAGEIF(Raw!B:B, A2, Raw!I:I)`
- avg_difficulty: `=AVERAGEIF(Raw!B:B, A2, Raw!J:J)`

## Alerts Logic
- Inactivity (>= 3 days): `=TODAY() - last_entry_date >= 3`
- Low satisfaction: `avg_satisfaction <= 2.5`
- High difficulty: `avg_difficulty >= 4`

## Charts
- Pie chart: G/P/S distribution (daily or weekly)
- Line chart: entries per day
- Bar chart: per-student total entries
