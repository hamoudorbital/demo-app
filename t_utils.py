import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import random
import string

def calculate_checksum(line):
    """Calculate TLE checksum"""
    s = 0
    for char in line[:68]:
        if char.isdigit():
            s += int(char)
        elif char == '-':
            s += 1
    return s % 10

def generate_random_launch_info():
    """Generate random launch year, number, and piece for diversity"""
    # Random launch year (last 5 years)
    current_year = datetime.now().year
    launch_years = list(range(current_year - 4, current_year + 1))
    launch_year = random.choice(launch_years)

    # Random launch number (1-999)
    launch_number = random.randint(1, 999)

    # Random launch piece (A-Z, AA-ZZ pattern)
    pieces = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    pieces.extend([chr(i) + chr(j) for i in range(ord('A'), ord('Z') + 1)
                   for j in range(ord('A'), ord('Z') + 1)])
    launch_piece = random.choice(pieces)

    return launch_year % 100, launch_number, launch_piece

def generate_constellation_tle(altitude, inclination, num_planes, sats_per_plane, walker_F, constellation_name="CONSTELLATION"):
    """
    Generate TLE data for a Walker constellation

    Parameters:
    - altitude: Satellite altitude in km
    - inclination: Orbital inclination in degrees
    - num_planes: Number of orbital planes
    - sats_per_plane: Number of satellites per plane
    - walker_F: Walker F parameter (phasing factor)
    - constellation_name: Name for the constellation satellites

    Returns:
    - tle_lines: List of TLE lines
    - constellation_data: Dictionary with constellation parameters
    """

    # Constants
    Re = 6378.137  # Earth radius (km)
    mu = 398600.4418  # Earth gravitational parameter (km^3/s^2)

    # Calculate orbital parameters
    a = Re + altitude  # semi-major axis (km)
    n = np.sqrt(mu / a**3) * 86400 / (2 * np.pi)  # mean motion (rev/day)
    e = 0.0  # circular orbit
    omega = 0  # argument of perigee (deg)

    # Epoch calculation
    current_date = datetime.now()
    epoch_year = current_date.year % 100
    day_of_year = current_date.timetuple().tm_yday
    hour_fraction = (current_date.hour + current_date.minute/60 +
                    current_date.second/3600) / 24
    epoch_day = day_of_year + hour_fraction

    # Constellation parameters
    total_sats = num_planes * sats_per_plane
    delta_raan = 360 / num_planes
    phase_unit = (walker_F * 360) / total_sats

    # Storage for TLE lines and satellite data
    tle_lines = []
    sat_data = []

    # Generate NORAD IDs starting from random number in 10000-90000 range, then sequential
    base_norad_id = random.randint(10000, 90000)
    
    sat_counter = 0

    for plane in range(num_planes):
        # RAAN for this plane
        raan = (plane * delta_raan) % 360

        # Walker phase offset for this plane
        walker_phase_offset = (plane * phase_unit) % 360

        for sat in range(sats_per_plane):
            # Mean anomaly within the plane
            in_plane_spacing = 360 / sats_per_plane
            M = (sat * in_plane_spacing + walker_phase_offset) % 360

            # Sequential NORAD ID starting from random base
            sat_number = base_norad_id + sat_counter
            launch_year, launch_number, launch_piece = generate_random_launch_info()

            # Clean constellation name (remove special characters, convert to uppercase)
            clean_name = ''.join(c for c in constellation_name if c.isalnum() or c in ['_', '-']).upper()
            
            # Satellite name in format: NAME###-##
            sat_name = f"{clean_name}{plane+1:03d}-{sat+1:02d}"

            # Create epoch string
            epoch_str = f"{epoch_year:02d}{epoch_day:012.8f}"

            # Line 1
            line1_body = (f"1 {sat_number:05d}U {launch_year:02d}"
                         f"{launch_number:03d}{launch_piece:<3s} {epoch_str} "
                         f" .00000000  00000+0  00000-0 0  9999")

            # Ensure exactly 68 characters
            line1_body = line1_body[:68].ljust(68)
            chk1 = calculate_checksum(line1_body)
            line1 = line1_body + str(chk1)

            # Line 2
            line2_body = (f"2 {sat_number:05d} {inclination:8.4f} {raan:8.4f} "
                         f"{int(e*1e7):07d} {omega:8.4f} {M:8.4f} "
                         f"{n:11.8f}    1")

            # Ensure exactly 68 characters
            line2_body = line2_body[:68].ljust(68)
            chk2 = calculate_checksum(line2_body)
            line2 = line2_body + str(chk2)

            # Add to results
            tle_lines.extend([sat_name, line1, line2])

            # Store satellite data for analysis
            sat_data.append({
                'plane': plane + 1,
                'sat': sat + 1,
                'norad_id': sat_number,
                'raan': raan,
                'mean_anomaly': M,
                'name': sat_name
            })

            sat_counter += 1

    # Create constellation data summary
    constellation_data = {
        'total_satellites': total_sats,
        'num_planes': num_planes,
        'sats_per_plane': sats_per_plane,
        'walker_F': walker_F,
        'altitude': altitude,
        'inclination': inclination,
        'mean_motion': n,
        'orbital_period': 1440 / n,  # minutes
        'raan_spacing': delta_raan,
        'phase_unit': phase_unit,
        'epoch_year': epoch_year,
        'epoch_day': epoch_day,
        'satellite_data': sat_data,
        'base_norad_id': base_norad_id
    }

    return tle_lines, constellation_data

