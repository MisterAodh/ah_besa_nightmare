from functions import *
import subprocess
import os
import shutil

# Paths
BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"
Sensor_file = "C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/source_files/sensors.elp"
Artificial_data_storage = "C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/Artificial_data"
temporary_storage = "C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/temporary_outputs"
mod_folder = "C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/mod_files"
num_generated_per_mod = 400

for i in range(12):
    if i == 6:  # Skip if trying to process P7 (index 6)
        print(f"Skipping P7 mod file (index 6) as it does not exist.")
        continue
    output_folder = os.path.join(Artificial_data_storage, f"dataset_{i + 1}")
    os.makedirs(output_folder, exist_ok=True)
    mod_file_name = f"P{i + 1}_NormalVision.mod"
    original_mod_path = os.path.join(mod_folder, mod_file_name)

    # Generate .simbat files with unique .mod files
    make_simbat_file(Sensor_file, original_mod_path, temporary_storage, i, num_generated_per_mod)

    for j in range(num_generated_per_mod):
        simbat_path = f"C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/source_files/generated_{i + 1}_{j + 1}.simbat"
        run_besa_simulation(simbat_path)
        dat_file_path = temporary_storage + f"/temp_{j + 1}.dat"
        generic_file_path = temporary_storage + f"/temp_{j + 1}.generic"
        csv_file_path = output_folder + f"/data_{j + 1}.csv"
        dat_to_csv(dat_file_path, generic_file_path, csv_file_path)

        # Delete generated simbat files after processing
        simbat_pattern = f"generated_{i + 1}_{j + 1}.simbat"
        simbat_full_path = os.path.join(
            "C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/source_files", simbat_pattern)
        if os.path.exists(simbat_full_path):
            os.remove(simbat_full_path)

    # Delete temporary files (including generated .mod files)
    for file in os.listdir(temporary_storage):
        os.remove(os.path.join(temporary_storage, file))