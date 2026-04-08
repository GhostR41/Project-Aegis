import math
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from shared.utils import load_json, standardize_asteroid_data

import os

def query_asteroid_database(query_str: str) -> str:
    """
    Search the entire local asteroid database for a specific keyword or property.
    Use this for queries like 'discovered in 2025', 'composition: iron', or 'highest impact probability'.
    
    Args:
        query_str: The search term or filter criteria.
        
    Returns:
        A formatted string listing the matching asteroids and their key details.
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "asteroids.json")
    data = load_json(db_path)
    if not data:
        return "Database is empty."
    
    query_lower = query_str.lower()
    matches = []
    
    for row in data:
        # Search all string values in the row
        row_str = str(row).lower()
        if query_lower in row_str:
            matches.append({
                "name": row.get("name"),
                "diameter": row.get("diameter"),
                "composition": row.get("composition"),
                "discovery_date": row.get("discovery_date"),
                "notes": row.get("notes")
            })
            
    if not matches:
        return f"No records found matching '{query_str}'."
        
    return json.dumps(matches, indent=2)

def lookup_asteroid(name: str) -> Optional[Dict[str, Any]]:
    """
    Search the local JSON database for an asteroid by name.
    
    Args:
        name: Name of the asteroid (e.g., 'Apophis-2026', 'Bennu')
        
    Returns:
        A dictionary containing the standardized asteroid data, or None if not found.
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "asteroids.json")
    data = load_json(db_path)
    if not data:
        return None
    
    name_lower = name.lower()
    for row in data:
        if name_lower in row.get("name", "").lower():
            return row
            
    return None

def search_web_for_asteroid(asteroid_name: str) -> Dict[str, Any]:
    """
    Fallback web-search tool. Queries Wikipedia to extract asteroid details
    when the local database does not have the target.
    
    Args:
        asteroid_name: Name of the asteroid to search.
        
    Returns:
        A dictionary containing extracted raw facts formatted for the internal schema.
    """
    query = urllib.parse.quote(f"asteroid {asteroid_name} diameter mass velocity composition")
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json&srlimit=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            search_results = result.get('query', {}).get('search', [])
            if not search_results:
                return {"error": "No web results found.", "raw_text": "No data found on Wikipedia."}
                
            page_title = search_results[0]['title']
            
            # Fetch snippet/extract
            extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageprops&exintro&explaintext&titles={urllib.parse.quote(page_title)}&format=json"
            req2 = urllib.request.Request(extract_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2) as resp2:
                extract_res = json.loads(resp2.read().decode())
                pages = extract_res.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    extract_text = page_data.get('extract', '')
                    
                    # Instead of just returning text, we inform the agent that it MUST parse this
                    # into AsteroidData schema. We provide the raw text as the source.
                    return {
                        "success": True, 
                        "source": "Wikipedia",
                        "raw_text": extract_text,
                        "metadata": {
                            "name": page_title,
                            "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                        }
                    }
                    
        return {"error": "Failed to extract web data."}
    except Exception as e:
        return {"error": f"Web search failed: {str(e)}"}

def calculate_impact_energy(mass_kg: float, velocity_km_s: float) -> Dict[str, float]:
    velocity_m_s = velocity_km_s * 1000
    energy_joules = 0.5 * mass_kg * (velocity_m_s ** 2)
    MEGATON_TNT_JOULES = 4.184e15
    energy_megatons = energy_joules / MEGATON_TNT_JOULES
    return {"energy_joules": energy_joules, "energy_megatons_tnt": energy_megatons}

def estimate_crater_diameter(impact_energy_joules: float) -> float:
    return 0.07 * (impact_energy_joules ** 0.25)

def estimate_damage_radius(energy_megatons: float) -> Dict[str, float]:
    if energy_megatons < 1:
        return {"fireball_km": 1, "severe_damage_km": 5, "moderate_damage_km": 20, "description": "Local damage"}
    elif energy_megatons < 100:
        return {"fireball_km": 5*(energy_megatons**0.33), "severe_damage_km": 20*(energy_megatons**0.33), "moderate_damage_km": 100*(energy_megatons**0.33), "description": "City-destroying impact"}
    elif energy_megatons < 10000:
        return {"fireball_km": 10*(energy_megatons**0.33), "severe_damage_km": 50*(energy_megatons**0.33), "moderate_damage_km": 200*(energy_megatons**0.33), "description": "Regional devastation"}
    else:
        return {"fireball_km": 50*(energy_megatons**0.33), "severe_damage_km": 200*(energy_megatons**0.33), "moderate_damage_km": 1000*(energy_megatons**0.33), "description": "Global catastrophe"}

def threat_calculator_tool(mass: float, velocity: float, diameter: float, impact_probability: float, name: str = "Unknown") -> Dict[str, Any]:
    """
    Calculate comprehensive threat assessment for an asteroid.
    
    Args:
        mass: Mass in kg
        velocity: Velocity in km/s
        diameter: Diameter in meters
        impact_probability: Probability of Earth impact (0 to 1)
        name: Name of asteroid
    """
    energy = calculate_impact_energy(mass, velocity)
    energy_mt = energy["energy_megatons_tnt"]
    damage = estimate_damage_radius(energy_mt)
    crater_km = estimate_crater_diameter(energy["energy_joules"])
    
    consequence_score = min(100, math.log10(max(1, energy_mt)) * 20)
    risk_score = impact_probability * consequence_score
    
    if risk_score >= 70 or (impact_probability >= 0.8 and energy_mt > 100):
        threat_level, urgency, action = "CRITICAL", "IMMEDIATE", "EMERGENCY DEFLECTION REQUIRED - Request Agent 2"
    elif risk_score >= 40 or (impact_probability >= 0.5 and energy_mt > 10):
        threat_level, urgency, action = "HIGH", "URGENT", "DEFLECTION MISSION RECOMMENDED - Request Agent 2"
    elif risk_score >= 15 or (impact_probability >= 0.1):
        threat_level, urgency, action = "MEDIUM", "ELEVATED", "CLOSE MONITORING - Consider planning"
    else:
        threat_level, urgency, action = "LOW", "ROUTINE", "STANDARD MONITORING"
        
    return {
        "asteroid_name": name,
        "threat_level": threat_level,
        "urgency": urgency,
        "risk_score": round(risk_score, 2),
        "impact_analysis": {
            "impact_probability_percent": round(impact_probability * 100, 2),
            "impact_energy_megatons_tnt": round(energy_mt, 2),
            "estimated_crater_diameter_km": round(crater_km, 2),
            "damage_assessment": damage["description"]
        },
        "recommended_action": action
    }
