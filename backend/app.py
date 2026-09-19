import json
import re
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from rag.retrieve import search_knowledge


# ============================================================
# APPLICATION SETUP
# ============================================================

app = Flask(__name__)
CORS(app)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "environmental_data.json"

SCIENTIFIC_REFERENCE_FILE = (
    BASE_DIR
    / "knowledge_base"
    / "documents"
    / "scientific_references.txt"
)


# ============================================================
# LOAD ENVIRONMENTAL DATA
# ============================================================

def load_environmental_data():
    """Load default environmental data from JSON file."""

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print("Could not load environmental data:", error)
        return create_empty_environmental_data()


def create_empty_environmental_data():
    """Create an empty environmental data structure."""

    return {
        "soil": {
            "ph": None,
            "organic_carbon_percent": None,
            "moisture_percent": None
        },

        "climate": {
            "rainfall_mm_per_year": None,
            "average_temperature_celsius": None
        },

        "land": {
            "land_use": None,
            "crop": None,
            "cropping_system": None
        },

        "biodiversity": {
            "species_richness": None,
            "habitat_diversity": None
        },

        "human_impact": {
            "pollution_level": None,
            "deforestation_pressure": None
        },

        "region": {
            "type": None
        }
    }


DEFAULT_ENVIRONMENTAL_DATA = load_environmental_data()


# ============================================================
# MULTI-TURN CONVERSATION MEMORY
# ============================================================

conversation_memory = {}


def get_session_id():
    """
    Get the conversation session ID.

    If the frontend does not provide one,
    use a default session.
    """

    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        session_id = "default-session"

    return session_id


def get_session_memory(session_id):
    """Create memory for a session if it does not already exist."""

    if session_id not in conversation_memory:

        conversation_memory[session_id] = {
            "history": [],
            "environmental_data": create_empty_environmental_data()
        }

    return conversation_memory[session_id]


# ============================================================
# COPY DATA
# ============================================================

def deep_copy(data):
    """Return a safe copy of a dictionary."""

    return json.loads(json.dumps(data))


# ============================================================
# MERGE ENVIRONMENTAL DATA
# ============================================================

def merge_environmental_data(existing, new_data):
    """
    Merge newly detected environmental information
    into existing conversation memory.
    """

    for category in new_data:

        if category not in existing:
            existing[category] = {}

        if isinstance(new_data[category], dict):

            for key, value in new_data[category].items():

                if value is not None:
                    existing[category][key] = value

    return existing


# ============================================================
# NUMBER EXTRACTION
# ============================================================

def extract_number(patterns, text):
    """
    Try several regex patterns and return the first
    valid number found.
    """

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            try:
                return float(match.group(1))

            except (ValueError, TypeError):
                continue

    return None


# ============================================================
# ENVIRONMENTAL INFORMATION EXTRACTION
# ============================================================

