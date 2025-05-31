import json
import numpy as np
import os

def load_lookup_tables():
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "lookup_tables", "wall_u_values.json"), encoding="utf-8") as f:
        wall_u_db = json.load(f)
    with open(os.path.join(base_dir, "lookup_tables", "window_type_values.json"), encoding="utf-8") as f:
        window_type_db = json.load(f)
    with open(os.path.join(base_dir, "lookup_tables", "roof_u_values.json"), encoding="utf-8") as f:
        roof_u_db = json.load(f)
    with open(os.path.join(base_dir, "lookup_tables", "floor_u_values.json"), encoding="utf-8") as f:
        floor_u_db = json.load(f)
    with open(os.path.join(base_dir, "lookup_tables", "climate_zone_data.json"), encoding="utf-8") as f:
        climate_zone_lookup = json.load(f)
    return wall_u_db, window_type_db, roof_u_db, floor_u_db, climate_zone_lookup

WALL_U_DB, WINDOW_TYPE_DB, ROOF_U_DB, FLOOR_U_DB, CLIMATE_ZONE_LOOKUP = load_lookup_tables()

ALLOWED_ORIENTATIONS = ["NV", "SV", "EV", "WV", "HOR"]


def get_wall_u_value(period, wall_group, wall_finish):
    try:
        return WALL_U_DB[period][wall_group][wall_finish]
    except KeyError:
        print("⚠️ Δεν βρέθηκε U-value για wall:", period, wall_group, wall_finish)
        return 3.4

def get_window_ug(window_type):
    try:
        return WINDOW_TYPE_DB[window_type]
    except KeyError:
        print("⚠️ Δεν βρέθηκε Ug για τον τύπο υαλοπίνακα:", window_type)
        return 5.7

def get_roof_u_value(period, roof_type):
    try:
        return ROOF_U_DB[period][roof_type.strip()]
    except Exception:
        print(f"⚠️ Δεν βρέθηκε U-value για roof: {period} {roof_type}")
        return 3.0

def get_floor_u_value(period, floor_type):
    try:
        return FLOOR_U_DB[period][floor_type.strip()]
    except Exception:
        print(f"⚠️ Δεν βρέθηκε U-value για floor: {period} {floor_type}")
        return 2.5

def get_kenak_period(year_built, renovated, year_renovated):
    year = year_renovated if (renovated and year_renovated) else year_built
    if year < 1980:
        return '5.1'
    elif 1980 <= year < 2010:
        return '5.2'
    elif 2010 <= year < 2017:
        return '5.3'
    else:
        return '5.4'

