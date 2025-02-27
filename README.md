# Green Space Accessibility Analysis

This tool analyzes accessibility to green spaces (parks, gardens, forests, etc.) from residential buildings using both straight-line and network distances.

## Overview

This script measures how accessible green spaces are to residential buildings within a defined urban area. It performs two types of accessibility analysis:

1. **Straight-line distance**: Direct "as the crow flies" measurement from buildings to the nearest green space
2. **Network distance**: The actual walking distance using the street network

The tool visualizes both analyses and provides statistics on the percentage of buildings that have access to green spaces within a standard 800-meter threshold.

## Dependencies

The script requires the following Python libraries:
- `osmnx`: For retrieving OpenStreetMap data and network analysis
- `pandas`: For data manipulation
- `geopandas`: For spatial data operations
- `matplotlib`: For visualization
- `networkx`: For graph operations on street networks
- `shapely`: For geometric operations
- `numpy`: For numerical operations

## Installation

```bash
pip install osmnx pandas geopandas matplotlib networkx shapely numpy
```

## Usage

1. Set the bounding box coordinates for your area of interest:
   ```python
   north = 40.76920
   south = 40.75207
   east = -111.87108
   west = -111.88794
   ```

2. Configure the tags to identify green spaces and residential buildings in OpenStreetMap:
   ```python
   green_tags = {
       'leisure': ['park', 'garden'],
       'landuse': ['recreation_ground', 'forest'],
       'natural': ['wood', 'grassland']
   }

   building_tags = {
       'building': ['house', 'residential', 'apartment']
   }
   ```

3. Run the script to:
   - Fetch data from OpenStreetMap
   - Calculate straight-line distances from buildings to green spaces
   - Calculate network distances along walkable paths
   - Generate visualizations
   - Output statistics

## Methodology

### Data Collection
- Uses OpenStreetMap data through the OSMnx library
- Retrieves green spaces and residential buildings within the specified bounding box
- Projects all geographic data to UTM zone 12 for accurate distance measurements

### Straight-line Distance Analysis
- Calculates the direct distance from each building to the nearest green space
- Classifies buildings based on whether they're within 800 meters of a green space

### Network Distance Analysis
1. Obtains the walkable street network for the area
2. Creates access points along the boundaries of green spaces (every 50 meters)
3. Finds the nearest network nodes to buildings and green space access points
4. Calculates the shortest path distance through the street network
5. Classifies buildings based on whether they're within 800 meters of a green space via the street network

### Visualization
- Generates color-coded maps showing buildings with and without green space access
- Green spaces are shown as transparent green polygons
- Buildings are colored based on their accessibility status

## Output

The script produces:
1. Statistical analysis of both measurement methods:
   - Total number of buildings
   - Number and percentage of buildings within 800m of green spaces
2. Visual maps for both straight-line and network distance analyses
3. Comparison between the two methods

## Example

For the sample area (appears to be in Salt Lake City, Utah), the analysis can show how many residential buildings have access to parks and green spaces, highlighting potential urban planning insights regarding green space distribution and accessibility.

## Notes

- The 800-meter threshold represents a common standard for accessibility (approximately a 10-minute walk)
- Network distance provides a more realistic measure of accessibility than straight-line distance
- Increasing the number of access points along green space boundaries improves accuracy

## Customization

To analyze a different area:
1. Update the bounding box coordinates
2. Adjust the UTM zone based on your location
3. Modify the green space and building tags if needed for your region's OSM tagging conventions
