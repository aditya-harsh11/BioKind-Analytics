import pandas as pd
import numpy as np

PROCESSED_DATA_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/processed_engagement_data.csv'

def verify_stats():
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # 1. Retention rate from 2nd to 3rd visit
    # The user says "Only about 22% return for a third visit."
    # Let's see how many had >= 2 visits vs >= 3 visits.
    at_least_2 = (df['TotalVisits'] >= 2).sum()
    at_least_3 = (df['TotalVisits'] >= 3).sum()
    if at_least_2 > 0:
        retention_2_to_3 = (at_least_3 / at_least_2) * 100
    else:
        retention_2_to_3 = 0
    
    overall_retention_3 = (at_least_3 / (df['TotalVisits'] >= 1).sum()) * 100
    
    print(f"Retention from 2nd to 3rd visit: {retention_2_to_3:.2f}%")
    print(f"Overall retention for 3rd visit (of all who visited): {overall_retention_3:.2f}%")
    
    # 2. Percentage of high-risk participants (Score 2 or 3)
    # The user says "about 6% of the kids are in a high-risk group."
    high_risk_count = (df['RiskScore'] >= 2).sum()
    total_kids = len(df)
    high_risk_pct = (high_risk_count / total_kids) * 100
    print(f"High-Risk Group Percentage (Score >= 2): {high_risk_pct:.2f}%")
    
    # 3. Average visits for high-risk vs low-risk
    # The user says "students labeled as high-risk are actually the ones who show up the most often."
    avg_visits_high = df[df['RiskScore'] >= 2]['TotalVisits'].mean()
    avg_visits_low = df[df['RiskScore'] < 2]['TotalVisits'].mean()
    print(f"Avg Visits (High Risk Score >= 2): {avg_visits_high:.2f}")
    print(f"Avg Visits (Low Risk Score < 2): {avg_visits_low:.2f}")
    
    # 4. Average visits for economically disadvantaged vs others
    # The user says "5.7 visits on average compared to 1.7"
    if 'HouseholdEconomicStatus' in df.columns:
        avg_econ = df[df['HouseholdEconomicStatus'] == 'Economically Disadvantaged']['TotalVisits'].mean()
        avg_other = df[df['HouseholdEconomicStatus'] != 'Economically Disadvantaged']['TotalVisits'].mean()
        print(f"Avg Visits (Economically Disadvantaged): {avg_econ:.2f}")
        print(f"Avg Visits (Others): {avg_other:.2f}")
    
    # 5. Seasonality/Club breakdown
    # (Just a peek at the clubs)
    if 'OrganizationName' in df.columns:
        print("\nClub Counts:")
        print(df['OrganizationName'].value_counts())

if __name__ == "__main__":
    verify_stats()
