import numpy as np
from tabulate import tabulate
import requests
import importlib.util
import sys
import os

decimal_places = 4  

url = "https://github.com/Lab2Phys/module-RLC/raw/refs/heads/main/module_RLC.so"
so_filename = "module_RLC.so"

try:
    response = requests.get(url)
    response.raise_for_status()
    with open(so_filename, "wb") as f:
        f.write(response.content)
    print("Downloaded module_RLC.so successfully")
except requests.RequestException as e:
    print(f"Error downloading module_RLC.so: {e}")
    raise

spec = importlib.util.spec_from_file_location("module_RLC", os.path.abspath(so_filename))
module_RLC = importlib.util.module_from_spec(spec)
sys.modules["module_RLC"] = module_RLC
spec.loader.exec_module(module_RLC)

np.set_printoptions(precision=decimal_places)

N = 6
f = 40
veff = 5
w = 2 * np.pi * f

R = 1000
L = 10e-3
c1 = 680e-9
c2 = 220e-9

i = 1j
x = i * L * w
x1 = 1 / (i * c1 * w)
x2 = 1 / (i * c2 * w)

edges = [
    (1, 2, x + x1), (1, 3, R + x1), (1, 4, R + x2), (2, 3, R + x2),
    (2, 4, R), (2, 5, R + x1), (2, 6, x + x2), (3, 5, R + x),
    (4, 6, x1 + x2), (5, 6, R)
]

source_branch_nodes = (2, 4)
ref_node = 6
pdf_filename = 'Exp.pdf'

T_currents, T_voltages_all = module_RLC.analyze_circuit(N, edges, source_branch_nodes, veff, i, ref_node)

print("\n\nBranch currents table:")
headers_currents = ["Node i", "Node j", "|I(i,j)| (mA)"]
table_data_currents_for_terminal = [
    [int(row[0]), int(row[1]), f"{row[2] * 1000:.{decimal_places}f}"]
    for row in T_currents
]
print(tabulate(table_data_currents_for_terminal, headers=headers_currents, tablefmt="grid",
               numalign="center", stralign="center"))

print("\n\nVoltage table between all node pairs:")
headers_voltages = ["Node i", "Node j", "|V(i,j)| (V)", "Phase (deg)"]
table_data_voltages_for_terminal = [
    [int(row[0]), int(row[1]), f"{row[2]:.{decimal_places}f}", f"{row[3]:.{decimal_places}f}"]
    for row in T_voltages_all
]
print(tabulate(table_data_voltages_for_terminal, headers=headers_voltages, tablefmt="grid",
               numalign="center", stralign="center"))

module_RLC.display_node_pair_selector(T_currents, T_voltages_all, decimal_places)
module_RLC.save_results_to_pdf(pdf_filename, T_currents, T_voltages_all, decimal_places)

