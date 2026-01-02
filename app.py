import streamlit as st
import numpy as np
from PIL import Image

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(page_title="GLOF Early Warning System", layout="wide")

st.title("🌊 GLOF Early Warning System")
st.caption("Jal Shakti Hackathon | Chamoli Case Study")

# ---------------------------------
# INPUT OPTIONS (VISIBLE UI)
# ---------------------------------
st.header("Input Selection")

mode = st.radio(
    "Choose analysis mode:",
    ["Select Demo Lake (Chamoli)", "Upload Preprocessed Data"]
)

# ---------------------------------
# LOAD DATA FUNCTIONS
# ---------------------------------
def load_demo_data():
    ndwi1 = np.load("data/ndwi_t1.npy")
    ndwi2 = np.load("data/ndwi_t2.npy")
    mask = np.load("data/lake_mask.npy")
    return ndwi1, ndwi2, mask

def load_uploaded_data(files):
    ndwi1 = np.load(files["ndwi_t1"])
    ndwi2 = np.load(files["ndwi_t2"])
    mask = np.load(files["lake_mask"])
    return ndwi1, ndwi2, mask

# ---------------------------------
# INPUT HANDLING
# ---------------------------------
if mode == "Select Demo Lake (Chamoli)":
    st.success("Demo lake selected: Chamoli (preloaded data)")
    ndwi1, ndwi2, mask = load_demo_data()

else:
    st.info("Upload preprocessed data files (.npy)")
    f1 = st.file_uploader("Upload NDWI T1 (.npy)", type="npy")
    f2 = st.file_uploader("Upload NDWI T2 (.npy)", type="npy")
    f3 = st.file_uploader("Upload Lake Mask (.npy)", type="npy")

    if f1 and f2 and f3:
        ndwi1 = np.load(f1)
        ndwi2 = np.load(f2)
        mask = np.load(f3)
    else:
        st.warning("Please upload all three files.")
        st.stop()

# ---------------------------------
# ANALYSIS
# ---------------------------------
if st.button("🚨 Run GLOF Early Warning Analysis"):

    pixel_area = 100  # 10m x 10m
    area1 = (ndwi1 > 0.1).sum() * pixel_area / 1e6
    area2 = mask.sum() * pixel_area / 1e6
    change = ((area2 - area1) / area1) * 100

    if change < 3:
        risk = "LOW"
    elif change < 8:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # ---------------------------------
    # RESULTS
    # ---------------------------------
    st.header("Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Lake Area T1 (km²)", f"{area1:.3f}")
    c2.metric("Lake Area T2 (km²)", f"{area2:.3f}")
    c3.metric("Change (%)", f"{change:.2f}")

    st.subheader("NDWI Maps")
    st.image(Image.open("data/ndwi_t1.png"), caption="NDWI – T1")
    st.image(Image.open("data/ndwi_t2.png"), caption="NDWI – T2")

    st.subheader("Detected Glacial Lake")
    st.image(Image.open("data/lake_mask.png"))

    # ---------------------------------
    # EARLY WARNING
    # ---------------------------------
    st.subheader("🚨 Early Warning & Decision Support")

    if risk == "HIGH":
        st.error(
            "HIGH GLOF RISK\n\n"
            "• Prepare downstream evacuation\n"
            "• Move livestock to higher ground\n"
            "• Restrict river-side activities"
        )
    elif risk == "MEDIUM":
        st.warning(
            "MEDIUM GLOF RISK\n\n"
            "• Increase monitoring\n"
            "• Alert local authorities"
        )
    else:
        st.success("LOW RISK – Normal monitoring recommended.")
