# amenities.py - Updated with score calculation
import requests
import math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Define amenity weights and scoring rules
AMENITY_WEIGHTS = {
    "hospital": {"weight": 15, "max_distance": 5000},      # 5km
    "pharmacy": {"weight": 10, "max_distance": 2000},      # 2km
    "school": {"weight": 12, "max_distance": 3000},        # 3km
    "college": {"weight": 8, "max_distance": 5000},        # 5km
    "bus_station": {"weight": 10, "max_distance": 1000},   # 1km
    "train_station": {"weight": 15, "max_distance": 2000}, # 2km
    "metro_station": {"weight": 20, "max_distance": 2000}, # 2km
    "restaurant": {"weight": 5, "max_distance": 1000},     # 1km
    "mall": {"weight": 8, "max_distance": 3000},           # 3km
    "police": {"weight": 10, "max_distance": 2000},        # 2km
    "bank": {"weight": 6, "max_distance": 2000},           # 2km
    "park": {"weight": 7, "max_distance": 1000},           # 1km
    "supermarket": {"weight": 8, "max_distance": 1500},    # 1.5km
    "gym": {"weight": 5, "max_distance": 1000},            # 1km
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def calculate_score(amenity_type, distance):
    """Calculate score for an amenity based on distance"""
    if amenity_type not in AMENITY_WEIGHTS:
        return 0
    
    config = AMENITY_WEIGHTS[amenity_type]
    if distance > config["max_distance"]:
        return 0
    
    # Score decreases linearly with distance
    distance_ratio = 1 - (distance / config["max_distance"])
    return config["weight"] * distance_ratio

def get_amenities_with_scores(lat, lon, radius=5000):
    """Get amenities and calculate liveability scores"""
    # Get all amenities in the area
    tags = list(AMENITY_WEIGHTS.keys())
    
    tag_query = ""
    for tag in tags:
        tag_query += f'node["amenity"="{tag}"](around:{radius},{lat},{lon});'
    
    # Also get public transport separately for commute stress
    transport_query = f'''
    node["public_transport"="station"](around:{radius},{lat},{lon});
    node["railway"="station"](around:{radius},{lat},{lon});
    node["railway"="halt"](around:{radius},{lat},{lon});
    '''
    
    query = f"""
    [out:json];
    (
      {tag_query}
      {transport_query}
    );
    out body;
    """
    
    try:
        res = requests.post(OVERPASS_URL, data=query, timeout=10)
        if res.status_code != 200:
            return {"amenities": [], "total_score": 0, "commute_stress": 0}
        
        data = res.json().get("elements", [])
        
        amenities = []
        total_score = 0
        transport_distances = []
        
        for e in data:
            amenity_type = e.get("tags", {}).get("amenity", "")
            if not amenity_type:
                # Check for transport types
                if "public_transport" in e.get("tags", {}):
                    amenity_type = e["tags"]["public_transport"]
                elif "railway" in e.get("tags", {}):
                    amenity_type = e["tags"]["railway"]
            
            if amenity_type in ["station", "halt"]:
                # Transport amenity for commute calculation
                distance = calculate_distance(lat, lon, e["lat"], e["lon"])
                transport_distances.append({
                    "type": amenity_type,
                    "name": e.get("tags", {}).get("name", "Unknown"),
                    "distance": distance,
                    "lat": e["lat"],
                    "lon": e["lon"]
                })
            else:
                # Regular amenity for scoring
                distance = calculate_distance(lat, lon, e["lat"], e["lon"])
                score = calculate_score(amenity_type, distance)
                
                amenities.append({
                    "type": amenity_type,
                    "name": e.get("tags", {}).get("name", "Unknown"),
                    "distance": distance,
                    "score": score,
                    "lat": e["lat"],
                    "lon": e["lon"]
                })
                total_score += score
        
        # Calculate commute stress (0-100, lower is better)
        commute_stress = 100
        if transport_distances:
            min_transport_distance = min([t["distance"] for t in transport_distances])
            if min_transport_distance <= 500:  # 500m or less
                commute_stress = 0
            elif min_transport_distance <= 2000:  # 2km or less
                commute_stress = min_transport_distance / 20  # Scale 0-100
            else:
                commute_stress = 100
        
        return {
            "amenities": amenities,
            "total_score": total_score,
            "commute_stress": min(100, commute_stress),
            "transport_points": transport_distances
        }
        
    except Exception as e:
        print(f"Error fetching amenities: {e}")
        return {"amenities": [], "total_score": 0, "commute_stress": 0}