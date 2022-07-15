from typing import TypedDict, List


class ShapefileSpec(TypedDict):
    name: str
    filename: str
    name_field: str


def shapefile(name: str, filename: str, name_field: str) -> ShapefileSpec:
    return {
        "name": name,
        "filename": filename,
        "name_field": name_field
    }


shapefiles: List[ShapefileSpec] = [
    shapefile(
        'Openspace MA',
        'data/openspace/OPENSPACE_POLY.shp',
        'SITE_NAME'
    ),

    shapefile(
        'PAD-US MA',
        'data/PADUS3_0_State_MA_SHP/PADUS3_0Combined_StateMA.shp',
        'Unit_Nm'
    ),

    shapefile(
        'NPS',
        'data/NPS_-_Land_Resources_Division_Boundary_and_Tract_Data_Service/' +
        'NPS_-_Land_Resources_Division_Boundary_and_Tract_Data_Service.shp',
        'UNIT_NAME'
    ),

    shapefile(
        'PAD-US RI',
        'data/PADUS3_0_State_RI_SHP/PADUS3_0Combined_StateRI.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US CT',
        'data/PADUS3_0_State_CT_SHP/PADUS3_0Combined_StateCT.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US OH',
        'data/PADUS3_0_State_OH_SHP/PADUS3_0Combined_StateOH.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US NY',
        'data/PADUS3_0_State_NY_SHP/PADUS3_0Combined_StateNY.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US AZ',
        'data/PADUS3_0_State_AZ_SHP/PADUS3_0Combined_StateAZ.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US NH',
        'data/PADUS3_0_State_NH_SHP/PADUS3_0Combined_StateNH.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US ME',
        'data/PADUS3_0_State_ME_SHP/PADUS3_0Combined_StateME.shp',
        'Unit_Nm'
    ),

    shapefile(
        'PAD-US VT',
        'data/PADUS3_0_State_VT_SHP/PADUS3_0Combined_StateVT.shp',
        'Unit_Nm'
    ),
]
