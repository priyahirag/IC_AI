import os

from pathlib import Path

import random



import streamlit as st

import pandas as pd

import pydeck as pdk



from priority import calculate_priority, get_priority_level





# ==========================================

# PAGE SETUP

# ==========================================



st.set_page_config(

    page_title="CrisisLens",

    page_icon="🚨",

    layout="wide"

)



st.markdown("""

<style>

.main-title {

    font-size: 42px;

    font-weight: 700;

    margin-bottom: 0px;

}



.subtitle {

    font-size: 20px;

    color: #666;

    margin-top: 0px;

}



.section-title {

    font-size: 28px;

    font-weight: 600;

    margin-top: 25px;

}

</style>

""", unsafe_allow_html=True)





st.markdown(

    '<div class="main-title">🚨 CrisisLens</div>',

    unsafe_allow_html=True

)



st.markdown(

    '<div class="subtitle">Disaster Intelligence Dashboard</div>',

    unsafe_allow_html=True

)





# ==========================================

# YOLO IMAGE / CV PROFILES

# ==========================================

#

# These are Nikhil's three existing YOLO

# outputs.

#

# Each profile contains:

# - image

# - person count

# - car count

# - boat count

# - CV severity

#

# A simulated incident will randomly receive

# one of these profiles.

# ==========================================



YOLO_PROFILES = [



    {

        "yolo_image": "flood1_detected.jpg",

        "person_count": 0,

        "car_count": 8,

        "boat_count": 0,

        "cv_severity": "MEDIUM"

    },



    {

        "yolo_image": "flood2_detected.jpg",

        "person_count": 1,

        "car_count": 2,

        "boat_count": 0,

        "cv_severity": "LOW"

    },



    {

        "yolo_image": "flood3_detected.jpg",

        "person_count": 0,

        "car_count": 0,

        "boat_count": 4,

        "cv_severity": "LOW"

    }



]





# ==========================================

# URGENCY CALCULATION

# ==========================================



def calculate_urgency(evidence):



    text = str(evidence).lower()



    if "trapped" in text or "immediate danger" in text:

        return 100



    elif "rescue" in text or "people affected" in text:

        return 90



    elif "blocked" in text or "rapid response" in text:

        return 75



    elif "damage" in text:

        return 60



    else:

        return 40





# ==========================================

# COMPUTER VISION URGENCY ADJUSTMENT

# ==========================================



def calculate_cv_adjustment(row):



    adjustment = 0



    person_count = pd.to_numeric(

        row.get("person_count", 0),

        errors="coerce"

    )



    car_count = pd.to_numeric(

        row.get("car_count", 0),

        errors="coerce"

    )



    boat_count = pd.to_numeric(

        row.get("boat_count", 0),

        errors="coerce"

    )



    if pd.isna(person_count):

        person_count = 0



    if pd.isna(car_count):

        car_count = 0



    if pd.isna(boat_count):

        boat_count = 0



    cv_severity = str(

        row.get("cv_severity", "N/A")

    ).upper()





    # --------------------------------------

    # PEOPLE

    # --------------------------------------



    if person_count >= 5:

        adjustment += 15



    elif person_count >= 1:

        adjustment += 10





    # --------------------------------------

    # CARS

    # --------------------------------------



    if car_count >= 10:

        adjustment += 15



    elif car_count >= 5:

        adjustment += 10



    elif car_count >= 1:

        adjustment += 5





    # --------------------------------------

    # BOATS

    # --------------------------------------



    if boat_count >= 5:

        adjustment += 15



    elif boat_count >= 1:

        adjustment += 10





    # --------------------------------------

    # CV SEVERITY

    # --------------------------------------



    if cv_severity == "HIGH":

        adjustment += 10



    elif cv_severity == "MEDIUM":

        adjustment += 5





    # Maximum CV contribution

    adjustment = min(

        adjustment,

        25

    )



    return adjustment





# ==========================================

# LOAD DATA

# ==========================================



if "data" not in st.session_state:



    # --------------------------------------

    # Load main incident CSV

    # --------------------------------------



    st.session_state.data = pd.read_csv(

        "final_incidents.csv"

    )





    # --------------------------------------

    # Load CV results

    # --------------------------------------



    if os.path.exists(

        "cv_results.csv"

    ):



        cv_df = pd.read_csv(

            "cv_results.csv"

        )



        st.session_state.data = (

            st.session_state.data.merge(

                cv_df,

                on="incident_id",

                how="left"

            )

        )



    else:



        st.session_state.data[

            "person_count"

        ] = 0



        st.session_state.data[

            "car_count"

        ] = 0



        st.session_state.data[

            "boat_count"

        ] = 0



        st.session_state.data[

            "cv_severity"

        ] = "N/A"





# ==========================================