def extract_environmental_data(question):
    """
    Extract environmental variables from natural-language input.

    Supported variables:

    - soil pH
    - soil organic carbon
    - soil moisture
    - rainfall
    - temperature
    - crop
    - cropping system
    - land use
    - species richness
    - habitat diversity
    - pollution
    - deforestation
    - region
    """

    text = question.lower()

    data = create_empty_environmental_data()


    # --------------------------------------------------------
    # SOIL ORGANIC CARBON
    # --------------------------------------------------------

    soc = extract_number(
        [
            r"organic\s+carbon(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%",
            r"soil\s+organic\s+carbon(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%",
            r"\bsoc(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%"
        ],
        question
    )

    if soc is not None:
        data["soil"]["organic_carbon_percent"] = soc


    # --------------------------------------------------------
    # SOIL pH
    # --------------------------------------------------------

    ph = extract_number(
        [
            r"soil\s+ph(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)",
            r"\bph(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)"
        ],
        question
    )

    if ph is not None:
        data["soil"]["ph"] = ph


    # --------------------------------------------------------
    # SOIL MOISTURE
    # --------------------------------------------------------

    moisture = extract_number(
        [
            r"soil\s+moisture(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%",
            r"\bmoisture(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%"
        ],
        question
    )

    if moisture is not None:
        data["soil"]["moisture_percent"] = moisture


    # --------------------------------------------------------
    # RAINFALL
    # --------------------------------------------------------

    rainfall = extract_number(
        [
            r"annual\s+rainfall(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*mm",
            r"rainfall(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*mm"
        ],
        question
    )

    if rainfall is not None:
        data["climate"]["rainfall_mm_per_year"] = rainfall


    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    temperature = extract_number(
        [
            r"average\s+temperature(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:°c|c|degrees)?",
            r"temperature(?:\s+is)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:°c|c|degrees)?"
        ],
        question
    )

    if temperature is not None:
        data["climate"]["average_temperature_celsius"] = temperature


    # --------------------------------------------------------
    # CROP
    # --------------------------------------------------------

    crop_patterns = {
        "wheat": "wheat",
        "rice": "rice",
        "maize": "maize",
        "corn": "maize",
        "millet": "millet",
        "sorghum": "sorghum",
        "groundnut": "groundnut",
        "cotton": "cotton",
        "sugarcane": "sugarcane",
        "soybean": "soybean"
    }

    for word, crop_name in crop_patterns.items():

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            text
        ):

            data["land"]["crop"] = crop_name
            break


    # --------------------------------------------------------
    # CROPPING SYSTEM
    # --------------------------------------------------------

    if "monoculture" in text:

        data["land"]["cropping_system"] = "monoculture"

    elif "intercropping" in text:

        data["land"]["cropping_system"] = "intercropping"

    elif "mixed cropping" in text:

        data["land"]["cropping_system"] = "mixed cropping"

    elif (
        "crop rotation" in text
        or "crop rotation system" in text
    ):

        data["land"]["cropping_system"] = "crop rotation"


    # --------------------------------------------------------
    # LAND USE
    # --------------------------------------------------------

    if (
        "agricultural land" in text
        or "agriculture" in text
    ):

        data["land"]["land_use"] = "agriculture"

    elif "forest" in text:

        data["land"]["land_use"] = "forest"

    elif "grassland" in text:

        data["land"]["land_use"] = "grassland"

    elif "urban" in text:

        data["land"]["land_use"] = "urban"


    # --------------------------------------------------------
    # SPECIES RICHNESS
    # --------------------------------------------------------

    richness_levels = [
        "very low",
        "low",
        "medium",
        "moderate",
        "high",
        "very high"
    ]

    for level in richness_levels:

        pattern = (
            r"(?:species\s+richness|species\s+diversity)"
            r".*?\b"
            + re.escape(level)
            + r"\b"
        )

        if re.search(pattern, text):

            data["biodiversity"]["species_richness"] = level
            break


    # --------------------------------------------------------
    # HABITAT DIVERSITY
    # --------------------------------------------------------

    for level in richness_levels:

        pattern = (
            r"(?:habitat\s+diversity|habitat)"
            r".*?\b"
            + re.escape(level)
            + r"\b"
        )

        if re.search(pattern, text):

            data["biodiversity"]["habitat_diversity"] = level
            break


    # --------------------------------------------------------
    # POLLUTION
    # --------------------------------------------------------

    pollution_levels = [
        "very low",
        "low",
        "medium",
        "moderate",
        "high",
        "very high"
    ]

    for level in pollution_levels:

        pattern = (
            r"pollution"
            r".*?\b"
            + re.escape(level)
            + r"\b"
        )

        if re.search(pattern, text):

            data["human_impact"]["pollution_level"] = level
            break


    # --------------------------------------------------------
    # DEFORESTATION
    # --------------------------------------------------------

    for level in pollution_levels:

        pattern = (
            r"deforestation"
            r".*?\b"
            + re.escape(level)
            + r"\b"
        )

        if re.search(pattern, text):

            data["human_impact"]["deforestation_pressure"] = level
            break


    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------

    if (
        "semi-arid" in text
        or "semi arid" in text
    ):

        data["region"]["type"] = "semi-arid"

    elif "arid" in text:

        data["region"]["type"] = "arid"

    elif "tropical" in text:

        data["region"]["type"] = "tropical"

    elif "temperate" in text:

        data["region"]["type"] = "temperate"


    return data


