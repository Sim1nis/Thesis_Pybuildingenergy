import os
import json
import numpy as np
from lookup_tables import *

def get_year(user_input):
    if user_input.get("renovated") and user_input.get("year_renovated"):
        return user_input["year_renovated"]
    return user_input["year_built"]

def get_building_period(year):
    if year < 1980:
        return "pre1980"
    elif year < 2001:
        return "1980-2001"
    elif year < 2010:
        return "2001-2010"
    else:
        return "post2010"

def safe_lookup(table, *args):
    """Προσπάθησε να βρεις την τιμή, αλλιώς βγάλε λογικό error."""
    try:
        v = table
        for arg in args:
            v = v[arg]
        if v is None:
            raise ValueError(f"Δεν υπάρχει τιμή για {'/'.join(map(str,args))}")
        return v
    except KeyError:
        raise ValueError(f"Λάθος key στα lookup tables: {'/'.join(map(str,args))}")

def get_U_wall(year, wall_group, wall_finish, climate_zone=None):
    period = get_building_period(year)
    if period in ["pre1980", "1980-2001"]:
        return safe_lookup(U_VALUES_WALLS_5_1, wall_group, wall_finish)
    # if period == "2001-2010":
    #     return safe_lookup(U_VALUES_WALLS_5_2, wall_group, wall_finish)
    # if period == "post2010":
    #     return safe_lookup(U_VALUES_WALLS_5_3[climate_zone], wall_group, wall_finish)
    raise ValueError("Δεν έχει οριστεί lookup για αυτό το έτος στους τοίχους.")

def get_U_roof(year, roof_type, climate_zone=None):
    period = get_building_period(year)
    if period in ["pre1980", "1980-2001"]:
        return safe_lookup(U_VALUES_ROOF_5_1, roof_type)
    # if period == "2001-2010":
    #     return safe_lookup(U_VALUES_ROOF_5_2, roof_type)
    # if period == "post2010":
    #     return safe_lookup(U_VALUES_ROOF_5_3[climate_zone], roof_type)
    raise ValueError("Δεν έχει οριστεί lookup για αυτό το έτος στη στέγη.")

def get_U_floor(year, floor_type, climate_zone=None):
    period = get_building_period(year)
    if period in ["pre1980", "1980-2001"]:
        return safe_lookup(U_VALUES_FLOOR_5_1, floor_type)
    # if period == "2001-2010":
    #     return safe_lookup(U_VALUES_FLOOR_5_2, floor_type)
    # if period == "post2010":
    #     return safe_lookup(U_VALUES_FLOOR_5_3[climate_zone], floor_type)
    raise ValueError("Δεν έχει οριστεί lookup για αυτό το έτος στο δάπεδο.")

def get_U_window(window_type):
    # Να βάζεις .capitalize() ή .strip() αν θες να πιάνει και input με λαθάκια
    key = window_type.strip()
    return safe_lookup(U_VALUES_GLASS, key)

def get_boiler_eff(boiler_type):
    return safe_lookup(BOILER_EFFICIENCY, boiler_type)

def get_fuel_factor(fuel_type):
    return safe_lookup(FUEL_CONVERSION_FACTOR, fuel_type)

def get_heating_period(climate_zone):
    return safe_lookup(HEATING_PERIOD, climate_zone)

def get_cooling_period(climate_zone):
    return safe_lookup(COOLING_PERIOD, climate_zone)

def get_water_temps(climate_zone):
    return safe_lookup(NETWORK_WATER_TEMPERATURE, climate_zone)

def build_actual_bui_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        user_input = json.load(f)

    year = get_year(user_input)
    climate_zone = user_input["climate_zone"]

    # Υπολογισμός επιφανειών
    bedrooms = user_input["num_bedrooms"]
    area = bedrooms * 15 + 30  # 30m2 βασικό + 15m2 ανά υπνοδωμάτιο
    window_area = area * 0.15

    # Υπολογισμός U-values
    U_wall = get_U_wall(year, user_input["wall_group"], user_input["wall_finish"], climate_zone)
    U_roof = get_U_roof(year, user_input["roof_type"], climate_zone)
    U_floor = get_U_floor(year, user_input["floor_type"], climate_zone)
    U_window = get_U_window(user_input["window_type"])

    user_bui = {
        "name": user_input.get("name", "ActualBuilding"),
        "a_use": area,
        "zone_area": area,
        "volume": area * 2.7,
        "latitude": 37.98,
        "longitude": 23.72,
        "periods": year,
        "annual_mean_external_temperature": 15,

        "typology_elements": np.array(["OP", "ROOF", "GR", "W"]),
        "orientation_elements": np.array(["SV", "HOR", "HOR", "SV"]),
        "solar_abs_elements": np.array([0.6, 0.0, 0.0, 0.0]),
        "area_elements": [area * 2.0, area, area, window_area],
        "transmittance_U_elements": [U_wall, U_roof, U_floor, U_window],
        "thermal_capacity_elements": [250, 250, 250, 0],
        "g_factor_windows": [0.0, 0.0, 0.0, 0.76],
        "heat_convective_elements_internal": np.array([2.5, 5.0, 5.0, 2.5]),
        "heat_radiative_elements_internal": np.array([5.13] * 4),
        "heat_convective_elements_external": np.array([20.0] * 4),
        "heat_radiative_elements_external": np.array([4.14] * 4),

        "air_change_rate_base_value": 0.35 * user_input["num_occupants"],
        "internal_gains_base_value": 2.0 + user_input["num_occupants"] * 0.8,
        "heating_mode": True,
        "cooling_mode": True,
        "heating_setpoint": 20,
        "cooling_setpoint": 27,
        "heating_setback": 15,
        "cooling_setback": 30,

        "boiler_eff": get_boiler_eff(user_input["boiler_type"]),
        "fuel_factor": get_fuel_factor(user_input["fuel_type"]),
        "heating_period": get_heating_period(climate_zone),
        "cooling_period": get_cooling_period(climate_zone),
        "water_network_temperatures": get_water_temps(climate_zone),

        "occ_level_wd": np.ones(24),
        "occ_level_we": np.ones(24),
        "comf_level_wd": np.ones(24),
        "comf_level_we": np.ones(24),
    }

    return user_bui
