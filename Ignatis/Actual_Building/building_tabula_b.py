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
file_dir = os.path.dirname(os.path.realpath(__file__))  # Τρέχων φάκελος αρχείου
ensure_directory_exists(file_dir + "/Result_Tabula_B")  # Δημιουργία φακέλου Result αν δεν υπάρχει
result_dir = os.path.join(file_dir, "Result_Tabula_B")
ensure_directory_exists(result_dir)

# === Ορισμός σχετικής διαδρομής για το custom αρχείο καιρού (EPW) ===
weather_file_path = os.path.join(file_dir, "..", "weather", "GRC_Athens_modified_for_kenak.epw")
weather_file_path = os.path.abspath(weather_file_path)  # Απόλυτο path για το EPW αρχείο

# === Ορισμός παραμέτρων Actual Κτηρίου ===
user_bui = {
    'building_type': 'actual',
    'periods': 2005,
    'latitude': 37.98,
    'longitude': 23.72,
    'volume': 287.0,
    'exposed_perimeter': 50.0,
    'slab_on_ground': 114.8,
    'wall_thickness': 0.3,
    'coldest_month': 1,
    'a_use': 115.0,
    'surface_envelope': 572.8,
    'surface_envelope_model': 572.8,
    'annual_mean_internal_temperature': 20.0,
    'annual_mean_external_temperature': 15.0,

    'heating_mode': True,
    'cooling_mode': True,
    'heating_setpoint': 20,
    'cooling_setpoint': 26,
    'heating_setback': 10,
    'cooling_setback': 27,
    'power_heating_max': 10000,
    'power_cooling_max': -10000,

    'air_change_rate_base_value': 0.75,
    'air_change_rate_extra': 0.0,
    'internal_gains_base_value': 13.2,
    'internal_gains_extra': 0.0,
    'thermal_bridge_heat': 0.1,

    'typology_elements': np.array(["OP", "OP", "OP", "GR", "GR", "GR", "W", "W"], dtype=object),
    'orientation_elements': np.array(["NV", "SV", "EV", "HOR", "HOR", "HOR", "SV", "SV"], dtype=object),
    'solar_abs_elements': np.array([0.6, 0.6, 0.6, 0.6, 0.0, 0.0, 0.0, 0.0], dtype=object),
    'area_elements': [136.8, 54.5, 26.8, 45.0, 95.8, 135.0, 109.9, 27.0],
    'transmittance_U_elements': [0.7, 0.7, 0.7, 1.21, 0.83, 0.5, 1.9, 2.0],
    'thermal_resistance_R_elements': [1/0.7, 1/0.7, 1/0.7, 1/1.21, 1/0.83, 1/0.5, 1/1.9, 1/2.0],
    'thermal_capacity_elements': [250, 250, 250, 250, 250, 250, 0, 0],
    'thermal_resistance_floor': 1/0.83,
    'g_factor_windows': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6, 0.6],
    'visible_transmittance_windows': 0.65,

    'heat_convective_elements_internal': np.array([2.5]*8, dtype=object),
    'heat_radiative_elements_internal': np.array([5.13]*8, dtype=object),
    'heat_convective_elements_external': np.array([20.0]*8, dtype=object),
    'heat_radiative_elements_external': np.array([4.14]*8, dtype=object),

    'occ_level_wd': np.ones(24),
    'occ_level_we': np.ones(24),
    'comf_level_wd': np.ones(24),
    'comf_level_we': np.ones(24),

    'heating_period_start': (11, 1),
    'heating_period_end': (4, 1),
    'cooling_period_start': (5, 15),
    'cooling_period_end': (9, 15),

    'construction_class': 'class_i',
    'weather_source': 'epw',

    'user_glazing_Ug': 5.7
}

# === Συντελεστές σκίασης (sky factors) ===
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