# ============================================================
# MISSING INFORMATION
# ============================================================

def get_missing_fields(environmental_data):
    """
    Identify important environmental variables
    that are still missing.
    """

    missing = []

    soil = environmental_data["soil"]
    climate = environmental_data["climate"]
    land = environmental_data["land"]
    biodiversity = environmental_data["biodiversity"]


    if soil["organic_carbon_percent"] is None:
        missing.append("soil organic carbon")

    if soil["ph"] is None:
        missing.append("soil pH")

    if soil["moisture_percent"] is None:
        missing.append("soil moisture")

    if climate["rainfall_mm_per_year"] is None:
        missing.append("annual rainfall")

    if climate["average_temperature_celsius"] is None:
        missing.append("average temperature")

    if land["land_use"] is None:
        missing.append("land use")

    if land["crop"] is None:
        missing.append("crop")

    if biodiversity["species_richness"] is None:
        missing.append("species richness")

    if biodiversity["habitat_diversity"] is None:
        missing.append("habitat diversity")


    return missing


# ============================================================
# FOLLOW-UP DETECTION
# ============================================================

def is_follow_up_question(question):
    """
    Detect whether the user is continuing
    the previous discussion.
    """

    text = question.lower().strip()

    follow_up_patterns = [

        "what about",

        "what should i do",

        "what should we do",

        "how can i improve",

        "how can we improve",

        "how to improve",

        "how do i improve",

        "why",

        "and biodiversity",

        "and soil",

        "and water",

        "and climate",

        "and land",

        "what about biodiversity",

        "what about soil",

        "what about water",

        "what about climate",

        "what about land"
    ]

    return any(
        pattern in text
        for pattern in follow_up_patterns
    )


# ============================================================
# SCIENTIFIC QUERY
# ============================================================

def build_scientific_query(question, environmental_data):
    """
    Build a focused query for the scientific knowledge layer.

    The query deliberately includes multiple environmental
    variables so that retrieval can connect different
    environmental dimensions.
    """

    context = json.dumps(
        environmental_data,
        ensure_ascii=False,
        indent=2
    )

    return f"""
Scientific environmental decision-support query.

User question:

{question}

Environmental context:

{context}

Find scientific evidence about relationships among:

- soil organic carbon
- soil moisture
- soil pH
- rainfall
- temperature
- land use
- cropping system
- biodiversity
- habitat diversity
- water availability
- human environmental impacts

Prioritize evidence from:

- FAO
- IPCC
- peer-reviewed reviews
- credible environmental research

Focus on:

1. scientifically supported management actions
2. mechanisms explaining why they work
3. environmental metrics that can be monitored
4. relationships between soil, water, climate, land use and biodiversity
5. realistic time horizons

Do not invent numerical improvements.
"""


# ============================================================
# SCIENTIFIC SOURCE METADATA
# ============================================================

