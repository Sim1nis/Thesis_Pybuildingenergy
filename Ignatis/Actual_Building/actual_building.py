## Πόσοι μένουν στο σπίτι	3	
## Πόσα υπνοδωμάτια έχει	3	
## Πότε χτίστηκε	1979	
## Αν έγινε ριζική ανακαίνιση (και πότε)	δεν εγινε	
## Κλιματική ζώνη	Α	
## Τύπος Τοίχων	Μπετό	3,65
## Τύπος Τελικής Επιφάνειας	χωρίς σοβά (γυμνό)	
## Τύπος Στέγης	Συμβατικού τύπου δώμα	3,05
## Τύπος  Δαπέδου	Επάνω από ανοικτό υπόστυλο χώρο (πιλοτή)	2,75
## Τύπος Παραθύρων	Μονός υαλοπίνακας	Ug = 5,7
## Τύπος λέβητα	Λέβητας (χωρίς στοιχεία)	0,75
## Τύπος καυσίμου	Πετρέλαιο	1,07



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
ensure_directory_exists(file_dir + "/Result")  # Δημιουργία φακέλου Result αν δεν υπάρχει

# === Ορισμός σχετικής διαδρομής για το custom αρχείο καιρού (EPW) ===
weather_file_path = os.path.join(file_dir, "..", "weather", "GRC_Athens_modified_for_kenak.epw")
weather_file_path = os.path.abspath(weather_file_path)  # Απόλυτο path για το EPW αρχείο

