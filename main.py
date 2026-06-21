# %%
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from scipy.optimize import minimize, Bounds, differential_evolution
import Modal
from ansys.mapdl.core import launch_mapdl
import pandas as pd
import time
from materials import get_material_properties
import os
from math import log10

### Modo 6 do M5 peguei com ODS 
### Modo 6 do M_all peguei com ODS 

"Parameters"
samples = ["M4_15", "M5_15", "M6_15", "M_all_15", "RE"]
modes = 7
maxiter = 200
nx, ny = 10, 10

start_time = time.time()
iteration_counter = {"count": 0}

run_mode = 'SIM'
job_name = 'testrun'

# =========================
# PARÂMETROS DA OTIMIZAÇÃO
# =========================

# x0 = [E1x, E1y, G1xy, v1xy, v1yz, E2x, E2y, G2xy, v2xy, v2yz]
x0 = [log10(41256048936.390884), log10(15499006888.460194), log10(4848482107.985826), 0.25118681160530887, 0.24219006433919646, log10(18145261535.04456), 0.25105304234857756,
      log10(8697184176.666458), log10(1388866443.4354243), log10(30259640.103518203), 0.5, 0.3182713029294523, log10(74823277.35676111), 0.42395678588486]

bounds_lb = np.array([6, 5, 5, 0.1, 0.1, 6, 0.1, 6, 5, 5, 0.1, 0.1, 6, 0.1])
bounds_ub = np.array([12, 12, 11, 0.5, 0.5, 12, 0.5, 12, 12, 11, 0.5, 0.5, 12, 0.5])


bounds = Bounds(lb=bounds_lb, ub=bounds_ub)


def check_material_stability(E_x, E_y, E_z, PR_xy, PR_yz, PR_xz):
    expr = 1.0 - (PR_xy**2 * E_y / E_x) - (PR_yz**2 * E_z / E_y) - (PR_xz**2 * E_z / E_x) \
           - 2.0 * PR_xy * PR_yz * PR_xz * E_z / E_x
    return expr > 0

############ Experimental ###########

folder_modal = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Exp_Modal\Modal_data.xlsx"
folder_pos = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Exp_Modal"
folder_mac = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\MAC\MAC_data.xlsx"

df_modal = pd.read_excel(folder_modal, index_col=0)

experimental_data = {}

for sample in samples:

    # Frequências experimentais
    Fexp_total = df_modal.loc[sample].to_numpy()
    Fexp = np.sort(Fexp_total[:modes])

    # Coordenadas
    path_pos = os.path.join(folder_pos, sample + ".csv")
    y_coords, x_coords, _ = Modal.get_coords(path_pos)

    # Modos experimentais
    df_mac = pd.read_excel(folder_mac, sheet_name=sample)
    df_mac = df_mac.dropna(how="all", axis=0).dropna(how="all", axis=1)
    df_mac = df_mac.set_index(df_mac.columns[0])

    uz_exp = df_mac.to_numpy()

    experimental_data[sample] = {
        "Fexp": Fexp,
        "x_coords": x_coords,
        "y_coords": y_coords,
        "uz_exp": uz_exp
    }

    print(f"\nSample: {sample}")
    print(f"Frequências experimentais: {Fexp}")

# def get_amplitude_phase(df, freq):
#     f_mag_exp = max((df["Forca"].values)-min(df["Forca"].values))/2
#     d_mag_exp = (max(df["Deslocamento"].values)-min(df["Deslocamento"].values))/2

#     print(f"Magnitude deslocamento:{d_mag_exp} para {freq} Hz")
#     print(f"Magnitude força:{f_mag_exp} para {freq} Hz")
    
#     return f_mag_exp, d_mag_exp

# folder = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Exp_Harmonic"
# path = os.path.join(folder, sample + ".csv")
# df_har = pd.read_csv(path,skiprows=4,header=None,index_col=0,usecols=[0,1,2,3], names=["Pontos", "Tempo", "Deslocamento", "Forca"])
# df_1hz = df_har[(df_har['Tempo'] >= (600+670)/2-1) & (df_har['Tempo'] <= (600+670)/2+1)]
# df_01hz = df_har[(df_har['Tempo'] >= (950+1500)/2-1/0.1) & (df_har['Tempo'] <= (950+1500)/2+1/0.1)]
# df_001hz = df_har[(df_har['Tempo'] >= (1750+max(df_har['Tempo']))/2-1/0.01) & (df_har['Tempo'] <= (1750+max(df_har['Tempo']))/2+1/0.01)]

