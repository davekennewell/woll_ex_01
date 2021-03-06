#----------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORT NECESSARY MODULES
#----------------------------------------------------------------------------------------------------------------------------------------------------
print ' About to Start Simulation:- Importing Modules'

import anuga, numpy, time, os, glob
from anuga.operators.rate_operators import Polygonal_rate_operator
from anuga import file_function, Polygon_function, read_polygon, create_mesh_from_regions, Domain
#----------------------------------------------------------------------------------------------------------------------------------------------------
#  ADD CATCHMENT INFORMATION HERE 
#----------------------------------------------------------------------------------------------------------------------------------------------------

CatchmentDictionary = {
    'Model/Bdy/Fine.csv':5
    }
#----------------------------------------------------------------------------------------------------------------------------------------------------
# FILENAMES, MODEL DOMAIN and VARIABLES
#----------------------------------------------------------------------------------------------------------------------------------------------------

basename = 'Model/DEM/R'
outname = 'woll_ex_01'
meshname = 'woll_ex_01.msh'

#----------------------------------------------------------------------------------------------------------------------------------------------------
# ENTER DOMAIN COORDINATES
#----------------------------------------------------------------------------------------------------------------------------------------------------
W=301300
N=6186300
E=302000
S=6185700

#------------------------------------------------------------------------------
# CREATING MESH
#------------------------------------------------------------------------------

bounding_polygon = [[W, S], [E, S], [E, N], [W, N]]
interior_regions = anuga.read_polygon_dir(CatchmentDictionary, 'Model/Bdy')
create_mesh_from_regions(bounding_polygon,
    boundary_tags={'south': [0], 'east': [1], 'north': [2], 'west': [3]},
    maximum_triangle_area=50,
    interior_regions=interior_regions,
    filename=meshname,
    use_cache=False, 
    verbose=True)

domain = Domain(meshname, use_cache=False, verbose=True)
domain.set_name(outname)
print domain.statistics()

domain.set_quantity('friction', 0.035)
domain.set_quantity('stage', 0.0)
domain.set_quantity('elevation', filename=basename+'.csv', use_cache=True, verbose=True, alpha=0.99) 
domain.set_minimum_storable_height(0.025)

#----------------------------------------------------------------------------------------------------------------------------------------------------
# APPLY RAINFALL
#----------------------------------------------------------------------------------------------------------------------------------------------------

Rainfall_Gauge_directory = 'Model/Rainfall/Gauge/'
for filename in os.listdir(Rainfall_Gauge_directory):
    Gaugefile = Rainfall_Gauge_directory+filename
    Rainfile = 'Model/Rainfall/rain/rain.tms'
    polygon = anuga.read_polygon(Gaugefile)
    rainfall = anuga.file_function(Rainfile, quantities='rate')
    op1 = Polygonal_rate_operator(domain, rate=rainfall, factor=1.0e-3, polygon=polygon, default_rate = 0.0)
               
#----------------------------------------------------------------------------------------------------------------------------------------------------
# SETUP BOUNDARY CONDITIONS
#----------------------------------------------------------------------------------------------------------------------------------------------------
    
print 'Available boundary tags', domain.get_boundary_tags()
    
Br = anuga.Reflective_boundary(domain)
Bd = anuga.Dirichlet_boundary([0.0,0.0,0.0])

domain.set_boundary({'interior': Br, 'exterior': Bd, 'west': Bd, 'south': Bd, 'north': Bd, 'east': Bd})
  
#----------------------------------------------------------------------------------------------------------------------------------------------------
# EVOLVE SYSTEM THROUGH TIME
#----------------------------------------------------------------------------------------------------------------------------------------------------
    
t0 = time.time()
    
for t in domain.evolve(yieldstep = 60.0, finaltime = 600.0):
    domain.write_time()
