import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import tempfile

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GLOF Early Warning System",
    layout="wide"
)

st.title("🌊 GLOF Early Warning System")
st.caption("Jal Shakti Hackathon | Chamoli Case Study")

# -----------------------------
# INPUT MODE
# -----------------------------
st.header("Input Selection")

mode = st.radio(
    "Choose Input Method",
    ["Select Demo Lake (Chamoli)", "Upload Sentinel-2 Images"]
)

# -----------------------------
# FUNCTIONS
# -----------------------------
def load_green_nir(path):
    """
    Load Green and NIR bands from Sentinel TIFF using tifffile
    Expected shape: (bands, height, width)
    """
    img = tiff.imread(path)

    if img.ndim != 3 or img.shape[0] < 2:
        raise ValueError("Invalid Sentinel TIFF format")

    green = img[0].astype("float32")
    nir = img[1].astype("float32")

    return green, nir

def compute_ndwi(green, nir):
    return (green - nir) / (green + nir + 1e-6)

def analyze_glof(img1, img2):
    green_t1, nir_t1 = load_green_nir(img1)
    green_t2, nir_t2 = load_green_nir(img2)

    ndwi_t1 = compute_ndwi(green_t1, nir_t1)
    ndwi_t2 = compute_ndwi(green_t2, nir_t2)

    threshold = 0.10
    mask_t1 = ndwi_t1 > threshold
    mask_t2 = ndwi_t2 > threshold

    pixel_area = 10 * 10  # Sentinel-2 resolution
    area_t1 = mask_t1.sum() * pixel_area / 1e6
    area_t2 = mask_t2.sum() * pixel_area / 1e6

    change = ((area_t2 - area_t1) / area_t1) * 100

    if change < 3:
        risk = "LOW"
    elif change < 8:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return ndwi_t1, ndwi_t2, mask_t2, area_t1, area_t2, change, risk

# -----------------------------
# INPUT HANDLING
# -----------------------------
if mode == "Select Demo Lake (Chamoli)":
    st.success("Demo lake selected: Chamoli")

    image_t1 = "data/Chamoli_Sentinel_T1.tif"
    image_t2 = "data/Chamoli_Sentinel_T2.tif"

else:
    uploaded_t1 = st.file_uploader("Upload Sentinel T1 (.tif)", type=["tif"])
    uploaded_t2 = st.file_uploader("Upload Sentinel T2 (.tif)", type=["tif"])

    if uploaded_t1 and uploaded_t2:
        tmp1 = tempfile.NamedTemporaryFile(delete=False)
        tmp1.write(uploaded_t1.read())

        tmp2 = tempfile.NamedTemporaryFile(delete=False)
        tmp2.write(uploaded_t2.read())

        image_t1 = tmp1.name
        image_t2 = tmp2.name
    else:
        st.warning("Please upload both Sentinel images.")
        st.stop()

# -----------------------------
# RUN ANALYSIS
# -----------------------------
if st.button("🚨 Run GLOF Early Warning Analysis"):

    with st.spinner("Analyzing satellite data..."):
        ndwi1, ndwi2, lake_mask, a1, a2, change, risk = analyze_glof(
            image_t1, image_t2
        )

    st.header("Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Lake Area T1", f"{a1:.3f} km²")
    col2.metric("Lake Area T2", f"{a2:.3f} km²")
    col3.metric("Change", f"{change:.2f}%")

    st.subheader("🚨 GLOF Risk Level")
    if risk == "HIGH":
        st.error(risk)
    elif risk == "MEDIUM":
        st.warning(risk)
    else:
        st.success(risk)

    st.subheader("NDWI Comparison")
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].imshow(ndwi1, cmap="Blues", vmin=-0.2, vmax=0.4)
    ax[0].set_title("NDWI - T1")
    ax[1].imshow(ndwi2, cmap="Blues", vmin=-0.2, vmax=0.4)
    ax[1].set_title("NDWI - T2")
    for a in ax:
        a.axis("off")
    st.pyplot(fig)

    st.subheader("Detected Glacial Lake (T2)")
    st.image(lake_mask.astype(int), clamp=True)

    st.header("Early Warning & Decision Support")

    if risk == "HIGH":
        st.error(
            "⚠️ HIGH GLOF RISK DETECTED\n\n"
            "• Prepare downstream evacuation\n"
            "• Move livestock to higher ground\n"
            "• Restrict river-side activities"
        )
    elif risk == "MEDIUM":
        st.warning(
            "⚠️ MEDIUM RISK\n\n"
            "• Increase monitoring\n"
            "• Alert local authorities"
        )
    else:
        st.info("LOW RISK – Normal monitoring recommended.")
