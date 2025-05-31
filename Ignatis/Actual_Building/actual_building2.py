## Πόσοι μένουν στο σπίτι	                                                            4	
## Πόσα υπνοδωμάτια έχει	                                                            4	
## Πότε χτίστηκε	                                                                    2001	
## Αν έγινε ριζική ανακαίνιση (και πότε)	                                            δεν εγινε	
## Κλιματική ζώνη	                                                                    Β	
## Τύπος Τοίχων	                Πέτρινο	                                                1
## Τύπος Τελικής Επιφάνειας	    με σοβά	
## Τύπος Στέγης	                Οριζόντια οροφή κάτω από μη θερμομονωμένη στέγη	        1
## Τύπος  Δαπέδου	            Επάνω από ανοικτό υπόστυλο χώρο (πιλοτή)	            0,9
## Τύπος Παραθύρων	            Δίδυμος υαλοπίνακας με διάκενο αέρα 6 mm	            Ug = 3,3
## Τύπος λέβητα	                Συνήθης λέβητας	                                        0,8
## Τύπος καυσίμου	            Πετρέλαιο	                                            1,07

import numpy as np
import os
import pandas as pd
from pybuildingenergy.source.utils import ISO52016
from pybuildingenergy.source.graphs import Graphs_and_report
from pybuildingenergy.data.building_archetype import Buildings_from_dictionary

# === Δημιουργία φακέλου αν δεν υπάρχει ===
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# === Ορισμός διαδρομής για αποθήκευση των αποτελεσμάτων ===
file_dir = os.path.dirname(os.path.realpath(__file__))
ensure_directory_exists(file_dir + "/Result2")

# === Ορισμός διαδρομής για custom αρχείο καιρού ===
weather_file_path = os.path.join(file_dir, "..", "weather", "GRC_Athens_modified_for_kenak.epw")
weather_file_path = os.path.abspath(weather_file_path)

# === Ορισμός παραμέτρων Κτηρίου ===
user_bui = {
    'building_type': 'actual',
    'periods': 2001,
    'latitude': 37.98, 'longitude': 23.72,
    'volume': 300.0, 'exposed_perimeter': 55.0,
    'slab_on_ground': 130.0, 'wall_thickness': 0.5,
    'coldest_month': 1, 'a_use': 130.0,
    'surface_envelope': 310.0, 'surface_envelope_model': 310.0,
    'annual_mean_internal_temperature': 20.0,
    'annual_mean_external_temperature': 15.0,

    'heating_mode': True, 'cooling_mode': True,
    'heating_setpoint': 20, 'cooling_setpoint': 26,
    'heating_setback': 10, 'cooling_setback': 27,
    'power_heating_max': 10000, 'power_cooling_max': -10000,

    'air_change_rate_base_value': 0.75, 'air_change_rate_extra': 0.0,
    'internal_gains_base_value': 8.9, 'internal_gains_extra': 0.0,
    'thermal_bridge_heat': 0.0,

    'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"], dtype=object),
    'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'], dtype=object),
    'solar_abs_elements': np.array([0.6, 0.6, 0.6, 0.6, 0.0, 0.6, 0.0], dtype=object),
    'area_elements': [25.0, 10.0, 18.0, 18.0, 55.0, 55.0, 15.0],
    'transmittance_U_elements': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.3],
    'thermal_resistance_R_elements': [1/1.0]*6 + [1/3.3],
    'thermal_capacity_elements': [250]*6 + [0],
    'thermal_resistance_floor': 1/0.9,
    'g_factor_windows': [0.0]*6 + [0.76],
    'visible_transmittance_windows': 0.65,
    'heat_convective_elements_internal': np.array([2.5]*4 + [0.7, 5.0, 2.5], dtype=object),
    'heat_radiative_elements_internal': np.array([5.13]*7, dtype=object),
    'heat_convective_elements_external': np.array([20.0]*7, dtype=object),
    'heat_radiative_elements_external': np.array([4.14]*7, dtype=object),

    'occ_level_wd': np.array([1]*18 + [0]*6),
    'occ_level_we': np.array([1]*18 + [0]*6),
    'comf_level_wd': np.array([1]*18 + [0]*6),
    'comf_level_we': np.array([1]*18 + [0]*6),

    'heating_period_start': (11, 1), 'heating_period_end': (4, 1),
    'cooling_period_start': (5, 15), 'cooling_period_end': (9, 15),

    'construction_class': 'class_i',
    'weather_source': 'epw',
    'user_glazing_type': 'Δίδυμος υαλοπίνακας με διάκενο αέρα 6 mm',
    'user_glazing_Ug': 3.3
}

