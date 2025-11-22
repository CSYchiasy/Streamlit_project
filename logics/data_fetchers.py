"""
API data fetchers for environmental data (weather, PSI, UV, dengue).
Handles all external API calls and returns standardized responses.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import requests
from helper_functions.constants import (
    HEADERS, REQUEST_TIMEOUT, NEA_API_BASE_URL, PSI_API_URL, REGION_MAP
)


def get_weather_2h(
    target_datetime: Optional[datetime] = None,
    target_region: str = "national"
) -> Dict[str, Any]:
    """
    Fetches the 2-hour weather forecast and summarizes it, filtered by the target region.
    
    Args:
        target_datetime (datetime, optional): Target datetime for forecast
        target_region (str): Target region (e.g., 'central', 'east', 'west')
        
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    dt_str = target_datetime.isoformat() if target_datetime else datetime.now().isoformat()
    url = f"{NEA_API_BASE_URL}/2-hour-weather-forecast?date_time={dt_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecasts = data.get('items', [{}])[0].get('forecasts', [])
        if not forecasts:
            return {"summary": "Current 2-hour weather forecast is unavailable (No data found).", "status": False}

        target_region_lower = target_region.lower()
        regional_forecasts = []
        
        # Filter by target region
        for item in forecasts:
            area_name_normalized = item['area'].lower().replace(' ', '').replace('-', '')
            mapped_region = next(
                (region for location, region in REGION_MAP.items() if area_name_normalized == location),
                None
            )
            if mapped_region == target_region_lower:
                regional_forecasts.append(item)
                
        if not regional_forecasts:
            # Fallback to national proxy
            general_forecast = forecasts[0]['forecast'] if forecasts else "Clear"
            summary = f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {general_forecast} (using national proxy)"
            return {"summary": summary, "status": True}

        # Summarize forecasts
        unique_forecasts = {item['forecast']: [] for item in regional_forecasts}
        for item in regional_forecasts:
            unique_forecasts[item['forecast']].append(item['area'])
            
        if len(unique_forecasts) == 1:
            forecast_only = next(iter(unique_forecasts))
            summary = f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {forecast_only}"
        else:
            summary_lines = [
                f"{target_region.capitalize()} areas (e.g., {areas[0]}): {forecast}"
                for forecast, areas in unique_forecasts.items()
            ]
            summary = "2-Hour Weather Forecast:\n" + "\n".join(summary_lines)
            
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        return {"summary": "Current 2-hour forecast is unavailable (API Error).", "status": False}


def get_weather_24h() -> Dict[str, Any]:
    """
    Fetches the 24-hour weather forecast and summarizes it.
    
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    url = f"{NEA_API_BASE_URL}/24-hour-weather-forecast"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('general', {})
        
        if not forecast_data:
            return {"summary": "24-hour forecast is unavailable (No data found).", "status": False}

        summary = (
            f"24-Hour Weather Outlook (General):\n"
            f"- Forecast: {forecast_data.get('forecast', 'N/A')}\n"
            f"- Temperature Range: {forecast_data.get('temperature', {}).get('low', 'N/A')}°C to "
            f"{forecast_data.get('temperature', {}).get('high', 'N/A')}°C\n"
            f"- Wind: {forecast_data.get('wind', {}).get('speed', 'N/A')} "
            f"{forecast_data.get('wind', {}).get('direction', 'N/A')}"
        )
            
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        return {"summary": "24-hour forecast is unavailable (API Error).", "status": False}


def get_weather_4day() -> Dict[str, Any]:
    """
    Fetches the 4-day weather outlook.
    
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    url = f"{NEA_API_BASE_URL}/4-day-weather-forecast"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('forecasts', [])
        if not forecast_data:
            return {"summary": "4-day weather outlook is unavailable (No data found).", "status": False}

        summary = "4-Day Weather Outlook:\n"
        for item in forecast_data:
            summary += (
                f"- **{item['date']}:** {item['forecast']} "
                f"(Temp: {item['temperature']['low']}°C - {item['temperature']['high']}°C)\n"
            )
            
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        return {"summary": "4-day weather outlook is unavailable (API Error).", "status": False}


def get_psi(target_region: str) -> Dict[str, Any]:
    """
    Fetches live PSI readings (3-hour prioritized, 24-hour fallback) for the target region.
    
    Args:
        target_region (str): Target region
        
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    url = PSI_API_URL
    target_region_lower = target_region.lower()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        readings = data.get('items', [{}])[0].get('readings', {})
        
        # Try 3-hour PSI first
        psi_data = readings.get('psi_three_hourly')
        source_type = "3-Hour"
        
        if not psi_data:
            # Fallback to 24-hour PSI
            psi_data = readings.get('psi_twenty_four_hourly')
            source_type = "24-Hour"
            if not psi_data:
                return {
                    "summary": "Live PSI data is unavailable: Both 3-hour and 24-hour readings are missing.",
                    "status": False
                }

        # Get region value
        region_value = psi_data.get(target_region_lower)
        
        if region_value is None:
            # Fallback to national
            region_value = psi_data.get('national')
            if region_value is None:
                return {
                    "summary": f"Live PSI data is unavailable: Region '{target_region}' and national reading missing.",
                    "status": False
                }
            else:
                summary = (
                    f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}** "
                    f"(Based on National reading)"
                )
                return {"summary": summary, "status": True}
                 
        summary = f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}**"
        return {"summary": summary, "status": True}

    except requests.exceptions.RequestException:
        return {"summary": "Live PSI data is unavailable: Network error.", "status": False}
    except Exception as e:
        return {"summary": "Live PSI data is unavailable: Internal parsing error.", "status": False}


def get_uv_index() -> Dict[str, Any]:
    """
    Fetches the latest UV index reading.
    
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    url = f"{NEA_API_BASE_URL}/uv-index"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        
        if items and items[0].get('index'):
            readings_list = items[0]['index']
            latest_reading_data = readings_list[0]
            latest_reading = latest_reading_data.get('value')
            
            if latest_reading is not None:
                return {
                    "summary": f"Current Live UV Index: {latest_reading}",
                    "status": True
                }
        
        return {"summary": "Live UV index data is unavailable (No reading found).", "status": False}
    
    except requests.exceptions.RequestException:
        return {"summary": "Live UV index data is unavailable (API Error).", "status": False}
    
    except Exception:
        return {"summary": "Live UV index data is unavailable (Internal Error).", "status": False}


def get_dengue_hotspots(user_query: str) -> Dict[str, Any]:
    """
    Fetches dengue hotspot data.
    Currently a placeholder - can be connected to real API later.
    
    Args:
        user_query (str): User's query
        
    Returns:
        Dict with 'summary' (str) and 'status' (bool)
    """
    return {
        "summary": (
            "Dengue Alert Level: **ORANGE**. There are **12 active clusters** in the East and "
            "**8 active clusters** in the Central region (e.g., Geylang, Aljunied, Bishan). "
            "Total 20 active clusters nationwide. Stay vigilant."
        ),
        "status": True
    }