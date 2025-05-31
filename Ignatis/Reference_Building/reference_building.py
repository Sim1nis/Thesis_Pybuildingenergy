import numpy as np
import os
import pandas as pd
from pybuildingenergy.source.utils import ISO52016
from pybuildingenergy.source.graphs import Graphs_and_report
from pybuildingenergy.data.building_archetype import Buildings_from_dictionary

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# Ορισμός του directory για αποθήκευση των αποτελεσμάτων
file_dir = os.path.dirname(os.path.realpath(__file__))
ensure_directory_exists(file_dir + "/Result")

weather_file_path = os.path.join(file_dir, "..", "weather", "GRC_Athens_modified_for_kenak.epw")
weather_file_path = os.path.abspath(weather_file_path)


# === Ορισμός παραμέτρων Reference Κτηρίου βάσει ΚΕΝΑΚ ===
user_bui = {
    # Γενικά χαρακτηριστικά κτηρίου (ΚΕΝΑΚ - γεωμετρία, κλίμα, χρήση)
    'building_type': 'reference',              # Τύπος reference κτηρίου
    'periods': 2020,                            # Έτος κατασκευής (τυπικά: reference period)
    'latitude': 37.98,                          # Γεωγραφικό πλάτος - Αθήνα
    'longitude': 23.72,                         # Γεωγραφικό μήκος - Αθήνα
    'volume': 250.0,                            # Όγκος κτηρίου (m³)
    'exposed_perimeter': 50.0,                  # Εκτεθειμένη περίμετρος (m)
    'slab_on_ground': 100.0,                    # Εμβαδόν δαπέδου σε επαφή με το έδαφος (m²)
    'wall_thickness': 0.3,                      # Πάχος τοιχοποιίας (m)
    'coldest_month': 1,                         # Ψυχρότερος μήνας (Ιανουάριος)
    'a_use': 100.0,                             # Χρήσιμη επιφάνεια (m²)
    'surface_envelope': 288.0,                  # Συνολική εξωτερική επιφάνεια (m²)
    'surface_envelope_model': 288.0,            # Εξωτερική επιφάνεια για μοντελοποίηση (m²)
    'annual_mean_internal_temperature': 20.0,   # Εσωτερική θερμοκρασία (°C)
    'annual_mean_external_temperature': 15.0,   # Μέση εξωτερική θερμοκρασία (°C)

    # Ρυθμίσεις θέρμανσης και ψύξης (βάσει ΚΕΝΑΚ)
    'heating_mode': True,
    'cooling_mode': True,
    'heating_setpoint': 20,                     # Θερμοκρασία ρύθμισης θέρμανσης (°C)
    'cooling_setpoint': 27,                     # Θερμοκρασία ρύθμισης ψύξης (°C)
    'heating_setback': 10,                      # Θερμοκρασία setback θέρμανσης (°C)
    'cooling_setback': 27,                      # Θερμοκρασία setback ψύξης (°C)
    'power_heating_max': 10000,                 # Μέγιστη ισχύς θέρμανσης (W)
    'power_cooling_max': -10000,                # Μέγιστη ισχύς ψύξης (W)

    # Εσωτερικά κέρδη και αερισμός (σύμφωνα με ΚΕΝΑΚ)
    'air_change_rate_base_value': 1.41,         # Συνολικός ρυθμός αερισμού (m³/h·m²)
    'air_change_rate_extra': 0.0,
    'internal_gains_base_value': 5.0,           # Εσωτερικά κέρδη (W/m²)
    'internal_gains_extra': 0.0,
    'thermal_bridge_heat': 0.0,                 # Θερμικές γέφυρες (W/K)

    # Δομικά στοιχεία - στοιχεία φακέλου (U-values & επιφάνειες κατά ΚΕΝΑΚ Ζώνη Γ)
    'typology_elements': np.array(["OP", "OP", "OP", "OP", "GR", "OP", "W"], dtype=object),
    'orientation_elements': np.array(['NV', 'SV', 'EV', 'WV', 'HOR', 'HOR', 'SV'], dtype=object),
    'solar_abs_elements': np.array([0.6, 0.6, 0.6, 0.6, 0.0, 0.6, 0.0], dtype=object),
    'area_elements': [21.6, 9.6, 16.2, 16.2, 48.0, 48.0, 12.0],
    'transmittance_U_elements': [0.44, 0.44, 0.44, 0.44, 0.38, 0.35, 2.8],  # U-values (W/m²·K)
    'thermal_resistance_R_elements': [2.27, 2.27, 2.27, 2.27, 2.63, 2.86, 0.36],  # 1/U για έλεγχο
    'thermal_capacity_elements': [250, 250, 250, 250, 250, 250, 0],
    'thermal_resistance_floor': 2.63,
    'g_factor_windows': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.76],             # g-value για παράθυρα (GT = 0.76 ΚΕΝΑΚ)
    'heat_convective_elements_internal': np.array([2.5, 2.5, 2.5, 2.5, 0.7, 5.0, 2.5], dtype=object),
    'heat_radiative_elements_internal': np.array([5.13]*7, dtype=object),
    'heat_convective_elements_external': np.array([20.0]*7, dtype=object),
    'heat_radiative_elements_external': np.array([4.14]*7, dtype=object),

    # Καμπύλες πληρότητας και άνεσης (σταθερές για reference)
    'occ_level_wd': np.ones(24),
    'occ_level_we': np.ones(24),
    'comf_level_wd': np.ones(24),
    'comf_level_we': np.ones(24),

    'construction_class': 'class_i',
    'weather_source': 'epw',    

    # GV - Ορατή διαπερατότητα (δεν επηρεάζει αλλά καταγράφεται)
    'visible_transmittance_windows': 0.65
}