# === Συντελεστές σκίασης ===
sky_factors = []
orientations = user_bui['orientation_elements']
types = user_bui['typology_elements']

for typ, orient in zip(types, orientations):
    if typ == "W":
        if orient == 'SV':
            sky_factors.append(0.5)
        elif orient in ['EV', 'WV']:
            sky_factors.append(0.6)
        else:
            sky_factors.append(0.7)
    else:
        sky_factors.append(0.9)

user_bui['sky_factor_elements'] = np.array(sky_factors)

# === Εκτέλεση προσομοίωσης ===
def main(bui_new, weather_type, path_weather_file_, path_hourly_sim_result,
         path_annual_sim_result, dir_chart_folder, name_report):

    BUI = Buildings_from_dictionary(bui_new)

    hourly_sim, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(
        BUI, weather_source=weather_type, path_weather_file=path_weather_file_)

    hourly_sim.to_csv(path_hourly_sim_result)
    annual_results_df.to_csv(path_annual_sim_result)

    Graphs_and_report(df=hourly_sim, season='heating_cooling').bui_analysis_page(
        folder_directory=dir_chart_folder,
        name_file=name_report)

    Q_H = annual_results_df['Q_H_annual'].values[0] / 1000
    Q_C = annual_results_df['Q_C_annual'].values[0] / 1000

    boiler_eff = 0.8
    PEF_fuel = 1.07
    SCOP = 3.2
    SEER = 3.0
    PEF_el = 2.6

    a_use = bui_new['a_use']
    dhw_demand_per_m2 = 22.3
    dhw_losses_percent = 0.20

    Q_dhw = a_use * dhw_demand_per_m2
    dhw_losses = Q_dhw * dhw_losses_percent
    Q_dhw_total = Q_dhw + dhw_losses

    final_dhw_boiler = Q_dhw_total / boiler_eff
    primary_dhw_boiler = final_dhw_boiler * PEF_fuel

    final_dhw_HP = Q_dhw_total / SCOP
    primary_dhw_HP = final_dhw_HP * PEF_el

    results = {
        'Q_H_annual (kWh)': Q_H,
        'Q_C_annual (kWh)': Q_C,
        'Final_H (boiler, kWh)': Q_H / boiler_eff,
        'Final_H (HP, kWh)': Q_H / SCOP,
        'Final_C (HP, kWh)': Q_C / SEER,
        'Primary_H (boiler, PEF 1.07)': (Q_H / boiler_eff) * PEF_fuel,
        'Primary_H (HP, PEF 2.6)': (Q_H / SCOP) * PEF_el,
        'Primary_C (HP, PEF 2.6)': (Q_C / SEER) * PEF_el,
        'Q_DHW_total (kWh)': Q_dhw_total,
        'Final_DHW (boiler, kWh)': final_dhw_boiler,
        'Primary_DHW (boiler, PEF 1.07)': primary_dhw_boiler,
        'Final_DHW (HP, kWh)': final_dhw_HP,
        'Primary_DHW (HP, PEF 2.6)': primary_dhw_HP
    }

    df_energy = pd.DataFrame([results])
    energy_result_path = os.path.join(dir_chart_folder, "energy_converted_building_2001.csv")
    df_energy.to_csv(energy_result_path, index=False)

    print(f"Ολοκληρώθηκε η προσομοίωση για το κτήριο του 2001:\n{energy_result_path}")

if __name__ == "__main__":
    main(
        bui_new=user_bui,
        weather_type='epw',
        path_weather_file_=weather_file_path,
        path_hourly_sim_result=file_dir + "/Result2/hourly_sim_building_2001.csv",
        path_annual_sim_result=file_dir + "/Result2/annual_sim_building_2001.csv",
        dir_chart_folder=file_dir + "/Result2",
        name_report="building_2001_report"
    )