# Histórico para gráfico
history = {

    "iter": [],

    # =========================
    # EPOXY
    # =========================
    "E_epoxy_x": [],
    "E_epoxy_y": [],
    "G_epoxy_xy": [],
    "G_epoxy_yz": [],
    "PR_epoxy_xy": [],
    "PR_epoxy_yz": [],

    # =========================
    # EPOXY2
    # =========================
    "E_epoxy2": [],
    "G_epoxy2": [],
    "PR_epoxy2": [],

    # =========================
    # PU
    # =========================
    "E_PU_x": [],
    "E_PU_y": [],
    "G_PU_xy": [],
    "G_PU_yz": [],
    "PR_PU_xy": [],
    "PR_PU_yz": [],

    # =========================
    # PU2
    # =========================
    "E_PU2": [],
    "G_PU2": [],
    "PR_PU2": [],

    # =========================
    # ERROS
    # =========================
    "err": [],
    "term_freq_sum": [],
    "term_mac_sum": []
}

mapdl = launch_mapdl(jobname=job_name, nproc=4, override=True, cleanup_on_exit=True)

csv_file = "optimization_history.csv"

# Cria cabeçalho se o arquivo não existir
if not os.path.exists(csv_file):
    pd.DataFrame(columns=[
    
        "iter",
    
        # epoxy
        "E_epoxy_x",
        "E_epoxy_y",
        "G_epoxy_xy",
        "G_epoxy_yz",
        "PR_epoxy_xy",
        "PR_epoxy_yz",
    
        # epoxy2
        "E_epoxy2",
        "G_epoxy2",
        "PR_epoxy2",
    
        # PU
        "E_PU_x",
        "E_PU_y",
        "G_PU_xy",
        "G_PU_yz",
        "PR_PU_xy",
        "PR_PU_yz",
    
        # PU2
        "E_PU2",
        "G_PU2",
        "PR_PU2",
    
        "err",
        "term_freq_sum",
        "term_mac_sum"
    
    ]).to_csv(csv_file, index=False)
def update_plot():

    fig, axes = plt.subplots(2, 3, figsize=(18, 8))

    fig.suptitle("Acompanhamento da Otimização", fontsize=14)

    # ==========================================================
    # ERRO
    # ==========================================================
    ax = axes[0, 0]

    ax.plot(history["iter"], history["term_freq_sum"],
            label="Freq", alpha=0.7)

    ax.plot(history["iter"], history["term_mac_sum"],
            label="MAC", alpha=0.7)

    ax.plot(history["iter"], history["err"],
            linewidth=2,
            label="Total")

    ax.set_title("Erro")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Erro")
    ax.grid(True)
    ax.legend()

    # ==========================================================
    # EPOXY
    # ==========================================================
    ax = axes[0, 1]

    ax.plot(history["iter"], history["E_epoxy_x"], label="E_x")
    ax.plot(history["iter"], history["E_epoxy_y"], label="E_y")
    ax.plot(history["iter"], history["G_epoxy_xy"], label="G_xy")
    ax.plot(history["iter"], history["G_epoxy_yz"], label="G_yz")

    ax.set_yscale("log")
    ax.set_title("Epoxy")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Pa")
    ax.grid(True)
    ax.legend(fontsize=8)

    # ==========================================================
    # EPOXY2
    # ==========================================================
    ax = axes[0, 2]

    ax.plot(history["iter"], history["E_epoxy2"], label="E")
    ax.plot(history["iter"], history["G_epoxy2"], label="G")

    ax.set_yscale("log")
    ax.set_title("Epoxy2")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Pa")
    ax.grid(True)
    ax.legend(fontsize=8)

    # ==========================================================
    # PU
    # ==========================================================
    ax = axes[1, 0]

    ax.plot(history["iter"], history["E_PU_x"], label="E_x")
    ax.plot(history["iter"], history["E_PU_y"], label="E_y")
    ax.plot(history["iter"], history["G_PU_xy"], label="G_xy")
    ax.plot(history["iter"], history["G_PU_yz"], label="G_yz")

    ax.set_yscale("log")
    ax.set_title("PU")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Pa")
    ax.grid(True)
    ax.legend(fontsize=8)

    # ==========================================================
    # PU2
    # ==========================================================
    ax = axes[1, 1]

    ax.plot(history["iter"], history["E_PU2"], label="E")
    ax.plot(history["iter"], history["G_PU2"], label="G")

    ax.set_yscale("log")
    ax.set_title("PU2")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Pa")
    ax.grid(True)
    ax.legend(fontsize=8)

    # ==========================================================
    # POISSONS
    # ==========================================================
    ax = axes[1, 2]

    ax.plot(history["iter"], history["PR_epoxy_xy"], label="epoxy_xy")
    ax.plot(history["iter"], history["PR_epoxy_yz"], label="epoxy_yz")

    ax.plot(history["iter"], history["PR_epoxy2"], "--", label="epoxy2")

    ax.plot(history["iter"], history["PR_PU_xy"], label="PU_xy")
    ax.plot(history["iter"], history["PR_PU_yz"], label="PU_yz")

    ax.plot(history["iter"], history["PR_PU2"], "--", label="PU2")

    ax.set_title("Poisson")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("ν")
    ax.grid(True)
    ax.legend(fontsize=7)

    plt.tight_layout()

