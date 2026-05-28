import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
import os

# Paths
PROCESSED_DATA_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/processed_engagement_data.csv'
WEEKLY_DATA_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/weekly_attendance.csv'
CLUB_MONTHLY_PATH = '/Users/aditya/Documents/Biokind-Analytics/code/monthly_club_attendance.csv'
VISUALIZATION_DIR = '/Users/aditya/Documents/Biokind-Analytics/visualization/'

# BGCDC-inspired Professional Palette
PALETTE = ["#E63946", "#457B9D", "#1D3557", "#A8DADC", "#F4A261", "#2A9D8F"]
sns.set_theme(style="white", palette=sns.color_palette(PALETTE))

def create_slide(filename, title_short, title_long, caption, plot_func, data):
    """
    Creates a slide-like visualization with a large title on the left, 
    the plot on the right, and an interpretive caption at the bottom.
    """
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    
    # Title Section (Left)
    fig.text(0.05, 0.88, title_short, fontsize=50, fontweight='bold', color='#1D3557', ha='left')
    fig.text(0.05, 0.78, title_long, fontsize=35, fontweight='light', color='#457B9D', ha='left')
    
    # Plot Section
    ax = fig.add_axes([0.1, 0.25, 0.8, 0.45])
    plot_func(ax, data)
    
    # Remove top/right spines for cleanliness
    sns.despine(ax=ax)

    # Caption Section (Bottom)
    wrapper = textwrap.TextWrapper(width=110)
    wrapped_caption = wrapper.fill(text=caption)
    fig.text(0.05, 0.08, wrapped_caption, fontsize=20, fontweight='light', color='#333333', linespacing=1.6, ha='left')

    plt.savefig(os.path.join(VISUALIZATION_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Slide: {filename}")

def plot_monthly_club(ax, data):
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    data = data.copy()
    data['MonthName'] = data['Month'].map(month_map)
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_df = data.pivot(index='MonthName', columns='OrganizationName', values='VisitCount').reindex(months_order)
    top_clubs = data.groupby('OrganizationName')['VisitCount'].sum().nlargest(3).index
    pivot_df[top_clubs].plot(kind='line', marker='o', linewidth=3, ax=ax)
    ax.set_xlabel('Month of Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Total Monthly Visits', fontsize=14, fontweight='bold')
    ax.legend(title='Club Location', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

def plot_retention_cliff(ax, data):
    sns.barplot(data=data, x='VisitCount', y='RetentionRate', hue='VisitCount', palette='Blues_d', ax=ax, legend=False)
    ax.set_xlabel('Number of Visits', fontsize=14, fontweight='bold')
    ax.set_ylabel('% of Students Returning', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.annotate('The Retention Cliff', xy=(2, 22), xytext=(4, 50),
                arrowprops=dict(facecolor='black', shrink=0.05),
                fontsize=16, fontweight='bold', color='#E63946')
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}%', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=12, fontweight='bold')

def plot_risk_definitions(ax, data):
    sns.countplot(data=data, x='RiskScore', hue='RiskScore', palette=PALETTE[:4], ax=ax, legend=False)
    ax.set_xlabel('Risk Score (Count of Factors)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Participant Count', fontsize=14, fontweight='bold')
    risk_text = "Risk Factors (Score +1 each):\n• Income < $25,000\n• Household Size > 4\n• Attendance < 5 visits"
    ax.text(0.95, 0.95, risk_text, transform=ax.transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#1D3557'))
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height), 
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=12, fontweight='bold')

def plot_correlation_heatmap(ax, data):
    corr_cols = ['EconomicRisk', 'HouseholdRisk', 'AttendanceRisk', 'TotalVisits']
    corr_matrix = data[corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0, fmt=".2f", ax=ax, cbar=False)
    ax.set_title('Strength of Relationship (Risk Factors)', fontsize=12, style='italic', pad=10)

def plot_equity_gap(ax, data):
    econ_df = data[data['HouseholdEconomicStatus'].isin(['Economically Disadvantaged', 'Not Economically Disadvantaged'])].copy()
    means = econ_df.groupby('HouseholdEconomicStatus')['TotalVisits'].mean().reset_index()
    sns.barplot(data=means, x='HouseholdEconomicStatus', y='TotalVisits', hue='HouseholdEconomicStatus', 
                palette=[PALETTE[0], PALETTE[1]], ax=ax, legend=False)
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f} visits', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=16, fontweight='bold', color='#1D3557')
    ax.set_xlabel('Economic Status Group', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Visits per Child', fontsize=14, fontweight='bold')

def plot_consistency(ax, data):
    data['Date'] = pd.to_datetime(data['Date'])
    ax.plot(data['Date'], data['VisitCount'], color='#E63946', linewidth=2)
    ax.set_xlabel('Timeline (2020-2024)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Total Weekly Visits', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    # Highlight the outlier
    ax.annotate('Data Anomaly?', xy=(pd.to_datetime('2022-01-16'), 9907), xytext=(pd.to_datetime('2022-06-01'), 9000),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                fontsize=12, fontweight='bold', color='#1D3557')

def run_visuals():
    df = pd.read_csv(PROCESSED_DATA_PATH)
    club_df = pd.read_csv(CLUB_MONTHLY_PATH)
    weekly_df = pd.read_csv(WEEKLY_DATA_PATH)

    # Slide 1: Consistency (New)
    create_slide(
        'slide1_consistency.png',
        'Attendance', 'Consistency',
        "This chart visualizes weekly attendance trends over a 4-year period. Significant 'dips' correspond to seasonal shifts. By identifying these gaps, BGCDC can launch targeted retention campaigns precisely when youth are historically most likely to disengage.",
        plot_consistency, weekly_df
    )

    # Slide 2: Attendance Trends (Shifted from 1)
    create_slide(
        'slide2_attendance_trends.png',
        'Attendance', 'Trends by Club',
        "Breaking down attendance by club reveals significant seasonality, particularly in after-school care. Clear drops occur during school transitions. Starting outreach two weeks before these periods can proactively maintain engagement.",
        plot_monthly_club, club_df
    )

    # Slide 3: Retention Cliff (Shifted from 2)
    attendance_counts = df[df['TotalVisits'] > 0]['TotalVisits']
    retention_rates = []
    for i in range(1, 11): 
        reached_count = (attendance_counts >= i).sum()
        rate = (reached_count / len(attendance_counts)) * 100
        retention_rates.append({'VisitCount': i, 'RetentionRate': rate})
    ret_df = pd.DataFrame(retention_rates)
    create_slide(
        'slide3_retention_cliff.png',
        'Retention', 'The Retention Cliff',
        "Most kids return a second time, but only 22% make it to their third visit. This 'Retention Cliff' is our biggest opportunity. If a student reaches their third visit, they are significantly more likely to stay long-term.",
        plot_retention_cliff, ret_df
    )

    # Slide 4: Risk Score (Shifted from 3)
    create_slide(
        'slide4_risk_defined.png',
        'Risk Score', 'Targeting Support',
        "A 3-factor risk score (Income, Household, Attendance) identifies the 6% of students needing extra support. This data-driven approach allows BGCDC to focus scholarships and transportation on the highest-need participants first.",
        plot_risk_definitions, df
    )

    # Slide 5: Predictors of Disengagement (Shifted from 4)
    create_slide(
        'slide5_disengagement_predictors.png',
        'Predictors of', 'Disengagement',
        "Correlation analysis helps us understand 'Why' kids might leave. Factors like lower economic status and larger household sizes are moderately linked to lower visit frequencies. Understanding these predictors allows BGCDC to move from reactive follow-ups to predictive support.",
        plot_correlation_heatmap, df
    )

    # Slide 6: Equity Gap (Shifted from 5)
    create_slide(
        'slide6_equity_gap.png',
        'Equity', 'Reducing Access Gaps',
        "Kids from lower-income backgrounds use the club almost 3x more often (5.7 vs 1.7 visits). BGCDC is successfully reaching those who need it most. The future challenge is ensuring staffing and resources can support this high usage.",
        plot_equity_gap, df
    )

if __name__ == "__main__":
    run_visuals()
