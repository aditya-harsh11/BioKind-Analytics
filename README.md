# Biokind Analytics: BGCDC Student Engagement & Retention Analysis

Data-driven analytics platform that processes and evaluates historical registration, membership, and attendance datasets for the **Boys & Girls Clubs of Dane County (BGCDC)**. This analysis helps identify equity gaps, consistency trends, and drop-out predictors to optimize youth retention programs and resource allocation.

## Key Insights & Statistics
- **The Retention Cliff**: Only **22%** of registered youth return for a 3rd visit. Reaching a 3rd visit is the single strongest indicator of long-term engagement.
- **The Equity Gap**: Economically disadvantaged students visit the club **3x** more frequently than their peers (an average of **5.7 visits** compared to **1.7 visits**).
- **High-Risk Segment**: A **3-Factor Risk Index** (based on income, household size, and early attendance) isolates the 6% of students in critical need of scholarships or transportation assistance.

## Project Structure
- `Data/`: Contains raw membership and attendance Excel spreadsheets.
- `code/`:
  - [analysis.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/analysis.py): Aggregates raw registers, calculates timelines, and computes student risk scoring profiles.
  - [visualize.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/visualize.py): Generates 6 custom presentation slides styled with BGCDC-inspired aesthetics.
  - [verify_stats.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/verify_stats.py): Validates retention statistics, risk groups, and equity figures from processed data.
- `visualization/`: Output folder for generated presentation slides (`slide1_consistency.png` to `slide6_equity_gap.png`).

## Setup & Usage

### 1. Install Requirements
Make sure you have Python 3 and the required libraries installed:
```bash
pip install pandas numpy seaborn matplotlib openpyxl
```

### 2. Run Data Processing
Clean the raw datasets, compile weekly/monthly timelines, and calculate risk scores:
```bash
python code/analysis.py
```
*Outputs: `processed_engagement_data.csv`, `weekly_attendance.csv`, and `monthly_club_attendance.csv`.*

### 3. Generate Visualizations
Generate presentation-ready slides:
```bash
python code/visualize.py
```
*Saves slides in the `visualization/` directory.*

### 4. Verify Dataset Stats
Quickly print dataset validation summaries (retention, high-risk groups, and average visits):
```bash
python code/verify_stats.py
```
