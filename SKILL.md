---
name: trendsMonitoring
description: Fetches and reports on real-time Google Trends for Guatemala in Politics, Law & Government, and Business & Finance.
allowed-tools:
  - shell
  - read_file
  - write_file
---

# Trends Monitoring Skill

Use this skill to monitor what is trending in Guatemala and generate automated reports.

## Commands
- `/monitoring:trends`: Executes the full pipeline (fetch, visualize, report).

## Technical Stack
- **Data Source:** Google Trends (pytrends)
- **Visualization:** Matplotlib
- **Reporting:** WeasyPrint + Jinja2
- **Automation:** GitHub Actions
