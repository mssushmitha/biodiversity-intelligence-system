# AI-Powered Biodiversity Intelligence and Environmental Decision Support System

## 🌱 Project Overview

The **AI-Powered Biodiversity Intelligence and Environmental Decision Support System** is an AI-based environmental intelligence platform developed for the **Darukaa.Earth Hackathon**.

The system analyzes environmental conditions such as soil health, climate, land use, biodiversity, and human impact. It combines structured environmental data with a **Retrieval-Augmented Generation (RAG)-style knowledge layer** to provide scientifically grounded environmental recommendations.

The system is designed as a **decision-support tool** and does not replace environmental scientists, agricultural experts, or other domain professionals.

---

## 🎯 Problem Statement

Environmental decision-making often requires connecting multiple factors such as:

* Soil health
* Soil organic carbon
* Soil moisture
* Climate conditions
* Rainfall
* Temperature
* Land-use patterns
* Biodiversity
* Habitat diversity
* Human impacts such as pollution and deforestation

These variables are interconnected. The system provides an intelligent conversational interface that analyzes these relationships and produces evidence-backed recommendations.

---

## ✨ Key Features

### 1. Environmental Intelligence

The system analyzes:

* Soil pH
* Soil organic carbon
* Soil moisture
* Rainfall
* Average temperature
* Land use
* Cropping system
* Species richness
* Habitat diversity
* Pollution level
* Deforestation pressure

### 2. AI-Based Conversational Analysis

Users can describe an environmental situation using natural language.

The system can:

* Extract environmental information from the input
* Identify missing information
* Ask clarification questions
* Maintain conversational context
* Generate an environmental assessment
* Provide recommendations based on retrieved scientific knowledge

### 3. RAG Knowledge Layer

The system uses a retrieval-based knowledge layer instead of relying only on a language model.

The knowledge base contains structured environmental documents covering:

* Soil health
* Biodiversity
* Climate
* Land use
* Conservation agriculture
* Scientific references

The system uses:

* Sentence Transformers
* FAISS vector search
* Semantic similarity retrieval
* Keyword-based relevance scoring
* Scientific reference prioritization

The current knowledge index contains **83 searchable chunks**.

### 4. Evidence-Based Recommendations

Each recommendation provides:

* What should be done
* Why the recommendation is relevant
* Environmental metrics affected
* Expected time horizon
* Scientific reference

The system avoids unsupported fixed numerical improvement claims.

### 5. Multi-Variable Environmental Reasoning

The system connects multiple environmental variables.

Examples include:

```text
Soil health → Soil moisture → Biodiversity
Land use → Habitat diversity → Species richness
Climate → Water availability → Vegetation → Biodiversity
Cropping system → Soil organic carbon → Soil biodiversity
```

### 6. Bilingual Interface

The frontend supports:

* English
* Kannada

The interface also includes voice input and text-to-speech functionality.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Input     │
                    │ Text / Environment  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Flask Backend     │
                    │ Environmental       │
                    │ Data Extraction     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Conversation       │
                    │  Memory / Context   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   RAG Retrieval     │
                    │ Sentence Transformer│
                    │ + FAISS             │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Scientific Knowledge│
                    │     Base            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Recommendation      │
                    │ Generation           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Frontend Dashboard  │
                    │ Summary / Metrics   │
                    │ Recommendations     │
                    │ Scientific Sources  │
                    └─────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive user interface
* English/Kannada language support
* Browser voice input
* Text-to-speech

### Backend

* Python
* Flask
* Flask-CORS

### AI / RAG

* Sentence Transformers
* `all-MiniLM-L6-v2`
* FAISS
* Semantic vector retrieval
* Keyword relevance scoring

### Data

* JSON-based environmental dataset
* Text-based scientific knowledge base
* FAISS vector index

### Development Tools

* Visual Studio Code
* Git
* GitHub
* Python Virtual Environment

---

## 📁 Project Structure

```text
darukaa-biodiversity-ai/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── chat.html
│   └── css/
│       └── style.css
│
├── knowledge_base/
│   └── documents/
│       ├── biodiversity.txt
│       ├── climate_land_use.txt
│       ├── scientific_references.txt
│       └── soil_health.txt
│
├── rag/
│   ├── ingest.py
│   ├── retrieve.py
│   └── vector_store/
│       ├── chunks.json
│       └── knowledge.index
│
├── data/
│   └── environmental_data.json
│
├── database/
│
├── README.md
└── .gitignore
```