# ENSURE CV COLUMNS

# ==========================================



if "person_count" not in st.session_state.data.columns:

    st.session_state.data["person_count"] = 0



if "car_count" not in st.session_state.data.columns:

    st.session_state.data["car_count"] = 0



if "boat_count" not in st.session_state.data.columns:

    st.session_state.data["boat_count"] = 0



if "cv_severity" not in st.session_state.data.columns:

    st.session_state.data["cv_severity"] = "N/A"





# ==========================================

# ASSIGN EXISTING YOLO IMAGES TO KNOWN

# INCIDENTS

# ==========================================



known_yolo_images = {

    "INC001": "flood1_detected.jpg",

    "INC002": "flood2_detected.jpg",

    "INC003": "flood3_detected.jpg"

}





if "yolo_image" not in st.session_state.data.columns:



    st.session_state.data[

        "yolo_image"

    ] = st.session_state.data[

        "incident_id"

    ].map(

        known_yolo_images

    )





# ==========================================

# BASE URGENCY

# ==========================================



if "base_urgency" not in st.session_state.data.columns:



    st.session_state.data[

        "base_urgency"

    ] = st.session_state.data[

        "evidence"

    ].apply(

        calculate_urgency

    )





# ==========================================
# SIMULATE NEW INCIDENT
# ==========================================

if st.button("🚨 Simulate New Incident"):

    # Cycle through all four priority levels for the demo.
    # priority.py remains unchanged.
    demo_profiles = [
        {
            "priority_target": "MEDIUM",
            "severity": 55,
            "exposure": 50,
            "vulnerability": 45,
            "evidence": "Floodwater is affecting the area"
        },
        {
            "priority_target": "HIGH",
            "severity": 70,
            "exposure": 65,
            "vulnerability": 60,
            "evidence": "Heavy flooding reported, people affected"
        },
        {
            "priority_target": "CRITICAL",
            "severity": 95,
            "exposure": 90,
            "vulnerability": 85,
            "evidence": "People are trapped and immediate rescue is required"
        },
        {
            "priority_target": "LOW",
            "severity": 30,
            "exposure": 25,
            "vulnerability": 25,
            "evidence": "Minor floodwater reported in the area"
        }
    ]

    if "demo_priority_index" not in st.session_state:
        st.session_state.demo_priority_index = 0

    demo = demo_profiles[
        st.session_state.demo_priority_index % len(demo_profiles)
    ]
    st.session_state.demo_priority_index += 1

    # Reuse Nikhil's existing YOLO outputs.
    selected_yolo = YOLO_PROFILES[
        st.session_state.demo_priority_index % len(YOLO_PROFILES)
    ]

    # Create a unique incident ID.
    new_id = f"INC{random.randint(100, 999)}"

    existing_ids = set(
        st.session_state.data["incident_id"].astype(str)
    )

    while new_id in existing_ids:
        new_id = f"INC{random.randint(100, 999)}"

    new_evidence = demo["evidence"]
    new_base_urgency = calculate_urgency(new_evidence)

    new_incident = {
        "incident_id": new_id,
        "disaster_type": "Flood",
        "severity": demo["severity"],
        "evidence": new_evidence,

        "location": random.choice([
            "Electronic City",
            "Whitefield",
            "Peenya",
            "Kengeri",
            "Bommanahalli"
        ]),

        "latitude": round(
            random.uniform(12.85, 13.05), 4
        ),

        "longitude": round(
            random.uniform(77.45, 77.75), 4
        ),

        "population_exposed": random.randint(
            1000, 8000
        ),

        "exposure": demo["exposure"],
        "vulnerability": demo["vulnerability"],
        "base_urgency": new_base_urgency,

        # Existing Nikhil YOLO/CV evidence.
        "person_count": selected_yolo["person_count"],
        "car_count": selected_yolo["car_count"],
        "boat_count": selected_yolo["boat_count"],
        "cv_severity": selected_yolo["cv_severity"],
        "yolo_image": selected_yolo["yolo_image"]
    }

    st.session_state.data = pd.concat(
        [
            st.session_state.data,
            pd.DataFrame([new_incident])
        ],
        ignore_index=True
    )

    st.rerun()


# ==========================================

# CURRENT DATA

# ==========================================



data = st.session_state.data





# ==========================================

# CALCULATE CV ADJUSTMENT

# ==========================================



data[

    "cv_adjustment"

] = data.apply(

    calculate_cv_adjustment,

    axis=1

)





# ==========================================

# CALCULATE FINAL URGENCY

# ==========================================



data[

    "urgency"

] = (

    data["base_urgency"]

    + data["cv_adjustment"]

).clip(

    upper=100

)





# ==========================================

# CALCULATE PRIORITY

# ==========================================



