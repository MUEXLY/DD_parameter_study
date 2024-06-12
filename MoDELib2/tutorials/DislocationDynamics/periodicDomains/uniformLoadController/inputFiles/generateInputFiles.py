import sys
sys.path.append("../../../../../python/")
from modlibUtils import *

# Make a local copy of simulation parameters file and modify that copy if necessary
DDfile='DD.txt'
shutil.copy2('../../'+DDfile, '.') 

pf=PolyCrystalFile("../../../MaterialsLibrary/AlMg5.txt");
pf.absoluteTemperature=0;
pf.dislocationMobilityType='default'
pf.meshFile='../../../MeshLibrary/unitCube.msh'
#pf.grain1globalX1=np.array([1,2,1])     # global x1 axis. Overwritten if alignToSlipSystem0=true
#pf.grain1globalX3=np.array([1,1,-3])    # global x3 axis. Overwritten if alignToSlipSystem0=true
pf.alignToSlipSystem0=1
#pf.boxEdges=np.array([[1,2,1],[2,1,1],[1,1,-3]]) # i-throw is the direction of i-th box edge
pf.boxScaling=np.array([400, 400, 3000]);
pf.X0=np.array([0.5,0.5,0.5]) # Centering unitCube mesh. Mesh nodes X are mapped to x=F*(X-X0)
pf.periodicFaceIDs=np.array([0,1,2,3,4,5])
pf.solidSolutionNoiseMode=0
pf.stackingFaultNoiseMode=1
pf.stackingFaultGridSize=np.array([1200,1200])
pf.stackingFaultCorrelationFile='../../../NoiseLibrary/AlMg5_Cx_R100_ISF.vtk'
pf.stackingFaultNoiseFile='../../../NoiseLibrary/noise_AlMg5.vtk'

pf.write()
#print(pf.A)
