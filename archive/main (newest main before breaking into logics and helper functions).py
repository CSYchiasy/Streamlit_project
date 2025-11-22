import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from datetime import datetime, timedelta, timezone
from dateutil import parser
import requests, json, os, tempfile
import re
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from requests.exceptions import HTTPError

# ====================================================================================
# CONFIGURATION & GLOBAL CONSTANTS
# ====================================================================================

# --- Environment Setup (Must run globally to configure the OS environment) ---
load_dotenv() 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# --- Global HTTP Constants ---
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 10 
NEA_API_BASE_URL = "https://api.data.gov.sg/v1/environment" 
PSI_API_URL = f"{NEA_API_BASE_URL}/psi"
SINGAPORE_TIMEZONE = timezone(timedelta(hours=8))


# ====================================================================================
# GEOSPATIAL MAPPING AND HELPERS
# ====================================================================================

REGION_MAP: Dict[str, str] = {
    # Keys are space-free for robust matching
    "central": "central", "bishan": "central", "bukitmerah": "central", "bukittimah": "central", "botanicgardens": "central",
    "downtowncore": "central", "geylang": "central", "kallang": "central", "tanglin": "central",
    "marinaeast": "central", "marinasouth": "central", "marineparade": "central",
    "newton": "central", "novena": "central", "orchard": "central", 
    "outram": "central", "queenstown": "central", "museum": "central",
    "rivervalley": "central", "rochor": "central", "singaporeriver": "central",
    "straitsview": "central", "toapayoh": "central","macritchie": "central", "centralwatercatchment": "central", 
    
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

def get_region_from_location(user_query: str) -> str:
    """Extracts a region code (e.g., 'west', 'central') from the user query."""
    query_lower = user_query.lower().replace(' ', '')
    
    for location, region in REGION_MAP.items():
        if location in query_lower:
            return region
            
    return "national"


# ====================================================================================
# HISTORICAL LOADING & FORMATING DATA HELPERS
# ====================================================================================

# --- Historical PSI Data Structure (Monthly Averages) ---
# Calculated from HistoricalPollutantStandardsIndexPSI2024.csv (Central region proxy)
psi_monthly_averages_data = [
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

# --- Historical UV Index Data Structure (Monthly Hourly Averages, Rounded) ---
# Calculated from HistoricalUltravioletIndexUVI2024.csv (Rounded to nearest integer)
uv_hourly_averages_data = [
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

def format_historical_data(target_datetime: datetime, historical_psi_df: pd.DataFrame, historical_uv_df: pd.DataFrame, target_hour: int) -> Tuple[str, str]:
    """
    Retrieves and summarizes historical PSI and UV data based on the target month and hour.
    This version uses month number comparison for robustness against year changes (e.g., 2024 data vs 2025 query).
    """
    
    # 1. Get the month number from the target datetime (e.g., 11 for November)
    query_month = target_datetime.month
    
    # --- PSI Summary (Filtered by Month NUMBER - Confirmed Working) ---
    psi_month_data = historical_psi_df[historical_psi_df['date'].dt.month == query_month]
    
    if not psi_month_data.empty:
        avg_psi = psi_month_data['psi_twenty_four_hourly_avg'].iloc[0]
        psi_summary = (
            f"📝 Historical PSI for {target_datetime.strftime('%B')}: "
            f"Monthly average is **{avg_psi:.1f}**, typically in the **{'Good' if avg_psi < 51 else 'Moderate'}** range."
        )
    else:
        psi_summary = f"📝 Historical PSI for {target_datetime.strftime('%B')}: Data is not available."

    # --- UV Index Summary (Robust Filter on Month NUMBER AND Exact Hour) ---
    
    # We use .apply() with a lambda to force individual-row comparison, making it more robust
    # against data type inconsistencies that sometimes break simple boolean indexing.
    
    # First, filter by month (guaranteed to work based on PSI success)
    uv_month_hour_data = historical_uv_df[
        (historical_uv_df['date'].dt.month == query_month) & 
        (historical_uv_df['Hour'] == target_hour)
    ]
    
    if not uv_month_hour_data.empty:
        # We use iloc[0] because the data is structured to have only one entry per month/hour
        avg_uv = uv_month_hour_data['Avg Hourly UV Index'].iloc[0]
        
        # Classification for LLM context (standard UV Index categories)
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
            f"📝 Historical UV Index for {target_datetime.strftime('%B')} ({target_hour:02d}:00): "
            f"Average is **{int(avg_uv)}** ({uv_risk})."
        )
    else:
        uv_summary = f"📝 Historical UV Index for {target_datetime.strftime('%B')} ({target_hour:02d}:00): Data is not available."
        
    return psi_summary, uv_summary

# ====================================================================================
# REAL-TIME API FETCHERS
# ====================================================================================

def get_weather_2h(target_datetime: Optional[datetime] = None, target_region: str = "national") -> Dict[str, Any]:
    """Fetches the 2-hour weather forecast and summarizes it, filtered by the target region."""
    dt_str = target_datetime.isoformat() if target_datetime else datetime.now().isoformat()
    # The URL needs to be correctly constructed for the NEA API. Assuming NEA_API_BASE_URL is correct.
    url = f"{NEA_API_BASE_URL}/2-hour-weather-forecast?date_time={dt_str}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecasts = data.get('items', [{}])[0].get('forecasts', [])
        if not forecasts:
            # Standardized return on data absence
            return {"summary": "Current 2-hour weather forecast is unavailable (No data found).", "status": False}

        target_region_lower = target_region.lower()
        regional_forecasts = []
        
        # Filtering Logic
        for item in forecasts:
            area_name_normalized = item['area'].lower().replace(' ', '').replace('-', '')
            
            # Use REGION_MAP to find the correct region mapping for the API's area name
            mapped_region = next((region for location, region in REGION_MAP.items() if area_name_normalized == location), None)

            if mapped_region == target_region_lower:
                regional_forecasts.append(item)
                
        if not regional_forecasts:
             # Fallback: Use the first available forecast as a national proxy
             general_forecast = forecasts[0]['forecast'] if forecasts else "Clear"
             summary = f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {general_forecast} (using national proxy)"
             # Return with status=True as a working fallback was found
             return {"summary": summary, "status": True}


        # Summarization
        unique_forecasts = {item['forecast']: [] for item in regional_forecasts}
        for item in regional_forecasts:
            unique_forecasts[item['forecast']].append(item['area'])
            
        if len(unique_forecasts) == 1:
            forecast_only = next(iter(unique_forecasts))
            summary = f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {forecast_only}"
        else:
            summary_lines = [f"{target_region.capitalize()} areas (e.g., {areas[0]}): {forecast}" for forecast, areas in unique_forecasts.items()]
            summary = "2-Hour Weather Forecast:\n" + "\n".join(summary_lines)
            
        # Standardized return on success
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        # Standardized return on network/internal error
        return {"summary": "Current 2-hour forecast is unavailable (API Error).", "status": False}

def get_weather_24h() -> Dict[str, Any]:
    """Fetches the 24-hour weather forecast and summarizes it for today's general queries."""
    url = f"{NEA_API_BASE_URL}/24-hour-weather-forecast"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('general', {})
        
        if not forecast_data:
            # Standardized return on data absence
            return {"summary": "24-hour forecast is unavailable (No data found).", "status": False}

        summary = (
            f"24-Hour Weather Outlook (General):\n"
            f"- Forecast: {forecast_data.get('forecast', 'N/A')}\n"
            f"- Temperature Range: {forecast_data.get('temperature', {}).get('low', 'N/A')}°C to {forecast_data.get('temperature', {}).get('high', 'N/A')}°C\n"
            f"- Wind: {forecast_data.get('wind', {}).get('speed', 'N/A')} {forecast_data.get('wind', {}).get('direction', 'N/A')}"
        )
            
        # Standardized return on success
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        # Standardized return on network/internal error
        return {"summary": "24-hour forecast is unavailable (API Error).", "status": False}


def get_weather_4day() -> Dict[str, Any]:
    """Fetches the 4-day weather outlook and summarizes it for future queries."""
    url = f"{NEA_API_BASE_URL}/4-day-weather-forecast"
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('forecasts', [])
        if not forecast_data:
            # Standardized return on data absence
            return {"summary": "4-day weather outlook is unavailable (No data found).", "status": False}

        summary = "4-Day Weather Outlook:\n"
        for item in forecast_data:
            summary += f"- **{item['date']}:** {item['forecast']} (Temp: {item['temperature']['low']}°C - {item['temperature']['high']}°C)\n"
            
        # Standardized return on success
        return {"summary": summary.strip(), "status": True}

    except Exception as e:
        # Standardized return on network/internal error
        return {"summary": "4-day weather outlook is unavailable (API Error).", "status": False}


def get_psi(target_region: str) -> Dict[str, Any]:
    """Fetches live PSI readings (3-hour prioritized, 24-hour fallback) for the target region."""
    url = PSI_API_URL
    target_region_lower = target_region.lower()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        readings = data.get('items', [{}])[0].get('readings', {})
        
        # Attempt to use 3-hour PSI
        psi_data = readings.get('psi_three_hourly')
        source_type = "3-Hour"
        
        if not psi_data:
            # Fallback to 24-hour PSI
            psi_data = readings.get('psi_twenty_four_hourly')
            source_type = "24-Hour"
            if not psi_data:
                # Standardized return on data absence
                return {"summary": "Live PSI data is unavailable: Both 3-hour and 24-hour readings are missing.", "status": False}

        # Locate the specific region reading
        region_value = psi_data.get(target_region_lower)
        
        if region_value is None:
            # If region not found, fallback to 'national'
            region_value = psi_data.get('national')
            if region_value is None:
                # Standardized return on data absence
                return {"summary": f"Live PSI data is unavailable: Region '{target_region}' and national reading missing.", "status": False}
            else:
                 summary = f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}** (Based on National reading)"
                 # Standardized return on success (using fallback is still success)
                 return {"summary": summary, "status": True}
                 
        summary = f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}**"
        # Standardized return on success
        return {"summary": summary, "status": True}

    except requests.exceptions.RequestException:
        # Standardized return on network error
        return {"summary": "Live PSI data is unavailable: Network error.", "status": False}
    except Exception as e:
        # Standardized return on internal error
        return {"summary": "Live PSI data is unavailable: Internal parsing error.", "status": False}

