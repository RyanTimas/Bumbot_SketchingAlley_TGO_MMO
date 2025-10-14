import folium
from folium import plugins
import webbrowser
import os

# Create a base map centered on Florida's panther territory
florida_map = folium.Map(location=[26.2, -81.4], zoom_start=9, tiles='OpenStreetMap')

# Define the 10 locations with their coordinates and likelihood percentages
locations = {
    "SR-29 (FPNWR Border)": {
        "coords": [26.0910, -81.4680],
        "panther": 4.5,
        "bobcat": 18,
        "bear": 15,
        "description": "Best overall location for panther sightings. Borders Florida Panther National Wildlife Refuge."
    },
    "Loop Road (Big Cypress)": {
        "coords": [25.7890, -80.9896],
        "panther": 4.0,
        "bobcat": 20,
        "bear": 18,
        "description": "Remote area with excellent habitat diversity. High likelihood for all three species."
    },
    "I-75 Crossings": {
        "coords": [26.1833, -81.3833],
        "panther": 3.5,
        "bobcat": 8,
        "bear": 5,
        "description": "Wildlife underpasses with fencing. Best viewed from safe pull-offs on I-75."
    },
    "Seminole Lands (Guided)": {
        "coords": [26.0333, -80.9667],
        "panther": 3.0,
        "bobcat": 22,
        "bear": 20,
        "description": "Requires special permission or guided tour. Excellent habitat with minimal human disturbance."
    },
    "Bear Island (Big Cypress)": {
        "coords": [25.9833, -81.1833],
        "panther": 2.5,
        "bobcat": 15,
        "bear": 16,
        "description": "Open prairies and pinelands with good sight lines. Popular for wildlife viewing."
    },
    "Fakahatchee Main Rd": {
        "coords": [25.9895, -81.4855],
        "panther": 2.0,
        "bobcat": 18,
        "bear": 12,
        "description": "Similar habitat to Jane's Scenic Drive but with slightly better visibility."
    },
    "Picayune Strand SF": {
        "coords": [26.0833, -81.5333],
        "panther": 1.5,
        "bobcat": 16,
        "bear": 14,
        "description": "Restored area becoming excellent habitat. Dispersal zone for young panthers."
    },
    "Corkscrew Boardwalk": {
        "coords": [26.4167, -81.6000],
        "panther": 1.0,
        "bobcat": 12,
        "bear": 8,
        "description": "Fixed boardwalk with many visitors. More likely to see tracks than actual panthers."
    },
    "Babcock Ranch Tour": {
        "coords": [26.8333, -81.9333],
        "panther": 0.5,
        "bobcat": 10,
        "bear": 9,
        "description": "Northern periphery of panther range. Better for other wildlife like bison and birds."
    },
    "Myakka River State Park": {
        "coords": [27.2333, -82.3167],
        "panther": 0.25,
        "bobcat": 14,
        "bear": 10,
        "description": "Only area with known panthers outside South Florida. Very low population density."
    }
}


# Define color ranges for each animal
def get_color_panther(percent):
    if percent >= 3.5:
        return 'red'
    elif percent >= 2.0:
        return 'orange'
    else:
        return 'beige'


def get_color_bobcat(percent):
    if percent >= 18:
        return 'darkgreen'
    elif percent >= 12:
        return 'green'
    else:
        return 'lightgreen'


def get_color_bear(percent):
    if percent >= 15:
        return 'darkblue'
    elif percent >= 10:
        return 'blue'
    else:
        return 'lightblue'


# Add markers for each location
for name, info in locations.items():
    # Create popup content with HTML formatting
    popup_html = f"""
    <div style="width: 250px;">
        <h4 style="margin-bottom: 5px;">{name}</h4>
        <p style="margin: 2px 0; font-size: 12px;">{info['description']}</p>
        <div style="background-color: #f0f0f0; padding: 5px; margin-top: 5px; border-radius: 3px;">
            <p style="margin: 2px 0; color: {get_color_panther(info['panther'])};">
                <b>Panther:</b> {info['panther']}% likelihood
            </p>
            <p style="margin: 2px 0; color: {get_color_bobcat(info['bobcat'])};">
                <b>Bobcat:</b> {info['bobcat']}% likelihood
            </p>
            <p style="margin: 2px 0; color: {get_color_bear(info['bear'])};">
                <b>Bear:</b> {info['bear']}% likelihood
            </p>
        </div>
    </div>
    """

    # Create icon with panther likelihood as color indicator
    icon = folium.Icon(
        color=get_color_panther(info['panther']),
        icon='paw',
        prefix='fa'
    )

    # Add marker to map
    folium.Marker(
        location=info['coords'],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{name} (Panther: {info['panther']}%)",
        icon=icon
    ).add_to(florida_map)

# Add a legend
legend_html = '''
<div style="
    position: fixed; 
    bottom: 50px; 
    left: 50px; 
    width: 280px; 
    height: 220px; 
    background-color: white; 
    border: 2px solid grey; 
    z-index: 9999; 
    font-size: 14px;
    padding: 10px;
    border-radius: 5px;
">
    <h4 style="margin-top: 0; text-align: center;">Sighting Likelihood Legend</h4>
    <p><i class="fa fa-paw" style="color: red;"></i> Panther: High (3.5%+)</p>
    <p><i class="fa fa-paw" style="color: orange;"></i> Panther: Medium (2.0-3.4%)</p>
    <p><i class="fa fa-paw" style="color: beige;"></i> Panther: Low (<2.0%)</p>
    <p style="color: darkgreen;">Bobcat: High (18%+)</p>
    <p style="color: green;">Bobcat: Medium (12-17%)</p>
    <p style="color: lightgreen;">Bobcat: Low (<12%)</p>
    <p style="color: darkblue;">Bear: High (15%+)</p>
    <p style="color: blue;">Bear: Medium (10-14%)</p>
    <p style="color: lightblue;">Bear: Low (<10%)</p>
</div>
'''

florida_map.get_root().html.add_child(folium.Element(legend_html))

# Add title
title_html = '''
<h3 align="center" style="font-size:20px; position: fixed; 
top: 10px; left: 50%; transform: translateX(-50%); 
background-color: white; padding: 5px 10px; 
border: 2px solid grey; z-index: 9999; border-radius: 5px;">
Florida Wildlife Sighting Likelihood
</h3>
'''
florida_map.get_root().html.add_child(folium.Element(title_html))

# Add layer control
folium.LayerControl().add_to(florida_map)

# Save the map
map_path = 'florida_wildlife_map.html'
florida_map.save(map_path)

# Open in browser
webbrowser.open('file://' + os.path.realpath(map_path))

print("Map generated successfully! Opening in browser...")