# === Ανάθεση shading factors ανά orientation (σύμφωνα με ΚΕΝΑΚ) ===
sky_factors = []
orientations = user_bui['orientation_elements']
types = user_bui['typology_elements']

for typ, orient in zip(types, orientations):
    if typ == "W":
        if orient == 'SV':
            sky_factors.append(0.5)  # Νότια όψη
        elif orient in ['EV', 'WV']:
            sky_factors.append(0.6)  # Ανατολή/Δύση
        else:
            sky_factors.append(0.7)  # Βόρεια ή άλλη
    else:
        sky_factors.append(0.9)      # Αδιαφανή στοιχεία

user_bui['sky_factor_elements'] = np.array(sky_factors)


# === Συνάρτηση κύριας εκτέλεσης προσομοίωσης ===
def main(bui_new: dict, weather_type: str, path_weather_file_: str,
         path_hourly_sim_result: str, path_annual_sim_result: str,
         dir_chart_folder: str, name_report: str):

    # Δημιουργία αντικειμένου κτηρίου
    BUI = Buildings_from_dictionary(bui_new)
    # Προσομοίωση ISO 52016 για θερμικές ανάγκες (θέρμανση/ψύξη)
    hourly_sim, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(
        BUI, weather_source=weather_type, path_weather_file=path_weather_file_)

    # Αποθήκευση αρχείων εξόδου
    hourly_sim.to_csv(path_hourly_sim_result)
    annual_results_df.to_csv(path_annual_sim_result)

    # Δημιουργία αναφοράς με γραφήματα
    Graphs_and_report(df=hourly_sim, season='heating_cooling').bui_analysis_page(
        folder_directory=dir_chart_folder,
        name_file=name_report)

    print(f"Η βασική προσομοίωση ολοκληρώθηκε!\n{path_annual_sim_result}")

    # === Υπολογισμός τελικής & πρωτογενούς ενέργειας ===
    Q_H = annual_results_df['Q_H_annual'].values[0] / 1000  # από Wh σε kWh
    Q_C = annual_results_df['Q_C_annual'].values[0] / 1000

    boiler_eff = 0.85   # Εποχιακός βαθμός απόδοσης λέβητα
    SCOP = 3.2          # Αντλία θερμότητας - θέρμανση
    SEER = 3.0          # Αντλία θερμότητας - ψύξη
    PEF_el = 2.6        # Συντελεστής πρωτογενούς ενέργειας ρεύματος
    PEF_fuel = 1.1      # Συντελεστής ΠΕ για πετρέλαιο/φυσικό αέριο

    # === Υπολογισμός ΖΝΧ ===
    a_use = bui_new['a_use']
    dhw_demand_per_m2 = 30           # Τυπική απαίτηση ΖΝΧ (kWh/m²)
    dhw_losses_percent = 0.20        # Απώλειες 20% (χωρίς επανακυκλοφορία)

    Q_dhw = a_use * dhw_demand_per_m2
    dhw_losses = Q_dhw * dhw_losses_percent
    Q_dhw_total = Q_dhw + dhw_losses

    final_dhw_boiler = Q_dhw_total / boiler_eff
    primary_dhw_boiler = final_dhw_boiler * PEF_fuel

    final_dhw_HP = Q_dhw_total / SCOP
    primary_dhw_HP = final_dhw_HP * PEF_el

    # === Δημιουργία αποτελεσμάτων ===
    results = {
        'Q_H_annual (kWh)': Q_H,                            # Ετήσια θερμική ενέργεια για θέρμανση (από ISO 52016)
        'Q_C_annual (kWh)': Q_C,                            # Ετήσια θερμική ενέργεια για ψύξη

        'Final_H (boiler, kWh)': Q_H / boiler_eff,          # Τελική ενέργεια θέρμανσης με λέβητα
        'Final_H (HP, kWh)': Q_H / SCOP,                    # Τελική ενέργεια θέρμανσης με αντλία θερμότητας
        'Final_C (HP, kWh)': Q_C / SEER,                    # Τελική ενέργεια ψύξης με αντλία θερμότητας

        'Primary_H (boiler, PEF 1.1)': (Q_H / boiler_eff) * PEF_fuel,       # Πρωτογενής ενέργεια θέρμανσης με λέβητα
        'Primary_H (HP, PEF 2.6)': (Q_H / SCOP) * PEF_el,                   # Πρωτογενής ενέργεια θέρμανσης με HP
        'Primary_C (HP, PEF 2.6)': (Q_C / SEER) * PEF_el,                   # Πρωτογενής ενέργεια ψύξης με HP

        'Q_DHW_total (kWh)': Q_dhw_total,                           # Ετήσια απαίτηση για ΖΝΧ (συμπ. απώλειες)
        'Final_DHW (boiler, kWh)': final_dhw_boiler,                # Τελική ενέργεια ΖΝΧ με λέβητα
        'Primary_DHW (boiler, PEF 1.1)': primary_dhw_boiler,        # Πρωτογενής ενέργεια ΖΝΧ με λέβητα
        'Final_DHW (HP, kWh)': final_dhw_HP,                        # Τελική ενέργεια ΖΝΧ με αντλία θερμότητας
        'Primary_DHW (HP, PEF 2.6)': primary_dhw_HP                 # Πρωτογενής ενέργεια ΖΝΧ με αντλία θερμότητας
    }

    # Αποθήκευση αποτελεσμάτων σε .csv
    df_energy = pd.DataFrame([results])
    energy_result_path = os.path.join(dir_chart_folder, "energy_converted_reference.csv")
    df_energy.to_csv(energy_result_path, index=False)

    print(f"Υπολογίστηκαν τελική και πρωτογενής ενέργεια (με ΖΝΧ):\n{energy_result_path}")


# === Εκτέλεση προσομοίωσης ===
if __name__ == "__main__":
    main(
        bui_new=user_bui,
        weather_type='epw',                         
        path_weather_file_=weather_file_path,        
        path_hourly_sim_result=file_dir + "/Result/hourly_sim_reference.csv",
        path_annual_sim_result=file_dir + "/Result/annual_sim_reference.csv",
        dir_chart_folder=file_dir + "/Result",
        name_report="reference_building_report"
    )
