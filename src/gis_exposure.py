import pandas as pd
import math
import json


# -----------------------------------
# 1. Calculate distance between points
# -----------------------------------

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -----------------------------------
# 2. Find nearby infrastructure
# -----------------------------------

def find_exposed_infrastructure(
    incident_lat,
    incident_lon,
    radius_km
):
    df = pd.read_csv("data/infrastructure.csv")

    exposed = []

    for _, row in df.iterrows():

        distance = haversine_distance(
            incident_lat,
            incident_lon,
            row["latitude"],
            row["longitude"]
        )

        if distance <= radius_km:

            exposed.append({
                "id": row["id"],
                "type": row["type"],
                "name": row["name"],
                "distance_km": round(distance, 2)
            })

    return exposed


# -----------------------------------
# 3. Calculate population exposure
# -----------------------------------

def calculate_population_exposure(
    incident_lat,
    incident_lon,
    radius_km
):
    df = pd.read_csv("data/population_zones.csv")

    total_population = 0
    exposed_zones = []

    for _, row in df.iterrows():

        distance = haversine_distance(
            incident_lat,
            incident_lon,
            row["latitude"],
            row["longitude"]
        )

        if distance <= radius_km:

            total_population += row["population"]

            exposed_zones.append({
                "zone_id": row["zone_id"],
                "population": row["population"],
                "vulnerability": row["vulnerability"],
                "distance_km": round(distance, 2)
            })

    return {
        "population_exposed": total_population,
        "exposed_zones": exposed_zones
    }


# -----------------------------------
# 4. Summarize infrastructure
# -----------------------------------

def summarize_infrastructure(exposed):

    summary = {
        "hospitals": 0,
        "schools": 0,
        "police_stations": 0,
        "roads": 0
    }

    for item in exposed:

        if item["type"] == "hospital":
            summary["hospitals"] += 1

        elif item["type"] == "school":
            summary["schools"] += 1

        elif item["type"] == "police":
            summary["police_stations"] += 1

        elif item["type"] == "road":
            summary["roads"] += 1

    return summary


# -----------------------------------
# 5. Calculate vulnerability score
# -----------------------------------

def calculate_vulnerability(population_result):

    zones = population_result["exposed_zones"]

    if not zones:
        return 0

    total_population = sum(
        zone["population"] for zone in zones
    )

    if total_population == 0:
        return 0

    weighted_score = sum(
        zone["population"] * zone["vulnerability"]
        for zone in zones
    )

    score = weighted_score / total_population

    return round(score, 2)


# -----------------------------------
# 6. Complete GIS exposure analysis
# -----------------------------------

def calculate_exposure(
    incident_id,
    incident_lat,
    incident_lon,
    radius_km
):

    # Find infrastructure
    infrastructure = find_exposed_infrastructure(
        incident_lat,
        incident_lon,
        radius_km
    )

    # Summarize infrastructure
    infrastructure_summary = summarize_infrastructure(
        infrastructure
    )

    # Find exposed population
    population_result = calculate_population_exposure(
        incident_lat,
        incident_lon,
        radius_km
    )

    # Calculate vulnerability
    vulnerability_score = calculate_vulnerability(
        population_result
    )

    # Final result
    result = {
        "incident_id": incident_id,
        "incident_latitude": incident_lat,
        "incident_longitude": incident_lon,
        "affected_radius_km": radius_km,

        "population_exposed":
            population_result["population_exposed"],

        "hospitals":
            infrastructure_summary["hospitals"],

        "schools":
            infrastructure_summary["schools"],

        "police_stations":
            infrastructure_summary["police_stations"],

        "roads":
            infrastructure_summary["roads"],

        "vulnerability_score":
            vulnerability_score,

        "infrastructure":
            infrastructure,

        "population_zones":
            population_result["exposed_zones"]
    }

    return result


# -----------------------------------
# 7. TEST
# -----------------------------------

if __name__ == "__main__":

    result = calculate_exposure(
        incident_id="INC001",
        incident_lat=12.8458,
        incident_lon=77.6601,
        radius_km=2
    )

    print("\n========== CRISISLENS GIS EXPOSURE ==========\n")

    print("Incident ID:",
          result["incident_id"])

    print("Incident Location:",
          result["incident_latitude"],
          result["incident_longitude"])

    print("Affected Radius:",
          result["affected_radius_km"],
          "km")

    print("Population Exposed:",
          result["population_exposed"])

    print("Hospitals:",
          result["hospitals"])

    print("Schools:",
          result["schools"])

    print("Police Stations:",
          result["police_stations"])

    print("Roads:",
          result["roads"])

    print("Vulnerability Score:",
          result["vulnerability_score"])

    print("\nNearby Infrastructure:")

    for item in result["infrastructure"]:
        print(
            f"- {item['type']} | "
            f"{item['name']} | "
            f"{item['distance_km']} km"
        )

    print("\nExposed Population Zones:")

    for zone in result["population_zones"]:
        print(
            f"- {zone['zone_id']} | "
            f"Population: {zone['population']} | "
            f"Vulnerability: {zone['vulnerability']} | "
            f"Distance: {zone['distance_km']} km"
        )

    print("\n=============================================\n")


    # -----------------------------------
    # 8. Save result as JSON
    # -----------------------------------

    with open("gis_exposure_result.json", "w") as file:
        json.dump(result, file, indent=4)

    print("GIS result saved to gis_exposure_result.json")
        # -----------------------------------
    # 9. Save final GIS CSV for integration
    # -----------------------------------

    exposure_reference_population = 10000

    exposure_score = min(
        (result["population_exposed"] / exposure_reference_population) * 100,
        100
    )

    final_gis = pd.DataFrame([{
        "incident_id": result["incident_id"],
        "latitude": result["incident_latitude"],
        "longitude": result["incident_longitude"],
        "population_exposed": result["population_exposed"],
        "exposure": round(exposure_score, 2),
        "vulnerability": result["vulnerability_score"]
    }])

    final_gis.to_csv(
        "prajan_final_gis_output.csv",
        index=False
    )

    print("Final GIS CSV saved to prajan_final_gis_output.csv")