data[

    "priority_score"

] = data.apply(



    lambda row:

        calculate_priority(



            row["severity"],



            row["exposure"],



            row["vulnerability"],



            row["urgency"]



        ),



    axis=1



)





data[

    "priority"

] = data[

    "priority_score"

].apply(

    get_priority_level

)





# ==========================================

# DASHBOARD SUMMARY

# ==========================================



critical = len(

    data[

        data["priority"]

        == "CRITICAL"

    ]

)



high = len(

    data[

        data["priority"]

        == "HIGH"

    ]

)



medium = len(

    data[

        data["priority"]

        == "MEDIUM"

    ]

)



low = len(

    data[

        data["priority"]

        == "LOW"

    ]

)





col1, col2, col3, col4 = st.columns(4)





col1.metric(

    "🚨 Active Incidents",

    len(data)

)



col2.metric(

    "🔴 Critical",

    critical

)



col3.metric(

    "🟠 High",

    high

)



col4.metric(

    "🟡 Medium",

    medium

)





# ==========================================

# INCIDENT & EXPOSURE MAP

# ==========================================



st.header(

    "🗺️ Incident & Exposure Map"

)





incident_options = data[
    "incident_id"
].tolist()


# Keep the dropdown as a normal incident selector.
selected_incident_id = st.selectbox(
    "🔎 Select Incident",
    incident_options
)


selected_incident = data[
    data["incident_id"]
    == selected_incident_id
].iloc[0]


# ==========================================

# MAP COLORS

# ==========================================



def get_marker_color(priority):



    if priority == "CRITICAL":

        return [255, 0, 0]



    elif priority == "HIGH":

        return [255, 140, 0]



    elif priority == "MEDIUM":

        return [255, 200, 0]



    else:

        return [0, 180, 0]





map_data = data.copy()





map_data[

    "color"

] = map_data[

    "priority"

].apply(

    get_marker_color

)





map_data[

    "radius"

] = map_data[

    "incident_id"

].apply(



    lambda x:



        1000



        if x == selected_incident_id



        else 500



)





# ==========================================

# PYDECK MAP

# ==========================================



layer = pdk.Layer(



    "ScatterplotLayer",



    data=map_data,



    get_position=[

        "longitude",

        "latitude"

    ],



    get_fill_color="color",



    get_radius="radius",



    pickable=True,



    auto_highlight=True



)





view_state = pdk.ViewState(



    latitude=

        selected_incident[

            "latitude"

        ],



    longitude=

        selected_incident[

            "longitude"

        ],



    zoom=11



)





deck = pdk.Deck(



    layers=[layer],



    initial_view_state=view_state,



    tooltip={



        "text":

            "Incident: {incident_id}\n"

            "Type: {disaster_type}\n"

            "Priority: {priority}\n"

            "Score: {priority_score}\n"

            "Urgency: {urgency}\n"

            "CV Severity: {cv_severity}\n"

            "YOLO Image: {yolo_image}\n"

            "Location: {location}"



    }



)





# Clicking an incident marker selects that incident.
# The selected incident is then used for the map view and details below.
map_event = st.pydeck_chart(
    deck,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-object"
)

if map_event and map_event.selection:
    selected_objects = map_event.selection.get("objects", [])

    if selected_objects:
        clicked_id = selected_objects[0].get("incident_id")

        if clicked_id and clicked_id in incident_options:
            selected_incident_id = clicked_id

            selected_incident = data[
                data["incident_id"] == selected_incident_id
            ].iloc[0]

            # Rebuild the map view around the clicked incident.
            st.rerun()





# ==========================================

# SELECTED INCIDENT DETAILS

# ==========================================



st.header(

    "📋 Selected Incident"

)





col1, col2 = st.columns(2)





# ==========================================

# INCIDENT INFORMATION

# ==========================================



with col1:



    st.subheader(



        f"{selected_incident['incident_id']}"

        f" — "

        f"{selected_incident['disaster_type']}"



    )



    st.write(

        f"📍 Location: "

        f"{selected_incident['location']}"

    )



    st.write(

        f"🎯 Priority Score: "

        f"**{selected_incident['priority_score']}**"

    )



    st.write(

        f"🚨 Priority Level: "

        f"**{selected_incident['priority']}**"

    )



    st.write(

        f"Severity: "

        f"**{selected_incident['severity']}**"

    )



    st.write(

        f"Exposure: "

        f"**{selected_incident['exposure']}**"

    )



    st.write(

        f"👥 Population Exposed: "

        f"**{selected_incident['population_exposed']}**"

    )



    st.write(

        f"Vulnerability: "

        f"**{selected_incident['vulnerability']}**"

    )



    st.write(

        f"Base Urgency: "

        f"**{selected_incident['base_urgency']}**"

    )



    st.write(

        f"🤖 CV Adjustment: "

        f"**+{selected_incident['cv_adjustment']}**"

    )



    st.write(

        f"⚡ Final Urgency: "

        f"**{selected_incident['urgency']}**"

    )