def draw_earth_map(ax):
    """Draw a simple Earth map background"""
    
    # Set ocean color (dark blue for better contrast)
    ax.set_facecolor('#003366')
    
    # Draw equator
    ax.axhline(y=0, color='yellow', linestyle='-', alpha=0.7, linewidth=2, label='Equator')
    
    # Draw tropics
    ax.axhline(y=23.5, color='orange', linestyle='--', alpha=0.6, linewidth=1.5, label='Tropic of Cancer')
    ax.axhline(y=-23.5, color='orange', linestyle='--', alpha=0.6, linewidth=1.5, label='Tropic of Capricorn')
    
    # Draw Arctic/Antarctic circles
    ax.axhline(y=66.5, color='cyan', linestyle=':', alpha=0.5, linewidth=1)
    ax.axhline(y=-66.5, color='cyan', linestyle=':', alpha=0.5, linewidth=1)
    
    # Draw prime meridian and international date line
    ax.axvline(x=0, color='white', linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(x=180, color='white', linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(x=-180, color='white', linestyle='--', alpha=0.4, linewidth=1)
    
    # Simple continent representations with better colors
    # North America
    na_lon = [-170, -170, -50, -50, -170]
    na_lat = [70, 15, 15, 70, 70]
    ax.fill(na_lon, na_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # South America
    sa_lon = [-85, -85, -35, -35, -85]
    sa_lat = [12, -55, -55, 12, 12]
    ax.fill(sa_lon, sa_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Europe
    eu_lon = [-15, -15, 70, 70, -15]
    eu_lat = [70, 35, 35, 70, 70]
    ax.fill(eu_lon, eu_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Africa
    af_lon = [-20, -20, 55, 55, -20]
    af_lat = [35, -35, -35, 35, 35]
    ax.fill(af_lon, af_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Asia
    as_lon = [70, 70, 180, 180, 70]
    as_lat = [70, 5, 5, 70, 70]
    ax.fill(as_lon, as_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Australia
    au_lon = [110, 110, 155, 155, 110]
    au_lat = [-10, -45, -45, -10, -10]
    ax.fill(au_lon, au_lat, color='#228B22', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Antarctica (simplified)
    ant_lon = [-180, 180, 180, -180, -180]
    ant_lat = [-60, -60, -90, -90, -60]
    ax.fill(ant_lon, ant_lat, color='white', alpha=0.9, edgecolor='black', linewidth=0.5)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='white')
    
    # Set limits and labels
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel('Longitude (degrees)', color='white')
    ax.set_ylabel('Latitude (degrees)', color='white')
    
    # Set tick colors
    ax.tick_params(colors='white')
    
    # Add major cities for reference
    cities = {
        'New York': (-74, 40.7),
        'London': (0, 51.5),
        'Tokyo': (139.7, 35.7),
        'Sydney': (151.2, -33.9),
        'Cairo': (31.2, 30.0),
        'Sao Paulo': (-46.6, -23.5)
    }
    
    for city, (lon, lat) in cities.items():
        ax.plot(lon, lat, 'o', color='red', markersize=4, alpha=0.8)
        ax.annotate(city, (lon, lat), xytext=(5, 5), textcoords='offset points', 
                   color='white', fontsize=8, alpha=0.7)

def create_constellation_plots(constellation_data):
    """Create visualization plots for the constellation"""

    sat_data = constellation_data['satellite_data']
    df = pd.DataFrame(sat_data)

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: RAAN vs Mean Anomaly
    scatter = ax1.scatter(df['raan'], df['mean_anomaly'],
                         c=df['plane'], cmap='tab20', alpha=0.7, s=30)
    ax1.set_xlabel('RAAN (degrees)')
    ax1.set_ylabel('Mean Anomaly (degrees)')
    ax1.set_title('Satellite Distribution in RAAN-MA Space')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 360)
    ax1.set_ylim(0, 360)
    plt.colorbar(scatter, ax=ax1, label='Plane Number')

    # Plot 2: Ground Track Pattern with Earth Map
    # First draw the Earth map
    draw_earth_map(ax2)
    
    # Calculate ground track positions
    lons = []
    lats = []
    plane_colors = []
    
    for _, sat in df.iterrows():
        # More realistic ground track calculation
        # Convert RAAN and Mean Anomaly to ground track
        
        # Simple approximation for demonstration
        # In reality, this would require proper orbital mechanics
        lon = (sat['raan'] + sat['mean_anomaly']) % 360
        if lon > 180:
            lon = lon - 360  # Convert to -180 to 180 range
            
        # Calculate latitude based on inclination and mean anomaly
        lat = np.arcsin(np.sin(np.radians(constellation_data['inclination'])) * 
                       np.sin(np.radians(sat['mean_anomaly']))) * 180/np.pi
        
        lons.append(lon)
        lats.append(lat)
        plane_colors.append(sat['plane'])
    
    # Plot satellites on Earth map with high visibility
    scatter2 = ax2.scatter(lons, lats, c=plane_colors, cmap='Set1', 
                          alpha=1.0, s=60, edgecolors='white', linewidth=2,
                          marker='*', zorder=10)
    ax2.set_title(f'Satellite Positions on Earth Map\nWalker {constellation_data["total_satellites"]}'
                 f'/{constellation_data["num_planes"]}/{constellation_data["walker_F"]}',
                 color='white', fontweight='bold')
    
    # Add colorbar for plane numbers
    cbar2 = plt.colorbar(scatter2, ax=ax2, label='Plane Number')
    cbar2.ax.yaxis.label.set_color('white')
    cbar2.ax.tick_params(colors='white')
    
    # Add satellite count text
    ax2.text(0.02, 0.02, f'Total Satellites: {len(lons)}', 
             transform=ax2.transAxes, color='white', fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

    # Plot 3: Satellites per Plane
    plane_counts = df['plane'].value_counts().sort_index()
    bars = ax3.bar(plane_counts.index, plane_counts.values, 
                   color='skyblue', alpha=0.7, edgecolor='navy', linewidth=0.5)
    ax3.set_xlabel('Plane Number')
    ax3.set_ylabel('Number of Satellites')
    ax3.set_title('Satellites Distribution by Plane')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontsize=8)

    # Plot 4: RAAN Distribution
    n_bins = min(30, constellation_data['num_planes'])
    n, bins, patches = ax4.hist(df['raan'], bins=n_bins, 
                               color='lightgreen', alpha=0.7, 
                               edgecolor='darkgreen', linewidth=0.5)
    ax4.set_xlabel('RAAN (degrees)')
    ax4.set_ylabel('Number of Satellites')
    ax4.set_title('RAAN Distribution')
    ax4.grid(True, alpha=0.3)

    # Add statistics text to RAAN plot
    mean_raan = df['raan'].mean()
    std_raan = df['raan'].std()
    ax4.text(0.02, 0.98, f'Mean: {mean_raan:.1f}°\nStd: {std_raan:.1f}°', 
             transform=ax4.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    return fig

def generate_tle_file_content(tle_lines):
    """Generate TLE file content as string"""
    return '\r\n'.join(tle_lines) + '\r\n'

def create_validation_report(constellation_data):
    """Create a validation report"""
    report = f"""Constellation TLE Validation Report
==========================================

Constellation Parameters:
- Walker notation: {constellation_data['total_satellites']}/{constellation_data['num_planes']}/{constellation_data['walker_F']}
- Altitude: {constellation_data['altitude']} km
- Inclination: {constellation_data['inclination']} degrees
- Eccentricity: 0.000
- Mean motion: {constellation_data['mean_motion']:.8f} rev/day
- Orbital period: {constellation_data['orbital_period']:.2f} minutes

Distribution Statistics:
- RAAN spacing: {constellation_data['raan_spacing']:.4f} degrees
- In-plane spacing: {360/constellation_data['sats_per_plane']:.4f} degrees
- Walker phase unit: {constellation_data['phase_unit']:.4f} degrees
- Number of unique RAAN values: {constellation_data['num_planes']}

TLE Format Details:
- Epoch year: {constellation_data['epoch_year']:02d}
- Epoch day: {constellation_data['epoch_day']:.8f}
- NORAD ID range: {constellation_data['base_norad_id']}-{constellation_data['base_norad_id'] + constellation_data['total_satellites'] - 1} (Sequential)
- Launch info: Randomized for diversity
- Line ending: CR+LF (Windows compatible)
"""
    return report
