def M4_15(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""

    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.001
    Zbm = 0.0002

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING PU AREA

    K, 100, 0, 0.110
    K, 1, 0, 0.02092
    K, 2, 0.02092, 0
    K, 3, 0.01451, 0.01451	   !middle point
    ARC, 1, 2, 3
    L, 666, 1
    L, 666, 2
    AL, 1, 2, 3
    K, 4, 0, 0.08908
    K, 5, 0.02092, 0.110
    K, 6, 0.01451, 0.09549 !middle point
    ARC, 4, 5, 6
    L, 100, 4
    L, 100, 5 
    AL, 4, 5, 6
    K, 7, 0.11182, 0
    K, 8, 0.15492, 0
    K, 9, 0.13337, 0.01915	   !middle point
    ARC, 7, 8, 9
    L, 8, 7 
    AL, 7, 8 
    K, 10, 0.11182, 0.110
    K, 11, 0.15492, 0.110
    K, 12, 0.13337, 0.09085	   !middle point
    ARC, 10, 11, 12
    L, 10, 11 
    AL, 9, 10
    K, 13, 0.2, 0.03975
    K, 14, 0.18173, 0.055
    K, 15, 0.1873, 0.0431	   !middle point
    K, 16, 0.2, 0.07025
    K, 17, 0.1873, 0.0669	   !middle point
    ARC, 13, 14, 15
    ARC, 14, 16, 17
    L, 13, 16
    AL, 11, 12, 13
    CYL4, 0.06717, 0.055, 0.034/2
    ALLSEL
    CM, Pu, area
    CMSEL, u, Pu
    
    ! CREATING EPOXY AREA
    RECTNG,0,X,0,Y			!plot the base of the geometry
    CM, Epoxy, area
    ALLSEL
    ASBA, Epoxy, Pu, , DELETE, KEEP   ! Subtract PU area from the base plate
    ALLSEL
    CMSEL, u, PU
    CM, Epoxy, area
    
    ! Meshing Epoxy
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,
    SECNUM, 1
    CMSEL, s, Epoxy
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, ALL

    ! Meshing PU
    ! activate free meshing
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    CMSEL, s, Pu
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, All

    ALLSEL
    NUMMRG,ALL

    ESLV
    NSLE
    /PNUM,mat,1
    /NUMBER,1


    """)
    
    
def M5_15(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""
    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.001
    Zbm = 0.0002

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING PU AREA
    K, 1, 0, 0.01507
    K, 2, 0.08612, 0
    K, 3, 0.0437, 0.01119	   !middle point
    ARC, 1, 2, 3
    L, 666, 1
    L, 666, 2
    AL, 1, 2, 3
    K, 4, 0, 0.04131
    K, 5, 0.08612, 0.055
    K, 6, 0.04358, 0.04483 !middle point
    K, 7, 0, 0.06869
    K, 8, 0.04358, 0.06517 !middle point
    ARC, 4, 5, 6
    ARC, 5, 7, 8
    L, 4, 7 
    AL, 4, 5, 6
    K, 9, 0, 0.09493
    K, 10, 0.08612, 0.110
    K, 11, 0.0437, 0.09881	   !middle point
    K, 12, 0, 0.110
    ARC, 9, 10, 11
    L, 12, 9
    L, 12, 10
    AL, 7, 8, 9
    CM, Pu, area
    CMSEL, u, Pu
    
    ! CREATING EPOXY AREA
    RECTNG,0,X,0,Y			!plot the base of the geometry
    CM, Epoxy, area
    ALLSEL
    ASBA, Epoxy, Pu, , DELETE, KEEP   ! Subtract PU area from the base plate
    ALLSEL
    CMSEL, u, PU
    CM, Epoxy, area
    
    ! Meshing Epoxy
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,
    SECNUM, 1
    CMSEL, s, Epoxy
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, ALL
    
    ! Meshing PU
    ! activate free meshing
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    CMSEL, s, Pu
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, All

    ALLSEL
    NUMMRG,ALL

    ESLV
    NSLE
    /PNUM,mat,1
    /NUMBER,1
    """)
    
