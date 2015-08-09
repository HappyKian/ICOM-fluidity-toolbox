import os, sys
#import gc
import fio, myfun
import vtktools
import numpy as np
import matplotlib  as mpl
mpl.use('ps')
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#gc.enable()

## WEAD archive (too many points... somehow)
# args: name, dayi, dayf, days

label = sys.argv[1]
basename = sys.argv[2]
dayi  = int(sys.argv[3])
dayf  = int(sys.argv[4])
days  = int(sys.argv[5])

path = '/tamay2/mensa/fluidity/'+label+'/'

try: os.stat('./plot/'+label)
except OSError: os.mkdir('./plot/'+label)

file0 = basename+'_' + str(1) + '.pvtu'
filepath = path+file0
#
data = vtktools.vtu(filepath)
coords = data.GetLocations()
del data

depths = sorted(list(set(coords[:,2])),reverse=True)

XM = max(coords[:,0])
Xm = min(coords[:,0])
YM = max(coords[:,1])
Ym = min(coords[:,1])

X = np.linspace(Xm,XM,10000/50)
Y = np.linspace(Ym,YM,10000/50)

for time in range(dayi,dayf,days):
 tlabel = str(time)
 while len(tlabel) < 3: tlabel = '0'+tlabel
 #
 file0 = basename+'_' + str(time) + '.pvtu'
 #
 filepath = path+file0
 file1 = 'W_'+label+'_' + tlabel
 fileout  = path + file1
 #
 print 'opening: ', filepath
 #
 data = vtktools.vtu(filepath)
 print 'fields: ', data.GetFieldNames()
 print 'extract V, W'
 #
 W = data.GetVectorField('Velocity_CG')
 del data
 #
 for d in range(len(depths)):
  Wt, = W[np.where(coords[:,2]==depths[d]),2]
  Xl = coords[coords[:,2] == depths[d],0]
  Yl = coords[coords[:,2] == depths[d],1]
  Wi = griddata(Xl,Yl,Wt,X,Y,interp='nn')
  #
  # TOTAL flux
  #
  fig = plt.figure() 
  #
  v = np.linspace(-5e-7, 5e-7, 50, endpoint=True)
  vl = np.linspace(-5e-7, 5e-7, 5, endpoint=True)
  plt.contourf(X,Y,Wi,50,extend='both',cmap=plt.cm.PiYG)
 # plt.contourf(X,Y,Wi,50,extend='both',cmap=plt.cm.PiYG)
 # plt.contourf(X,Y,Wi,50,extend='both',cmap=plt.cm.PiYG)
  plt.colorbar()
  #plt.colorbar(ticks=vl)
  # plt.contour(Xl,depths,rho,rl,colors='k',linewidths=1)
  #plt.autumn()
  plt.xlabel('X (m)')
  plt.ylabel('Z (m)')
  # plt.xticks(range(lati,lonf,1000),(range(0,15,1)))
  # plt.yticks(range(depthi,depthf,10),(range(0,15,1)))
  plt.title('Velocity')
  #
  plt.savefig('./plot/'+label+'/'+file1+'_'+str(abs(depths[d]))+'.eps',bbox_inches='tight')
  plt.close()
  print 'saved '+'./plot/'+label+'/'+file1+'.eps\n'

