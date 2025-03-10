import os
import numpy as np
import subprocess
import random

def dat_to_csv(dat_file: str, generic_file: str, csv_file: str):
    """
    Convert BESA .dat + .generic to a single CSV file with columns:
      Time, Chan1, Chan2, ...
    """
    if not os.path.exists(dat_file) or not os.path.exists(generic_file):
        raise FileNotFoundError(f"Missing {dat_file} or {generic_file}")

    # Parse .generic to find nChannels, nSamples, sRate
    header_info = {}
    with open(generic_file, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                header_info[key.strip()] = val.strip()

    n_channels = int(header_info.get("nChannels", 0))
    n_samples  = int(header_info.get("nSamples", 0))
    s_rate     = float(header_info.get("sRate", 500.0))

    # Read the float32 data
    raw_data = np.fromfile(dat_file, dtype=np.float32)
    if raw_data.size != (n_channels * n_samples):
        raise ValueError("Mismatch reading .dat: expected "
                         f"{n_channels*n_samples} floats, got {raw_data.size}.")

    raw_data = raw_data.reshape((n_channels, n_samples))
    time_axis = np.arange(n_samples) / s_rate

    # Write CSV
    with open(csv_file, "w") as out_f:
        headers = ["Time"] + [f"Chan{i+1}" for i in range(n_channels)]
        out_f.write(",".join(headers) + "\n")

        for idx in range(n_samples):
            row_vals = [f"{time_axis[idx]:.5f}"] + [
                f"{val:.5f}" for val in raw_data[:, idx]
            ]
            out_f.write(",".join(row_vals) + "\n")


import os
import random
import math

def make_simbat_file(Sensor_file, Mod_file, temp_outputs, num, num_files):
    for i in range(num_files):
        # Create a unique .mod file for this simulation
        mod_filename = os.path.basename(Mod_file).replace(".mod", f"_temp_{i + 1}.mod")
        new_mod_path = os.path.join(temp_outputs, mod_filename)

        # Copy the original .mod file content
        with open(Mod_file, "r") as f:
            mod_content = f.readlines()

        # Generate 1-4 noise sources
        num_noise_sources = random.randint(1, 4)
        noise_sources = []
        for n in range(num_noise_sources):
            # Random location
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            z = random.uniform(0, 1)  # Per Constraints z=0 1
            # Random orientation (ox, oy, oz between -1 and 1)
            ox = random.uniform(-1, 1)
            oy = random.uniform(-1, 1)
            oz = random.uniform(-1, 1)
            # Random amplitude bounds between 0.1 and 0.4 µV
            lower_bound = random.uniform(0.1, 0.3)  # Ensure lower < upper
            upper_bound = random.uniform(lower_bound, 0.7)
            # Convert µV to nAm (1 µV ≈ 0.1 nAm)
            lower_bound_nam = round(lower_bound * 0.1, 6)  # Round to 6 decimal places
            upper_bound_nam = round(upper_bound * 0.1, 6)  # Round to 6 decimal places
            # Random frequency: oscillate every 10 to 30 samples
            freq_samples = random.randint(10, 30)
            # Generate oscillating waveform (333 points)
            waveform = []
            for t in range(250):
                # Use a sinusoidal oscillation between lower and upper bounds
                phase = (2 * math.pi * t) / freq_samples
                # Map sine wave (-1 to 1) to [lower_bound_nam, upper_bound_nam]
                amplitude = lower_bound_nam + (upper_bound_nam - lower_bound_nam) * (math.sin(phase) + 1) / 2
                waveform.append(round(amplitude, 6))  # Round each amplitude value
            # Create the noise source line
            noise_line = (
                f"{x:.6f}\t{y:.6f}\t{z:.6f}\t{ox:.6f}\t{oy:.6f}\t{oz:.6f}\t0\t333\t250\t"
                + "\t".join(f"{amp:.6e}" for amp in waveform)
                + "\n"
            )
            noise_sources.append(noise_line)

        # Write the new .mod file with noise sources
        with open(new_mod_path, "w") as f:
            f.writelines(mod_content)  # Original content
            f.writelines(noise_sources)  # Append noise sources

        # Create the .simbat file
        simbat_path = f"C:/Users/PHELANLE/PycharmProjects/Testing_batch/unified_generation_pipeline/source_files/generated_{num + 1}_{i + 1}.simbat"
        simbat_script = [
            "Logging off",
            f"SensorsLoad \"{Sensor_file}\"",
            "Settings samples=333",
            "Settings interval=2.0",
            "Settings baselinesamples=50",
            "HeadModel default",
            "Constraints x=-1 1 y=-1 1 z=0 1 ecc=0.1 0.9",
            "ModelClear noquery",
            f"ModelLoad \"{new_mod_path}\"",
            f"Settings currentrawfolder=\"{temp_outputs}\"",
            f"RawData ntrigs=1 target=\"temp_{i + 1}.dat\"",
            "RawData go",
            f"DataSave \"temp_{i + 1}\" gen",
            f"ModelSave \"{os.path.join(temp_outputs, 'saved_model')}\""
        ]

        simbat_file = simbat_path
        with open(simbat_file, "w") as f:
            f.write("\n".join(simbat_script))


def run_besa_simulation(simbat_path):

    BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"

    # Start BESA with the batch script, making the window visible
    proc = subprocess.Popen(
        [BESA_EXE, "-batchdisplay", simbat_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(simbat_path)
    )

    try:
        stdout, stderr = proc.communicate(timeout=600)
        print("BESA stdout:\n", stdout)
        print("BESA stderr:\n", stderr)
        log_path = os.path.join(os.path.dirname(simbat_path), "debug.log")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                print("Debug log:\n", f.read())
    except subprocess.TimeoutExpired:
        proc.kill()
        print("Process timed out or manually terminated")