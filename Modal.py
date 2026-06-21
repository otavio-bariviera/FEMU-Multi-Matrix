# %%
import matplotlib.pyplot as plt
from ansys.mapdl.core import launch_mapdl
import numpy as np
import os
from ansys.mapdl.core.plotting import GraphicsBackend
import time
from materials import get_material_properties
import pandas as pd

modes = 7
sample = "RE"

# Start measuring execution time
start_time = time.time()

nx, ny = 10, 10

folder_pos = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Exp_Modal"
path_pos = os.path.join(folder_pos, sample + ".csv")

folder_modal = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Códigos pyansys\Modal_data.xlsx"
df_modal = pd.read_excel(folder_modal, index_col=0)
Fexp_total = df_modal.loc[sample].to_numpy()
Fexp = np.sort(Fexp_total[:modes])

def get_coords(path_pos):
    
    df = pd.read_csv(
        path_pos,
        sep=';',
        skiprows=6,
        header=None,
        index_col=0,
        usecols=[0,1,2,3],
        names=["Index", "x", "y", "z"]
    )
    
    df["x"] = (abs(min(df["x"])) + df["x"])/1000
    df["y"] = (abs(min(df["y"])) + df["y"])/1000
    df["z"] = (abs(min(df["z"])) + df["z"])/1000
    
    altura = max(df["y"]) + abs(min(df["y"]))
    largura = max(df["x"]) + abs(min(df["x"]))
    
    x_ideal_coords = np.linspace(0, largura, nx)
    y_ideal_coords = np.linspace(0, altura, ny)

    exp_nodes = []
    
    for y in y_ideal_coords:
        for x in x_ideal_coords:
            dist = 10e9
            for n in range(len(df["x"])):
                node_test_x = df["x"].iloc[n]
                node_test_y = df["y"].iloc[n]
                dist_new = np.sqrt((node_test_x-x)**2+(node_test_y-y)**2)
                if dist_new < dist:
                    nsel = df.index[n]
                    dist = dist_new
            exp_nodes.append(nsel)
            
    x_coords = df.loc[exp_nodes, "x"]
    y_coords = df.loc[exp_nodes, "y"]
    
    folder_mac = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\MAC\MAC_data.xlsx"
    df = pd.read_excel(folder_mac, sheet_name=sample)
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    df = df.set_index(df.columns[0])
    uz_exp = df.to_numpy()
    
    return x_coords, y_coords, uz_exp


def solve(mapdl):
    mapdl.esel('all')
    mapdl.allsel()
    mapdl.slashsolu()
    mapdl.antype('MODAL')
    mapdl.modopt('LANB', 20)

