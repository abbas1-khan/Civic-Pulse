import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import st_folium
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Awaz Map - Civic Reporting",
    page_icon="🗺️",
    layout="wide"
)

# ==========================================
# 2. CNIC CITY MAPPING LOGIC
# ==========================================
# Pakistani CNIC First 5 Digits District Mapping Examples
CNIC_CITY_MAP = {
    "41304": {"city": "Hyderabad", "coords": [25.3960, 68.3578], "group": "Hyderabad Civic Group"},
    "41303": {"city": "Hyderabad", "coords": [25.3960, 68.3578], "group": "Hyderabad Civic Group"},
    "42101": {"city": "Karachi", "coords": [24.8607, 67.0011], "group": "Karachi Central Group"},
    "42201": {"city": "Karachi", "coords": [24.8607, 67.0011], "group": "Karachi East Group"},
    "35202": {"city": "Lahore", "coords": [31.5204, 74.3587], "group": "Lahore Metropolitan Group"},
    "61101": {"city": "Islamabad", "coords": [33.6844, 73.0479], "group": "Capital Area Group"}
}

def get_city_from_cnic(cnic_str):
    """Extract first 5 digits and return city info"""
    clean_cnic = cnic_str.replace("-", "").strip()
    prefix = clean_cnic[:5]
    if prefix in CNIC_CITY_MAP:
        return CNIC_CITY_MAP[prefix]
    else:
        # Default fallback if unknown code
        return {"city": "General / National", "coords": [25.3960, 68.3578], "group": "National Civic Forum"}

# ==========================================
# 3. USER AUTHENTICATION & LOGIN GATEWAY
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_name"] = ""
    st.session_state["user_cnic"] = ""
    st.session_state["user_city_info"] = None

if not st.session_state["authenticated"]:
    st.title("🗺️ Awaz Map - Welcome")
    st.subheader("Your Voice, Your City")
    st.caption("Made by Jari Abbas, Daniyal Ahmed, Yasir Hakro")
    st.info("Enter your full name and CNIC to report civic issues and join your city's official group.")

    with st.form("login_form"):
        name_input = st.text_input("Your Name (Full Name)", placeholder="e.g. Jari Abbas")
        cnic_input = st.text_input("CNIC Number (13 Digits)", placeholder="e.g. 41304-1234567-1")
        submit_btn = st.form_submit_button("Enter Awaz Map 🚀")

        if submit_btn:
            if len(cnic_input.replace("-", "").strip()) >= 5 and name_input.strip():
                city_info = get_city_from_cnic(cnic_input)
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = name_input
                st.session_state["user_cnic"] = cnic_input
                st.session_state["user_city_info"] = city_info
                st.rerun()
            else:
                st.error("Please enter a valid name and at least the first 5 digits of your CNIC number.")
    st.stop()

# ==========================================
# 4. MAIN APPLICATION DASHBOARD
# ==========================================
user_name = st.session_state["user_name"]
city_data = st.session_state["user_city_info"]

# Sidebar Profile Header
st.sidebar.title(f"👤 Welcome, {user_name}!")
st.sidebar.success(f"📍 Detected City: **{city_data['city']}**")
st.sidebar.info(f"💬 Joined Group: **{city_data['group']}**")

# API Keys Input Option (In Sidebar)
st.sidebar.markdown("---")
api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Enter your Gemini API Key here")

# Navigation Menu
page = st.sidebar.radio("Navigation", ["📸 Report Issue", "🗺️ Live Map", "📊 Progress Tracker", "💬 Official City Chat"])

# Credits Footer in Sidebar
st.sidebar.markdown("---")
st.sidebar.caption("👨‍💻 **Made by:**\nJari Abbas, Daniyal Ahmed, Yasir Hakro")

# Session State for Local Database Simulation
if "reports" not in st.session_state:
    st.session_state["reports"] = [
        {"id": "#101", "category": "Potholes", "city": city_data["city"], "area": "Main Road", "status": "In Progress", "lat": city_data["coords"][0]+0.01, "lon": city_data["coords"][1]+0.01},
        {"id": "#102", "category": "Garbage", "city": city_data["city"], "area": "Sector B", "status": "Pending", "lat": city_data["coords"][0]-0.01, "lon": city_data["coords"][1]-0.01}
    ]

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"user": "Admin", "msg": f"Welcome to {city_data['group']}! You can report and discuss your city's civic issues here."}
    ]

