# welcome to my personal project 🌸

i am training for a marathon and triathlon next year, so naturally a massive fan of strava and garmin. i love training
and i track everything here... but they don't talk to each other. strava shows pace, segments while garmin shows vo2 max, sleep but none of it connects.
i want to understand how my sleep affected my runs, or how training load is linked to recovery, to optimise my training! 🚀 <br/>

so... i decided to turn my endurance life into a data project! i plan to pull everything into one place and treat this as a data science experiment. 
exploring and analysing patterns, trends before forecasting performance... (or fatigue!) - not just looking at single trends in isolation. 
i am trying to make sense of the scattered metrics and numbers to uncover the hidden relationships and discover hidden insights. ✨

# roadmap 🧭
1 [define goal](#define-goal) <br/>
2 [collect data](#collect-data) <br/>
3 [transform](#transform) <br/>
4 [analyse and forecast](#analyse-and-forecast) <br/>
5 [visualise](#visualise) <br/>

## define goal 🌠
- trend analysis
- predictive insights
- dashboard
  
what do i want to discover?

| **key area**    | **question**                                         |
| --------------- | ---------------------------------------------------- |
| **performance** | how has my swim and run pace improved over the year? |
|                 | what conditions correlate with best performance?     |
|                 | what is my aerobic efficiency trend?                 |
| **motivation**  | what days and times do i perform better?             |
| **recovery**    | how does poor sleep affect my pace and HR?           |
| **external conditions** | what is my aerobic efficiency trend?         |

## collect data 📊
strava:
- strava api - python
- garmin - manual export connect.garmin.com (desktop) → Activities → Select any → Export → choose .CSV or .FIT.
  
## transform 🔧
- standardise fields
- merge using datetime
- single dataset in pandas df
  
## analyse and forecast 👩🏻‍💻
- exploratory data analysis:
- trend analysis (pace, HR, mileage), distribution (HR zones, run pace, weekly distance) correlation (cadence vs efficiency)
- forecast (predict future performance)
## visualise 📈
python (pandas, matplotlib):
- line charts - pace, mileage
- scatter plots - HR vs. pace, sleep vs. performance
- calendar heatmaps <br/>
powerbi:
- dashboard



