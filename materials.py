def get_material_properties():

    materials = {

        # -------------------------
        # Transversalmente isotrópico
        # -------------------------
        "epoxy": {
            "type": "trans_iso",
            "E_x": None,
            "E_y": None,
            "PR_xy": None,
            "PR_yz": None,
            "G_xy": None,
            "DENS": 2000,
        },

        "PU": {
            "type": "trans_iso",
            "E_x": None,
            "E_y": None,
            "PR_xy": None,
            "PR_yz": None,
            "G_xy": None,
            "DENS": 2000,
        },

        # -------------------------
        # Isotrópico
        # -------------------------
        "epoxy2": {
            "type": "iso",
            "E": None,
            "PR": None,
            "DENS": 2000,
        },

        "PU2": {
            "type": "iso",
            "E": None,
            "PR": None,
            "DENS": 2000,
        },
    }

    # -------------------------
    # Processamento
    # -------------------------
    for mat in materials.values():

        # -------------------------
        # ISOTRÓPICO
        # -------------------------
        if mat["type"] == "iso":

            E = mat["E"]
            nu = mat["PR"]

            mat["E_x"] = mat["E_y"] = mat["E_z"] = E
            mat["PR_xy"] = mat["PR_yz"] = mat["PR_xz"] = nu

            if E and nu:
                G = E / (2 * (1 + nu))
                mat["G_xy"] = mat["G_yz"] = mat["G_xz"] = G

        # -------------------------
        # TRANSVERSALMENTE ISOTRÓPICO
        # -------------------------
        elif mat["type"] == "trans_iso":

            # Plano yz isotrópico
            mat["E_z"] = mat["E_y"]
            mat["PR_xz"] = mat["PR_xy"]
            mat["G_xz"] = mat["G_xy"]

            # Relação no plano isotrópico
            if mat.get("E_y") and mat.get("PR_yz"):
                mat["G_yz"] = mat["E_y"] / (2 * (1 + mat["PR_yz"]))

        # -------------------------
        # Garantia: todas as 9 propriedades existem
        # -------------------------
        required = ["E_x","E_y","E_z","G_xy","G_yz","G_xz","PR_xy","PR_yz","PR_xz"]
        for key in required:
            if key not in mat:
                mat[key] = None

    return materials
