import os, sys

import vtktools
import numpy as np
import matplotlib  as mpl
mpl.use('ps')
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from paraview.simple import *

## READ archive (too many points... somehow)

label = sys.argv[1]
dayi  = int(sys.argv[2])
dayf  = int(sys.argv[3])
days  = int(sys.argv[4])

path = '/tamay/mensa/fluidity/hycom_winter/'+label+'/'
reader = XMLPartitionedUnstructuredGridReader()
filter = CleantoGrid(reader)
writer  = XMLPUnstructuredGridWriter(Input=filter)

try: os.stat('./plot/'+label)
except OSError: os.mkdir('./plot/'+label)

Tmax = 21.0
Tmin = 19.8

for time in range(dayi,dayf,days):
 tlabel = str(time)
 while len(tlabel) < 3: tlabel = '0'+tlabel

 file0 = 'mli_' + str(time) + '.pvtu'
 filepath = path+file0
 file1 = label+'_' + tlabel
 fileout  = path + file1

 filetemp = './temp_'+label+'.pvtu'

 print 'opening: ', filepath

 reader.FileName = filepath
 reader.PointArrayStatus = ['Temperature','Velocity']
 filter = CleantoGrid(reader)
 writer.FileName = filetemp
 writer.Input = filter
 writer.UpdatePipeline()
 
 data = vtktools.vtu(filetemp)
 
 #print 'fields: ', data.GetFieldNames()
 coord = data.GetLocations()
 T = data.GetScalarField('Temperature')
 U = data.GetVectorField('Velocity')
 #T = data.GetScalarField('T')

 del data

 id_T = np.asarray(np.where(coord[:,2] == 0)) # values from surface
 
 x = coord[id_T,0].flatten()
 y = coord[id_T,1].flatten()

 Us = U[id_T,0].flatten()
 Vs = U[id_T,1].flatten()
 Ws = U[id_T,2].flatten()

 Ts = T[id_T].flatten()
 Ts[np.asarray(np.where(Ts > Tmax))]  = Tmax
 Ts[np.asarray(np.where(Ts < Tmin))]  = Tmin

 ## PLOT

 # mask quiver for legend
 id_x = np.asarray(np.where(x > 21000)) 
 id_y = np.asarray(np.where(y > 49000)) 
 Us[np.intersect1d(id_x,id_y)] = float('NaN')
 Vs[np.intersect1d(id_x,id_y)] = float('NaN')
 
 plt.figure()
 plt.gca().set_aspect('equal')
 plt.autoscale(enable=True, axis='both', tight=True)
 if time == 0:
  plt.triplot(x,y,linewidth=0.5,color='gray')
 v1 = np.linspace(Tmin, Tmax, 50, endpoint=True)
 v2 = np.linspace(Tmin, Tmax, 11, endpoint=True)
 plt.tricontourf(x,y,Ts,v1)
 plt.colorbar(ticks=v2)
# q = plt.quiver(x,y,Us,Vs,units='width',scale=1/0.25)
# p = plt.quiverkey(q,25000,50000,1,"1 m/s",coordinates='data')
 plt.ylabel('Longitude')
 plt.xlabel('Latitude')
 plt.xticks(range(0,35000,5000),(range(0,35,5)))
 plt.yticks(range(0,60000,10000),(range(0,60,10)))
 plt.title('T, 2Km, '+str(np.trunc(time*5/24)/10.0)+' day')
 plt.savefig('./plot/'+label+'/'+file1+'.eps',bbox_inches='tight')
 plt.close()
 print 'saved '+'./plot/'+label+'/'+file1+'.eps\n'


# os.system('gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dTextAlphaBits=4 -r300 -sOutputFile=./plot/'+label+'/'+file1+'.png ./plot/'+label+'/'+file1+'.eps')
 os.system('gs -sDEVICE=jpeg -dJPEGQ=100 -dNOPAUSE -dBATCH -dSAFER -dTextAlphaBits=4 -r300 -sOutputFile=./plot/'+label+'/'+file1+'.jpg ./plot/'+label+'/'+file1+'.eps')
 os.system('mogrify ./plot/'+label+'/'+file1+'.jpg -trim ./plot/'+label+'/'+file1+'.jpg')
# os.system('mogrify ./plot/'+label+'/'+file1+'.png -trim ./plot/'+label+'/'+file1+'.png')

print 'Making movie animation'

fr  = '10'
br  = '4096k'
crf = '24'

opts = '-y -f image2 -r '+fr+' -i ./plot/'+label+'/'+label+'_%03d.jpg -vcodec'

#ffmpeg_ogg = 'ffmpeg '+opts+' libtheora -b:v '+br+' ./plot/'+label+'/'+label+'.ogg'
ffmpeg_mp4 = 'ffmpeg '+opts+' libx264 -threads 0 -crf '+crf+' -s 1250x1620 ./plot/'+label+'/'+label+'.avi'

#print ffmpeg_ogg
#os.system(ffmpeg_ogg)

print ffmpeg_mp4
os.system(ffmpeg_mp4)