# === Συνάρτηση εκτέλεσης προσομοίωσης ===
def main(bui_new: dict, weather_type: str, path_weather_file_: str,
         path_hourly_sim_result: str, path_annual_sim_result: str,
         dir_chart_folder: str, name_report: str):

    BUI = Buildings_from_dictionary(bui_new)  # Μετατροπή dict σε αντικείμενο κτηρίου

    # === Εκτέλεση προσομοίωσης ISO 52016 ===
    hourly_sim, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(
        BUI, weather_source=weather_type, path_weather_file=path_weather_file_)

    # === Αποθήκευση raw αποτελεσμάτων ===
    hourly_sim.to_csv(path_hourly_sim_result)
    annual_results_df.to_csv(path_annual_sim_result)

    # === Δημιουργία γραφικής αναφοράς ===
    Graphs_and_report(df=hourly_sim, season='heating_cooling').bui_analysis_page(
        folder_directory=dir_chart_folder,
        name_file=name_report)

    print(f"Η βασική προσομοίωση ολοκληρώθηκε!\n{path_annual_sim_result}")

       # === Ανάγνωση αποτελεσμάτων θέρμανσης/ψύξης ===
    Q_H = annual_results_df['Q_H_annual'].values[0] / 1000  # Wh → kWh
    Q_C = annual_results_df['Q_C_annual'].values[0] / 1000

    # === Παράμετροι συστημάτων ===
    boiler_eff = 0.96           # Απόδοση λέβητα
    PEF_fuel = 1.1              # ΠΕΦ για πετρέλαιο
    SCOP = 3.2                  # Αντλία θερμότητας (θέρμανση)
    SEER = 3.0                  # Αντλία θερμότητας (ψύξη)
    PEF_el = 2.83               # ΠΕΦ ηλεκτρισμού (για ΖΝΧ)

    # === Υπολογισμός ΖΝΧ μόνο με ηλεκτρικό θερμοσίφωνα (όπως TABULA) ===
    a_use = bui_new['a_use']
    dhw_demand_per_m2 = 14.0
    dhw_losses_percent = 0.83  # (39.6 / 14.0 - 1)

    Q_dhw = a_use * dhw_demand_per_m2
    dhw_losses = Q_dhw * dhw_losses_percent
    Q_dhw_total = Q_dhw + dhw_losses

    final_dhw_electric = Q_dhw_total
    primary_dhw_electric = final_dhw_electric * PEF_el

    # === Απώλειες διανομής θέρμανσης όπως στο TABULA (~6.2 kWh/m²·y) ===
    dist_losses = 6.2 * a_use  # σε kWh

    # === Υπολογισμός τελικής & πρωτογενούς ενέργειας ===
    results = {
        'Q_H_annual (kWh)': Q_H,
        'Q_C_annual (kWh)': Q_C,

        'Final_H (boiler, kWh)': Q_H / boiler_eff,
        'Final_H (HP, kWh)': Q_H / SCOP,
        'Final_C (HP, kWh)': Q_C / SEER,

        'Primary_H (boiler, PEF 1.1)': (Q_H / boiler_eff) * PEF_fuel,
        'Primary_H (HP, PEF 2.6)': (Q_H / SCOP) * PEF_el,
        'Primary_C (HP, PEF 2.6)': (Q_C / SEER) * PEF_el,

        'Q_DHW_total (kWh)': Q_dhw_total,

        # Μηδενισμός boiler για ΖΝΧ (σύμφωνα με TABULA)
        'Final_DHW (boiler, kWh)': 0.0,
        'Primary_DHW (boiler, PEF 1.1)': 0.0,

        # ΖΝΧ μόνο ηλεκτρικό (τύπου ηλεκτρικός θερμοσίφωνας)
        'Final_DHW (HP, kWh)': final_dhw_electric,
        'Primary_DHW (HP, PEF 2.6)': primary_dhw_electric,

        # Νέα: Προσθήκη απωλειών διανομής
        'Distribution_losses (kWh)': dist_losses,

        # Τελική συνολική ΠΡΩΤΟΓΕΝΗΣ ενέργεια (πετρέλαιο + ΖΝΧ + απώλειες)
        'Primary_Total_adjusted (kWh)': (Q_H / boiler_eff) * PEF_fuel + primary_dhw_electric + dist_losses
    }


    # === Αποθήκευση αρχείου .csv με αποτελέσματα ===
    df_energy = pd.DataFrame([results])
    energy_result_path = os.path.join(dir_chart_folder, "energy_converted_tabula_b.csv")
    df_energy.to_csv(energy_result_path, index=False)

    print(f"Υπολογίστηκαν τελική και πρωτογενής ενέργεια (με ΖΝΧ):\n{energy_result_path}")


# === Εκτέλεση προσομοίωσης ===
if __name__ == "__main__":
    main(
    bui_new=user_bui,
    weather_type='epw',
    path_weather_file_=weather_file_path,
    path_hourly_sim_result=os.path.join(result_dir, "hourly_sim_tabula_b.csv"),
    path_annual_sim_result=os.path.join(result_dir, "annual_sim_tabula_b.csv"),
    dir_chart_folder=result_dir,
    name_report="tabula_b_building_report"
)
