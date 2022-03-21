# Example 3: Conversion of German tax revenue data at the level of tax
# districts 1926-1938 into administrative districts (Landkreise)
# of the respective year. Invalid geometries in the Landkreis shapefiles 
# were corrected manually beforehand.
#
# Data sources:
#
# Brockmann, P.; Halbmeier, C.; and Sierminska, E. (2022): Geocoded Tax Data
# for the German Interwar Period: A Novel Database for Regional Analyses 
#	
# MPIDR [Max Planck Institute for Demographic Research] 
# and CGG [Chair for Geodesy and Geoinformatics, University of Rostock] 2011: 
# MPIDR Population History GIS Collection
# (partly based on Hubatsch and Klein 1975 ff.) – Rostock.
#
# Hubatsch, W. and T. Klein (eds.) 1975 ff.: Grundriß der deutschen
# Verwaltungsgeschichte – Marburg
#

import os
import sys
import geopandas as gpd
import fiona

# Add script directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import districtconversion as dv

# Directory with tax district shapefiles
taxdistrictPath = "C:/..." 

# Directory with Landkreis shapefiles
landkreisPath = "C:/.../german_empire_1871-1945/German Empire 1871-1945/modified/" 

# Geodataframes are converted into an equal-area projection to calculate areas correctly; 
# EPSG:3035 is suitable for Germany
projection = 'epsg:3035'

# List of variables to be converted
variables = ['p_revenue', 'i_revenue', 'c_revenue', 'w_revenue', 
         'su_revenue', 't_revenue', 'population']


for year in range(1926, 1927):
    print(year)

    ### Prepare target dataframe, source: GeoBasis-DE / BKG
    divisionBFile = os.path.join(landkreisPath, "German_Empire_"+ str(year) +"_v.1.0.shp")
    with fiona.Env():
        divisionB = gpd.read_file(divisionBFile, encoding='utf-8')
    
    # Dataframe manipulations
    divisionB_clean = (
        divisionB.pipe(dv.consistency_check)
                 .to_crs(projection)
    )

    ### Prepare source dataframe; Brockmann et al. (2022)
    divisionAFile = os.path.join(taxdistrictPath, 'taxdistricts' + str(year) + '.shp' )
    with fiona.Env():
        divisionA = gpd.read_file(divisionAFile, encoding='utf-8')
        
    # Remove regions with missing geometry
    if year==1938:
        divisionA = divisionA[divisionA['district']!="Rokitnitz"]
        
    # Dataframe manipulations
    divisionA_clean = (
        divisionA.reset_index() 
                 .pipe(dv.consistency_check) 
                 .to_crs(projection)
    )
    
    ### Convert regional data from admininistrative division A into division B
    divisionB_clean, overlap1, overlap2 = dv.convert_admin_division(source=divisionA_clean,
                                                                    target=divisionB_clean,
                                                                    columns=variables)
    
    # Keep required columns, rename, and save
    (divisionB_clean.loc[:, ['AREA', 'PERIMETER', 'LAND', 'NAME', 'STATUS', 'ID'] + variables]
                    .to_csv('taxData_landkreise_'+str(year)+'.csv', encoding='utf-8', na_rep='', index=False)

    )


print('Done')
    
