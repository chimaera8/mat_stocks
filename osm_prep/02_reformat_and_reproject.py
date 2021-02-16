#!/usr/bin/python3
import os
import sys
import subprocess
import re
import osr, ogr


##### translates sqlite into shape if necessary and reprojects to a given reference system file
##### _______________________________________
    
inputPath = str(sys.argv[1]).split(" ")[0]  ## osm db .sqlite
country = str(sys.argv[2]).split(" ")[0]  ## country to be computed 
outputDir = str(sys.argv[3]).split(" ")[0]  ## output directory 
reprojectedDir = str(sys.argv[4]).split(" ")[0]  ## output directory 
type = str(sys.argv[5]).split(" ")[0]  ## "line" or "polygon" 
refShp = str(sys.argv[6]).split(" ")[0]  ## shapefile with srs reference
outputFormat = str(sys.argv[7]).split(" ")[0]  ## ".shp" or ".sqlite"

def main():    
    base=os.path.basename(inputPath)
    fn = os.path.splitext(base)[0]
    
    outputDir = outputDir + "/" + country + "/extracted/"
    outputPath = outputDir + fn + ".shp"
    reprojectedDir = outputDir + "/" + country + "/reprojected/"
    reprojectedPath = reprojectedDir + fn + ".shp"
    
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    if not os.path.exists(reprojectedDir):
        os.makedirs(reprojectedDir)
        
    if(type == "line"):
        geoType = ogr.wkbLine
        m = "multilines"
        p = "LINE"
    elif(type == "polygon"):
        geoType = ogr.wkbPolygon
        m = "multipolygons"
        p = "POLYGON"
    
    subprocess.call(["ogr2ogr", "-f", "ESRI Shapefile", outputPath, inputPath, "-dsco", "SPATIALITE=YES", "-sql","SELECT * FROM {m}", "-nlt", '{p}')
    
    ##### reproject shape to target srs
    #refShp = "/data/Jakku/osm_test/EQUI7_V13_AF_PROJ_LAND.shp"
    
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataset = driver.Open(refShp)
    inLayer = dataset.GetLayer()
    targetRef = inLayer.GetSpatialRef()
    
    dataset1 = driver.Open(outputPath)
    inLayer1 = dataset1.GetLayer()
    sourceRef = inLayer1.GetSpatialRef()

    coordTrans = osr.CoordinateTransformation(sourceRef, targetRef)

    # create the output layer
    outputShapefile = reprojectedPath
    
    if(outputFormat == ".shp"):
        driver2 = ogr.GetDriverByName("ESRI Shapefile")
    elif(outputFormat == ".sqlite"):
        ogr.GetDriverByName("SQLite")
        
    if os.path.exists(outputShapefile):
        driver2.DeleteDataSource(outputShapefile)
    outDataSet = driver2.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("layer", targetRef, geom_type=geoType)

    # add fields
    inLayerDefn = inLayer1.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer1.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # dereference the features and get the next input feature
        outFeature = None
        inFeature = inLayer1.GetNextFeature()

    # Save and close the shapefiles
    dataset = None
    outDataSet = None
    
    
if __name__ == '__main__':
    main()

                    
                    
                        
                        
                
                