def build_actual_bui_from_json(json_directory):
    idx = input("Δώσε αριθμό JSON (1–5): ")
    try:
        idx = int(idx)
        assert 1 <= idx <= 5
    except Exception:
        raise ValueError("Πρέπει να δώσεις αριθμό από το 1 έως το 5")
    json_path = os.path.join(json_directory, f"actual_input_{idx}.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    period = get_kenak_period(data['year_built'], data['renovated'], data['year_renovated'])

    u_wall = get_wall_u_value(period, data['wall_group'], data['wall_finish'])
    ug = get_window_ug(data['τύπος_υαλοπίνακα'])
    u_roof = get_roof_u_value(period, data['roof_type'])
    u_floor = get_floor_u_value(period, data['floor_type'])

    num_occupants = data['num_occupants']
    num_bedrooms = data['num_bedrooms']
    climate_zone = data['climate_zone']

    climate_data = CLIMATE_ZONE_LOOKUP[climate_zone]
    network_water_temperature = climate_data["network_water_temperature"]
    heating_period = climate_data["heating_period"]
    cooling_period = climate_data["cooling_period"]

    a_use = 100.0
    occ_profile = np.zeros(24)
    occ_profile[:18] = 0.75
    gains_people = (80 * num_occupants) / a_use
    gains_equip = 2.0
    internal_gains = gains_people + gains_equip

    typology_elements = ["OP", "OP", "OP", "OP", "GR", "OP", "W"]
    orientation_elements = ["NV", "SV", "EV", "WV", "HOR", "HOR", "SV"]
    solar_abs_elements = [0.6, 0.6, 0.6, 0.6, 0.0, 0.6, 0.0]
    area_elements = [15.0, 15.0, 15.0, 15.0, 48.0, 60.0, 3.0]
    transmittance_U_elements = [u_wall] * 4 + [u_roof, u_roof, ug]
    thermal_resistance_R_elements = [1/u if u > 0 else 1 for u in transmittance_U_elements]
    thermal_capacity_elements = [250] * 6 + [0]
    g_factor_windows = [0.0]*6 + [0.76]
    heat_convective_elements_internal = [2.5]*4 + [0.7, 5.0, 2.5]
    heat_radiative_elements_internal = [5.13]*7
    heat_convective_elements_external = [20.0]*7
    heat_radiative_elements_external = [4.14]*7
    sky_factor_elements = [0.9]*6 + [0.5]

    for ori in orientation_elements:
        if ori not in ALLOWED_ORIENTATIONS:
            raise ValueError(f"❌ Μη αποδεκτός προσανατολισμός: '{ori}' – Επιτρεπόμενοι: {ALLOWED_ORIENTATIONS}")

    user_bui = {
        'building_type': 'actual',
        'periods': data['year_renovated'] if data['renovated'] else data['year_built'],
        'latitude': 37.98,
        'longitude': 23.72,
        'a_use': a_use,
        'volume': 250.0,
        'wall_thickness': 0.3,
        'coldest_month': 1,
        'annual_mean_internal_temperature': 20.0,
        'annual_mean_external_temperature': 15.0,
        'heating_mode': True,
        'cooling_mode': True,
        'heating_setpoint': 20,
        'cooling_setpoint': 26,
        'heating_setback': 10,
        'cooling_setback': 27,
        'air_change_rate_base_value': 1.41,
        'air_change_rate_extra': 0.0,
        'internal_gains_base_value': internal_gains,
        'internal_gains_extra': 0.0,
        'thermal_bridge_heat': 0.0,
        'surface_envelope': 288.0,
        'surface_envelope_model': 288.0,
        'exposed_perimeter': 50.0,
        'slab_on_ground': 100.0,
        'power_heating_max': 10000,
        'power_cooling_max': -10000,
        'typology_elements': typology_elements,
        'orientation_elements': orientation_elements,
        'solar_abs_elements': solar_abs_elements,
        'area_elements': area_elements,
        'transmittance_U_elements': transmittance_U_elements,
        'thermal_resistance_R_elements': thermal_resistance_R_elements,
        'thermal_capacity_elements': thermal_capacity_elements,
        'thermal_resistance_floor': 2.63,
        'g_factor_windows': g_factor_windows,
        'heat_convective_elements_internal': heat_convective_elements_internal,
        'heat_radiative_elements_internal': heat_radiative_elements_internal,
        'heat_convective_elements_external': heat_convective_elements_external,
        'heat_radiative_elements_external': heat_radiative_elements_external,
        'sky_factor_elements': sky_factor_elements,
        'occupancy_hours': 18,
        'occ_level_wd': occ_profile,
        'occ_level_we': occ_profile,
        'comf_level_wd': np.ones(24),
        'comf_level_we': np.ones(24),
        'construction_class': 'class_i',
        'weather_source': 'pvgis',
        'num_occupants': num_occupants,
        'num_bedrooms': num_bedrooms,
        'climate_zone': climate_zone,
        'network_water_temperature': network_water_temperature,
        'heating_period': heating_period,
        'cooling_period': cooling_period
    }

    print("\n========= SUMMARY STRUCTURE =========")
    for i, (t, a, u) in enumerate(zip(typology_elements, area_elements, transmittance_U_elements)):
        print(f"[{i}] {t} | Area: {a:.2f} | U: {u:.2f}")
    print("=====================================")

    return user_bui
