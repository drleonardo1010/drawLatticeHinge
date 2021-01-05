import rhinoscriptsyntax as rs
import drawlatticehinge as lh
import math

def clear_all():
    all_obs = rs.ObjectsByType(0)
    rs.DeleteObjects(all_obs)

clear_all()

parameter = [37.5,0.2,0.4,1.5,10]
lattice = lh.LatticeHinge(parameter)

startPoint = (0,0,0)
endPoint = (200,200,0)

lattice.draw_lattice_follow_crosspoint(startPoint,endPoint)