def runModal(
    mapdl,
    sample,
    x_coords,
    y_coords,

    # -------- EPOXY --------
    E_epoxy_x,
    E_epoxy_y,
    G_epoxy_xy,
    PR_epoxy_xy,
    PR_epoxy_yz,
    
    # -------- EPOXY+BM --------
    E_epoxy2,
    PR_epoxy2,

    # -------- PU --------
    E_PU_x,
    E_PU_y,
    G_PU_xy,
    PR_PU_xy,
    PR_PU_yz,

    # -------- PU+BM --------
    E_PU2,
    PR_PU2,

    save_images=False
):
    
    mats = get_material_properties()
    
    # =========================
    # EPOXY
    # =========================
    for name in ["epoxy"]:
    
        mats[name]["E_x"] = E_epoxy_x
        mats[name]["E_y"] = E_epoxy_y
        mats[name]["G_xy"] = G_epoxy_xy
        mats[name]["G_yz"] = E_epoxy_y / (2 * (1 + PR_epoxy_yz))
        mats[name]["PR_xy"] = PR_epoxy_xy
        mats[name]["PR_yz"] = PR_epoxy_yz
    
    # =========================
    # PU
    # =========================
    for name in ["PU"]:
    
        mats[name]["E_x"] = E_PU_x
        mats[name]["E_y"] = E_PU_y
        mats[name]["G_xy"] = G_PU_xy
        mats[name]["G_yz"] = E_PU_y / (2 * (1 + PR_PU_yz))
        mats[name]["PR_xy"] = PR_PU_xy
        mats[name]["PR_yz"] = PR_PU_yz
        
        
    # =========================
    # EPOXY2
    # =========================
    for name in ["epoxy2"]:
    
        E = E_epoxy2
        nu = PR_epoxy2
        G = E / (2 * (1 + nu))
    
        mats[name]["E_x"] = mats[name]["E_y"] = mats[name]["E_z"] = E
        mats[name]["PR_xy"] = mats[name]["PR_yz"] = mats[name]["PR_xz"] = nu
        mats[name]["G_xy"] = mats[name]["G_yz"] = mats[name]["G_xz"] = G
    
    # =========================
    # PU2
    # =========================
    for name in ["PU2"]:
    
        E = E_PU2
        nu = PR_PU2
        G = E / (2 * (1 + nu))
    
        mats[name]["E_x"] = mats[name]["E_y"] = mats[name]["E_z"] = E
        mats[name]["PR_xy"] = mats[name]["PR_yz"] = mats[name]["PR_xz"] = nu
        mats[name]["G_xy"] = mats[name]["G_yz"] = mats[name]["G_xz"] = G
        
    # Initialize model (REBUILD NORMAL)
    mapdl.finish()
    mapdl.clear()
    mapdl.prep7()
    mapdl.et(1, 'SHELL281')
    
    material_ids = {
        "epoxy": 1,
        "epoxy2": 3,
        "PU": 2,
        "PU2": 4,
    }
    
    for name, mat_id in material_ids.items():
        props = mats[name]
    
        mapdl.mp('EX',   mat_id, props["E_x"])
        mapdl.mp('EY',   mat_id, props["E_y"])
        mapdl.mp('EZ',   mat_id, props["E_y"])
        mapdl.mp('DENS', mat_id, props["DENS"])
        mapdl.mp('PRXY', mat_id, props["PR_xy"])
        mapdl.mp('PRYZ', mat_id, props["PR_yz"])
        mapdl.mp('PRXZ', mat_id, props["PR_xy"])
        mapdl.mp('GXY',  mat_id, props["G_xy"])
        mapdl.mp('GYZ',  mat_id, props["G_yz"])
        mapdl.mp('GXZ',  mat_id, props["G_xy"])
    
    # Geometria
    import geometries2
    if hasattr(geometries2, sample):
        getattr(geometries2, sample)(mapdl)
    else:
        raise ValueError(f"Geometria '{sample}' não encontrada")

    mapdl.run_multiline("""
    LSEL,S,LOC,X,X,X
    LSEL,R,LOC,Y,0,Y  
    CM,Line_1,line
    CMSEL,S,Line_1
    DL,ALL,,ALL
    ALLSEL
    """)

    # Solve
    solve(mapdl)
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()
    mapdl.set('LIST', 20)

    if save_images:
        # Plot mesh ########
        mapdl.view(1, 1, 1, 1)
        mapdl.show('PNG', 'REV')
        mapdl.eplot(graphics_backend=GraphicsBackend.MAPDL)
        mapdl.show('CLOSE')

    # Prepare array to store results
    result = np.zeros((7, 2))  # 10 rows, 2 columns: [frequency, mode number]
    
    # Select nodes
    nodes = []
    mapdl.allsel()
    nodes_id = mapdl.mesh.nnum        
    coords_nodes = mapdl.mesh.nodes


    for i in range(nx*ny):
        dist = 10e9
        for n in range(len(nodes_id)):
            node_test_x = coords_nodes[n, 0]
            node_test_y = coords_nodes[n, 1]
            dist_new = np.sqrt((node_test_x-x_coords.iloc[i])**2+(node_test_y-y_coords.iloc[i])**2)
            # dist_new = np.sqrt((node_test_x-x_offset.iloc[i])**2+(node_test_y-y_offset.iloc[i])**2)
            if dist_new < dist:
                nsel = nodes_id[n]
                dist = dist_new
        nodes.append(nsel)

    mapdl.allsel()
    uz = np.zeros((7, len(nodes)))
    
    for i in range(1, 8):
        mapdl.set(lstep=1, sbstep=i)
    
        # frequência (ok manter get, é só 7 chamadas)
        freq = mapdl.get(f'FREQ{i}', 'MODE', i, 'FREQ')
        result[i - 1, 0] = freq
        result[i - 1, 1] = i
    
        # pega TODOS deslocamentos de uma vez
        disp = mapdl.post_processing.nodal_displacement("Z")
    
        # mapear apenas os nós desejados
        node_id_array = mapdl.mesh.nnum
        node_index_map = {nid: idx for idx, nid in enumerate(node_id_array)}
    
        for j, node in enumerate(nodes):
            uz[i - 1, j] = disp[node_index_map[node]]
        
        uz_max = np.max(abs(uz[i-1, :]))
        
        uz[i-1, :] = (uz[i-1, :]) / uz_max

    return np.array(result), uz

