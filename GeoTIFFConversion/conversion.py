#!/c/Python27/ python
from osgeo import gdal,ogr,osr
import geojson
import os
import urllib2
from geojson import Feature, Point, FeatureCollection
import json
import sys
import boto3

def process(filename):
	raster=filename
	ds=gdal.Open(raster)

	time=ds.GetMetadataItem("TIFFTAG_DATETIME")
	#print time

	gt=ds.GetGeoTransform()
	originX = gt[0]
	originY = gt[3]
	pixelX = gt[1]
	pixelY = gt[5]

	cols = ds.RasterXSize
	rows = ds.RasterYSize
	#print cols
	#print rows

	originX = originX + pixelX*cols/2.0
	originY = originY + pixelY*rows/2.0


	#Get the size of the image 
	xLength=abs(pixelX*cols)
	yLength=abs(pixelY*rows)
	#print xLength
	#print yLength

	#Get area of the image 
	area=xLength*yLength
	#print area

	old_cs= osr.SpatialReference()
	old_cs.ImportFromWkt(ds.GetProjectionRef())

	# create the new coordinate system
	wgs84_wkt = """
	GEOGCS["WGS 84",
	    DATUM["WGS_1984",
	        SPHEROID["WGS 84",6378137,298.257223563,
	            AUTHORITY["EPSG","7030"]],
	        AUTHORITY["EPSG","6326"]],
	    PRIMEM["Greenwich",0,
	        AUTHORITY["EPSG","8901"]],
	    UNIT["degree",0.01745329251994328,
	        AUTHORITY["EPSG","9122"]],
	    AUTHORITY["EPSG","4326"]]"""
	new_cs = osr.SpatialReference()
	new_cs .ImportFromWkt(wgs84_wkt)

	# create a transform object to convert between coordinate systems
	transform = osr.CoordinateTransformation(old_cs,new_cs) 

	#get the coordinates in lat long
	latlong = transform.TransformPoint(originX, originY) 
	longitude = latlong[0]
	latitude = latlong[1]

	#print latitude
	#print longitude

	filerootname = raster.split(".")[0]
	lat = str(round(latitude,3))+" N"
	if(latitude < 0):
		lat = str(round(-latitude,3))+" S"
	longt = str(round(longitude,3))+" E"
	if(longitude < 0):
		longt = str(round(-longitude,3))+" W"

	description={"Name":filerootname, "Size":str(xLength)+" x "+str(yLength), "Area":str(area), "Time":str(time), "Co-ordinates":str(lat)+", "+str(longt)}
	marker = Feature(geometry=Point((longitude, latitude)), properties=description)
	geojsonfile = FeatureCollection([marker],name=filerootname) 

	with open(filerootname+'.json', 'w') as outfile:
	    json.dump(geojsonfile, outfile, sort_keys=True)

	result_filename=filerootname+'.json'
	result=open(os.path.join(cwd, result_filename))
	return result

s3 = boto3.resource('s3')
bucket = s3.Bucket("geotiff-files")


#download all images in the AWS bucket to a folder
for object in bucket.objects.all():
	bucket.download_file(object.key, os.path.join(os.curdir, object.key)

cwd = str(os.getcwd())
#jsonObjects = []
#print(cwd)
#Convert each image to GeoJSON then, remove the image from the folder
for f in os.listdir(cwd):
	if f!='conversion.py':
	 	#jsonObjects.append(process(f))
	 	os.remove(f)
	 	result1=(str(f).split(".")[0])
	 	result=result1+'.json'
	 	os.remove(result)
#return jsonObjects
