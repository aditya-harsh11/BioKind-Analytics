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
    
    # 2. Average visits for economically disadvantaged vs others
    # The user says "5.7 visits on average compared to 1.7"
    if 'HouseholdEconomicStatus' in df.columns:
        avg_econ = df[df['HouseholdEconomicStatus'] == 'Economically Disadvantaged']['TotalVisits'].mean()
        avg_other = df[df['HouseholdEconomicStatus'] != 'Economically Disadvantaged']['TotalVisits'].mean()
        print(f"Avg Visits (Economically Disadvantaged): {avg_econ:.2f}")
        print(f"Avg Visits (Others): {avg_other:.2f}")
    
    # 3. Seasonality/Club breakdown
    # (Just a peek at the clubs)
    if 'OrganizationName' in df.columns:
        print("\nClub Counts:")
        print(df['OrganizationName'].value_counts())

if __name__ == "__main__":
    verify_stats()
