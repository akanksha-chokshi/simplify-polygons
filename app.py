import streamlit as st
import geopandas as gpd
import os

def simplify_geometries(gdf, tolerance=0.01):
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

def save_to_geojson(gdf, filename):
    gdf.to_file(filename, driver='GeoJSON')

def recommend_tolerance(gdf):
    gdf_projected = gdf.to_crs(epsg=3857)
    avg_area = gdf_projected['geometry'].area.mean()
    recommended_tolerance = avg_area ** 0.5 * 0.01  
    return recommended_tolerance


st.title("GeoJSON Polygon Simplification Tool")

uploaded_file = st.file_uploader("Upload your GeoJSON file", type="geojson")

if uploaded_file:
    original_filename = os.path.splitext(uploaded_file.name)[0]
    gdf = gpd.read_file(uploaded_file)
    
    recommended_tolerance = recommend_tolerance(gdf)
    st.info(f"Recommended Tolerance: {recommended_tolerance:.2f} m")

    simplify_option = st.radio(
        "Choose an option to simplify:",
        ('Simplify with Recommended Threshold', 'Simplify with Custom Threshold')
    )

    if simplify_option == 'Simplify with Custom Threshold':
        tolerance = st.number_input(
            "Simplification Tolerance (in metres)", 
            min_value=0.01, 
            max_value=100.00, 
            value=1.00, 
            step=0.1
        )
    else:
        tolerance = recommended_tolerance

    if st.button("Simplify"):
        simplified_gdf = simplify_geometries(gdf, tolerance)
        
        st.success("Simplification has been performed.")
        
        simplified_geojson = f"simplified_{original_filename}.geojson"
        save_to_geojson(simplified_gdf, simplified_geojson)
        
        with open(simplified_geojson, "rb") as f:
            st.download_button("Download Simplified GeoJSON", f, file_name=simplified_geojson)
else:
    st.info("Please upload a GeoJSON file to begin.")
