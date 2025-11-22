"""
RAG (Retrieval-Augmented Generation) runner for the environmental bot.
Handles LLM initialization, document loading, and query processing.
"""

import os
import re
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from helper_functions.constants import (
    HEADERS, REQUEST_TIMEOUT, PSI_MONTHLY_AVERAGES_DATA,
    UV_HOURLY_AVERAGES_DATA, PDF_SOURCES, URL_SOURCES
)
from helper_functions.formatters import get_region_from_location, format_historical_data
from .data_fetchers import (
    get_weather_2h, get_weather_24h, get_weather_4day,
    get_psi, get_uv_index, get_dengue_hotspots
)

# ====================================================================================
# PROMPT TEMPLATE
# ====================================================================================

PROMPT_TEMPLATE = """
You are a weather assistant bot called SteadyDayEveryday. Your goal is to provide concise, factual, and actionable public data and health advice regarding environmental hazards like bad weather (rain or heat stress), air pollution, and active dengue clusters.

Your response must strictly adhere to the following rules:
1. **Mandatory Report:** Always start by generating a report using ALL data summaries provided below (Weather, PSI, UV Index, and Dengue Clusters, including the **Dengue Alert Level**). You MUST include sections 1, 2, and 3. You MUST only include Section 4 (Dengue Risk) if the 'Dengue Data' ({live_dengue_summary}) is NOT empty.
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

--- OUTPUT FORMAT EXAMPLE ---
## ⚠️ ENVIRONMENTAL REPORT: [Target region]

### 1. Weather Data (2-Hour Forecast)
[Use relevant emojis and provided data]
🌧️ Forecast: [forecast data] \n
🌡️ Temperature Range: [temperature range]

### 2. Air Quality (PSI)
😷 Live 3-Hour PSI for **[target region]**: **[PSI value]** [PSI category] \n
📊 Historical Expectation for November: Avg 24-hr PSI is typically [PSI value]

### 3. UV Index
☀️ Current Live UV Index: **[UV index value]** [UV index level] \n
📊 Historical Expectation for [month] (hour): Average UV Index is [UV index value].

### 4. Dengue Risk
🦟 Dengue Alert Level: **[dengue alert level]**. [active clusters if relevant] Stay vigilant.

---
### Public Health Advice
Based on the data and retrieved context, here is your actionable advice:
* Advice Point 1
* Advice Point 2
* Advice Point 3
"""

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE,
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
# RAG COMPONENT LOADER
# ====================================================================================