# ==========================================
# PAGE 1: REPORT ISSUE WITH AI DETECTION
# ==========================================
if page == "📸 Report Issue":
    st.header("📸 Report a Civic Problem")
    st.write(f"Reporting directly for the **{city_data['city']}** region.")

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload Image of Issue", type=["jpg", "jpeg", "png"])
        additional_notes = st.text_area("Voice Note Transcript / Extra Comments (Optional)")
        area_name = st.text_input("Specific Area / Landmark", placeholder="e.g. Saddar Main Road")

    with col2:
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
            if st.button("🤖 Analyze with AI & Submit"):
                with st.spinner("AI is analyzing the image..."):
                    
                    ai_result = ""
                    if api_key:
                        try:
                            # Gemini API Integration Code
                            client = genai.Client(api_key=api_key)
                            bytes_data = uploaded_file.getvalue()
                            
                            prompt = """
                            Analyze this civic issue image (Potholes, Drainage, Transformer, Broken Wires, Building Maintenance, Garbage, Public Disturbance).
                            Format output in short bullet points:
                            - Issue Category:
                            - Severity Level: High/Medium/Low
                            - Summary:
                            """
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[prompt, types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type)]
                            )
                            ai_result = response.text
                        except Exception as e:
                            ai_result = f"API Call Error: {e}. Fallback: Pothole / Damaged Road Detected."
                    else:
                        # Fallback Demo AI Output
                        ai_result = "**Detected Issue:** Potholes & Damaged Asphalt\n**Severity:** High\n**Summary:** Multiple road cracks identified."

                    st.success("Issue Successfully Identified & Reported!")
                    st.markdown("### AI Analysis Result")
                    st.write(ai_result)

                    # Save to local records
                    new_id = f"#{len(st.session_state['reports']) + 101}"
                    st.session_state["reports"].append({
                        "id": new_id,
                        "category": "Potholes/Damaged Road",
                        "city": city_data["city"],
                        "area": area_name if area_name else "City Highway",
                        "status": "Pending",
                        "lat": city_data["coords"][0] + 0.005,
                        "lon": city_data["coords"][1] + 0.005
                    })

# ==========================================
# PAGE 2: LIVE INTERACTIVE MAP
# ==========================================
elif page == "🗺️ Live Map":
    st.header(f"🗺️ Live City Map - {city_data['city']}")
    st.write(f"Displaying reported issues in **{city_data['city']}** and connecting highways.")

    # Initialize Folium Map at User's City Coordinates
    m = folium.Map(location=city_data["coords"], zoom_start=13)

    # Add Markers for Reports
    for rep in st.session_state["reports"]:
        color = "red" if rep["status"] == "Pending" else "orange" if rep["status"] == "In Progress" else "green"
        folium.Marker(
            location=[rep["lat"], rep["lon"]],
            popup=f"{rep['id']} - {rep['category']} ({rep['status']})",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)

    st_folium(m, width=1000, height=500)

# ==========================================
# PAGE 3: PROGRESS TRACKER
# ==========================================
elif page == "📊 Progress Tracker":
    st.header("📊 Multi-Tier Progress Tracking")
    
    tab1, tab2, tab3 = st.tabs(["Area Level", "City Level", "City Connecting Highways"])

    df = pd.DataFrame(st.session_state["reports"])

    with tab1:
        st.subheader("📍 Area Level Reports")
        st.dataframe(df[df["city"] == city_data["city"]], use_container_width=True)

    with tab2:
        st.subheader("🏙️ City Level Overview")
        st.metric("Total Active City Issues", len(df))
        st.metric("Pending Repairs", len(df[df["status"] == "Pending"]))

    with tab3:
        st.subheader("🛣️ Highways & Main Connecting Roads")
        st.info("Tracking critical road damages on city connecting routes.")

# ==========================================
# PAGE 4: OFFICIAL CITY GROUP CHAT
# ==========================================
elif page == "💬 Official City Chat":
    st.header(f"💬 Official Group: {city_data['group']}")
    st.caption(f"Connected users for {city_data['city']} civic updates.")

    # Display Chat History
    for chat in st.session_state["chat_messages"]:
        with st.chat_message("user" if chat["user"] == user_name else "assistant"):
            st.write(f"**{chat['user']}**: {chat['msg']}")

    # New Message Input
    user_msg = st.chat_input("Type your update or question...")
    if user_msg:
        st.session_state["chat_messages"].append({"user": user_name, "msg": user_msg})
        st.rerun()