# === Ορισμός παραμέτρων Actual Κτηρίου ===
user_bui = {
    'building_type': 'actual',                               # Πραγματικό κτήριο
    'periods': 1979,                                         # Έτος κατασκευής
    'latitude': 37.98, 'longitude': 23.72,                   # Συντεταγμένες Αθήνας
    'volume': 250.0,                                         # Όγκος 
    'exposed_perimeter': 50.0,                               # Εκτεθειμένη περίμετρος
    'slab_on_ground': 100.0,                                 # Εμβαδόν δαπέδου
    'wall_thickness': 0.3,                                   # Πάχος τοιχοποιίας
    'coldest_month': 1,                                      # Ψυχρότερος μήνας
    'a_use': 100.0,                                          # Χρήσιμη επιφάνεια
    'surface_envelope': 288.0, 
    'surface_envelope_model': 288.0,
    'annual_mean_internal_temperature': 20.0,                # Εσωτερική θερμοκρασία
    'annual_mean_external_temperature': 15.0,                # Εξωτερική θερμοκρασία

    # === Ρυθμίσεις θέρμανσης και ψύξης ===
    'heating_mode': True, 'cooling_mode': True,
    'heating_setpoint': 20, 'cooling_setpoint': 26,
    'heating_setback': 10, 'cooling_setback': 27,
    'power_heating_max': 10000, 'power_cooling_max': -10000,

    # === Αερισμός και εσωτερικά κέρδη ===
    'air_change_rate_base_value': 0.75, 'air_change_rate_extra': 0.0,
    'internal_gains_base_value': 8.9, 'internal_gains_extra': 0.0,
    'thermal_bridge_heat': 0.0,

    # === Δομικά στοιχεία (U-values, επιφάνειες, προσανατολισμοί) ===
    'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"], dtype=object),
    'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'], dtype=object),
    'solar_abs_elements': np.array([0.6, 0.6, 0.6, 0.6, 0.0, 0.6, 0.0], dtype=object),
    'area_elements': [21.6, 9.6, 16.2, 16.2, 48.0, 48.0, 12.0],
    'transmittance_U_elements': [3.65, 3.65, 3.65, 3.65, 3.05, 3.05, 5.7],
    'thermal_resistance_R_elements': [0.274, 0.274, 0.274, 0.274, 0.328, 0.328, 0.175],
    'thermal_capacity_elements': [250, 250, 250, 250, 250, 250, 0],
    'thermal_resistance_floor': 0.364,
    'g_factor_windows': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.76],
    'visible_transmittance_windows': 0.65,
    'heat_convective_elements_internal': np.array([2.5, 2.5, 2.5, 2.5, 0.7, 5.0, 2.5], dtype=object),
    'heat_radiative_elements_internal': np.array([5.13]*7, dtype=object),
    'heat_convective_elements_external': np.array([20.0]*7, dtype=object),
    'heat_radiative_elements_external': np.array([4.14]*7, dtype=object),

    # === Πληρότητα και άνεση (18 ώρες) ===
    'occ_level_wd': np.array([1]*18 + [0]*6),
    'occ_level_we': np.array([1]*18 + [0]*6),
    'comf_level_wd': np.array([1]*18 + [0]*6),
    'comf_level_we': np.array([1]*18 + [0]*6),

    # === Περίοδοι λειτουργίας ===
    'heating_period_start': (11, 1), 'heating_period_end': (4, 1),
    'cooling_period_start': (5, 15), 'cooling_period_end': (9, 15),

    'construction_class': 'class_i',
    'weather_source': 'epw',
    'user_glazing_type': 'Μονός υαλοπίνακας',
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
    boiler_eff = 0.75     # Απόδοση λέβητα
    PEF_fuel = 1.07       # ΠΕΦ για πετρέλαιο
    SCOP = 3.2            # Αντλία θερμότητας (θέρμανση)
    SEER = 3.0            # Αντλία θερμότητας (ψύξη)
    PEF_el = 2.6          # ΠΕΦ ηλεκτρισμού

    # === Υπολογισμός ΖΝΧ ===
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

    # === Υπολογισμός τελικής & πρωτογενούς ενέργειας ===
    results = {
        'Q_H_annual (kWh)': Q_H,                                 # Ετήσια θερμική ενέργεια θέρμανσης
        'Q_C_annual (kWh)': Q_C,                                 # Ετήσια θερμική ενέργεια ψύξης

        'Final_H (boiler, kWh)': Q_H / boiler_eff,               # Τελική θέρμανση με λέβητα
        'Final_H (HP, kWh)': Q_H / SCOP,                         # Τελική θέρμανση με αντλία θερμότητας
        'Final_C (HP, kWh)': Q_C / SEER,                         # Τελική ψύξη με αντλία θερμότητας

        'Primary_H (boiler, PEF 1.1)': (Q_H / boiler_eff) * PEF_fuel,     # Πρωτογενής θέρμανση με λέβητα
        'Primary_H (HP, PEF 2.6)': (Q_H / SCOP) * PEF_el,                 # Πρωτογενής θέρμανση με HP
        'Primary_C (HP, PEF 2.6)': (Q_C / SEER) * PEF_el,                 # Πρωτογενής ψύξη με HP

        'Q_DHW_total (kWh)': Q_dhw_total,                       # Συνολική ενέργεια ΖΝΧ (με απώλειες)
        'Final_DHW (boiler, kWh)': final_dhw_boiler,            # Τελική ΖΝΧ με λέβητα
        'Primary_DHW (boiler, PEF 1.1)': primary_dhw_boiler,    # Πρωτογενής ΖΝΧ με λέβητα
        'Final_DHW (HP, kWh)': final_dhw_HP,                    # Τελική ΖΝΧ με αντλία θερμότητας
        'Primary_DHW (HP, PEF 2.6)': primary_dhw_HP             # Πρωτογενής ΖΝΧ με αντλία θερμότητας
    }

    # === Αποθήκευση αρχείου .csv με αποτελέσματα ===
    df_energy = pd.DataFrame([results])
    energy_result_path = os.path.join(dir_chart_folder, "energy_converted_actual.csv")
    df_energy.to_csv(energy_result_path, index=False)

    print(f"Υπολογίστηκαν τελική και πρωτογενής ενέργεια (με ΖΝΧ):\n{energy_result_path}")


# === Εκτέλεση προσομοίωσης ===
if __name__ == "__main__":
    main(
        bui_new=user_bui,
        weather_type='epw',
        path_weather_file_=weather_file_path,
        path_hourly_sim_result=file_dir + "/Result/hourly_sim_actual.csv",
        path_annual_sim_result=file_dir + "/Result/annual_sim_actual.csv",
        dir_chart_folder=file_dir + "/Result",
        name_report="actual_building_report"
    )