SCIENTIFIC_SOURCE_METADATA = [

    {
        "match": "Recarbonizing Global Soils",
        "title": "FAO - Recarbonizing Global Soils",
        "url": "https://www.fao.org/agroecology/in-action/detail/recarbonizing-global-soils-a-technical-manual-of-recommended-sustainable-soil-management/en"
    },

    {
        "match": "Conservation Agriculture Effects on Soil Water Holding Capacity",
        "title": "Abdallah et al. (2021) - Conservation Agriculture and Soil Water Holding Capacity",
        "url": "https://agris.fao.org/search/en/providers/123818/records/67235ca7b605bda15e0aa27d"
    },

    {
        "match": "Soil Organic Cover",
        "title": "FAO - Soil Organic Cover",
        "url": "https://www.fao.org/conservation-agriculture/in-practice/soil-organic-cover/en/"
    },

    {
        "match": "Conservation Agriculture Principles",
        "title": "FAO - Conservation Agriculture Principles",
        "url": "https://www.fao.org/conservation-agriculture/overview/conservation-agriculture-principles/en/"
    },

    {
        "match": "Benefits of Conservation Agriculture",
        "title": "FAO - Benefits of Conservation Agriculture",
        "url": "https://www.fao.org/conservation-agriculture/impact/benefits-of-ca/en/"
    },

    {
        "match": "Soil Biodiversity",
        "title": "FAO - Soil Biodiversity",
        "url": "https://www.fao.org/agriculture/crops/thematic-sitemap/theme/spi/soil-biodiversity/initiatives/adaptive-management/en/"
    },

    {
        "match": "Integrated Soil and Water Management in India",
        "title": "FAO - Integrated Soil and Water Management in India",
        "url": "https://www.fao.org/india/news/detail/Integrated-soil-and-water-management-essential-to-achieve-food-security-in-India-FAO/en"
    },

    {
        "match": "Conservation Agriculture",
        "title": "FAO - Conservation Agriculture",
        "url": "https://www.fao.org/conservation-agriculture"
    }
]


# ============================================================
# SOURCE METADATA LOOKUP
# ============================================================

def get_source_metadata(text):
    """
    Identify scientific source metadata from retrieved text.

    More specific source names are placed before generic
    names so that the correct source is selected.
    """

    if not text:
        return None

    text_lower = text.lower()


    # Specific matches first
    for metadata in SCIENTIFIC_SOURCE_METADATA:

        match_text = metadata["match"].lower()

        if match_text in text_lower:
            return metadata


    return None


# ============================================================
# RAG SOURCE CLEANING
# ============================================================

def format_rag_source(result):
    """
    Convert raw retriever result into a
    frontend-friendly object.
    """

    text = result.get("text", "")

    source = result.get(
        "source",
        result.get(
            "filename",
            "knowledge_base"
        )
    )

    metadata = get_source_metadata(text)


    formatted = {
        "source": source,
        "text": text,
        "score": round(
            float(
                result.get(
                    "score",
                    0
                )
            ),
            4
        ),
        "keyword_score": result.get(
            "keyword_score",
            0
        ),
        "reference_score": result.get(
            "reference_score",
            0
        )
    }


    if metadata:

        formatted["title"] = metadata["title"]
        formatted["url"] = metadata["url"]


    return formatted


# ============================================================
# MERGE RAG RESULTS
# ============================================================

