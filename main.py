# %%
import numpy as np
from math import sqrt
# import tensorflow as tf
import matplotlib.pyplot as plt
from scipy.optimize import minimize, Bounds, minimize_scalar
import pickle
import Modal
from ansys.mapdl.core import launch_mapdl
import pandas as pd
import time
from materials import get_material_properties

"Parameters"
sample = "M_all_15"
modes = 6
maxiter = 200

start_time = time.time()
iteration_counter = {"count": 0}

run_mode = 'SIM'
job_name = 'testrun'

def check_material_stability(E_x, E_y, E_z, PR_xy, PR_yz, PR_xz):
    expr = 1.0 - (PR_xy**2 * E_y / E_x) - (PR_yz**2 * E_z / E_y) - (PR_xz**2 * E_z / E_x) \
           - 2.0 * PR_xy * PR_yz * PR_xz * E_z / E_x
    return expr > 0

mapdl = launch_mapdl(jobname=job_name, nproc=4, override=True, cleanup_on_exit=True)

"Experimental"
df = pd.read_excel("Modal_data.xlsx", index_col=0)
Fexp_total = df.loc[sample].to_numpy()
Fexp=Fexp_total[:modes]

# df = pd.read_excel("MAC_data.xlsx", sheet_name=sample)
# df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
# df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
# df = df.set_index(df.columns[0])
# uz_exp = df.to_numpy()


def objectivefunc(x):
    iteration_counter["count"] += 1
    iter_num = iteration_counter["count"]
    
    print(f"\n--- Iteração {iter_num} ---")
    print(f"Parâmetros atuais: {x}")
    #E2_x, E2_y = x
    E1_x, E1_y, E1_z, G1_xy, G1_yz, G1_xz = x
    
    mats = get_material_properties()
    PRXY = mats["PU"]["PR_xy"]
    PRYZ = mats["PU"]["PR_yz"]
    PRXZ = mats["PU"]["PR_xz"]

    if not check_material_stability(E1_x, E1_y, E1_z, PRXY, PRYZ, PRXZ):
        print(f"Iteração {iter_num}: Material instável. Pulando simulação.")
        return 1e6

    # Start measuring execution time
    start_time_int = time.time()
    Fnum, uz_num = Modal.runModal(mapdl, sample, E1_x, E1_y, E1_z, G1_xy, G1_yz, G1_xz)

    # MAC = np.zeros((modes))
    # for i in range(modes):
    #     MAC[i]=np.abs(np.dot(uz_exp[i][:],uz_num[i][:]))**2/(np.dot(uz_exp[i][:],uz_exp[i][:])*np.dot(uz_num[i][:],uz_num[i][:]))


    err = sqrt(np.sum(((Fnum[:modes, 0] - Fexp) / (Fexp)) ** 2))
    # v=0.5
    # term_freq = (Fnum[:modes, 0] - Fexp) / (Fexp) ** 2
    # term_mac = 1-(np.sqrt(MAC)**2)/MAC
    # err = np.sum((v*term_freq+(1-v)*(term_mac)))
    
    end_time_int = time.time()
    total_time_int = end_time_int - start_time_int
    print("")
    print(f"Erro = {err:.6f} | Tempo = {total_time_int:.2f}s")
    # print("")
    # print("MAC")
    # print(MAC)
    print("")
    print(f"Frequências experimentais de {sample}:")
    print(Fexp_total[:modes])
    print(f"Frequências númericas de {sample}:")
    print(np.array2string(Fnum[:modes, 0], formatter={'float_kind':lambda x: f"{x:.1f}"}))
    print("----------------------------")
    
    
    return err


#bounds = Bounds(lb=[1e6, 1e4, 1e4, 1e4, 0.1, 0.1], ub=[5e10, 1e9, 1e10, 1e10, 0.48, 0.48])
bounds = Bounds(lb=[1e6, 1e4, 1e4, 1e4, 1e4, 1e4 ], ub=[1e12, 1e12, 1e12, 1e11, 1e11, 1e11])

x0 = [1e10, 1e9, 1e9, 5e9, 5e9, 5e9]

ret2 = minimize(objectivefunc, x0=np.array(x0), bounds=bounds, method='L-BFGS-B')

ret4 = minimize(objectivefunc, x0=np.array(x0), bounds=bounds, method='Nelder-Mead', options={'fatol':1e4, 'maxiter': maxiter})

selSol = ret4

mapdl.exit()

result = [selSol.x[0], selSol.x[1], selSol.x[2], selSol.x[3], selSol.x[4], selSol.x[5]]
# result = [selSol.x[0], selSol.x[1]]

end_time = time.time()
total_time = end_time - start_time

print("\n===============================")
print(f"Tempo total: {total_time:.4f} seconds")
print(f"Otimização concluída em {iteration_counter['count']} iterações.")
print(f"Melhor solução: {result}")

np.savetxt('EpoxyProperties_test.txt', np.array([result]))