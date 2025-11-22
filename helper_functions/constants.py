"""
Configuration and constants for the environmental bot.
Contains API URLs, region mappings, and historical data.
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ====================================================================================
# ENVIRONMENT SETUP
# ====================================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ====================================================================================
# API CONFIGURATION
# ====================================================================================

HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 10
NEA_API_BASE_URL = "https://api.data.gov.sg/v1/environment"
PSI_API_URL = f"{NEA_API_BASE_URL}/psi"
SINGAPORE_TIMEZONE = timezone(timedelta(hours=8))

# ====================================================================================
# REGION MAPPING (Singapore Areas to Regions)
# ====================================================================================

REGION_MAP = {
    # Keys are space-free for robust matching
    "central": "central", "bishan": "central", "bukitmerah": "central", "bukittimah": "central", 
    "botanicgardens": "central", "downtowncore": "central", "geylang": "central", "kallang": "central", 
    "tanglin": "central", "marinaeast": "central", "marinasouth": "central", "marineparade": "central",
    "newton": "central", "novena": "central", "orchard": "central", "outram": "central", 
    "queenstown": "central", "museum": "central", "rivervalley": "central", "rochor": "central", 
    "singaporeriver": "central", "straitsview": "central", "toapayoh": "central", "macritchie": "central", 
    "centralwatercatchment": "central",
    
    "east": "east", "bedok": "east", "changi": "east", "changibay": "east", "hougang": "east",
    "northeasternislands": "east", "pasirris": "east", "payalebar": "east",
    "punggol": "east", "sengkang": "east", "serangoon": "east",
    "tampines": "east", "northeast": "east",
    
    "north": "north", "angmokio": "north", "limchukang": "north",
    "mandai": "north", "seletar": "north", "sembawang": "north",
    "simpang": "north", "sungeikadut": "north", "woodlands": "north",
    
    "south": "south", "southernislands": "south", "harbourfront": "south", "telokblangah": "south",
    
    "west": "west", "boonlay": "west", "bukitbatok": "west", "bukitpanjang": "west",
    "choachukang": "west", "clementi": "west", "jurongeast": "west",
    "jurongwest": "west", "pioneer": "west", "tengah": "west",
    "tuas": "west", "westernwatercatchment": "west"
}

# ====================================================================================
# HISTORICAL PSI DATA (Monthly Averages for 2024)
# ====================================================================================

PSI_MONTHLY_AVERAGES_DATA = [
    {'Month': '2024-01', 'psi_twenty_four_hourly_avg': 37.076923},
    {'Month': '2024-02', 'psi_twenty_four_hourly_avg': 34.000000},
    {'Month': '2024-03', 'psi_twenty_four_hourly_avg': 36.562500},
    {'Month': '2024-04', 'psi_twenty_four_hourly_avg': 40.033333},
    {'Month': '2024-05', 'psi_twenty_four_hourly_avg': 39.533333},
    {'Month': '2024-06', 'psi_twenty_four_hourly_avg': 39.100000},
    {'Month': '2024-07', 'psi_twenty_four_hourly_avg': 39.580645},
    {'Month': '2024-08', 'psi_twenty_four_hourly_avg': 40.032258},
    {'Month': '2024-09', 'psi_twenty_four_hourly_avg': 42.100000},
    {'Month': '2024-10', 'psi_twenty_four_hourly_avg': 45.419355},
    {'Month': '2024-11', 'psi_twenty_four_hourly_avg': 39.666667},
    {'Month': '2024-12', 'psi_twenty_four_hourly_avg': 34.903226}
]

# ====================================================================================
# HISTORICAL UV INDEX DATA (Monthly Hourly Averages for 2024)
# ====================================================================================

UV_HOURLY_AVERAGES_DATA = [
    {'Month': '2024-01', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 9, 'Avg Hourly UV Index': 1},
    {'Month': '2024-01', 'Hour': 10, 'Avg Hourly UV Index': 4}, {'Month': '2024-01', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-01', 'Hour': 12, 'Avg Hourly UV Index': 7}, {'Month': '2024-01', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-01', 'Hour': 14, 'Avg Hourly UV Index': 5}, {'Month': '2024-01', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-01', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-01', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-01', 'Hour': 23, 'Avg Hourly UV Index': 0},

    {'Month': '2024-02', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-02', 'Hour': 10, 'Avg Hourly UV Index': 4}, {'Month': '2024-02', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-02', 'Hour': 12, 'Avg Hourly UV Index': 8}, {'Month': '2024-02', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-02', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-02', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-02', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-02', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-02', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-03', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-03', 'Hour': 10, 'Avg Hourly UV Index': 5}, {'Month': '2024-03', 'Hour': 11, 'Avg Hourly UV Index': 7},
    {'Month': '2024-03', 'Hour': 12, 'Avg Hourly UV Index': 8}, {'Month': '2024-03', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-03', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-03', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-03', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-03', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-03', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-04', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-04', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-04', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-04', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-04', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-04', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-04', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-04', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-04', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-04', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-04', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-05', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-05', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-05', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-05', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-05', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-05', 'Hour': 13, 'Avg Hourly UV Index': 9},
    {'Month': '2024-05', 'Hour': 14, 'Avg Hourly UV Index': 7}, {'Month': '2024-05', 'Hour': 15, 'Avg Hourly UV Index': 4},
    {'Month': '2024-05', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-05', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-05', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-06', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-06', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-06', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-06', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-06', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-06', 'Hour': 13, 'Avg Hourly UV Index': 9},
    {'Month': '2024-06', 'Hour': 14, 'Avg Hourly UV Index': 7}, {'Month': '2024-06', 'Hour': 15, 'Avg Hourly UV Index': 4},
    {'Month': '2024-06', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-06', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-06', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-07', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-07', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-07', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-07', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-07', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-07', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-07', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-07', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-07', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-07', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-07', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-08', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-08', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-08', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-08', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-08', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-08', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-08', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-08', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-08', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-08', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-08', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-09', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 8, 'Avg Hourly UV Index': 1}, {'Month': '2024-09', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-09', 'Hour': 10, 'Avg Hourly UV Index': 6}, {'Month': '2024-09', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-09', 'Hour': 12, 'Avg Hourly UV Index': 9}, {'Month': '2024-09', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-09', 'Hour': 14, 'Avg Hourly UV Index': 6}, {'Month': '2024-09', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-09', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-09', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-09', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-10', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-10', 'Hour': 10, 'Avg Hourly UV Index': 5}, {'Month': '2024-10', 'Hour': 11, 'Avg Hourly UV Index': 7},
    {'Month': '2024-10', 'Hour': 12, 'Avg Hourly UV Index': 8}, {'Month': '2024-10', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-10', 'Hour': 14, 'Avg Hourly UV Index': 5}, {'Month': '2024-10', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-10', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-10', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-10', 'Hour': 23, 'Avg Hourly UV Index': 0},
    
    {'Month': '2024-11', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-11', 'Hour': 10, 'Avg Hourly UV Index': 4}, {'Month': '2024-11', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-11', 'Hour': 12, 'Avg Hourly UV Index': 7}, {'Month': '2024-11', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-11', 'Hour': 14, 'Avg Hourly UV Index': 5}, {'Month': '2024-11', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-11', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-11', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-11', 'Hour': 23, 'Avg Hourly UV Index': 0},

    {'Month': '2024-12', 'Hour': 0, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 2, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 4, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 6, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 8, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 9, 'Avg Hourly UV Index': 1},
    {'Month': '2024-12', 'Hour': 10, 'Avg Hourly UV Index': 4}, {'Month': '2024-12', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-12', 'Hour': 12, 'Avg Hourly UV Index': 7}, {'Month': '2024-12', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-12', 'Hour': 14, 'Avg Hourly UV Index': 5}, {'Month': '2024-12', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-12', 'Hour': 16, 'Avg Hourly UV Index': 1}, {'Month': '2024-12', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 18, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 20, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 22, 'Avg Hourly UV Index': 0}, {'Month': '2024-12', 'Hour': 23, 'Avg Hourly UV Index': 0}
]

# ====================================================================================
# PDF AND URL SOURCES FOR RAG
# ====================================================================================

PDF_SOURCES = {
    "Dengue 2025 Q2 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q2-2025-dengue-surveillance-data-(110kb).pdf",
    "Dengue 2025 Q1 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q1-2025-dengue-surveillance-data.pdf",
    "UV Radiation & UV Protection": "https://www.weather.gov.sg/wp-content/uploads/2015/07/Personal-Guidebook-to-UV-Radiation.pdf"
}

URL_SOURCES = {
    "NEA Dengue Prevention": "https://www.nea.gov.sg/dengue-zika/stop-dengue-now",
    "HealthHub Haze Advice": "https://www.healthhub.sg/live-healthy/1922/how-to-protect-yourself-against-haze",
    "NEA Haze Guidelines": "https://www.nea.gov.sg/our-services/pollution-control/air-pollution/managing-haze",
    "Seasonal Heat Stress": "https://www.weather.gov.sg/heat-stress/"
}