def merge_rag_sources(
    results_a,
    results_b,
    top_k=5
):
    """
    Merge two retrieval passes.

    Pass 1:
        Environmental-context retrieval.

    Pass 2:
        Scientific-evidence retrieval.
    """

    combined = []
    seen = set()


    for result in results_a + results_b:

        text = result.get(
            "text",
            ""
        ).strip()

        if not text:
            continue


        key = text[:250].lower()

        if key in seen:
            continue

        seen.add(key)

        combined.append(result)


    # Prefer scientific reference document results
    # when scientific evidence is requested.

    combined.sort(
        key=lambda item: (
            1
            if "scientific_references"
            in item.get("source", "")
            else 0,

            float(
                item.get(
                    "score",
                    0
                )
            )
        ),
        reverse=True
    )


    return [
        format_rag_source(result)
        for result in combined[:top_k]
    ]


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_recommendations(environmental_data):
    """
    Generate evidence-backed recommendations.

    Every recommendation contains:

    - action
    - scientific reason
    - impacted metric
    - time horizon
    - reference
    """

    recommendations = []

    soil = environmental_data["soil"]
    climate = environmental_data["climate"]
    land = environmental_data["land"]
    biodiversity = environmental_data["biodiversity"]


    # --------------------------------------------------------
    # COMMON BIODIVERSITY CONDITIONS
    # --------------------------------------------------------

    low_species = biodiversity["species_richness"] in [
        "very low",
        "low"
    ]

    low_habitat = biodiversity["habitat_diversity"] in [
        "very low",
        "low"
    ]


    # --------------------------------------------------------
    # RECOMMENDATION 1
    # LOW SOC
    # --------------------------------------------------------

    soc = soil["organic_carbon_percent"]

    if (
        soc is not None
        and soc < 1.0
    ):

        recommendations.append(
            {
                "action": (
                    "Increase soil organic inputs using crop residues, "
                    "cover crops, compost or other suitable organic amendments."
                ),

                "reason": (
                    "Adding organic material can increase carbon inputs "
                    "to soil and support soil structure and biological "
                    "activity. This is particularly relevant when soil "
                    "organic carbon is low."
                ),

                "metric": (
                    "Soil organic carbon percentage; "
                    "soil biological activity; "
                    "soil structure"
                ),

                "time_horizon": (
                    "Multi-season to multi-year monitoring"
                ),

                "reference": (
                    "FAO - Recarbonizing Global Soils"
                )
            }
        )


    # --------------------------------------------------------
    # RECOMMENDATION 2
    # LOW RAINFALL OR LOW MOISTURE
    # --------------------------------------------------------

    rainfall = climate["rainfall_mm_per_year"]
    moisture = soil["moisture_percent"]


    if (
        (
            rainfall is not None
            and rainfall < 800
        )
        or
        (
            moisture is not None
            and moisture < 20
        )
    ):

        recommendations.append(
            {
                "action": (
                    "Maintain soil cover with crop residues or mulch "
                    "and reduce unnecessary soil disturbance. Combine "
                    "this with water-conserving field practices "
                    "appropriate to the site."
                ),

                "reason": (
                    "Soil cover can reduce direct evaporation and "
                    "protect the soil surface. Conservation-agriculture "
                    "practices can also influence infiltration, water "
                    "storage and soil structure."
                ),

                "metric": (
                    "Soil moisture; "
                    "water infiltration; "
                    "water holding capacity; "
                    "soil organic carbon"
                ),

                "time_horizon": (
                    "Effects on soil surface conditions can be monitored "
                    "within a growing season; soil-carbon effects require "
                    "longer-term monitoring."
                ),

                "reference": (
                    "Abdallah et al. (2021) - "
                    "Conservation Agriculture and Soil Water Holding Capacity"
                )
            }
        )


    # --------------------------------------------------------
    # RECOMMENDATION 3
    # MONOCULTURE
    # --------------------------------------------------------

    if land["cropping_system"] == "monoculture":

        recommendations.append(
            {
                "action": (
                    "Introduce crop diversification through crop rotation, "
                    "legume integration or suitable intercropping."
                ),

                "reason": (
                    "Crop diversification changes the types and timing "
                    "of plant inputs to the soil and can support soil "
                    "biological processes. Diversification can also "
                    "reduce dependence on a single crop and create "
                    "more varied habitat conditions."
                ),

                "metric": (
                    "Crop diversity; "
                    "soil organic carbon; "
                    "soil biodiversity; "
                    "habitat diversity"
                ),

                "time_horizon": (
                    "From the next growing season for management changes; "
                    "biodiversity and soil-carbon responses require "
                    "repeated monitoring over multiple seasons."
                ),

                "reference": (
                    "FAO - Conservation Agriculture Principles"
                )
            }
        )


    # --------------------------------------------------------
    # RECOMMENDATION 4
    # LOW BIODIVERSITY
    # --------------------------------------------------------

    if low_species or low_habitat:

        recommendations.append(
            {
                "action": (
                    "Create or restore habitat diversity using native "
                    "vegetation strips, flowering plants, field margins "
                    "and small habitat patches where appropriate."
                ),

                "reason": (
                    "Increasing vegetation and habitat variety can "
                    "provide food, shelter and breeding resources for "
                    "different organisms. Habitat diversity also creates "
                    "ecological connections within agricultural landscapes."
                ),

                "metric": (
                    "Species richness; "
                    "habitat diversity; "
                    "vegetation cover"
                ),

                "time_horizon": (
                    "Seasonal changes can be observed relatively quickly, "
                    "while measurable changes in species richness generally "
                    "require repeated monitoring across seasons or years."
                ),

                "reference": (
                    "FAO - Soil Biodiversity"
                )
            }
        )


    # --------------------------------------------------------
    # RECOMMENDATION 5
    # SOIL + WATER + BIODIVERSITY
    # --------------------------------------------------------

    if (
        soc is not None
        and soc < 1.0
        and moisture is not None
        and moisture < 20
        and (
            low_species
            or low_habitat
        )
    ):

        recommendations.append(
            {
                "action": (
                    "Use an integrated soil-and-biodiversity strategy: "
                    "retain organic residues, maintain vegetation cover, "
                    "diversify crops and establish suitable habitat elements."
                ),

                "reason": (
                    "These practices address several connected environmental "
                    "processes rather than treating soil, water and biodiversity "
                    "as independent problems. Organic inputs and vegetation "
                    "cover can support soil structure and water-related "
                    "functions, while diversified vegetation provides habitat."
                ),

                "metric": (
                    "Soil organic carbon; "
                    "soil moisture; "
                    "water infiltration; "
                    "species richness; "
                    "habitat diversity"
                ),

                "time_horizon": (
                    "Monitor soil and water indicators seasonally and "
                    "biodiversity indicators across multiple seasons or years."
                ),

                "reference": (
                    "FAO - Integrated Soil and Water Management in India"
                )
            }
        )


    # --------------------------------------------------------
    # RECOMMENDATION 6
    # WARM + DRY CONDITIONS
    # --------------------------------------------------------

    temperature = climate["average_temperature_celsius"]


    if (
        temperature is not None
        and temperature >= 30
        and rainfall is not None
        and rainfall < 800
    ):

        recommendations.append(
            {
                "action": (
                    "Prioritize drought-adapted crop choices, soil cover, "
                    "water-conserving practices and diversified planting "
                    "systems suitable for the local climate."
                ),

                "reason": (
                    "Higher temperatures combined with limited rainfall "
                    "increase the importance of conserving available soil "
                    "water. Vegetation diversity can also provide different "
                    "rooting patterns and habitat structures."
                ),

                "metric": (
                    "Soil moisture; "
                    "water availability; "
                    "crop diversity; "
                    "vegetation cover"
                ),

                "time_horizon": (
                    "Water-management effects can be monitored during "
                    "the next growing season; ecosystem responses require "
                    "longer observation."
                ),

                "reference": (
                    "FAO - Conservation Agriculture"
                )
            }
        )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append(
            {
                "action": (
                    "Continue monitoring soil, climate, land-use and "
                    "biodiversity indicators and maintain diversified, "
                    "soil-protective management."
                ),

                "reason": (
                    "Regular measurement helps identify changes in "
                    "environmental conditions and evaluate whether "
                    "management actions are improving the system."
                ),

                "metric": (
                    "Soil organic carbon; "
                    "soil moisture; "
                    "rainfall; "
                    "biodiversity"
                ),

                "time_horizon": (
                    "Seasonal and annual monitoring"
                ),

                "reference": (
                    "FAO environmental and soil-management guidance"
                )
            }
        )


    return recommendations


