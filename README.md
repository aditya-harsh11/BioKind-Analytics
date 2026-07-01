# Biokind Analytics: BGCDC Student Engagement & Retention Analysis

Data-driven analytics platform that processes and evaluates historical registration, membership, and attendance datasets for the **Boys & Girls Clubs of Dane County (BGCDC)**. This analysis helps identify equity gaps, consistency trends, and drop-out predictors to optimize youth retention programs and resource allocation.

## Key Insights & Statistics
- **The Retention Cliff**: Only **22%** of registered youth return for a 3rd visit. Reaching a 3rd visit is the single strongest indicator of long-term engagement.
- **The Equity Gap**: Economically disadvantaged students visit the club **3x** more frequently than their peers (an average of **5.7 visits** compared to **1.7 visits**).
- **Disengagement Model**: A gradient boosting classifier predicts which youth will disengage (fail to reach a 3rd visit) from demographic features at **0.76 ROC-AUC**, surfacing the highest-need kids for targeted outreach.

## Project Structure
- `Data/`: Contains raw membership and attendance Excel spreadsheets.
- `code/`:
  - [analysis.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/analysis.py): Aggregates raw registers and compiles per-participant attendance timelines.
  - [model.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/model.py): Trains a gradient boosting model to predict youth disengagement from demographic features.
  - [visualize.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/visualize.py): Generates presentation slides styled with BGCDC-inspired aesthetics.
  - [verify_stats.py](file:///Users/aditya/Documents/Resume/2. Biokind-Analytics/code/verify_stats.py): Validates retention and equity figures from processed data.
- `visualization/`: Output folder for generated presentation slides (`slide1_consistency.png` to `slide5_disengagement_model.png`).

## Setup & Usage

### 1. Install Requirements
Make sure you have Python 3 and the required libraries installed:
```bash
pip install pandas numpy seaborn matplotlib openpyxl
```

### 2. Run Data Processing
Clean the raw datasets and compile weekly/monthly attendance timelines:
```bash
python code/analysis.py
```
*Outputs: `processed_engagement_data.csv`, `weekly_attendance.csv`, and `monthly_club_attendance.csv`.*

### 3. Train the Disengagement Model
Train and evaluate the gradient boosting classifier (prints ROC-AUC and top predictors, saves a performance slide):
```bash
python code/model.py
```

### 4. Generate Visualizations
Generate presentation-ready slides:
```bash
python code/visualize.py
```
*Saves slides in the `visualization/` directory.*

### 5. Verify Dataset Stats
Quickly print dataset validation summaries (retention and equity figures):
```bash
python code/verify_stats.py
```