def M6_15(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""
    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.001
    Zbm = 0.0002

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING PU AREA
    K, 1, 0, 0.0138
    K, 2, 0.02886, 0
    K, 3, 0.0159, 0.00998	   !middle point
    ARC, 1, 2, 3
    L, 666, 1
    L, 666, 2
    AL, 1, 2, 3
    K, 4, 0, 0.04018
    K, 5, 0.02886, 0.055
    K, 6, 0.01612, 0.0443 !middle point
    K, 7, 0, 0.06982
    K, 8, 0.01612, 0.0657 !middle point
    ARC, 4, 5, 6
    ARC, 5, 7, 8
    L, 4, 7 
    AL, 4, 5, 6
    K, 9, 0, 0.0962
    K, 10, 0.02886, 0.110
    K, 11, 0.0159, 0.10002	   !middle point
    K, 12, 0, 0.110
    ARC, 9, 10, 11
    L, 12, 9
    L, 12, 10
    AL, 7, 8, 9
    K, 13, 0.10542, 0.055
    K, 14, 0.16218, 0.055
    K, 15, 0.1338, 0.04163   !middle point
    K, 16, 0.1338, 0.06837   !middle point
    ARC, 13, 14, 15
    ARC, 13, 14, 16
    AL, 10, 11
    K, 17, 0.10542, 0
    K, 18, 0.16219, 0
    K, 19, 0.13381, 0.01403   !middle point
    ARC, 17, 18, 19
    L, 17, 18
    AL, 12, 13
    K, 20, 0.10542, 0.110
    K, 21, 0.16219, 0.110
    K, 22, 0.13381, 0.09597  !middle point
    ARC, 20, 21, 22
    L, 20, 21
    AL, 14, 15
    CM, Pu, area
    CMSEL, u, Pu
    
    ! CREATING EPOXY AREA
    RECTNG,0,X,0,Y			!plot the base of the geometry
    CM, Epoxy, area
    ALLSEL
    ASBA, Epoxy, Pu, , DELETE, KEEP   ! Subtract PU area from the base plate
    ALLSEL
    CMSEL, u, PU
    CM, Epoxy, area
    
    ! Meshing Epoxy
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,
    SECNUM, 1
    CMSEL, s, Epoxy
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, ALL

    ! Meshing PU
    ! activate free meshing
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    CMSEL, s, Pu
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, All

    ALLSEL
    NUMMRG,ALL

    ESLV
    NSLE
    /PNUM,mat,1
    /NUMBER,1
    """)
    
def M_all_15(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""
    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.001
    Zbm = 0.0002

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING PU AREA
    K, 1, 0, 0.0177
    K, 2, 0.02723, 0
    K, 3, 0.01596, 0.01249	   !middle point
    ARC, 1, 2, 3
    L, 666, 1
    L, 666, 2
    AL, 1, 2, 3
    K, 4, 0, 0.0389
    K, 5, 0.02838, 0.055
    K, 6, 0.01608, 0.04361 !middle point
    K, 7, 0, 0.0711
    K, 8, 0.01608, 0.06639 !middle point
    ARC, 4, 5, 6
    ARC, 5, 7, 8
    L, 4, 7 
    AL, 4, 5, 6
    K, 9, 0, 0.09223
    K, 10, 0.02723, 0.110
    K, 11, 0.01596, 0.09751	   !middle point
    K, 12, 0, 0.110
    ARC, 9, 10, 11
    L, 12, 9
    L, 12, 10
    AL, 7, 8, 9
    K, 13, 0.04425, 0.055
    K, 14, 0.09076, 0.055
    K, 15, 0.06751, 0.04683   !middle point
    K, 16, 0.06751, 0.06317   !middle point
    ARC, 13, 14, 15
    ARC, 13, 14, 16
    AL, 10, 11
    K, 17, 0.11142, 0
    K, 18, 0.15808, 0
    K, 19, 0.13475, 0.0162   !middle point
    ARC, 17, 18, 19
    L, 17, 18
    AL, 12, 13
    K, 20, 0.11142, 0.110
    K, 21, 0.15808, 0.110
    K, 22, 0.13475, 0.0938  !middle point
    ARC, 20, 21, 22
    L, 20, 21
    AL, 14, 15
    CYL4, 0.13475, 0.055, 0.02209/2
    CM, Pu, area
    CMSEL, u, Pu
    
    ! CREATING EPOXY AREA
    RECTNG,0,X,0,Y			!plot the base of the geometry
    CM, Epoxy, area
    ALLSEL
    ASBA, Epoxy, Pu, , DELETE, KEEP   ! Subtract PU area from the base plate
    ALLSEL
    CMSEL, u, PU
    CM, Epoxy, area
    
    ! Meshing Epoxy
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,
    SECNUM, 1
    CMSEL, s, Epoxy
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, ALL
    
    ! Meshing PU
    ! activate free meshing
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    CMSEL, s, Pu
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    AMESH, All

    ALLSEL
    NUMMRG,ALL

    ESLV
    NSLE
    /PNUM,mat,1
    /NUMBER,1
    """)
    
def RE(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""

    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.001
    Zbm = 0.0002

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING EPOXY AREA
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,

    RECTNG,0,X,0,Y	
    CM, Epoxy, area
    ALLSEL

    ! activate free meshing
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    ALLSELL
    AMESH, All

    """)