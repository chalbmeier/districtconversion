# Main functions

import numpy as np


def convert_admin_division(source, target, columns):
    '''
        Main function. Calls functions to calculate area overlap between
        source and target administrative division. Then, based on the overlap,
        converts the data  
        
        Input: source: Geodataframe with N_A polygon geometries. 
                       Contains geodata to be converted.
               target: Geodataframe with N_B polygon geometries.
                       Geometries to be converted into.
               columns: list of data columns in source to be converted into
                        geometries of target

         Output: df: copy of target with additional columns containing coverted data
                     overlap1:
                     overlap2:

    '''
    
    overlap1, overlap2 = calculate_area_overlap(source, target)
    
    df = convert_data(source, target, overlap1_B_A=overlap1, overlap2_B_A=overlap2,
                      columns=columns)
    
    
    return df, overlap1, overlap2


def calculate_area_overlap(source, target):

    '''
        Input: source: Geodataframe with N_A polygon geometries. 
                       Contains geodata to be converted.
               target: Geodataframe with N_B polygon geometries. 
                       Geometries to be converted into.

        Output: overlap_B_A: Matrix (N_B x N_A) of shares (0-1) that indicate
                             the area overlap between each region of source
                             and target dataframe

    '''

    # Calculate share = area overlap / area of source 
    N_A = source.shape[0]
    N_B = target.shape[0]
    overlap1_B_A = np.zeros((N_B, N_A))
    overlap2_B_A = np.zeros((N_B, N_A))

    for indexA, regionA in source.iterrows():
        for indexB, regionB in target.iterrows():

            if regionA['geometry'].intersects(regionB['geometry']):

                intersection = regionA['geometry'].intersection(regionB['geometry']).area 
                share1 = intersection / regionA['geometry'].area 
                share2 = intersection / regionB['geometry'].area

                overlap1_B_A[indexB, indexA] = round(share1, 3)
                overlap2_B_A[indexB, indexA] = round(share2, 3)

    return overlap1_B_A, overlap2_B_A



def convert_data(source, target, overlap1_B_A, overlap2_B_A, columns):
    
    '''
        Convert data from source to target geodataframe

        Input: source: Geodataframe with N_A polygon geometries. 
                       Contains geodata to be converted.
               target: Geodataframe with N_B polygon geometries. 
                       Geometries to be converted into.
               overlap_B_A: Matrix (N_B x N_A) of shares (0-1) that indicate 
                            the area overlap between each region of source and target
               columns: list of columns of source with numerical data to be converted

        Output: convertedData: Array of converted data

    '''

    for column in columns:
        data = source[column]
        NaNIndicator = source[column].isnull()

        # Missing values=0 such that matrix multiplication works
        data.fillna(0, inplace=True)  

        # Calculate new value for division of gdf_A
        target[column] = np.dot(overlap1_B_A, data)

        # Add missing values for those regions in target division that 
        # overlap with a region from source division with missing values
        NaNs = np.dot(overlap1_B_A, NaNIndicator)
        NaNs = NaNs != 0  # Convert to true/false
        target.loc[NaNs, column] = np.NaN

        # Second source of missings: regions in target division not completely
        # covered by regions from source division
        checkSum = np.sum(overlap2_B_A, axis=1)
        indexCoverage = (checkSum<0.80)  		#XXX
        target.loc[indexCoverage, column] = np.NaN

    return target



def consistency_check(gdf):
    '''
        Runs a series of consistency checks to ensure
        that geodataframe has a valid geometry

        Input: gdf: geodataframe with polygon geometries

        Output: gdf: unaltered geodataframe
    '''

    # Empty geometries, XXX
    if len(gdf[gdf.geometry==None])>0:
        raise ValueError("Geodataframe has empty geometries. Please remove these from geodataframe.")
        # Improve, raise ValueError does not abort code

    # Invalid geometries
    for i, region in gdf.iterrows():
        if region['geometry'].is_valid==False:
            raise ValueError("Invalid geometry. Please analyze and fix, e.g., in QGIS. Affected polygon:\n", region, '\n')
    return gdf




def index_coverageA(gdf_A, overlap_B_A):
    '''
        Show regions of gdf_A that are not fully covered by regions of gdf_B
        Input: gdf_A: Geodataframe with N_A polygon geometries.
               overlap_B_A: Matrix (N_B x N_A) of shares (0-1) that indicate the area overlap between
                            each region of gdf_A and gdf_B
    '''
    checkSum = np.sum(overlap_B_A, axis=0)
    indexCoverage = (checkSum<0.95) | (checkSum>1.05)

    return indexCoverage



