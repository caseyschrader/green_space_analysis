import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point, LineString
import numpy as np

ox.settings.use_cache = True
ox.settings.log_console = True

# coordinates gathered from openstreetmap.org -> export -> manually select area
north = 40.76920
south = 40.75207
east = -111.87108
west = -111.88794

bbox = (west, south, east, north)

# found in openstreetmaps wiki's 'tag list'
green_tags = {
    'leisure': ['park', 'garden'],
    'landuse': ['recreation_ground', 'forest'],
    'natural': ['wood', 'grassland']
}

building_tags = {
    'building': ['house', 'residential', 'apartment']
}

print("fetching data from OpenStreetMap...")
greenspaces_df = ox.features.features_from_bbox(bbox=bbox, tags=green_tags)
buildings_df = ox.features.features_from_bbox(bbox=bbox, tags=building_tags)

# convert to UTM zone 12
print("converting to UTM coordinates...")
greenspaces_utm = greenspaces_df.to_crs('EPSG:32612')
buildings_utm = buildings_df.to_crs('EPSG:32612')

# straight line calculation
print("\nCalculating straight-line distances...")
straight_line_distances = []

for i, building in buildings_utm.iterrows():
    distances = [building.geometry.distance(green) for green in greenspaces_utm.geometry]
    min_distance = min(distances)
    straight_line_distances.append(min_distance)

buildings_utm['straight_line_distance'] = straight_line_distances
buildings_utm['has_straight_line_access'] = buildings_utm['straight_line_distance'] <= 800

# print straight-line stats
print("\nstraight-line distance analysis:")
print(f"total buildings: {len(buildings_utm)}")
print(f"buildings within 800m (straight-line): {sum(buildings_utm['has_straight_line_access'])}")
print(f"percentage with straight-line access: {(sum(buildings_utm['has_straight_line_access']) / len(buildings_utm)) * 100:.2f}%")

# visualize straight line access
fig, ax = plt.subplots(figsize=(15, 10))
buildings_utm.plot(ax=ax, 
                  column='has_straight_line_access',
                  legend=True,
                  legend_kwds={'title': 'has park access (straight-line <= 800m)'},
                  categorical=True,
                  cmap='RdYlGn')
greenspaces_utm.plot(ax=ax, color='green', alpha=0.3)
plt.title('Building Access to Green Spaces (Straight-line Distance)')
plt.show()

# network distances calculation
print("\ncalculating network distances...")
walk_network = ox.graph_from_bbox(bbox=bbox, network_type='walk')
walk_network_proj = ox.project_graph(walk_network, to_crs='EPSG:32612')

# create access points
print("creating park access points...")
all_points = []
for geom in greenspaces_utm.geometry:
    # get boundary points
    boundary = geom.boundary
    if boundary.geom_type == 'LineString':
        # creating points along boundary (every 50m)
        length = boundary.length
        # ensure that even boundaries less than 50m get a point
        num_points = max(1, int(length / 50))
        #creating the points
        for i in range(num_points):
            point = boundary.interpolate(i * length / num_points)
            all_points.append((point.x, point.y))
    # now applying to multilinestrings as well
    elif boundary.geom_type == 'MultiLineString':
        for line in boundary.geoms:
            length = line.length
            num_points = max(1, int(length / 50))
            for i in range(num_points):
                point = line.interpolate(i * length / num_points)
                all_points.append((point.x, point.y))

access_points = gpd.GeoDataFrame(
    geometry=[Point(p[0], p[1]) for p in all_points],
    crs=greenspaces_utm.crs
)

# find nearest network nodes
print("finding nearest network nodes...")
building_nodes = ox.distance.nearest_nodes(
    walk_network_proj,
    X=buildings_utm.geometry.centroid.x,
    Y=buildings_utm.geometry.centroid.y   
)

access_nodes = ox.distance.nearest_nodes(
    walk_network_proj,
    X=access_points.geometry.x,
    Y=access_points.geometry.y
)

# calculate network distances
print("\ncalculating network distances...")
network_distances = []
# print progress for every 10 buildings
for i, building_node in enumerate(building_nodes):
    if i % 10 == 0:
        print(f"processing building {i+1}/{len(building_nodes)}")
    
    min_distance = float('inf')
    for park_node in access_nodes:
        try:
            distance = nx.shortest_path_length(
                walk_network_proj, 
                building_node, 
                park_node, 
                weight='length'
            )
            min_distance = min(min_distance, distance)
        except nx.NetworkXNoPath:
            continue
    
    network_distances.append(min_distance)

buildings_utm['network_distance'] = network_distances
buildings_utm['has_network_access'] = buildings_utm['network_distance'] <= 800

# print network distance stats
print("\nnetwork distance analysis:")
print(f"total buildings: {len(buildings_utm)}")
print(f"buildings within 800m (network): {sum(buildings_utm['has_network_access'])}")
print(f"percentage with network access: {(sum(buildings_utm['has_network_access']) / len(buildings_utm)) * 100:.2f}%")

# visualize network access
fig, ax = plt.subplots(figsize=(15, 10))
buildings_utm.plot(ax=ax, 
                  column='has_network_access',
                  legend=True,
                  legend_kwds={'title': 'Has Park Access (Network <= 800m)'},
                  categorical=True,
                  cmap='RdYlGn')
greenspaces_utm.plot(ax=ax, color='green', alpha=0.3)
plt.title('Building Access to Green Spaces (Network Distance)')
plt.show()

# compare the results
print("\ncomparison of methods:")
print("buildings with straight-line access:", sum(buildings_utm['has_straight_line_access']))
print("buildings with network access:", sum(buildings_utm['has_network_access']))