def objectivefunc(x):
    iteration_counter["count"] += 1
    iter_num = iteration_counter["count"]
    
    print(f"\n--- Iteração {iter_num} ---")

    (logE_epoxy_x, logE_epoxy_y, logG_epoxy_xy, PR_epoxy_xy, PR_epoxy_yz, logE_epoxy2, PR_epoxy2, 
     logE_PU_x, logE_PU_y, logG_PU_xy, PR_PU_xy, PR_PU_yz, logE_PU2, PR_PU2) = x
    
    # =========================
    # EPOXY
    # =========================
    E_epoxy_x = 10**logE_epoxy_x
    E_epoxy_y = 10**logE_epoxy_y
    G_epoxy_xy = 10**logG_epoxy_xy
    
    # =========================
    # EPOXY2
    # =========================
    E_epoxy2 = 10**logE_epoxy2
    
    # =========================
    # PU
    # =========================
    E_PU_x = 10**logE_PU_x
    E_PU_y = 10**logE_PU_y
    G_PU_xy = 10**logG_PU_xy
    
    # =========================
    # PU2
    # =========================
    E_PU2 = 10**logE_PU2
    
    # ==========================================================
    # DERIVADOS
    # ==========================================================
    G_epoxy_yz = E_epoxy_y / (2 * (1 + PR_epoxy_yz))
    G_epoxy2 = E_epoxy2 / (2 * (1 + PR_epoxy2))
    
    G_PU_yz = E_PU_y / (2 * (1 + PR_PU_yz))
    G_PU2 = E_PU2 / (2 * (1 + PR_PU2))
        
    print(
        f"""
    Parâmetros atuais: 
    
    {"EPOXY":<28}{"PU":<28}
    {"-"*12:<28}{"-"*12:<28}
    
    E_x    = {E_epoxy_x:.3e}      E_x    = {E_PU_x:.3e}
    E_y    = {E_epoxy_y:.3e}      E_y    = {E_PU_y:.3e}
    G_xy   = {G_epoxy_xy:.3e}      G_xy   = {G_PU_xy:.3e}
    PR_xy  = {PR_epoxy_xy:.4f}          PR_xy  = {PR_PU_xy:.4f}
    PR_yz  = {PR_epoxy_yz:.4f}          PR_yz  = {PR_PU_yz:.4f}
    
    {"EPOXY2":<28}{"PU2":<28}
    {"-"*12:<28}{"-"*12:<28}
    
    E      = {E_epoxy2:.3e}      E      = {E_PU2:.3e}
    PR     = {PR_epoxy2:.4f}          PR     = {PR_PU2:.4f}
    """
    )


    # -------- EPOXY --------
    if not check_material_stability(
        E_epoxy_x,
        E_epoxy_y,
        E_epoxy_y,
        PR_epoxy_xy,
        PR_epoxy_yz,
        PR_epoxy_xy
    ):
        return 1e6
    
    # -------- EPOXY2 --------
    if not check_material_stability(
        E_epoxy2,
        E_epoxy2,
        E_epoxy2,
        PR_epoxy2,
        PR_epoxy2,
        PR_epoxy2
    ):
        return 1e6
    
    # -------- PU --------
    if not check_material_stability(
        E_PU_x,
        E_PU_y,
        E_PU_y,
        PR_PU_xy,
        PR_PU_yz,
        PR_PU_xy
    ):
        return 1e6
    
    # -------- PU2 --------
    if not check_material_stability(
        E_PU2,
        E_PU2,
        E_PU2,
        PR_PU2,
        PR_PU2,
        PR_PU2
    ):
        return 1e6
    
    start_time_int = time.time()

    all_term_freq = []
    all_term_mac = []
    
    for sample in samples:
    
        data = experimental_data[sample]
    
        Fexp = data["Fexp"]
        x_coords = data["x_coords"]
        y_coords = data["y_coords"]
        uz_exp = data["uz_exp"]
    
        # Roda FEM
        Fnum, uz_num = Modal.runModal(
            mapdl,
            sample,
            x_coords,
            y_coords,
        
            E_epoxy_x,
            E_epoxy_y,
            G_epoxy_xy,
            PR_epoxy_xy,
            PR_epoxy_yz,
        
            E_epoxy2,
            PR_epoxy2,
        
            E_PU_x,
            E_PU_y,
            G_PU_xy,
            PR_PU_xy,
            PR_PU_yz,
        
            E_PU2,
            PR_PU2
        )
    
        # MAC
        MAC = np.zeros(modes)
    
        for i in range(modes):
            MAC[i] = (
                np.abs(np.dot(uz_exp[i][:], uz_num[i][:]))**2
                /
                (
                    np.dot(uz_exp[i][:], uz_exp[i][:])
                    *
                    np.dot(uz_num[i][:], uz_num[i][:])
                )
            )
    
        # Termos erro
        term_freq = np.abs((Fnum[:modes, 0] - Fexp) / Fexp)
        term_mac = (1 - MAC)
    
        all_term_freq.extend(term_freq)
        all_term_mac.extend(term_mac)
        
        print(f"\n--- {sample} ---")
        print(f"Freq exp: {np.round(Fexp,1)}")
        print(f"Freq num: {np.round(Fnum[:modes,0],1)}")
        print(f"MAC: {np.round(MAC,3)}")
        total_time_int = time.time() - start_time_int
    
    v = 0.5
    all_term_freq = np.array(all_term_freq)
    all_term_mac = np.array(all_term_mac)
    err = np.sum((v * all_term_freq + (1 - v) * all_term_mac)**2)

    print(f"\nErro total = {err:.6f} | Tempo = {total_time_int:.2f}s")
    print(f"Erro de frequência = {np.sum(all_term_freq):.6f} | Erro MAC = {np.sum(all_term_mac):.6f}")
    print(f"Frequências exp: {Fexp}")
    print(f"Frequências num: {np.array2string(Fnum[:modes, 0], formatter={'float_kind':lambda x: f'{x:.1f}'})}")
    print("----------------------------")
    
    # ==========================================================
    # HISTORY
    # ==========================================================
    history["iter"].append(iter_num)
    
    # -------- epoxy --------
    history["E_epoxy_x"].append(E_epoxy_x)
    history["E_epoxy_y"].append(E_epoxy_y)
    history["G_epoxy_xy"].append(G_epoxy_xy)
    history["G_epoxy_yz"].append(G_epoxy_yz)
    history["PR_epoxy_xy"].append(PR_epoxy_xy)
    history["PR_epoxy_yz"].append(PR_epoxy_yz)
    
    # -------- epoxy2 --------
    history["E_epoxy2"].append(E_epoxy2)
    history["G_epoxy2"].append(G_epoxy2)
    history["PR_epoxy2"].append(PR_epoxy2)
    
    # -------- PU --------
    history["E_PU_x"].append(E_PU_x)
    history["E_PU_y"].append(E_PU_y)
    history["G_PU_xy"].append(G_PU_xy)
    history["G_PU_yz"].append(G_PU_yz)
    history["PR_PU_xy"].append(PR_PU_xy)
    history["PR_PU_yz"].append(PR_PU_yz)
    
    # -------- PU2 --------
    history["E_PU2"].append(E_PU2)
    history["G_PU2"].append(G_PU2)
    history["PR_PU2"].append(PR_PU2)
    
    # -------- erro --------
    history["err"].append(err)
    history["term_freq_sum"].append(np.sum(all_term_freq))
    history["term_mac_sum"].append(np.sum(all_term_mac))
    
    row = pd.DataFrame([{
    
        "iter": iter_num,
    
        # ==========================================================
        # EPOXY
        # ==========================================================
        "E_epoxy_x": E_epoxy_x,
        "E_epoxy_y": E_epoxy_y,
        "G_epoxy_xy": G_epoxy_xy,
        "G_epoxy_yz": G_epoxy_yz,
        "PR_epoxy_xy": PR_epoxy_xy,
        "PR_epoxy_yz": PR_epoxy_yz,
    
        # ==========================================================
        # EPOXY2
        # ==========================================================
        "E_epoxy2": E_epoxy2,
        "G_epoxy2": G_epoxy2,
        "PR_epoxy2": PR_epoxy2,
    
        # ==========================================================
        # PU
        # ==========================================================
        "E_PU_x": E_PU_x,
        "E_PU_y": E_PU_y,
        "G_PU_xy": G_PU_xy,
        "G_PU_yz": G_PU_yz,
        "PR_PU_xy": PR_PU_xy,
        "PR_PU_yz": PR_PU_yz,
    
        # ==========================================================
        # PU2
        # ==========================================================
        "E_PU2": E_PU2,
        "G_PU2": G_PU2,
        "PR_PU2": PR_PU2,
    
        # ==========================================================
        # ERRO
        # ==========================================================
        "err": err,
        "term_freq_sum": np.sum(all_term_freq),
        "term_mac_sum": np.sum(all_term_mac)
    
    }])
    
    row.to_csv(csv_file, mode='a', header=False, index=False)

    return err

