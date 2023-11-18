import geopandas as gpd
from shapely.geometry import Point

geojson_file_path = '/Users/aravinthvenkateshnatarajan/Downloads/Buildings.geojson'
gdf = gpd.read_file(geojson_file_path)
column_names = gdf.columns
# Print the column names
geometry_column = gdf['geometry']
# Access the coordinates of the first MultiPolygon in the GeoDataFrame
building_centroid = []
for geometry in geometry_column:
    # Check if the geometry is a MultiPolygon
    if geometry.geom_type == 'MultiPolygon':
        # Iterate over individual Polygons within the MultiPolygon
        sum_x = 0
        sum_y = 0
        num_build = 0
        for polygon in geometry.geoms:
            coordinates = list(polygon.exterior.coords)
            for coordinate in coordinates:
                num_build = num_build + 1
                sum_x = sum_x + coordinate[0]
                sum_y = sum_y + coordinate[1]
        cent_x, cent_y = sum_x/num_build, sum_y/num_build
        toPutMulti = {"type": "Point", "coordinates": [cent_x, cent_y]}
        building_centroid.append(toPutMulti)
    else:
        # Handle the case when the geometry is a single Polygon
        coordinates = list(geometry.exterior.coords)
        sum_x = 0
        sum_y = 0
        num_build = 0
        for coordinate in coordinates:
            num_build = num_build + 1
            sum_x = sum_x + coordinate[0]
            sum_y = sum_y + coordinate[1]
        cent_x, cent_y = sum_x/num_build, sum_y/num_build
        toPutPoly = {"type": "Point", "coordinates": [cent_x, cent_y]}
        building_centroid.append(toPutPoly)

gdf['building_centroid'] = building_centroid
print(gdf)
gdf.to_file('/Users/aravinthvenkateshnatarajan/Downloads/BuildingsWithCent.geojson', driver='GeoJSON')
