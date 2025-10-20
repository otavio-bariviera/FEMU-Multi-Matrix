def M4_25(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""

    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.0009
    Zbm = 0.0001

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING EPOXY AREA
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,

    RECTNG,0,X,0,0.04125	
    RECTNG,0,X,0.06875,Y		
    CM, Epoxy, area
    ALLSEL

    ! activate free meshing
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    ALLSELL
    AMESH, All
    
    !CREATING PU AREA    
    CMSEL, u, Epoxy
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    RECTNG,0,X,0.04125,0.06875
    CM, Pu, area
    
    ! activate free meshing
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

def M4_50(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""

    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.0009
    Zbm = 0.0001

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668

    ! CREATING EPOXY AREA
    SECTYPE, 1, SHELL, , ,
    SECDATA,Zm,1,0.0,
    SECDATA,Zbm,3,0.0,
    SECDATA,Zm,1,0.0,

    RECTNG,0,X,0,0.0275	
    RECTNG,0,X,0.0825,Y		
    CM, Epoxy, area
    ALLSEL

    ! activate free meshing
    ESYS, 11				!SET THE ELEMENT COORDENATE SYSTEM
    SMRT,6
    ESIZE, 0.002
    ALLSELL
    AMESH, All
    
    !CREATING PU AREA    
    CMSEL, u, Epoxy
    SECTYPE, 2, SHELL, , ,
    SECDATA,Zm,2,0.0,
    SECDATA,Zbm,4,0.0,
    SECDATA,Zm,2,0.0,
    SECNUM,2
    RECTNG,0,X,0.0275,0.0825
    CM, Pu, area
    
    ! activate free meshing
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

def M3_50(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""
                        
    X = 0.200	
    Y = 0.110	
    Z = 0.0022			
    
    ! Layers
    Zm = 0.0009
    Zbm = 0.0001

    K, 666, 0, 0, 0
    K, 667, 1, 0, 0
    K, 668, 0, 1, 0
    CSKP, 11, 0, 666, 667, 668
    
    ! CREATING PU AREA
    K, 1, 0.01414, 0
    K, 2, 0, 0.01414
    K, 3, 0.18566, 0.11
    K, 4, 0.2, 0.11	  
    K, 5, 0.2, 0.09586
    L, 666, 1
    L, 666, 2
    L, 2, 3
    L, 3, 4
    L, 4, 5
    L, 5, 1
    AL, 1, 2, 3, 4, 5, 6
    K, 6, 0, 0.09586
    K, 7, 0, 0.110
    K, 8, 0.01414, 0.11
    K, 9, 0.18586, 0
    K, 10, 0.2, 0
    K, 11, 0.2, 0.01414
    L, 6, 7
    L, 7, 8
    L, 8, 11
    L, 11, 10
    L, 10, 9
    L, 9, 6
    AL, 7, 8, 9, 10, 11, 12
    ALLSEL
    AOVLAP, ALL
    AGLUE, ALL
    CM, Pu, area
    CMSEL, u, PU
    
    ! CREATING EPOXY AREA
    
    RECTNG,0,X,0,Y			!plot the base of the geometry
    CM, Epoxy, area
    ALLSEL
    ASBA, Epoxy, Pu, , DELETE, KEEP      			  ! Subtract PU area from the base plate
    ALLSEL
    CMSEL, u, PU
    CM, Epoxy, area
    
    
    ! MESHING EPOXY
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
    
    ! MESHING PU
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

def Re(mapdl):
    # Geometry and meshing
    mapdl.run_multiline("""

    X = 0.200	
    Y = 0.110	
    Z = 0.0022			

    ! Layers
    Zm = 0.0009
    Zbm = 0.0001

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