# ============================================================
# SUMMARY
# ============================================================

def create_summary(environmental_data):
    """
    Create a concise environmental assessment summary.
    """

    soil = environmental_data["soil"]
    climate = environmental_data["climate"]
    land = environmental_data["land"]
    biodiversity = environmental_data["biodiversity"]

    parts = []


    # Soil organic carbon

    if soil["organic_carbon_percent"] is not None:

        if soil["organic_carbon_percent"] < 1.0:

            parts.append(
                "soil organic carbon is relatively low"
            )

        else:

            parts.append(
                "soil organic carbon is being monitored"
            )


    # Rainfall

    if climate["rainfall_mm_per_year"] is not None:

        if climate["rainfall_mm_per_year"] < 800:

            parts.append(
                "annual rainfall is relatively limited"
            )


    # Temperature

    if climate["average_temperature_celsius"] is not None:

        if climate["average_temperature_celsius"] >= 30:

            parts.append(
                "temperature is relatively high"
            )


    # Cropping system

    if land["cropping_system"] == "monoculture":

        parts.append(
            "the land is managed as a monoculture"
        )


    # Species richness

    if biodiversity["species_richness"] in [
        "very low",
        "low"
    ]:

        parts.append(
            "species richness is low"
        )


    # Habitat diversity

    if biodiversity["habitat_diversity"] in [
        "very low",
        "low"
    ]:

        parts.append(
            "habitat diversity is low"
        )


    if not parts:

        return (
            "The system needs additional environmental information "
            "for a detailed assessment."
        )


    return (
        "The environmental assessment indicates that "
        + ", ".join(parts)
        + "."
    )


