# Google Sheets Dashboard Formulas (v1.0)

Apply these formulas to your Google Sheets tabs for automatic data analysis.

## Sheet 1: Raw Data
- Primary data source connected to Google Form.
- **Column L (Auto Label)**: Populated by Apps Script.
- **Column M (ID Hash)**: Populated by Apps Script.

## Sheet 2: Per Student
| Field | Formula (Apply to Row 2 and drag down) |
| :--- | :--- |
| **Unique Hash List** | `=UNIQUE('Raw Data'!M2:M)` |
| **Total Logs** | `=COUNTIF('Raw Data'!$M$2:$M, A2)` |
| **% Guide (G)** | `=COUNTIFS('Raw Data'!$M$2:$M, A2, 'Raw Data'!$L$2:$L, "G") / B2` |
| **% Practice (P)** | `=COUNTIFS('Raw Data'!$M$2:$M, A2, 'Raw Data'!$L$2:$L, "P") / B2` |
| **% Solve (S)** | `=COUNTIFS('Raw Data'!$M$2:$M, A2, 'Raw Data'!$L$2:$L, "S") / B2` |
| **Avg Satisfaction**| `=AVERAGEIF('Raw Data'!$M$2:$M, A2, 'Raw Data'!$I$2:$I)` |

## Sheet 3: Alerts
| Alert Type | Formula |
| :--- | :--- |
| **Zero Activity (3 days)** | Populated via `src/tools/gas_script.js` (Email alerting). |
| **Highly Dissatisfied** | `=FILTER('Raw Data'!A2:M, 'Raw Data'!I2:I <= 2)` |

## Sheet 4: GPS Tracker
- **Total Distribution**: `=QUERY('Raw Data'!A2:M, "SELECT L, COUNT(L) GROUP BY L LABEL COUNT(L) 'Total'")`
- **Activity Over Time**: Create a pivot table from `Raw Data` with `Timestamp` (grouped by Day) as Rows and `ID Hash` (Count) as Values.

---
**Note**: Ensure your `Raw Data` range matches the column letters in the formulas.