---

## 📊 Environmental Data Schema

The system uses structured JSON environmental information.

Example:

```json
{
  "soil": {
    "ph": 6.2,
    "organic_carbon_percent": 0.3,
    "moisture_percent": 12
  },
  "climate": {
    "rainfall_mm_per_year": 500,
    "average_temperature_celsius": 31
  },
  "land": {
    "land_use": "agriculture",
    "crop": "wheat",
    "cropping_system": "monoculture"
  },
  "biodiversity": {
    "species_richness": "low",
    "habitat_diversity": "low"
  },
  "human_impact": {
    "pollution_level": "low",
    "deforestation_pressure": "medium"
  }
}
```

---

## 🔎 Knowledge Base

The knowledge base includes environmental and scientific information related to:

* Soil organic carbon
* Soil biodiversity
* Soil moisture
* Conservation agriculture
* Crop diversification
* Habitat diversity
* Biodiversity
* Climate and land use
* Soil and water management

### Scientific References

The project references resources including:

* Food and Agriculture Organization of the United Nations (FAO)
* FAO Recarbonizing Global Soils
* FAO Conservation Agriculture
* FAO Soil Biodiversity
* FAO Soil and Water Management in India
* Abdallah et al. (2021), Conservation Agriculture and Soil Water Holding Capacity

---

## ⚙️ Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mssushmitha/biodiversity-intelligence-system.git
cd biodiversity-intelligence-system
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r backend/requirements.txt
```

### 4. Start the Backend

```powershell
python backend/app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

### 5. Open the Frontend

Open:

```text
frontend/index.html
```

in a browser.

---

## 🔌 API

### Analyze Environmental Conditions

```text
POST /api/analyze
```

Example request:

```json
{
  "question": "The soil organic carbon is low, rainfall is limited, and the area has monoculture farming with low biodiversity.",
  "language": "en"
}
```

The API returns:

* Environmental summary
* Recommendations
* Impacted environmental metrics
* Scientific knowledge
* Retrieved sources
* Conversation status
* Environmental data

---

## 🧠 RAG Workflow

The RAG pipeline works as follows:

```text
Scientific Documents
        ↓
Text Chunking
        ↓
Sentence Transformer Embeddings
        ↓
FAISS Vector Index
        ↓
User Environmental Query
        ↓
Semantic Retrieval
        ↓
Keyword Relevance Scoring
        ↓
Scientific Evidence
        ↓
Evidence-Backed Recommendation
```

This ensures that recommendations are connected to retrieved environmental knowledge rather than being generated only from a general-purpose language model.

---

## 🔗 GitHub Repository

https://github.com/mssushmitha/biodiversity-intelligence-system

---

## 🚀 Current Project Status

The current prototype includes:

* Functional Flask backend
* Environmental data processing
* Conversational clarification
* Conversation memory
* RAG knowledge retrieval
* FAISS vector database
* Scientific source retrieval
* Evidence-backed recommendations
* English/Kannada interface
* Voice input interface
* Text-to-speech interface
* GitHub repository

---

## 🔄 CI/CD

CI/CD automation has not been configured in the current prototype.

The project currently uses:

* Git for version control
* GitHub for source-code hosting
* Local development and testing

---

## ⚠️ Limitations

This prototype is intended for environmental decision support and educational/research purposes.

It should not be treated as a replacement for:

* Environmental scientists
* Agricultural experts
* Ecologists
* Government environmental assessments
* Professional field measurements

Environmental recommendations should be validated against local field conditions and expert knowledge before implementation.

---

## 🌍 Future Enhancements

Future versions can include:

* Real-time weather data
* GIS and satellite imagery
* Geo-coordinate-based environmental analysis
* Land-cover classification
* Remote sensing data
* Real environmental sensor integration
* Larger scientific knowledge base
* Advanced biodiversity datasets
* Expert feedback loops
* Cloud deployment
* Automated CI/CD
* Improved Kannada voice recognition
* Additional Indian regional languages

---

## 👩‍💻 Developed For

**Darukaa.Earth AI Hackathon**

### Project

**AI-Powered Biodiversity Intelligence and Environmental Decision Support System**

### Repository

https://github.com/mssushmitha/biodiversity-intelligence-system
