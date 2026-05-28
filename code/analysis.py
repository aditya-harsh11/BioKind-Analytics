# https://docs.google.com/presentation/d/1-TcTsfK1-2tNN3NurmWQmb5zc6FTyVFshHdjTZfSLog/edit?slide=id.g3d733b0061d_0_4#slide=id.g3d733b0061d_0_4

import pandas as pd
import numpy as np
import os

# Paths
ATTENDANCE_PATH = '/Users/aditya/Documents/Biokind-Analytics/Data/Historical Attendance Data Others.xlsx'
MEMBERSHIP_PATH = '/Users/aditya/Documents/Biokind-Analytics/Data/Historical Membership Data Others.xlsx'
PROCESSED_DATA_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/processed_engagement_data.csv'
WEEKLY_DATA_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/weekly_attendance.csv'
CLUB_MONTHLY_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/monthly_club_attendance.csv'

def load_and_process():
    print("Loading datasets...")
    df_att = pd.read_excel(ATTENDANCE_PATH)
    df_mem = pd.read_excel(MEMBERSHIP_PATH)

    # --- IDEA 9: Aggregate Weekly Data ---
    print("Processing Idea 9 (Consistency Over Time)...")
    df_att['AttendanceDate'] = pd.to_datetime(df_att['AttendanceDate'], errors='coerce')
    df_att = df_att.dropna(subset=['AttendanceDate'])
    
    # Weekly aggregate
    weekly_visits = df_att.set_index('AttendanceDate').resample('W').size().reset_index()
    weekly_visits.columns = ['Date', 'VisitCount']
    weekly_visits.to_csv(WEEKLY_DATA_PATH, index=False)
    print(f"Saved weekly trends to {WEEKLY_DATA_PATH}")

    # --- NEW: Monthly Club Breakdown ---
    print("Processing Monthly Club Trends...")
    df_att['Month'] = df_att['AttendanceDate'].dt.month
    df_att['Year'] = df_att['AttendanceDate'].dt.year
    
    # Filter to last 4 years (2020-2024 as per user script)
    df_recent = df_att[df_att['Year'] >= 2020]
    
    # Group by Club and Month
    club_monthly = df_recent.groupby(['OrganizationName', 'Month']).size().reset_index(name='VisitCount')
    club_monthly.to_csv(CLUB_MONTHLY_PATH, index=False)
    print(f"Saved monthly club trends to {CLUB_MONTHLY_PATH}")

    # --- IDEA 11: Calculate Risk Metrics ---
    print("Processing Idea 11 (High-Risk Identification)...")
    
    # Calculate attendance frequency per participant
    att_freq = df_att.groupby('ParticipantNumber').size().reset_index(name='TotalVisits')
    
    # First visit date for cohort analysis
    first_visits = df_att.groupby('ParticipantNumber')['AttendanceDate'].min().reset_index(name='FirstVisitDate')
    
    # Merge with Membership
    df_merged = pd.merge(df_mem, att_freq, on='ParticipantNumber', how='left')
    df_merged = pd.merge(df_merged, first_visits, on='ParticipantNumber', how='left')
    df_merged['TotalVisits'] = df_merged['TotalVisits'].fillna(0)

    # Risk Scoring Logic
    # 1. Economic Risk
    df_merged['EconomicRisk'] = (
        (df_merged['HouseholdEconomicStatus'] == 'Economically Disadvantaged') | 
        (df_merged['IncomeCategory'] == '$24,999 and under')
    ).astype(int)
    
    # 2. Household Risk
    df_merged['HouseholdRisk'] = (df_merged['TotalInHousehold'] > 4).astype(int)
    
    # 3. Attendance Risk
    # We'll define "Low Attendance" as < 5 visits
    df_merged['AttendanceRisk'] = ((df_merged['TotalVisits'] > 0) & (df_merged['TotalVisits'] < 5)).astype(int)
    
    # Total Risk Score
    df_merged['RiskScore'] = df_merged['EconomicRisk'] + df_merged['HouseholdRisk'] + df_merged['AttendanceRisk']
    
    df_merged.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Saved processed engagement data to {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    load_and_process()
