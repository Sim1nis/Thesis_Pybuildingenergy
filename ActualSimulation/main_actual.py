# main_actual.py
import os
import sys
import pandas as pd
from pybuildingenergy.source.utils import ISO52016
from pybuildingenergy.source.graphs import Graphs_and_report
from pybuildingenergy.data.building_archetype import Buildings_from_dictionary

# Προσθήκη τρέχοντος φακέλου στο path για local import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from input_utils import build_actual_bui_from_json

# === Δημιουργία φακέλου αποθήκευσης αν δεν υπάρχει ===
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Ορισμός διαδρομών
file_dir = os.path.dirname(os.path.realpath(__file__))
result_dir = os.path.join(file_dir, "Result")
ensure_directory_exists(result_dir)

# === Δημιουργία actual bui από JSON input ===
json_directory = os.path.join(file_dir, "inputs")
user_bui = build_actual_bui_from_json(json_directory)

# === Ορισμός path αρχείου καιρού ===
weather_file_path = os.path.join(file_dir, "weather", "GRC_Athens_modified_for_kenak.epw")

# === Εκτέλεση Προσομοίωσης ===
def main():
    BUI = Buildings_from_dictionary(user_bui)
    # Προσοχή: Βάζουμε path_weather_file=weather_file_path και weather_source=None ή "custom"
    hourly_sim, annual_results_df = ISO52016().Temperature_and_Energy_needs_calculation(
        BUI, 
        weather_source=None,  # ή "custom", αν το απαιτεί η βιβλιοθήκη
        path_weather_file=weather_file_path
    )

    # Αποθήκευση αποτελεσμάτων
    hourly_sim_path = os.path.join(result_dir, "hourly_sim_actual.csv")
    annual_sim_path = os.path.join(result_dir, "annual_sim_actual.csv")
    hourly_sim.to_csv(hourly_sim_path)
    annual_results_df.to_csv(annual_sim_path)

    # Αναφορά
    Graphs_and_report(df=hourly_sim, season='heating_cooling').bui_analysis_page(
        folder_directory=result_dir,
        name_file="actual_building_report")

    print("Προσομοίωση actual κτηρίου ολοκληρώθηκε!")
    print(f"Αποτελέσματα: {annual_sim_path}")

if __name__ == "__main__":
    main()