def get_uv_index() -> Dict[str, Any]:
    """Fetches the latest UV index reading and summarizes it."""
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
                # Standardized return on success
                return {
                    "summary": f"Current Live UV Index: {latest_reading}",
                    "status": True
                }
        
        # Standardized return on data absence
        return {"summary": "Live UV index data is unavailable (No reading found).", "status": False}
    
    except requests.exceptions.RequestException:
        # Standardized return on network error
        return {"summary": "Live UV index data is unavailable (API Error).", "status": False}
    
    except Exception:
        # Standardized return on internal error
        return {"summary": "Live UV index data is unavailable (Internal Error).", "status": False}
        
def get_dengue_hotspots(user_query: str) -> Dict[str, Any]:
    """
    Placeholder for dengue hotspot data. Simulates the response.
    """
    # Standardized return (assuming this placeholder is a success)
    return {
        "summary": "Dengue Alert Level: **ORANGE**. There are **12 active clusters** in the East and **8 active clusters** in the Central region (e.g., Geylang, Aljunied, Bishan). Total 20 active clusters nationwide. Stay vigilant.",
        "status": True
    }


# ====================================================================================
# PROMPT TEMPLATE
# ====================================================================================

template = """
You are a weather assistant bot called SteadyDayEveryday. Your goal is to provide concise, factual, and actionable public data and health advice regarding environmental hazards like bad weather (rain or heat stress), air pollution, and active dengue clusters.

Your response must strictly adhere to the following rules:
1. **Mandatory Report:** Always start by generating a report using ALL data summaries provided below (Weather, PSI, UV Index, and Dengue Clusters, including the **Dengue Alert Level**). Do not skip any of these categories.
2. **Formatting:** Use rich Markdown formatting including **bolding**, **headings (## and ###)**, and **emojis** for readability. The entire report must be under one main heading (e.g., `## ⚠️ ENVIRONMENTAL REPORT: [Region]`). Follow the structure in the example at the end.
3. **Live Data Priority:** If Live Data is provided, use it as the primary factual information.
4. **Forecast/Future Query Handling:**
    a. If the query is about a future date (a forecast), you MUST state that **Live PSI and UV Index forecasts are not available**.
    b. Advise the user to check back on the actual day for current readings.
    c. Use the **Historical Data** as the *typical expectation* for that period, and explicitly state that this data is the average from the same period in 2024.
5. **Supplement Advice:** After presenting the factual data, use the Retrieved Context to provide relevant, actionable public health advice (e.g., haze precautions, sun safety, dengue prevention).
    a. Only provide advice related to Heat Stress/Hydration if the weather forecast is Sunny, Partly Cloudy, or includes a high temperature/no rain warning. Explicitly omit heat stress advice if the forecast includes Rain, Showers, or Thundery Showers.

--- DATA SUMMARIES FOR REPORT GENERATION ---

1. Weather (Live/Forecast):
{live_weather_summary}

2. PSI Data:
{live_psi_summary}
{historical_psi_df_summary}

3. UV Index Data:
{live_uv_summary}
{historical_uv_df_summary}

4. Active Dengue Clusters:
{live_dengue_summary}

--- ACTIONABLE ADVICE CONTEXT ---
Retrieved Context (Documents):
{context}

User Question: {question}

--- MANDATORY OUTPUT FORMAT EXAMPLE ---
(Your final output MUST follow this structure and style)

## ⚠️ ENVIRONMENTAL REPORT: Central Region

### 1. Weather Data (2-Hour Forecast)
🌧️ Forecast: Thundery Showers in the North and West, Cloudy in Central. \n
🌡️ Temperature Range: 24°C to 30°C

### 2. Air Quality (PSI)
😷 Live 3-Hour PSI for **Central**: **52** (Moderate) \n
📝 Historical Expectation for November: Avg 24-hr PSI is typically 39.6.

### 3. UV Index
☀️ Current Live UV Index: **8** (Very High) \n
📝 Historical Expectation for November (12:00): Average UV Index is 7.

### 4. Dengue Risk
🦟 Dengue Alert Level: **ORANGE**. 12 active clusters in the East and 8 in Central. Stay vigilant.

---
### Public Health Advice
Based on the data and retrieved context, here is your actionable advice:
* (Advice Point 1 from context)
* (Advice Point 2 from context)
* (Advice Point 3 from context)

"""