# Otimização
ret2 = differential_evolution(objectivefunc, bounds=bounds, x0=np.array(x0), mutation=(0.5, 1.2), recombination=0.85)

selSol = ret2
mapdl.exit()

result_log = selSol.x

result = {

    # =========================
    # EPOXY
    # =========================
    "epoxy": {
        "E_x": 10**result_log[0],
        "E_y": 10**result_log[1],
        "G_xy": 10**result_log[2],
        "PR_xy": result_log[3],
        "PR_yz": result_log[4],
    },

    # =========================
    # EPOXY2
    # =========================
    "epoxy2": {
        "E": 10**result_log[5],
        "PR": result_log[6],
    },

    # =========================
    # PU
    # =========================
    "PU": {
        "E_x": 10**result_log[7],
        "E_y": 10**result_log[8],
        "G_xy": 10**result_log[9],
        "PR_xy": result_log[10],
        "PR_yz": result_log[11],
    },

    # =========================
    # PU2
    # =========================
    "PU2": {
        "E": 10**result_log[12],
        "PR": result_log[13],
    }
}

# Cálculo de G_yz correspondente à melhor solução
E1_y_best = result[1]
PR1_yz_best = result[4]
G1_yz_best = E1_y_best / (2 * (1 + PR1_yz_best))

end_time = time.time()
total_time = end_time - start_time

print("\n===============================")
print(f"Tempo total: {total_time:.4f} seconds")
print(f"Otimização concluída em {iteration_counter['count']} iterações.")
print(f"Melhor solução (E_x, E_y, G_xy, PR_xy, PR_yz, E, PR): {result} | G_yz calculado: {G1_yz_best:.3e} Pa")


plt.ioff()
update_plot()
plt.show()