# ==========================================

# COMPUTER VISION EVIDENCE

# ==========================================



with col2:



    st.subheader(

        "🤖 Computer Vision Evidence"

    )



    person_count = selected_incident.get(

        "person_count",

        0

    )



    car_count = selected_incident.get(

        "car_count",

        0

    )



    boat_count = selected_incident.get(

        "boat_count",

        0

    )



    cv_severity = selected_incident.get(

        "cv_severity",

        "N/A"

    )



    yolo_image_name = selected_incident.get(

        "yolo_image",

        "N/A"

    )



    st.write(

        f"👤 Persons Detected: "

        f"**{person_count}**"

    )



    st.write(

        f"🚗 Cars Detected: "

        f"**{car_count}**"

    )



    st.write(

        f"🚤 Boats Detected: "

        f"**{boat_count}**"

    )



    st.write(

        f"🧠 CV Severity: "

        f"**{cv_severity}**"

    )



    st.write(

        f"📈 CV Urgency Adjustment: "

        f"**+{selected_incident['cv_adjustment']}**"

    )



    st.write(

        f"🖼️ YOLO Image: "

        f"**{yolo_image_name}**"

    )



    st.write(

        f"📝 Evidence: "

        f"**{selected_incident['evidence']}**"

    )





# ==========================================

# YOLO DETECTION IMAGE

# ==========================================



st.subheader(

    "📸 YOLO Detection Result"

)





BASE_DIR = Path(

    __file__

).resolve().parent





OUTPUT_DIR = (

    BASE_DIR / "output"

)





# ------------------------------------------

# Get image assigned to selected incident

# ------------------------------------------



selected_yolo_image = selected_incident.get(

    "yolo_image",

    None

)





if pd.isna(selected_yolo_image):



    selected_yolo_image = None





if selected_yolo_image:



    image_path = (

        OUTPUT_DIR

        / str(selected_yolo_image)

    )





    if image_path.is_file():



        st.image(



            str(image_path),



            caption=(

                f"YOLO Detection — "

                f"{selected_incident_id}"

                f" — "

                f"{selected_yolo_image}"

            ),



            use_container_width=True



        )



    else:



        st.error(

            "YOLO image could not be found."

        )



        st.write(

            f"Expected: "

            f"{image_path}"

        )





else:



    st.info(

        "No YOLO detection image "

        "assigned to this incident."

    )





# ==========================================

# TOP PRIORITY INCIDENT

# ==========================================



top_incident = data.sort_values(



    "priority_score",



    ascending=False



).iloc[0]





st.header(

    "🚨 Top Priority Incident"

)





col1, col2 = st.columns(2)





with col1:



    st.subheader(



        f"{top_incident['incident_id']}"

        f" — "

        f"{top_incident['disaster_type']}"



    )



    st.write(

        f"📍 Location: "

        f"{top_incident['location']}"

    )



    st.write(

        f"🎯 Priority Score: "

        f"**{top_incident['priority_score']}**"

    )



    st.write(

        f"🚨 Priority Level: "

        f"**{top_incident['priority']}**"

    )





with col2:



    st.write(

        f"Severity: "

        f"**{top_incident['severity']}**"

    )



    st.write(

        f"Exposure: "

        f"**{top_incident['exposure']}**"

    )



    st.write(

        f"👥 Population Exposed: "

        f"**{top_incident['population_exposed']}**"

    )



    st.write(

        f"Vulnerability: "

        f"**{top_incident['vulnerability']}**"

    )



    st.write(

        f"Base Urgency: "

        f"**{top_incident['base_urgency']}**"

    )



    st.write(

        f"🤖 CV Adjustment: "

        f"**+{top_incident['cv_adjustment']}**"

    )



    st.write(

        f"⚡ Final Urgency: "

        f"**{top_incident['urgency']}**"

    )



    st.write(

        f"Evidence: "

        f"**{top_incident['evidence']}**"

    )



    st.write(

        f"🤖 CV Severity: "

        f"**{top_incident.get('cv_severity', 'N/A')}**"

    )



    st.write(

        f"👤 Persons: "

        f"**{top_incident.get('person_count', 0)}**"

    )



    st.write(

        f"🚗 Cars: "

        f"**{top_incident.get('car_count', 0)}**"

    )



    st.write(

        f"🚤 Boats: "

        f"**{top_incident.get('boat_count', 0)}**"

    )



    st.write(

        f"🖼️ YOLO Image: "

        f"**{top_incident.get('yolo_image', 'N/A')}**"

    )