def load_rag_components() -> Dict[str, Any]:
    """
    Loads and initializes all RAG components: LLM, Historical DataFrames, and Vector Store.
    This is called once at app startup.
    
    Returns:
        Dict containing: llm, retriever, historical_psi_df, historical_uv_df
    """
    print("\n--- Running load_rag_components() for one-time initialization ---")
    
    # 1. Initialize LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    print("✅ LLM initialized.")
    
    # 2. Load Historical DataFrames
    historical_psi_df = pd.DataFrame(PSI_MONTHLY_AVERAGES_DATA)
    historical_psi_df['date'] = pd.to_datetime(historical_psi_df['Month'], format='%Y-%m')

    historical_uv_df = pd.DataFrame(UV_HOURLY_AVERAGES_DATA)
    historical_uv_df['date'] = pd.to_datetime(historical_uv_df['Month'], format='%Y-%m')
    historical_uv_df['Hour'] = historical_uv_df['Hour'].astype(int)
    print("✅ Historical DataFrames loaded.")

    # 3. Data Loading (PDFs + URLs)
    all_docs: List[Document] = []
    
    # Load PDFs
    for label, url in PDF_SOURCES.items():
        tmp_file_path = None
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            if not response.headers.get('Content-Type', '').startswith('application/pdf'):
                continue
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["label"] = label
                doc.metadata["source"] = url
            all_docs.extend(docs)
        except Exception as e:
            print(f"⚠️ Failed to load PDF {label}: {e}")
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    # Load URLs
    for label, url in URL_SOURCES.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            all_docs.append(Document(page_content=text, metadata={"source": url, "label": label}))
        except Exception as e:
            print(f"⚠️ Failed to load URL {label}: {e}")

    print(f"✅ Total RAG documents loaded: {len(all_docs)}")

    # 4. Vectorization and Retriever Creation
    retriever = None
    if all_docs:
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
            chunks = text_splitter.split_documents(all_docs)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vectorstore = FAISS.from_documents(chunks, embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            print(f"✅ Vector Store (FAISS) created with {len(chunks)} chunks!")
            print("✅ Retriever initialized.")
        except Exception as e:
            print(f"❌ VECTORIZATION FAILED: {e}")

    return {
        "llm": llm,
        "retriever": retriever,
        "historical_psi_df": historical_psi_df,
        "historical_uv_df": historical_uv_df
    }


# ====================================================================================
# MAIN RAG QUERY RUNNER
# ====================================================================================

def run_rag_query(
    user_query: str,
    retriever: Any,
    historical_psi_df: pd.DataFrame,
    historical_uv_df: pd.DataFrame,
    llm: ChatOpenAI
) -> Dict[str, Any]:
    """
    Main RAG function combining live data, forecast logic, document context, and historical data.
    
    Args:
        user_query (str): User's question
        retriever: Document retriever for RAG
        historical_psi_df (pd.DataFrame): Historical PSI data
        historical_uv_df (pd.DataFrame): Historical UV data
        llm (ChatOpenAI): LLM instance
        
    Returns:
        Dict with 'response' and API status flags
    """
    
    # Initialize status flags
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
    historical_psi_summary = "Historical PSI data could not be summarized."
    historical_uv_summary = "Historical UV data could not be summarized."
    
    try:
        # --- A. Determine Date/Time and Region ---
        current_time = datetime.now()
        query_date = current_time.date()
        target_hour = current_time.hour
        target_region = get_region_from_location(user_query)
        
        # Check for "tomorrow"
        if "tomorrow" in user_query.lower():
            query_date = current_time.date() + timedelta(days=1)
        
        # Extract time from query
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

        # --- B. Determine which weather forecast to use ---
        is_today = (query_date == current_time.date())
        weather_result = {"summary": "Weather API failed to load.", "status": False}
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
            
        live_weather_summary = f"Weather Data ({weather_source}):\n{weather_result['summary']}"
        api_statuses["weather_status"] = weather_result['status']

        # --- C. Fetch Live Data ---
        if is_today:
            live_psi_result = get_psi(target_region=target_region)
            live_uv_result = get_uv_index()
            
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
        
        # --- D. Format Historical Data ---
        historical_psi_summary, historical_uv_summary = format_historical_data(
            datetime.combine(query_date, datetime.min.time()),
            historical_psi_df, historical_uv_df, target_hour
        )
        
        # --- E. Retrieve Context Documents ---
        if retriever:
            try:
                retrieved_docs = retriever.get_relevant_documents(user_query)
                context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
            except Exception as e:
                context_text = "RAG context unavailable due to retrieval error."
        
        # --- F. Final Prompt and LLM Execution ---
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
        
        response = llm.invoke(final_prompt)
        response_content = response.content

        return {
            "response": response_content,
            "weather_status": api_statuses["weather_status"],
            "psi_status": api_statuses["psi_status"],
            "uv_status": api_statuses["uv_status"],
            "dengue_status": api_statuses["dengue_status"],
        }
    
    except Exception as e:
        error_message = f"System Error: Failed to process query due to internal data fetching issue: {e}"
        print(f"FATAL RAG RUNNER ERROR: {error_message}")
        
        return {
            "response": error_message,
            "weather_status": False,
            "psi_status": False,
            "uv_status": False,
            "dengue_status": False,
        }