# %%
import matplotlib.pyplot as plt
from ansys.mapdl.core import launch_mapdl
import numpy as np
import os
from ansys.mapdl.core.plotting import GraphicsBackend
import time
from materials import get_material_properties

sample = "RE"

# Start measuring execution time
start_time = time.time()

### 5M4_25

nx, ny = 5, 5

def solve(mapdl):
    mapdl.esel('all')
    mapdl.allsel()
    mapdl.slashsolu()
    mapdl.antype('MODAL')
    mapdl.modopt('LANB', 20)


def runModal(mapdl, sample, E1_x, E1_y, E1_z, G1_xy, G1_yz, G1_xz):
    
    mats = get_material_properties()
    
    for name in ["PU", "PU2"]:
        mats[name]["E_x"] = E1_x
        mats[name]["E_y"] = E1_y
        mats[name]["E_z"] = E1_z
        mats[name]["G_xy"] = G1_xy
        mats[name]["G_yz"] = G1_yz
        mats[name]["G_xz"] = G1_xz

    # Initialize model
    mapdl.finish()
    mapdl.clear()
    mapdl.prep7()
    mapdl.et(1, 'SHELL281')

    #Define materials
    for mat_id, (name, props) in enumerate(mats.items(), start=1):
        mapdl.mp('EX',   mat_id, props["E_x"])
        mapdl.mp('EY',   mat_id, props["E_y"])
        mapdl.mp('EZ',   mat_id, props["E_z"])
        mapdl.mp('DENS', mat_id, props["DENS"])
        mapdl.mp('PRXY', mat_id, props["PR_xy"])
        mapdl.mp('PRYZ', mat_id, props["PR_yz"])
        mapdl.mp('PRXZ', mat_id, props["PR_xz"])
        mapdl.mp('GXY',  mat_id, props["G_xy"])
        mapdl.mp('GYZ',  mat_id, props["G_yz"])
        mapdl.mp('GXZ',  mat_id, props["G_xz"])

    # Define geometry
    import geometries1
    import geometries2
    if hasattr(geometries2, sample):
        geo_func = getattr(geometries2, sample)
        geo_func(mapdl)
    else:
        raise ValueError(f"Geometria '{sample}' não encontrada em geometries2.py")
    Lx, Ly = 0.2, 0.11

    mapdl.run_multiline("""

    ! select and place into a component the faces that will fix the plate
    LSEL,S,LOC,X,X,X
    LSEL,R,LOC,Y,0,Y  
    CM,Line_1,line
        
    ! Fix the plate
    CMSEL,S,Line_1
    DL,ALL,,ALL
    ALLSEL
    """)

    # Run modal analysis
    solve(mapdl)
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()
    mapdl.set('LIST', 20)
    mapdl.view(1, 1, 1, 1)
    mapdl.angle(1)
    """
    # Plot mesh ########
    mapdl.view(1, 1, 1, 1)
    mapdl.show('PNG', 'REV')
    mapdl.eplot(graphics_backend=GraphicsBackend.MAPDL)
    mapdl.show('CLOSE')
    """
    # Prepare array to store results
    result = np.zeros((6, 2))  # 10 rows, 2 columns: [frequency, mode number]
    
    x_coords = np.linspace(0, Lx, nx)
    y_coords = np.linspace(0, Ly, ny)
    
    # Select nodes
    nodes = []
    mapdl.allsel()
    nodes_id = mapdl.mesh.nnum        
    coords_nodes = mapdl.mesh.nodes

    for x in x_coords:
        for y in y_coords:
            dist = 10e9
            for n in range(len(nodes_id)):
                node_test_x = coords_nodes[n, 0]
                node_test_y = coords_nodes[n, 1]
                dist_new = np.sqrt((node_test_x-x)**2+(node_test_y-y)**2)
                if dist_new < dist:
                    nsel = nodes_id[n]
                    dist = dist_new
            nodes.append(nsel)
    if dist>0.01:
        print("Distancia maior que mínimo 0,01mm")
    
    mapdl.allsel()
    uz = np.zeros((6, len(nodes)))

    for i in range(1, 7):  # modes 1 to 10
        mapdl.set(lstep=1, sbstep=i)
        freq = mapdl.get(f'FREQ{i}', 'MODE', i, 'FREQ')
        result[i - 1, 0] = freq
        result[i - 1, 1] = i
    
        # Save mode shape image
        # mapdl.show('PNG','REV')
        # mapdl.plnsol('U', 'SUM')
        # mapdl.show('CLOSE')

        for j, node in enumerate(nodes):
            uz[i - 1, j] = mapdl.get(f"UZ_{i}_{j}", "NODE", node, "U", "Z")

    return np.array(result), uz

if __name__ == '__main__':

    run_mode = 'SIM'
    job_name = 'testrun'

    from ansys.mapdl import core as pymapdl

    new_path = "C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v252\\ansys\\bin\\winx64\\ANSYS252.exe"
    pymapdl.change_default_ansys_path(new_path)

    mapdl = launch_mapdl(jobname=job_name, nproc=4, override=True, cleanup_on_exit=True, mode='grpc')

    # Fnum, uz = runModal(mapdl, sample, 1e10, 8e9, 2000, 0.3, 0.3, 1e9, 1e9)
    Fnum, uz = runModal(mapdl, sample, 4.04e10, 1.55e10, 6.51e10, 5.07e9, 7.53e9, 2.92e10)

    print("Deslocamentos em Z (por modo, por nó):")
    print(uz)
    print("Modal frequencies (Hz):")
    print(Fnum)

    mapdl.exit()
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.4f} seconds")

