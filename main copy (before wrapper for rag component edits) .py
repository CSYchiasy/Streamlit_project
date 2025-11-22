# ====================================================================================
# STEP 1: Dependencies, Imports, and Initialization
# ====================================================================================

import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_openai.embeddings import OpenAIEmbeddings
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from datetime import datetime, timedelta, timezone
from dateutil import parser
import requests, json, os, tempfile
from tqdm import tqdm
from shapely.geometry import Point, shape # Used for geospatial checks
from geopy.geocoders import Nominatim # Used for geocoding location names
import re
import pandas as pd
from typing import Optional, Dict, Any
from requests.exceptions import HTTPError


# --- Load Environment Variables ---
load_dotenv() 

# --- Set OpenAI API Key ---
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# ====================================================================================
# STEP 2: Load Historical Data for PSI and UV Index (Separate DataFrames)
# ====================================================================================

# --- 2A. Historical PSI Data Structure (Monthly Averages) ---
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

# --- 2B. Historical UV Index Data Structure (Monthly Hourly Averages, Rounded) ---
# Calculated from HistoricalUltravioletIndexUVI2024.csv (Rounded to nearest integer)
uv_hourly_averages_data = [
    {'Month': '2024-01', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 9, 'Avg Hourly UV Index': 1},
    {'Month': '2024-01', 'Hour': 10, 'Avg Hourly UV Index': 4},
    {'Month': '2024-01', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-01', 'Hour': 12, 'Avg Hourly UV Index': 7},
    {'Month': '2024-01', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-01', 'Hour': 14, 'Avg Hourly UV Index': 5},
    {'Month': '2024-01', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-01', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-01', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-01', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-02', 'Hour': 10, 'Avg Hourly UV Index': 4},
    {'Month': '2024-02', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-02', 'Hour': 12, 'Avg Hourly UV Index': 8},
    {'Month': '2024-02', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-02', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-02', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-02', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-02', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-02', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-03', 'Hour': 10, 'Avg Hourly UV Index': 5},
    {'Month': '2024-03', 'Hour': 11, 'Avg Hourly UV Index': 7},
    {'Month': '2024-03', 'Hour': 12, 'Avg Hourly UV Index': 8},
    {'Month': '2024-03', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-03', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-03', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-03', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-03', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-03', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-04', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-04', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-04', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-04', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-04', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-04', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-04', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-04', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-04', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-04', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-05', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-05', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-05', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-05', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-05', 'Hour': 13, 'Avg Hourly UV Index': 9},
    {'Month': '2024-05', 'Hour': 14, 'Avg Hourly UV Index': 7},
    {'Month': '2024-05', 'Hour': 15, 'Avg Hourly UV Index': 4},
    {'Month': '2024-05', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-05', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-05', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-06', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-06', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-06', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-06', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-06', 'Hour': 13, 'Avg Hourly UV Index': 9},
    {'Month': '2024-06', 'Hour': 14, 'Avg Hourly UV Index': 7},
    {'Month': '2024-06', 'Hour': 15, 'Avg Hourly UV Index': 4},
    {'Month': '2024-06', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-06', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-06', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-07', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-07', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-07', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-07', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-07', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-07', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-07', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-07', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-07', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-07', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-08', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-08', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-08', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-08', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-08', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-08', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-08', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-08', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-08', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-08', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 8, 'Avg Hourly UV Index': 1},
    {'Month': '2024-09', 'Hour': 9, 'Avg Hourly UV Index': 3},
    {'Month': '2024-09', 'Hour': 10, 'Avg Hourly UV Index': 6},
    {'Month': '2024-09', 'Hour': 11, 'Avg Hourly UV Index': 8},
    {'Month': '2024-09', 'Hour': 12, 'Avg Hourly UV Index': 9},
    {'Month': '2024-09', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-09', 'Hour': 14, 'Avg Hourly UV Index': 6},
    {'Month': '2024-09', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-09', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-09', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-09', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-10', 'Hour': 10, 'Avg Hourly UV Index': 5},
    {'Month': '2024-10', 'Hour': 11, 'Avg Hourly UV Index': 7},
    {'Month': '2024-10', 'Hour': 12, 'Avg Hourly UV Index': 8},
    {'Month': '2024-10', 'Hour': 13, 'Avg Hourly UV Index': 8},
    {'Month': '2024-10', 'Hour': 14, 'Avg Hourly UV Index': 5},
    {'Month': '2024-10', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-10', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-10', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-10', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 9, 'Avg Hourly UV Index': 2},
    {'Month': '2024-11', 'Hour': 10, 'Avg Hourly UV Index': 4},
    {'Month': '2024-11', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-11', 'Hour': 12, 'Avg Hourly UV Index': 7},
    {'Month': '2024-11', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-11', 'Hour': 14, 'Avg Hourly UV Index': 5},
    {'Month': '2024-11', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-11', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-11', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-11', 'Hour': 23, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 0, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 1, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 2, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 3, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 4, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 5, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 6, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 7, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 8, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 9, 'Avg Hourly UV Index': 1},
    {'Month': '2024-12', 'Hour': 10, 'Avg Hourly UV Index': 4},
    {'Month': '2024-12', 'Hour': 11, 'Avg Hourly UV Index': 6},
    {'Month': '2024-12', 'Hour': 12, 'Avg Hourly UV Index': 7},
    {'Month': '2024-12', 'Hour': 13, 'Avg Hourly UV Index': 6},
    {'Month': '2024-12', 'Hour': 14, 'Avg Hourly UV Index': 5},
    {'Month': '2024-12', 'Hour': 15, 'Avg Hourly UV Index': 3},
    {'Month': '2024-12', 'Hour': 16, 'Avg Hourly UV Index': 1},
    {'Month': '2024-12', 'Hour': 17, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 18, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 19, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 20, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 21, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 22, 'Avg Hourly UV Index': 0},
    {'Month': '2024-12', 'Hour': 23, 'Avg Hourly UV Index': 0}
]

# 2A. PSI Data Frame
historical_psi_df = pd.DataFrame(psi_monthly_averages_data)
# Convert 'Month' string to datetime object for easier date filtering later
historical_psi_df['date'] = pd.to_datetime(historical_psi_df['Month'], format='%Y-%m') 

# 2B. UV Index Data Frame
historical_uv_df = pd.DataFrame(uv_hourly_averages_data)
# Convert 'Month' string to datetime object for easier date filtering later
historical_uv_df['date'] = pd.to_datetime(historical_uv_df['Month'], format='%Y-%m')

# ====================================================================================
# STEP 3: Data Loading (PDFs + URLs)
# ====================================================================================

HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_TIMEOUT = 10 
all_docs = [] # Use this single list for all documents (PDFs + URLs)

# --- 3A. Load PDFs with context labels ---

pdf_paths = {
    "Dengue 2025 Q2 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q2-2025-dengue-surveillance-data-(110kb).pdf",
    "Dengue 2025 Q1 data": "https://www.nea.gov.sg/docs/default-source/default-document-library/q1-2025-dengue-surveillance-data.pdf",
    "UV Radiation & UV Protection": "https://www.weather.gov.sg/wp-content/uploads/2015/07/Personal-Guidebook-to-UV-Radiation.pdf"
}

pdf_docs = []
for label, url in pdf_paths.items():
    tmp_file_path = None
    try:
        # Use robust headers and timeout, and check for HTTP errors
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() 
        
        # Add a basic check for content type to help diagnose issues like the previous error
        if not response.headers.get('Content-Type', '').startswith('application/pdf'):
            print(f"⚠️ Warning: URL {url} for '{label}' did not return a PDF Content-Type. Skipping document.")
            continue
            
        # Write content to temp file with delete=False for safety before loading
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
        
        # Load and parse the PDF
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        
        # Add consistent metadata
        for doc in docs:
            doc.metadata["label"] = label
            doc.metadata["source"] = url
        pdf_docs.extend(docs)
        
        print(f"✅ Loaded PDF: {label} (Pages: {len(docs)})")
        
    except HTTPError as e:
        # Handle specific HTTP issues (404, 403, etc.)
        print(f"❌ Failed to download PDF {label} (HTTP Error: {e.response.status_code}). Skipping.")
    except Exception as e:
        # Handle PdfStreamError and other file processing issues
        print(f"❌ Failed to process PDF {label}: {e}. (This could mean content was not a valid PDF)")
    finally:
        # Clean up the temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

all_docs.extend(pdf_docs)
print(f"\n✅ Total PDF pages loaded: {len(pdf_docs)}")


# --- 3B. Load URLs with context labels ---

urls = {
    "NEA Dengue Prevention": "https://www.nea.gov.sg/dengue-zika/stop-dengue-now",
    "HealthHub Haze Advice": "https://www.healthhub.sg/live-healthy/1922/how-to-protect-yourself-against-haze",
    "NEA Haze Guidelines": "https://www.nea.gov.sg/our-services/pollution-control/air-pollution/managing-haze",
    "Seasonal Heat Stress": "https://www.weather.gov.sg/heat-stress/"
}

web_docs = []
for label, url in urls.items():
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True) # Use strip=True for cleaner text
        
        # FIX: Ensure metadata uses 'label' for consistency and fix typo in print statement
        web_docs.append(Document(page_content=text, metadata={"source": url, "label": label}))
        print(f"✅ Loaded website: {label}")
        
    except Exception as e:
        print(f"❌ Failed to load {label}: {e}")

all_docs.extend(web_docs)
print(f"\n✅ Total web documents loaded: {len(web_docs)}")

# ====================================================================================
# STEP 4: Vectorization (Chunking, Embedding, and Vector Store Creation - User's Robust Logic)
# ====================================================================================

# --- 4A. Split Documents into Chunks ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, # User's preferred chunk size
    chunk_overlap=50, # User's preferred overlap
    length_function=len,
    is_separator_regex=False,
)

print("\nStarting document chunking...")
chunks = text_splitter.split_documents(all_docs)
print(f"✅ Documents split into {len(chunks)} searchable chunks.")


# --- 4B. Embed and Store in Vector Store (FAISS) with Batching ---
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("✅ Embeddings model initialized.")
    
    batch_size = 50
    vectorstores = []
    
    print(f"Starting embedding and batching process (batch size: {batch_size})...")
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        # ⚠️ This is where the API call to OpenAI embeddings happens!
        vs = FAISS.from_documents(batch, embeddings)
        vectorstores.append(vs)

    # Merge all batch vectorstores into one
    if not vectorstores:
        raise ValueError("No documents were successfully loaded or chunked.")

    vectorstore = vectorstores[0]
    for vs in vectorstores[1:]:
        vectorstore.merge_from(vs)

    print(f"✅ Vector Store (FAISS) created and merged successfully with {len(chunks)} chunks!")
    
    # 4C. Create the Retriever 
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) 
    print("✅ Retriever initialized.")

except Exception as e:
    print(f"❌ VECTORIZATION FAILED: The Vector Store was NOT created. Please ensure your API key is active and correct. Error: {e}")


# ====================================================================================
# STEP 5A: Define the Prompt Template (The RAG Bot's Personality)
# ====================================================================================

template = """
You are a weather assistant bot called SteadyDayEveryday. Your goal is to provide concise, factual, and actionable public data and health advice regarding environmental hazards like bad weather (rain or heat stress), air pollution and active dengue clusters.

Your response must strictly adhere to the following rules:
1. **Mandatory Report:** Always start by generating a report using ALL data summaries provided below (Weather, PSI, UV Index, and Dengue Clusters, including the **Dengue Alert Level**). Do not skip any of these categories.
2. **Live Data Priority:** If Live Data is provided, use it as the primary factual information.
3. **Forecast/Future Query Handling:** 
    a. If the query is about a future date (a forecast), you MUST state that **Live PSI and UV Index forecasts are not available**.
    b. Advise the user to check back on the actual day for current readings.
    c. Use the **Historical Data** as the *typical expectation* for that period, and explicitly state that this data is the average from the same period in 2024.
4. **Supplement Advice:** After presenting the factual data, use the Retrieved Context to provide relevant, actionable public health advice (e.g., haze precautions, sun safety, dengue prevention).
    a. Only provide advice related to Heat Stress/Hydration if the weather forecast is Sunny, Partly Cloudy, or includes a high temperature/no rain warning. Explicitly omit heat stress advice if the forecast includes Rain, Showers, or Thundery Showers.
5. **Format:** Use markdown headings and lists for a clear, professional presentation.

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

print("✅ Prompt Template (Step 5A) defined")


# ====================================================================================
# STEP 5B: Historical Data Helper (Formatting)
# ====================================================================================

def format_historical_data(query_date, historical_psi_df, historical_uv_df, target_hour=None):
    """
    Filters and formats historical PSI and UV data for the LLM prompt.
    """
    # 1. Determine the proxy month (2024 equivalent of the query month)
    proxy_month = query_date.strftime("2024-%m")
    
    # 2. Filter PSI Data
    psi_data = historical_psi_df[historical_psi_df['Month'] == proxy_month]
    if not psi_data.empty:
        psi_avg = psi_data['psi_twenty_four_hourly_avg'].iloc[0]
        psi_summary = f"Average 24-hr PSI for {query_date.strftime('%B')} (Historical 2024): {psi_avg:.1f}"
    else:
        psi_summary = f"No historical PSI data found for the proxy month of {query_date.strftime('%B')}."

    # 3. Filter UV Data
    uv_data_filtered = historical_uv_df[historical_uv_df['Month'] == proxy_month]
    
    if target_hour is not None:
        uv_data_filtered_hourly = uv_data_filtered[uv_data_filtered['Hour'] == target_hour]
        
        if not uv_data_filtered_hourly.empty:
            uv_avg = uv_data_filtered_hourly['Avg Hourly UV Index'].iloc[0]
            uv_summary = f"Average UV Index at {target_hour:02d}:00 for {query_date.strftime('%B')} (Historical 2024): {uv_avg:.0f}"
        else:
            uv_summary = f"No historical UV index data found for {query_date.strftime('%B')} at {target_hour:02d}:00."
    else:
        # Fallback to daily max if no hour is specified
        if not uv_data_filtered.empty:
            uv_avg_daily_max = uv_data_filtered['Avg Hourly UV Index'].max()
            uv_summary = f"Average Daily Max UV Index for {query_date.strftime('%B')} (Historical 2024): {uv_avg_daily_max:.0f}"
        else:
             uv_summary = f"No historical UV index data found for {query_date.strftime('%B')}."

    return psi_summary, uv_summary

print("✅ Historical data formatter defined.")

# ====================================================================================
# STEP 5C: Robust Real-Time API Functions (FINAL)
# ====================================================================================

def get_weather_2h(target_datetime: Optional[datetime] = None, target_region: str = "national") -> Dict[str, Any]:
    """
    Fetches the 2-hour weather forecast and summarizes it, filtered by the target region.
    """
    # 1. API Call (Logic remains the same)
    dt_str = target_datetime.isoformat() if target_datetime else datetime.now().isoformat()
    url = f"https://api.data.gov.sg/v1/environment/2-hour-weather-forecast?date_time={dt_str}"
    a
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        forecasts = data.get('items', [{}])[0].get('forecasts', [])
        if not forecasts:
            return {"error": "No 2-hour forecast data available.", "summary": "Current 2-hour weather forecast is unavailable."}

        # 2. Filtering Logic
        target_region_lower = target_region.lower()
        regional_forecasts = []
        
        # Iterate through the API's list of forecasts
        for item in forecasts:
            # Check if the API's area name maps to the target region
            area_name_normalized = item['area'].lower().replace(' ', '').replace('-', '')
            
            # Find the region this API area belongs to, using the detailed REGION_MAP
            # NOTE: We iterate over the REGION_MAP to find the mapping.
            mapped_region = None
            for location, region in REGION_MAP.items():
                if area_name_normalized == location:
                    mapped_region = region
                    break

            if mapped_region == target_region_lower:
                regional_forecasts.append(item)
                
        # 3. Summarization
        
        if not regional_forecasts:
             # Fallback: If filtering fails, return a general summary using the first available forecast
             general_forecast = forecasts[0]['forecast'] if forecasts else "Clear"
             return {"summary": f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {general_forecast}", "error": None}


        # Group identical forecasts for conciseness (e.g., Central: Cloudy, Cloudy, Cloudy -> Central: Cloudy)
        unique_forecasts = {}
        for item in regional_forecasts:
            forecast_key = item['forecast']
            if forecast_key not in unique_forecasts:
                unique_forecasts[forecast_key] = []
            unique_forecasts[forecast_key].append(item['area'])
            
        summary_lines = []
        for forecast, areas in unique_forecasts.items():
            # Summarize the forecast concisely: e.g., "Central areas: Cloudy"
            summary_lines.append(f"{target_region.capitalize()} areas (including {areas[0]}): {forecast}")

        # Final summary structure: just state the forecast for the whole region if all are the same
        if len(unique_forecasts) == 1:
            forecast_only = next(iter(unique_forecasts))
            summary = f"2-Hour Weather Forecast for {target_region.capitalize()} Region: {forecast_only}"
        else:
            summary = "2-Hour Weather Forecast:\n" + "\n".join(summary_lines)
            
        return {"summary": summary.strip(), "error": None}

    except Exception as e:
        return {"error": f"Could not fetch 2-hour weather forecast (API Error: {e})", "summary": "Current 2-hour forecast is unavailable."}

def get_weather_24h() -> Dict[str, Any]:
    """Fetches the 24-hour weather forecast and summarizes it for today's queries."""
    url = "https://api.data.gov.sg/v1/environment/24-hour-weather-forecast"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('general', {})
        
        if not forecast_data:
            return {"error": "No 24-hour forecast data available.", "summary": "24-hour forecast is unavailable."}

        summary = (
            f"24-Hour Weather Outlook (General):\n"
            f"- Forecast: {forecast_data.get('forecast', 'N/A')}\n"
            f"- Temperature Range: {forecast_data.get('temperature', {}).get('low', 'N/A')}°C to {forecast_data.get('temperature', {}).get('high', 'N/A')}°C\n"
            f"- Wind: {forecast_data.get('wind', {}).get('speed', 'N/A')} {forecast_data.get('wind', {}).get('direction', 'N/A')}"
        )
            
        return {"summary": summary.strip(), "error": None}

    except Exception as e:
        return {"error": f"Could not fetch 24-hour forecast (API Error: {e})", "summary": "24-hour forecast is unavailable."}


def get_weather_4day() -> Dict[str, Any]:
    """Fetches the 4-day weather outlook and summarizes it for forecast queries."""
    url = "https://api.data.gov.sg/v1/environment/4-day-weather-forecast"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = data.get('items', [{}])[0].get('forecasts', [])
        if not forecast_data:
            return {"error": "No 4-day forecast data available.", "summary": "4-day weather outlook is unavailable."}

        summary = "4-Day Weather Outlook:\n"
        for item in forecast_data:
            summary += f"- **{item['date']}:** {item['forecast']} (Temp: {item['temperature']['low']}°C - {item['temperature']['high']}°C)\n"
            
        return {"summary": summary.strip(), "error": None}

    except Exception as e:
        return {"error": f"Could not fetch 4-day weather outlook (API Error: {e})", "summary": "4-day weather outlook is unavailable."}


def get_psi(target_region: str) -> Dict[str, Any]:
    """
    Fetches the live PSI readings, prioritizing 3-hour PSI, then falling back to 
    24-hour PSI, and retrieves the value for the target region.
    """
    url = PSI_API_URL
    target_region_lower = target_region.lower()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # PSI data is under 'items' -> [0] -> 'readings'
        readings = data.get('items', [{}])[0].get('readings', {})
        
        # --- 1. Attempt to use 3-hour PSI (Prioritize) ---
        psi_data = readings.get('psi_three_hourly')
        source_type = "3-Hour"
        
        if not psi_data:
            # --- 2. Fallback to 24-hour PSI ---
            psi_data = readings.get('psi_twenty_four_hourly')
            source_type = "24-Hour"
            if not psi_data:
                # Both 3-hour and 24-hour PSI are missing
                return {"summary": "Live PSI data is unavailable: Both 3-hour and 24-hour readings are missing."}

        # --- 3. Locate the specific region reading ---
        region_value = psi_data.get(target_region_lower)
        
        if region_value is None:
            # If the specific region is not found, fallback to 'national'
            region_value = psi_data.get('national')
            if region_value is None:
                return {"summary": f"Live PSI data is unavailable: Region '{target_region}' and national reading missing."}
            else:
                 # Inform the user that a fallback occurred
                 summary = f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}** (Based on National reading)"
                 return {"summary": summary, "error": None}
                 
        # --- 4. Success Summary ---
        summary = f"Live {source_type} PSI for **{target_region.capitalize()}**: **{region_value}**"
        return {"summary": summary, "error": None}

    except requests.exceptions.RequestException as e:
        return {"summary": "Live PSI data is unavailable: Network error."}
    except Exception as e:
        return {"summary": f"Live PSI data is unavailable: Internal parsing error ({type(e).__name__})."}

def get_uv_index() -> Dict[str, Any]:
    """Fetches the latest UV index reading and summarizes it using the standard V1 API."""
    
    url = "https://api.data.gov.sg/v1/environment/uv-index" 
    
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 1. Access the readings list
        # data['items'] is a list, typically with one element containing the 'index' list
        items = data.get("items", [])
        
        if items and items[0].get('index'):
            readings_list = items[0]['index']
            
            # 2. Retrieve the LATEST reading (usually the FIRST element [0] in the index list)
            latest_reading_data = readings_list[0] 
            
            latest_reading = latest_reading_data.get('value')
            timestamp = latest_reading_data.get('timestamp')
            
            if latest_reading is not None:
                return {
                    "value": latest_reading,
                    "timestamp": timestamp,
                    "summary": f"Current Live UV Index: {latest_reading}",
                    "context": "UV Index 3-5 is Moderate, 6-7 is High, 8-10 is Very High, 11+ is Extreme.",
                    "error": None
                }
        
        # Fallback if structure is missing keys or empty
        return {"error": "No recent UV index found.", "summary": "Live UV index data is unavailable.", "value": None}
    
    except requests.exceptions.RequestException as e:
        # Specific handling for network issues
        return {"error": f"Could not fetch live UV index data (API Error: {e})", "summary": "Live UV index data is unavailable.", "value": None}
    
    except Exception as e:
        # General handling for parsing or unexpected errors
        return {"error": f"Could not fetch live UV index data (Internal Error: {type(e).__name__})", "summary": "Live UV index data is unavailable.", "value": None}

        
# ====================================================================================
# STEP 5D: Location to Region Mapping (Final Robust Version)
# ====================================================================================

REGION_MAP: Dict[str, str] = {
    # Central (rCE) - Keys are now space-free
    "central": "central", "bishan": "central", "bukitmerah": "central", "bukittimah": "central", "botanicgardens": "central",
    "downtowncore": "central", "geylang": "central", "kallang": "central", "tanglin": "central",
    "marinaeast": "central", "marinasouth": "central", "marineparade": "central",
    "newton": "central", "novena": "central", "orchard": "central", 
    "outram": "central", "queenstown": "central", "museum": "central",
    "rivervalley": "central", "rochor": "central", "singaporeriver": "central",
    "straitsview": "central", "toapayoh": "central","macritchie": "central", "centralwatercatchment": "central", # CWC is centralized
    
    # East (rEA) - Keys are now space-free
    "east": "east", "bedok": "east", "changi": "east", "changibay": "east", "hougang": "east",
    "northeasternislands": "east", "pasirris": "east", "payalebar": "east",
    "punggol": "east", "sengkang": "east", "serangoon": "east",
    "tampines": "east", "northeast": "east",
    
    # North (rNO) - Keys are now space-free
    "north": "north", "angmokio": "north", "limchukang": "north",
    "mandai": "north", "seletar": "north", "sembawang": "north",
    "simpang": "north", "sungeikadut": "north", "woodlands": "north",
    
    # South (rSO) - Keys are now space-free
    "south": "south", "southernislands": "south", "harbourfront": "south", "telokblangah": "south",
    
    # West (rWE) - Keys are now space-free
    "west": "west", "boonlay": "west", "bukitbatok": "west", "bukitpanjang": "west",
    "choachukang": "west", "clementi": "west", "jurongeast": "west",
    "jurongwest": "west", "pioneer": "west", "tengah": "west",
    "tuas": "west", "westernwatercatchment": "west" # Added Western Water Catchment back for robustness
}

def get_region_from_location(user_query: str) -> str:
    # Function body is perfectly fine and requires no change.
    query_lower = user_query.lower().replace(' ', '')
    
    for location, region in REGION_MAP.items():
        if location in query_lower:
            return region
            
    return "national"

    # ====================================================================================
# STEP 6: Final RAG Query (AMENDED TO PASS TARGET_REGION TO 2H WEATHER)
# ====================================================================================

# NOTE: You must ensure 'datetime', 'timedelta', 're', 'PROMPT', 
# 'get_region_from_location', 'get_weather_2h', 'get_weather_24h', 
# 'get_weather_4day', 'get_psi', 'get_uv_index', 'get_dengue_hotspots', 
# and 'format_historical_data' are defined and accessible before this function.

def run_rag_query(user_query: str, retriever, historical_psi_df, historical_uv_df, llm):
    """
    The main RAG function combining live data, forecast logic, document context, 
    and historical data to generate a mandatory comprehensive report.
    """
    
    # --- A. Determine Date/Time and Region for Lookup ---
    current_time = datetime.now() 
    query_date = current_time.date()
    target_hour = current_time.hour
    
    # Determine the most specific region from the query using the lookup table
    target_region = get_region_from_location(user_query)
    
    # Check for keywords that suggest a future time (Tomorrow / Date Parsing)
    if "tomorrow" in user_query.lower():
        query_date = current_time.date() + timedelta(days=1)
    
    # Safer regex to extract time: Focuses on explicit formats (Xam/pm or HH:MM).
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

    # --- B. Weather Forecast Decision Logic (AMENDED CALLS BELOW) ---
    is_today = (query_date == current_time.date())
    
    if is_today:
        time_diff_hours = (target_hour - current_time.hour) % 24 
        
        if time_diff_hours <= 2 and time_diff_hours >= 0:
            # 1. Immediate: Use 2-hour forecast (highest granularity)
            # ➡️ PASSING target_region to filter the 2H forecast
            weather_result = get_weather_2h(
                datetime.combine(query_date, datetime.min.time().replace(hour=target_hour)),
                target_region=target_region # 👈 AMENDMENT HERE
            )
            weather_source = "2-Hour Forecast"
        elif time_diff_hours > 2:
            # 2. Later Today: Use 24-hour general forecast
            weather_result = get_weather_24h()
            weather_source = "24-Hour Forecast"
        else: # Covers past hours today, just use current
             # ➡️ PASSING target_region to filter the 2H forecast
             weather_result = get_weather_2h(
                datetime.combine(query_date, datetime.min.time().replace(hour=current_time.hour)),
                target_region=target_region # 👈 AMENDMENT HERE
             )
             weather_source = "Current 2-Hour Forecast"
    else:
        # 3. Future Day: Use 4-day forecast
        weather_result = get_weather_4day()
        weather_source = "4-Day Outlook"

    live_weather_summary = f"Weather Data ({weather_source}):\n{weather_result['summary']}"
    
    # --- C. Live Data Fetching (PSI, UV, Dengue) ---
    
    # Note: Only fetch live PSI/UV if the query is for today/current
    if is_today:
        # Fetch live data using the specific target_region
        live_psi_result = get_psi(target_region=target_region)
        live_uv_result = get_uv_index()
        
        live_psi_summary = live_psi_result['summary']
        live_uv_summary = live_uv_result['summary']
    else:
        live_psi_summary = f"Live PSI forecast for {query_date.strftime('%B %d')} is not available."
        live_uv_summary = f"Live UV Index forecast for {query_date.strftime('%B %d')} is not available."

    # Dengue is always current (not forecast), so we fetch it once
    live_dengue_result = get_dengue_hotspots(user_query)
    live_dengue_summary = live_dengue_result['summary']
    
    # --- D. Historical Data Summaries (Contextual Expectation) ---
    historical_psi_summary, historical_uv_summary = format_historical_data(
        datetime.combine(query_date, datetime.min.time()), 
        historical_psi_df, historical_uv_df, target_hour
    )
    
    # --- E. Retrieve Context Documents ---
    retrieved_docs = retriever.get_relevant_documents(user_query)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
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
    return response.content

    