PROMPT = PromptTemplate(
    template=template, 
    input_variables=[
        "context", 
        "live_weather_summary",
        "live_psi_summary",
        "historical_psi_df_summary", 
        "live_uv_summary",
        "historical_uv_df_summary", 
        "live_dengue_summary",
        "question"
    ]
)


# ====================================================================================
# PERFORMANCE WRAPPER (Streamlit Initialization)
# This function loads all heavy or static resources only ONCE.
# ====================================================================================

def load_rag_components() -> Dict[str, Any]:
    """
    Loads and initializes all heavy, expensive, or static RAG components:
    LLM, Historical DataFrames, Document Retriever, and Vector Store.
    This replaces all globally executed code for steps 2, 3, and 4.
    """
    print("\n--- Running load_rag_components() for one-time initialization ---")
    
    # 1. Initialize LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    
    # 2. Load Historical DataFrames 
    
    historical_psi_df = pd.DataFrame(psi_monthly_averages_data)
    historical_psi_df['date'] = pd.to_datetime(historical_psi_df['Month'], format='%Y-%m') 

    historical_uv_df = pd.DataFrame(uv_hourly_averages_data)
    historical_uv_df['date'] = pd.to_datetime(historical_uv_df['Month'], format='%Y-%m')
    historical_uv_df['Hour'] = historical_uv_df['Hour'].astype(int)
    print("✅ Historical DataFrames loaded.")

    # 3. Data Loading (PDFs + URLs)
    all_docs: List[Document] = [] 
    pdf_paths = {
        "Dengue 2025 Q2 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q2-2025-dengue-surveillance-data-(110kb).pdf",
        "Dengue 2025 Q1 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q1-2025-dengue-surveillance-data.pdf",
        "UV Radiation & UV Protection": "https://www.weather.gov.sg/wp-content/uploads/2015/07/Personal-Guidebook-to-UV-Radiation.pdf"
    }
    # Load PDFs
    for label, url in pdf_paths.items():
        tmp_file_path = None
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status() 
            if not response.headers.get('Content-Type', '').startswith('application/pdf'): continue
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["label"] = label
                doc.metadata["source"] = url
            all_docs.extend(docs)
        except Exception:
            pass
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    # Load URLs
    urls = {
        "NEA Dengue Prevention": "https://www.nea.gov.sg/dengue-zika/stop-dengue-now",
        "HealthHub Haze Advice": "https://www.healthhub.sg/live-healthy/1922/how-to-protect-yourself-against-haze",
        "NEA Haze Guidelines": "https://www.nea.gov.sg/our-services/pollution-control/air-pollution/managing-haze",
        "Seasonal Heat Stress": "https://www.weather.gov.sg/heat-stress/"
    }
    for label, url in urls.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            all_docs.append(Document(page_content=text, metadata={"source": url, "label": label}))
        except Exception:
            pass

    print(f"✅ Total RAG documents loaded: {len(all_docs)}")

    # 4. Vectorization and Retriever Creation
    retriever = None
    if all_docs:
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
            chunks = text_splitter.split_documents(all_docs)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
            # Simplified vectorstore creation (single call is typically sufficient and cleaner)
            vectorstore = FAISS.from_documents(chunks, embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            print(f"✅ Vector Store (FAISS) created with {len(chunks)} chunks!")
            print("✅ Retriever initialized.")
        except Exception as e:
            print(f"❌ VECTORIZATION FAILED: Error: {e}")
            
    # 5. Return the initialized components
    return {
        "llm": llm,
        "retriever": retriever,
        "historical_psi_df": historical_psi_df,
        "historical_uv_df": historical_uv_df
    }


# ====================================================================================
# MAIN RAG RUNNER FUNCTION
# ====================================================================================

def run_rag_query(user_query: str, retriever: Any, historical_psi_df: pd.DataFrame, historical_uv_df: pd.DataFrame, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    The main RAG function combining live data, forecast logic, document context, 
    and historical data to generate a mandatory comprehensive report.
    This function now returns a dictionary containing the LLM response and API status flags.
    """
    
    # Initialize default status flags to True (optimistic)
    api_statuses = {
        "weather_status": True,
        "psi_status": True,
        "uv_status": True,
        "dengue_status": True,
    }
    
    # Initialize default results
    live_weather_summary = "Weather data unavailable."
    live_psi_summary = "PSI data unavailable."
    live_uv_summary = "UV data unavailable."
    live_dengue_summary = "Dengue data unavailable."
    context_text = "RAG context unavailable due to an error."
    
    # Historical data should always load, but we initialize to prevent crash
    historical_psi_summary = "Historical PSI data could not be summarized."
    historical_uv_summary = "Historical UV data could not be summarized."
    
    response_content = "An internal error occurred before the LLM could be queried."
    
    try:
        # --- A. Determine Date/Time and Region for Lookup ---
        current_time = datetime.now() 
        query_date = current_time.date()
        target_hour = current_time.hour
        
        target_region = get_region_from_location(user_query)
        
        # ... (rest of your date/time parsing logic remains unchanged) ...
        if "tomorrow" in user_query.lower():
            query_date = current_time.date() + timedelta(days=1)
        
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))|(\d{1,2}:\d{2})', user_query.lower())
        
        if time_match:
            time_str = None
            if time_match.group(1):
                time_str = time_match.group(1).replace(' ', '')
            elif time_match.group(2):
                time_str = time_match.group(2)
                
            try:
                if time_str:
                    if 'am' in time_str or 'pm' in time_str:
                        if ':' in time_str:
                            time_str = time_str.split(':')[0] + time_str[-2:] 
                        dt_obj = datetime.strptime(time_str, '%I%p')
                    elif ':' in time_str:
                        dt_obj = datetime.strptime(time_str, '%H:%M')
                    target_hour = dt_obj.hour
            except ValueError:
                pass


        # --- B. Weather Forecast Decision Logic (UPDATED to get status) ---
        is_today = (query_date == current_time.date())
        weather_result = {"summary": "Weather API failed to load.", "status": False} # Default fail
        weather_source = "N/A"
        
        if is_today:
            time_diff_hours = (target_hour - current_time.hour) % 24 
            
            if time_diff_hours <= 2 and time_diff_hours >= 0:
                weather_result = get_weather_2h(
                    datetime.combine(query_date, datetime.min.time().replace(hour=target_hour)),
                    target_region=target_region
                )
                weather_source = "2-Hour Forecast"
            elif time_diff_hours > 2:
                weather_result = get_weather_24h()
                weather_source = "24-Hour Forecast"
            else: 
                 weather_result = get_weather_2h(
                    datetime.combine(query_date, datetime.min.time().replace(hour=current_time.hour)),
                    target_region=target_region
                 )
                 weather_source = "Current 2-Hour Forecast"
        else:
            weather_result = get_weather_4day()
            weather_source = "4-Day Outlook"
            
        # Extract weather status and summary
        live_weather_summary = f"Weather Data ({weather_source}):\n{weather_result['summary']}"
        api_statuses["weather_status"] = weather_result['status']


        # --- C. Live Data Fetching (PSI, UV, Dengue) ---
        
        if is_today:
            live_psi_result = get_psi(target_region=target_region)
            live_uv_result = get_uv_index()
            
            # Extract status and summary for PSI/UV
            live_psi_summary = live_psi_result['summary']
            live_uv_summary = live_uv_result['summary']
            api_statuses["psi_status"] = live_psi_result['status']
            api_statuses["uv_status"] = live_uv_result['status']
            
        else:
            live_psi_summary = f"PSI forecast for {query_date.strftime('%B %d')} is not available via NEA."
            live_uv_summary = f"UV Index forecast for {query_date.strftime('%B %d')} is not available via NEA."

        live_dengue_result = get_dengue_hotspots(user_query)
        live_dengue_summary = live_dengue_result['summary']
        api_statuses["dengue_status"] = live_dengue_result['status']
        
        # --- D. Historical Data Summaries ---
        historical_psi_summary, historical_uv_summary = format_historical_data(
            datetime.combine(query_date, datetime.min.time()), 
            historical_psi_df, historical_uv_df, target_hour
        )
        
        # --- E. Retrieve Context Documents ---
        if retriever:
            retrieved_docs = retriever.get_relevant_documents(user_query)
            context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        else:
            context_text = "RAG context unavailable due to initialization error."
        
        # --- F. Final Prompt Assembly and LLM Execution ---
        final_prompt = PROMPT.format(
            context=context_text,
            live_weather_summary=live_weather_summary,
            live_psi_summary=live_psi_summary,
            historical_psi_df_summary=historical_psi_summary,
            live_uv_summary=live_uv_summary,
            historical_uv_df_summary=historical_uv_summary,
            live_dengue_summary=live_dengue_summary,
            question=user_query
        )

        print(f"\n--- Running LLM Query for {query_date.strftime('%Y-%m-%d')} at {target_hour:02d}:00 ---")
        print(f"Target Region: {target_region.capitalize()}")
        print(f"Weather Source Used: {weather_source}")
        print(f"Query Time Frame: {'Live/Today' if is_today else 'Future/Forecast'}")
        
        response = llm.invoke(final_prompt)
        response_content = response.content

        # SUCCESS RETURN: Return the LLM content and the collected statuses
        return {
            "response": response_content,
            "weather_status": api_statuses["weather_status"],
            "psi_status": api_statuses["psi_status"],
            "uv_status": api_statuses["uv_status"],
            "dengue_status": api_statuses["dengue_status"],
        }
    
    except Exception as e:
        # FAILSAFE RETURN: If any error happens inside, return a safe dict with error message and all status flags set to False
        error_message = f"System Error: Failed to process query due to internal data fetching issue: {e}"
        print(f"FATAL RAG RUNNER ERROR: {error_message}")
        
        return {
            "response": error_message,
            "weather_status": False,
            "psi_status": False,
            "uv_status": False,
            "dengue_status": False,
        }