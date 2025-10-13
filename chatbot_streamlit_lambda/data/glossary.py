# data/glossary.py


GLOSARIO = {
    "wip": {"min": 10001, "max": 65535},
    "lineas_validas": set(["ZZCAMPREC", "ZZVENTA", "ZZCOMPRA"]),
    "cuentas_validas": set(["I741351", "E123456"]),
    "pdv_validos": set([
        "17","45","70","71","76","90","91","98","99",
        "A1","A2","A3","A4","A5",
        "Bg","Bm",
        "Ce","Cm","Cs",
        "D5",
        "Eh","Em","Eu",
        "Fc","Ff","Fg","Fm","Ft",
        "Gb","Gc","Gf","Gm","Gv",
        "H3","H5","H6","H7","Hb","Hl","Hm","Hn","Hz",
        "Ie",
        "Jb","Je","Jg","Jm","Jp","Jr","Js","Ju",
        "Ka","Kb","Kc","Kh","Km","Ko","Kr","Kt","Ku",
        "Lb","Lc","Lm","Lu",
        "Mc","Mi",
        "Nb","Nh","Np",
        "Oc","Od","Og","Oj","Ok","Op","Oq","Or","Os",
        "Pa","Pb","Pf","Pg","Ph","Pm","Po","Pp","Pq","Pr","Pv",
        "Qh","Qm","Qp","Qx",
        "Ra","Rb","Rc","Rd","Re","Rf","Rg","Ri","Rk","Rl","Rm","Rn","Rp","Rr","Rs","Rt","Ru","Rv","Rx",
        "Sl","Sx",
        "Ti","Tj","To","Tr","Tt",
        "Ub","Um","Uv",
        "V1","V2","Vb","Vc","Vg","Vh","Vm","Vp","Vs","Vt","Vv",
        "Xc","Xe","Xm",
        "Yc",
        "Zv","Zx"
    ]),
    "incompatibilidades": [
        {"linea": "ZZCAMPREC", "cuentas_prohibidas_prefijo": "I"}
    ]
}