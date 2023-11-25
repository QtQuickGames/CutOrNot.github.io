library(terra)
library(lidR)
library(sf)

#import LAS/LAZ
LASfile <- "D:\\HACKATON\\4p.las"
las <- readLAS(LASfile, select = "xyzr", filter = "-drop_z_below 0")
#układ
crs(las) = "EPSG:2180" 


#rasteryzacja koron (.las, rozmiar piksela, algorytm)
#p2r - Point to Raster
chm_p2r_05 <- rasterize_canopy(las, 1, p2r(subcircle = 0.2))


##wygładzanie (średnia)
kernel <- matrix(1,3,3)
chm_p2r_05_smoothed <- terra::focal(chm_p2r_05, w = kernel, fun = mean, na.rm = TRUE)
#zapis rastra z koronami drzew do formatu TIFF
setwd("D:\\HACKATON")
writeRaster(chm_p2r_05_smoothed, "korona_ras_1m_4pkt.tiff")


###Lokalizacja drzew
##lmf - local maximum filter [m] - algorytm znajduje najwyższy punkt w całym sąsiedztwie
##Sąsiedztwo - obszar wokół każdego punktu wyznaczone jako drzewo
ttops_chm_p2r_05_smoothed <- locate_trees(chm_p2r_05_smoothed, lmf(6))

#segmentacja
algo <- dalponte2016(chm_p2r_05_smoothed, ttops_chm_p2r_05_smoothed)
las_segm <- segment_trees(las, algo)
###ostateczne korony - poligony
crowns <- crown_metrics(las_segm, func = .stdtreemetrics, geom = "convex")

#zapis plików końcowych
st_write(ttops_chm_p2r_05_smoothed, "korona_4p_trees_6.shp", driver="ESRI Shapefile",  layer_options = "SHPT=POINTZ")
st_write(crowns, "korona_4p_6.shp", driver="ESRI Shapefile")

