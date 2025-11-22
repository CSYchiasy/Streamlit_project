"""
Data formatting and helper functions for the environmental bot.
Handles region extraction, data summarization, and formatting.
"""

from datetime import datetime
from typing import Tuple
import pandas as pd
from .constants import REGION_MAP


def get_region_from_location(user_query: str) -> str:
    """
    Extracts a region code (e.g., 'west', 'central') from the user query.
    
    Args:
        user_query (str): User's input query
        
    Returns:
        str: Region code ('central', 'east', 'north', 'south', 'west', or 'national')
    """
    query_lower = user_query.lower().replace(' ', '')
    
    for location, region in REGION_MAP.items():
        if location in query_lower:
            return region
            
    return "national"


def format_historical_data(
    target_datetime: datetime,
    historical_psi_df: pd.DataFrame,
    historical_uv_df: pd.DataFrame,
    target_hour: int
) -> Tuple[str, str]:
    """
    Retrieves and summarizes historical PSI and UV data based on the target month and hour.
    Uses month number comparison for robustness against year changes.
    
    Args:
        target_datetime (datetime): Target date to look up
        historical_psi_df (pd.DataFrame): Historical PSI data
        historical_uv_df (pd.DataFrame): Historical UV data
        target_hour (int): Target hour (0-23)
        
    Returns:
        Tuple[str, str]: (psi_summary, uv_summary)
    """
    
    # Get the month number from the target datetime (e.g., 11 for November)
    query_month = target_datetime.month
    
    # --- PSI Summary (Filtered by Month NUMBER) ---
    psi_month_data = historical_psi_df[historical_psi_df['date'].dt.month == query_month]
    
    if not psi_month_data.empty:
        avg_psi = psi_month_data['psi_twenty_four_hourly_avg'].iloc[0]
        psi_category = 'Good' if avg_psi < 51 else 'Moderate'
        psi_summary = (
            f"📊 Historical PSI for {target_datetime.strftime('%B')}: "
            f"Monthly average is **{avg_psi:.1f}**, typically in the **{psi_category}** range."
        )
    else:
        psi_summary = f"📊 Historical PSI for {target_datetime.strftime('%B')}: Data is not available."

    # --- UV Index Summary (Filter on Month NUMBER AND Exact Hour) ---
    uv_month_hour_data = historical_uv_df[
        (historical_uv_df['date'].dt.month == query_month) & 
        (historical_uv_df['Hour'] == target_hour)
    ]
    
    if not uv_month_hour_data.empty:
        avg_uv = uv_month_hour_data['Avg Hourly UV Index'].iloc[0]
        
        # Classify UV Index risk level
        if avg_uv < 3:
            uv_risk = "Low"
        elif avg_uv < 6:
            uv_risk = "Moderate"
        elif avg_uv < 8:
            uv_risk = "High"
        elif avg_uv < 11:
            uv_risk = "Very High"
        else:
            uv_risk = "Extreme"

        uv_summary = (
            f"☀️ Historical UV Index for {target_datetime.strftime('%B')} ({target_hour:02d}:00): "
            f"Average is **{int(avg_uv)}** ({uv_risk})."
        )
    else:
        uv_summary = (
            f"☀️ Historical UV Index for {target_datetime.strftime('%B')} ({target_hour:02d}:00): "
            f"Data is not available."
        )
        
    return psi_summary, uv_summary