
import subprocess
import os

# Paths
BESA_EXE = r"C:\Program Files (x86)\BESA\Simulator\BesaSimulator.exe"
simbat_path = r"C:\Users\PHELANLE/PycharmProjects/Testing_batch/output/generated.simbat"

# Start BESA with the batch script, making the window visible
proc = subprocess.Popen(
    [BESA_EXE, "-batchdisplay", simbat_path],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(simbat_path)
)

# Optionally wait for user confirmation or let it run
try:
    stdout, stderr = proc.communicate(timeout=600)  # 10-minute timeout as a safety net
    print("BESA stdout:\n", stdout)
    print("BESA stderr:\n", stderr)
    log_path = os.path.join(os.path.dirname(simbat_path), "debug.log")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            print("Debug log:\n", f.read())
except subprocess.TimeoutExpired:
    proc.kill()
    print("Process timed out or manually terminated")