if __name__ == '__main__':

    run_mode = 'SIM'
    job_name = 'testrun'

    from ansys.mapdl import core as pymapdl

    new_path = "C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v252\\ansys\\bin\\winx64\\ANSYS252.exe"
    pymapdl.change_default_ansys_path(new_path)

    mapdl = launch_mapdl(jobname=job_name, nproc=4, override=True, cleanup_on_exit=True, mode='grpc')

    folder_pos = r"C:\Users\Otavio Augusto\OneDrive\Imagens\Documentos\Geral Facul\TCC\Exp_Modal"
    path_pos = os.path.join(folder_pos, sample + ".csv")
    x_coords, y_coords, uz_exp = get_coords(path_pos)
    
    # def runModal(mapdl, sample, E1_x, E1_y, G1_xy, PR1_xy, PR1_yz, save_images=False):       
    # Fnum, uz = runModal(mapdl, sample, 4.04e10, 1.54e10, 5.02e9, 0.27, 0.1, save_images=True)
    Fnum, uz = runModal(mapdl, sample, y_coords, x_coords, 35100023676*0.9, 14412051343, 5505790508, 0.14074262, 0.255810311, 49066278917, 0.31024377,
                                                           76343303930, 2048369963, 51747462, 0.274868224, 0.366715631, 4982644.004, 0.456929203, save_images=True)

    print("Deslocamentos em Z (por modo, por nó):")
    print(uz)
    print("Modal frequencies (Hz):")
    print(Fnum)

    mapdl.exit()
    
    MAC = np.zeros((modes))
    for i in range(modes):
        MAC[i]=np.abs(np.dot(uz_exp[i][:],uz[i][:]))**2/(np.dot(uz_exp[i][:],uz_exp[i][:])*np.dot(uz[i][:],uz[i][:]))
    print(MAC)
    
    v = 0.5
    term_freq = ((Fnum[:modes, 0] - Fexp) / Fexp)**2
    term_mac = (1 - MAC)**2  
    term_mac = (1-np.sqrt(MAC)**2)/MAC
    err = (np.sum(v * term_freq + (1 - v) * term_mac))
    
    print(f"Valor função objetivo: {err:.6}")
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.4f} seconds")


    from mpl_toolkits.mplot3d import Axes3D

    def Modal_shape():
        
        phi_sel = np.array(uz) 
        fn_sel = Fnum[:, 0]   # pegar só frequências
    
        # garantir 2D
        if phi_sel.ndim == 1:
            phi_sel = phi_sel.reshape(1, -1)
    
        n_modes_plot = phi_sel.shape[0]
    
        for mode_idx in range(n_modes_plot):
            
            phi_mode = phi_sel[mode_idx]
    
            phi_mode = phi_mode / np.max(np.abs(phi_mode))
    
            phi_grid = phi_mode.reshape(ny, nx)[::-1, :]
            
            X = x_coords.values.reshape(ny, nx)
            Y = y_coords.values.reshape(ny, nx)[::-1, :]
            
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()
            
            surf = ax.plot_surface(
                X, Y, phi_grid,
                cmap='jet',
                edgecolor='k',
                linewidth=0.3,
                antialiased=True
            )
            
            ax.set_box_aspect([Lx, Ly, 0.3*max(Lx, Ly)])
            fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, label='Amplitude')
    
            ax.invert_yaxis()
            ax.set_zticks([])
            ax.set_zlabel("")
            ax.set_xticks([])
            ax.set_yticks([])
            
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.grid(False)

            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            plt.show()
            # ax.set_title(f"Modo {mode_idx+1} - {fn_sel[mode_idx]:.2f} Hz")
            # ax.set_xlabel("X")
            # ax.set_ylabel("Y")
            # ax.set_zlabel("Deslocamento")
            
            plt.show()
        
    def Modal_shape_OMA():
        
        phi_sel = np.array(uz_exp) 
        fn_sel = Fexp  
    
        # garantir 2D
        if phi_sel.ndim == 1:
            phi_sel = phi_sel.reshape(1, -1)
    
        n_modes_plot = phi_sel.shape[0]
    
        for mode_idx in range(n_modes_plot):
            
            phi_mode = phi_sel[mode_idx]
    
            phi_mode = phi_mode / np.max(np.abs(phi_mode))
    
            phi_grid = phi_mode.reshape(ny, nx)[::-1, :]
            
            X = x_coords.values.reshape(ny, nx)
            Y = y_coords.values.reshape(ny, nx)[::-1, :]
            
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()
            
            surf = ax.plot_surface(
                X, Y, phi_grid,
                cmap='jet',
                edgecolor='k',
                linewidth=0.3,
                antialiased=True
            )
            ax.set_zticks([])
            ax.set_zlabel("")
            ax.set_xticks([])
            ax.set_yticks([])
            
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.grid(False)
    
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            
            ax.set_box_aspect([Lx, Ly, 0.3*max(Lx, Ly)])
            # fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, label='Amplitude')
    
            ax.invert_yaxis()
            
            # ax.set_title(f"Modo {mode_idx+1} - {fn_sel[mode_idx]:.2f} Hz")
            # ax.set_xlabel("X")
            # ax.set_ylabel("Y")
            # ax.set_zlabel("Deslocamento")
            
            plt.show()

    def Modal_shape_compare():
    
        phi_num = np.array(uz)
        phi_exp = np.array(uz_exp)
        fn_sel = Fexp
    
        # garantir 2D
        if phi_num.ndim == 1:
            phi_num = phi_num.reshape(1, -1)
        if phi_exp.ndim == 1:
            phi_exp = phi_exp.reshape(1, -1)
    
        n_modes_plot = min(phi_num.shape[0], phi_exp.shape[0])
    
        for mode_idx in range(n_modes_plot):
    
            # --- NUMÉRICO ---
            phi_n = phi_num[mode_idx]
            phi_n = phi_n / np.max(np.abs(phi_n))
    
            # --- EXPERIMENTAL (ODS) ---
            phi_e = phi_exp[mode_idx]
            phi_e = phi_e / np.max(np.abs(phi_e))
    
            if np.dot(phi_n, phi_e) < 0:
                phi_e = -phi_e
    
            # reshape para malha
            phi_n_grid = phi_n.reshape(ny, nx)[::-1, :]
            phi_e_grid = phi_e.reshape(ny, nx)[::-1, :]
    
            X = x_coords.values.reshape(ny, nx)
            Y = y_coords.values.reshape(ny, nx)[::-1, :]
    
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
    
            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()
    
            ax.plot_surface(
                X, Y, phi_n_grid,
                color='blue',
                edgecolor='k',
                linewidth=0.3,
                alpha=0.6
            )
    
            ax.plot_wireframe(
                X, Y, phi_e_grid,
                color='red',
                linewidth=1.2
            )
    
            ax.set_box_aspect([Lx, Ly, 0.3 * max(Lx, Ly)])
            ax.invert_yaxis()
    
            # ax.set_title(f"Comparação Modo {mode_idx+1} - {fn_sel[mode_idx]:.2f} Hz")
            # ax.set_xlabel("X")
            # ax.set_ylabel("Y")
            # ax.set_zlabel("Deslocamento")
            
            # remove apenas os textos
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])
            
            # remove os títulos dos eixos
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_zlabel("")
            
            # mantém a grade
            ax.grid(True)
    
            # legenda manual
            # from matplotlib.patches import Patch
            # legend_elements = [
            #     Patch(facecolor='blue', label='Numérico (Superfície)'),
            #     Patch(facecolor='red', label='Experimental (Wireframe)')
            # ]
            # ax.legend(handles=legend_elements)
    
            plt.show()
