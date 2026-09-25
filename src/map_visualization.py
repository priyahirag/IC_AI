import folium
import pandas as pd


# -----------------------------------
# Incident information
# -----------------------------------

incident_id = "INC001"
incident_lat = 12.8458
incident_lon = 77.6601
radius_km = 2


# -----------------------------------
# Create map
# -----------------------------------

m = folium.Map(
    location=[incident_lat, incident_lon],
    zoom_start=14,
    tiles=None
)


# -----------------------------------
# ArcGIS World Street Map
# -----------------------------------

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri",
    name="ArcGIS World Street Map",
    overlay=False,
    control=True
).add_to(m)


# -----------------------------------
# Incident marker
# -----------------------------------

folium.Marker(
    [incident_lat, incident_lon],
    popup=f"{incident_id} - Flood Incident",
    tooltip="Incident",
    icon=folium.Icon(color="red")
).add_to(m)


# -----------------------------------
# Affected area
# -----------------------------------

folium.Circle(
    [incident_lat, incident_lon],
    radius=radius_km * 1000,
    popup=f"Affected Area - {radius_km} km",
    tooltip="Affected Area",
    fill=True
).add_to(m)


# -----------------------------------
# Infrastructure
# -----------------------------------

df = pd.read_csv("data/infrastructure.csv")

for _, row in df.iterrows():

    folium.Marker(
        [row["latitude"], row["longitude"]],
        popup=f"{row['type']}: {row['name']}",
        tooltip=row["name"]
    ).add_to(m)


# -----------------------------------
# Layer control
# -----------------------------------

folium.LayerControl().add_to(m)


# -----------------------------------
# Save map
# -----------------------------------

m.save("incident_map.html")

print("Map created successfully!")
print("Output: incident_map.html")