# ============================================================
# SCIENTIFIC KNOWLEDGE SUMMARY
# ============================================================

def build_scientific_knowledge(rag_sources):
    """
    Create a readable scientific evidence section
    for the frontend.
    """

    knowledge = []


    for source in rag_sources:

        item = {
            "source": source.get(
                "source"
            ),

            "title": source.get(
                "title",
                source.get(
                    "source"
                )
            ),

            "evidence": source.get(
                "text"
            ),

            "score": source.get(
                "score"
            )
        }


        if source.get("url"):

            item["url"] = source["url"]


        knowledge.append(item)


    return knowledge


# ============================================================
# API: ANALYZE
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    try:

        body = request.get_json(
            silent=True
        )


        if not body:

            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Invalid or missing JSON request."
                    )
                }
            ), 400


        question = body.get(
            "question",
            ""
        ).strip()


        language = body.get(
            "language",
            "en"
        )


        if not question:

            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Please enter a question."
                    )
                }
            ), 400


        # ----------------------------------------------------
        # SESSION MEMORY
        # ----------------------------------------------------

        session_id = get_session_id()

        memory = get_session_memory(
            session_id
        )


        # ----------------------------------------------------
        # EXTRACT ENVIRONMENTAL DATA
        # ----------------------------------------------------

        extracted_data = extract_environmental_data(
            question
        )


        # ----------------------------------------------------
        # OPTIONAL STRUCTURED JSON DATA
        # ----------------------------------------------------

        structured_data = body.get(
            "environmental_data"
        )


        if isinstance(
            structured_data,
            dict
        ):

            extracted_data = merge_environmental_data(
                extracted_data,
                structured_data
            )


        # ----------------------------------------------------
        # MERGE WITH MEMORY
        # ----------------------------------------------------

        environmental_data = merge_environmental_data(
            memory["environmental_data"],
            extracted_data
        )


        memory["environmental_data"] = environmental_data


        # ----------------------------------------------------
        # FOLLOW-UP DETECTION
        # ----------------------------------------------------

        follow_up = is_follow_up_question(
            question
        )


        # ----------------------------------------------------
        # MISSING DATA
        # ----------------------------------------------------

        missing_fields = get_missing_fields(
            environmental_data
        )


        # ----------------------------------------------------
        # CLARIFICATION
        # ----------------------------------------------------

        if (
            missing_fields
            and not follow_up
            and len(memory["history"]) == 0
        ):

            missing_text = ", ".join(
                missing_fields[:5]
            )


            if language == "kn":

                clarification = (
                    "ಹೆಚ್ಚು ವಿಶ್ವಾಸಾರ್ಹ ಪರಿಸರ ವಿಶ್ಲೇಷಣೆ ನೀಡಲು "
                    "ದಯವಿಟ್ಟು ಈ ಮಾಹಿತಿಯನ್ನು ನೀಡಿ: "
                    + missing_text
                    + "."
                )

            else:

                clarification = (
                    "To provide a more reliable environmental "
                    "assessment, please provide: "
                    + missing_text
                    + "."
                )


            memory["history"].append(
                {
                    "question": question,
                    "type": "clarification",
                    "language": language
                }
            )


            return jsonify(
                {
                    "success": True,
                    "type": "clarification",
                    "clarification_required": True,
                    "clarification": clarification,
                    "missing_fields": missing_fields,
                    "environmental_data": environmental_data,
                    "language": language,
                    "memory_active": True
                }
            )


        # ----------------------------------------------------
        # RAG QUERY 1
        # ----------------------------------------------------

        context_query = build_scientific_query(
            question,
            environmental_data
        )


        # ----------------------------------------------------
        # RAG QUERY 2
        # ----------------------------------------------------

        focused_query = f"""
Scientific evidence needed for this environmental question:

{question}

Current environmental conditions:

{json.dumps(
    environmental_data,
    ensure_ascii=False,
    indent=2
)}

Find evidence related to:

soil organic carbon,

soil moisture,

water holding capacity,

conservation agriculture,

crop diversification,

soil biodiversity,

habitat diversity,

species richness,

land-use effects,

climate stress,

and integrated soil and water management.

Prefer credible scientific references,
especially FAO and peer-reviewed
environmental research.
"""


        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        try:

            results_a = search_knowledge(
                context_query,
                top_k=10
            )

        except Exception as error:

            print(
                "RAG context retrieval error:",
                error
            )

            results_a = []


        try:

            results_b = search_knowledge(
                focused_query,
                top_k=10
            )

        except Exception as error:

            print(
                "RAG scientific retrieval error:",
                error
            )

            results_b = []


        # ----------------------------------------------------
        # MERGE RAG SOURCES
        # ----------------------------------------------------

        rag_sources = merge_rag_sources(
            results_a,
            results_b,
            top_k=5
        )


        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        recommendations = generate_recommendations(
            environmental_data
        )


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = create_summary(
            environmental_data
        )


        # ----------------------------------------------------
        # SCIENTIFIC KNOWLEDGE
        # ----------------------------------------------------

        scientific_knowledge = build_scientific_knowledge(
            rag_sources
        )


        # ----------------------------------------------------
        # SAVE CONVERSATION
        # ----------------------------------------------------

        memory["history"].append(
            {
                "question": question,
                "type": "analysis",
                "language": language
            }
        )


        # Keep only last 10 turns

        memory["history"] = memory["history"][-10:]


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        response = {

            "success": True,

            "status": "success",

            "type": "analysis",

            "question": question,

            "language": language,

            "memory_active": True,

            "summary": summary,

            "environmental_data": environmental_data,

            "recommendations": recommendations,

            "rag_sources": rag_sources,

            "knowledge_sources": rag_sources,

            "scientific_knowledge": scientific_knowledge,

            "missing_fields": missing_fields
        }


        return jsonify(response)


    except Exception as error:

        print(
            "API error:",
            error
        )


        return jsonify(
            {
                "success": False,
                "error": str(error)
            }
        ), 500


# ============================================================
# API: CLEAR MEMORY
# ============================================================

@app.route(
    "/api/clear-memory",
    methods=["POST"]
)
def clear_memory():

    session_id = get_session_id()


    if session_id in conversation_memory:

        del conversation_memory[
            session_id
        ]


    return jsonify(
        {
            "success": True,
            "message": (
                "Conversation memory cleared."
            )
        }
    )


# ============================================================
# ROOT ROUTE
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify(
        {
            "project": (
                "AI-Powered Biodiversity Intelligence "
                "and Environmental Decision Support System"
            ),

            "status": "running",

            "features": [

                "RAG",

                "FAISS",

                "Scientific knowledge retrieval",

                "Environmental reasoning",

                "Multi-turn memory",

                "Structured environmental data",

                "Biodiversity analysis",

                "Soil analysis",

                "Climate analysis",

                "Land-use analysis",

                "Evidence-backed recommendations"

            ]
        }
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "AI-Powered Biodiversity Intelligence "
        "and Environmental Decision Support System"
    )

    print("=" * 70)

    print(
        "Backend running at: "
        "http://127.0.0.1:5000"
    )

    print(
        "RAG knowledge layer enabled."
    )

    print("=" * 70)


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )