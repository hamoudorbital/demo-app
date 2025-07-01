import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import random
import string
from datetime import datetime
from t_utils import (
    generate_constellation_tle,
    create_constellation_plots,
    generate_tle_file_content,
    create_validation_report
)

# Function to generate random constellation name
def generate_random_constellation_name():
    """Generate a random constellation name"""
    prefixes = ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "THETA", "LAMBDA", 
                "SIGMA", "OMEGA", "PHOENIX", "ORION", "VEGA", "NOVA", "STELLAR", "COSMIC",
                "NEXUS", "QUANTUM", "PULSAR", "NEBULA", "ASTRO", "CELESTIAL", "ORBITAL"]
    suffixes = ["SAT", "NET", "LINK", "GRID", "MESH", "CONNECT", "COMM", "SYSTEM", 
                "CONSTELLATION", "NETWORK", "CLUSTER", "ARRAY", "FLEET"]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    number = random.randint(1, 999)
    
    return f"{prefix}_{suffix}_{number}"

# Function to generate random parameters
def get_random_parameters():
    """Generate random but realistic constellation parameters"""
    # Random altitude between 400-1200 km (typical LEO range)
    altitude = random.randint(40, 120) * 10  # 400-1200 in steps of 10
    
    # Random inclination - common values
    inclinations = [28.5, 45.0, 53.0, 63.4, 70.0, 85.0, 97.4]  # Common orbital inclinations
    inclination = random.choice(inclinations)
    
    # Random number of planes (reasonable for different constellation sizes)
    plane_options = [6, 8, 12, 18, 24, 36, 48, 72, 96, 120, 144, 180, 216, 288]
    num_planes = random.choice(plane_options)
    
    # Random satellites per plane (1-20 is reasonable)
    sats_per_plane = random.randint(1, 20)
    
    # Random Walker F parameter (usually smaller than total satellites)
    total_sats = num_planes * sats_per_plane
    walker_F = random.randint(1, min(total_sats, 500))
    
    return altitude, inclination, num_planes, sats_per_plane, walker_F

# Password protection
def check_password():
    """Returns True if password is correct"""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "SUN2025":  # Change this password
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.markdown("### 🛰️ TLE Constellation Generator")
        st.markdown("Enter password to access the application:")
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )

        st.info("💡 **For team members**: Contact admin for access password")
        return False

    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.markdown("### 🛰️ TLE Constellation Generator")
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😞 Password incorrect. Please try again.")
        return False

    else:
        # Password correct
        return True

def main():
    """Main application"""

    # Check password first
    if not check_password():
        return

    # Initialize random parameters if not already set
    if 'random_params_set' not in st.session_state:
        rand_alt, rand_inc, rand_planes, rand_sats, rand_f = get_random_parameters()
        st.session_state.rand_altitude = rand_alt
        st.session_state.rand_inclination = rand_inc
        st.session_state.rand_num_planes = rand_planes
        st.session_state.rand_sats_per_plane = rand_sats
        st.session_state.rand_walker_F = rand_f
        st.session_state.constellation_name = generate_random_constellation_name()
        st.session_state.random_params_set = True

    # App header
    st.set_page_config(
        page_title="TLE Constellation Generator",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🛰️ TLE Constellation Generator")
    st.markdown("Generate Two-Line Element (TLE) files for Walker satellite constellations")

    # Sidebar for parameters
    st.sidebar.header("Constellation Parameters")
    
    # Add randomize button
    if st.sidebar.button("🎲 Randomize Parameters"):
        rand_alt, rand_inc, rand_planes, rand_sats, rand_f = get_random_parameters()
        st.session_state.rand_altitude = rand_alt
        st.session_state.rand_inclination = rand_inc
        st.session_state.rand_num_planes = rand_planes
        st.session_state.rand_sats_per_plane = rand_sats
        st.session_state.rand_walker_F = rand_f
        st.session_state.constellation_name = generate_random_constellation_name()
        st.rerun()

    # Input widgets with random defaults
    altitude = st.sidebar.slider(
        "Altitude (km)",
        min_value=200,
        max_value=2000,
        value=st.session_state.rand_altitude,
        step=10,
        help="Satellite orbital altitude above Earth's surface"
    )

    inclination = st.sidebar.slider(
        "Inclination (degrees)",
        min_value=0.0,
        max_value=180.0,
        value=st.session_state.rand_inclination,
        step=0.1,
        help="Orbital inclination angle"
    )

    num_planes = st.sidebar.number_input(
        "Number of Orbital Planes",
        min_value=1,
        max_value=500,
        value=st.session_state.rand_num_planes,
        step=1,
        help="Total number of orbital planes in the constellation"
    )

    sats_per_plane = st.sidebar.number_input(
        "Satellites per Plane",
        min_value=1,
        max_value=50,
        value=st.session_state.rand_sats_per_plane,
        step=1,
        help="Number of satellites in each orbital plane"
    )

    walker_F = st.sidebar.number_input(
        "Walker F Parameter",
        min_value=0,
        max_value=1000,
        value=st.session_state.rand_walker_F,
        step=1,
        help="Walker constellation phasing factor"
    )

    # Display current constellation name
    st.sidebar.markdown(f"**Constellation Name:** `{st.session_state.constellation_name}`")

    # Generate button
    if st.sidebar.button("🚀 Generate Constellation", type="primary"):
        st.session_state.generate_constellation = True

    # Information section
    with st.sidebar.expander("ℹ️ About Walker Constellations"):
        st.markdown("""
        **Walker constellations** are characterized by three parameters:
        - **T**: Total number of satellites
        - **P**: Number of orbital planes
        - **F**: Phasing factor

        The notation is T/P/F (e.g., 1584/72/22)

        **Key Features:**
        - Even satellite distribution
        - Optimized global coverage
        - Reduced coverage gaps
        """)

    # Main content area
    if hasattr(st.session_state, 'generate_constellation') and st.session_state.generate_constellation:

        # Calculate total satellites
        total_sats = num_planes * sats_per_plane

        # Show constellation info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Satellites", total_sats)
        with col2:
            st.metric("Orbital Planes", num_planes)
        with col3:
            st.metric("Walker Notation", f"{total_sats}/{num_planes}/{walker_F}")
        with col4:
            orbital_period = 2 * np.pi * np.sqrt((6378.137 + altitude)**3 / 398600.4418) / 60
            st.metric("Orbital Period", f"{orbital_period:.1f} min")

        # Generate constellation
        with st.spinner("Generating constellation TLE data..."):
            try:
                tle_lines, constellation_data = generate_constellation_tle(
                    altitude, inclination, num_planes, sats_per_plane, walker_F
                )

                # Create tabs for different outputs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualization", "📄 TLE Data", "📋 Report", "📈 Statistics"])

                with tab1:
                    st.subheader("Constellation Visualization")

                    # Generate and display plots
                    fig = create_constellation_plots(constellation_data)
                    st.pyplot(fig)

                    # Download plot
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    st.download_button(
                        label="📥 Download Plots (PNG)",
                        data=buf.getvalue(),
                        file_name=f"{st.session_state.constellation_name}_plots.png",
                        mime="image/png"
                    )

                with tab2:
                    st.subheader("Generated TLE Data")

                    # Show first few TLE entries as preview
                    st.markdown("**Preview (first 5 satellites):**")
                    preview_lines = tle_lines[:15]  # 5 satellites * 3 lines each
                    st.code('\n'.join(preview_lines), language='text')

                    # Download TLE file with random name
                    tle_content = generate_tle_file_content(tle_lines)
                    st.download_button(
                        label="📥 Download Complete TLE File (.txt)",
                        data=tle_content,
                        file_name=f"{st.session_state.constellation_name}_{total_sats}sats.txt",
                        mime="text/plain"
                    )

                    st.info(f"📊 Generated {total_sats} satellites across {num_planes} orbital planes")

                with tab3:
                    st.subheader("Validation Report")

                    report = create_validation_report(constellation_data)
                    st.text(report)

                    # Download report with random name
                    st.download_button(
                        label="📥 Download Report (.txt)",
                        data=report,
                        file_name=f"{st.session_state.constellation_name}_report.txt",
                        mime="text/plain"
                    )

                with tab4:
                    st.subheader("Satellite Statistics")

                    # Create DataFrame from satellite data
                    df = pd.DataFrame(constellation_data['satellite_data'])

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**RAAN Distribution:**")
                        raan_stats = df['raan'].describe()
                        st.dataframe(raan_stats)

                        st.markdown("**Mean Anomaly Distribution:**")
                        ma_stats = df['mean_anomaly'].describe()
                        st.dataframe(ma_stats)

                    with col2:
                        st.markdown("**Satellites by Plane:**")
                        plane_counts = df['plane'].value_counts().sort_index()
                        st.dataframe(plane_counts.head(10))

                        st.markdown("**Sample Satellite Data:**")
                        st.dataframe(df[['name', 'plane', 'norad_id', 'raan', 'mean_anomaly']].head(10))

                    # Full data download with random name
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Full Satellite Data (.csv)",
                        data=csv_data,
                        file_name=f"{st.session_state.constellation_name}_data.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error generating constellation: {str(e)}")
                st.exception(e)

    else:
        # Landing page
        st.markdown("""
        ### Welcome to the TLE Constellation Generator! 🛰️

        This tool generates **Two-Line Element (TLE)** files for Walker satellite constellations,
        designed to be compatible with **NCAT (Network Coverage Analysis Tool)** and other orbital analysis software.

        #### Key Features:
        - 🎯 **Randomized NORAD IDs** - No duplicate satellite identifiers
        - 🚀 **Diverse Launch Info** - Realistic launch years, numbers, and pieces
        - 📊 **Interactive Visualizations** - RAAN/MA distribution and ground track patterns
        - 📄 **Multiple Export Formats** - TLE files, reports, and CSV data
        - ✅ **NCAT Compatible** - Proper formatting with CR+LF line endings
        - 🎲 **Random Parameters** - Starts with randomized constellation parameters

        #### How to Use:
        1. **Review random parameters** in the sidebar (or click "Randomize" for new ones)
        2. **Adjust parameters** as needed (altitude, inclination, planes, etc.)
        3. **Click "Generate Constellation"** to create your TLE data
        4. **Download files** for use in NCAT or other tools

        #### Parameter Guidelines:
        - **Altitude**: 200-2000 km (400-1200 km is typical for LEO constellations)
        - **Inclination**: Common values: 28.5°, 45°, 53°, 63.4°, 97.4°
        - **Planes**: More planes = better coverage but higher complexity
        - **Sats per plane**: Balance between coverage and cost
        - **Walker F**: Phasing factor for optimal satellite distribution

        **Ready to start?** Check the random parameters in the sidebar and click Generate! 🚀
        """)

        # Add some example constellations
        st.markdown("### Example Configurations:")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("""
            **Starlink-like**
            📊 1584/72/22
            ✈️ 550 km altitude
            📐 53° inclination
            """)

        with col2:
            st.info("""
            **Small Test**
            📊 24/12/5
            ✈️ 500 km altitude
            📐 45° inclination
            """)
            
        with col3:
            st.info("""
            **Medium Constellation**
            📊 288/36/50
            ✈️ 800 km altitude
            📐 70° inclination
            """)

if __name__ == "__main__":
    main()
