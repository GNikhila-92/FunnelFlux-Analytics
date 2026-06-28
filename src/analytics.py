import pandas as pd

def compute_funnel_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes a sequential cohort analysis on e-commerce clickstream frames.
    Returns calculated absolute volume, absolute retention, and marginal stage drop-off.
    """
    if df.empty:
        return pd.DataFrame(columns=['Stage', 'Unique_Users', 'Conversion from Total (%)', 'Drop-off from Previous (%)'])

    # Aggregate discrete event actions per unique user session token
    funnel_data = df.groupby('stage')['user_id'].nunique().reset_index()
    funnel_data.columns = ['Stage', 'Unique_Users']
    funnel_data = funnel_data.sort_values(by='Stage').reset_index(drop=True)
    
    # Calculate baseline conversion rates relative to cohort entry point
    base_volume = funnel_data['Unique_Users'].iloc[0]
    funnel_data['Conversion from Total (%)'] = ((funnel_data['Unique_Users'] / base_volume) * 100).round(2)
    
    # Compute marginal step-wise decay percentages
    funnel_data['Previous_Stage_Users'] = funnel_data['Unique_Users'].shift(1)
    funnel_data['Drop-off from Previous (%)'] = (
        100 - (funnel_data['Unique_Users'] / funnel_data['Previous_Stage_Users'] * 100)
    ).fillna(0).round(2)
    
    return funnel_data.drop(columns=['Previous_Stage_Users'])

def identify_funnel_anomalies(df: pd.DataFrame):
    """
    Scans categorical intersections (Device x Location) to flag statistically 
    significant conversion anomalies that indicate engineering or UX bugs.
    """
    insights = []
    
    # Check if we have the fallback columns or remote dataset structure
    stage_col = 'stage' if 'stage' in df.columns else None
    
    if not stage_col or df.empty:
        return insights
        
    # Isolate segment combinations with lower conversion rates
    segment_perf = df.groupby(['device', 'location', 'stage'])['user_id'].nunique().unstack(fill_value=0)
    
    # Find matching drop-offs safely
    if '1. Visit' in segment_perf.columns and '4. Purchase' in segment_perf.columns:
        segment_perf['CR'] = segment_perf['4. Purchase'] / segment_perf['1. Visit']
        
        # Flag any operational segments converting below a 5% threshold
        underperforming = segment_perf[segment_perf['CR'] < 0.05].reset_index()
        for _, row in underperforming.head(2).iterrows():
            insights.append({
                "device": row['device'],
                "location": row['location'],
                "cr": round(row['CR'] * 100, 2)
            })
            
    return insights