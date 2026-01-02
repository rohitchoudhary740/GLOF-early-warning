import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="GLOF Early Warning System", layout="wide")

st.title("🌊 GLOF Early Warning System")
st.caption("Jal Shakti Hackathon | Chamoli Case Study")

ndwi1 = np.load("data/ndwi_t1.npy")
ndwi2 = np.load("data/ndwi_t2.npy")
mask = np.load("data/lake_mask.npy")

area1 = (ndwi1 > 0.1).sum() * 100 / 1e6
area2 = mask.sum() * 100 / 1e6
change = ((area2 - area1) / area1) * 100

if change < 3:
    risk = "LOW"
elif change < 8:
    risk = "MEDIUM"
else:
    risk = "HIGH"

if st.button("🚨 Run GLOF Early Warning Analysis"):

    col1, col2, col3 = st.columns(3)
    col1.metric("Lake Area T1 (km²)", f"{area1:.3f}")
    col2.metric("Lake Area T2 (km²)", f"{area2:.3f}")
    col3.metric("Change (%)", f"{change:.2f}")

    st.subheader("NDWI Maps")
    st.image(Image.open("data/ndwi_t1.png"), caption="NDWI T1")
    st.image(Image.open("data/ndwi_t2.png"), caption="NDWI T2")

    st.subheader("Detected Glacial Lake")
    st.image(Image.open("data/lake_mask.png"))

    st.subheader("🚨 Early Warning")
    if risk == "HIGH":
        st.error("HIGH GLOF RISK – Evacuate downstream areas and move livestock.")
    elif risk == "MEDIUM":
        st.warning("MEDIUM RISK – Increase monitoring and preparedness.")
    else:
        st.success("LOW RISK – Normal monitoring.")
