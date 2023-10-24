
import numpy as np
import random
#calculo de "tesela" de longitud de tesela
#buscamos en google maps la longitud y la latitud de las sedes
sedes = [[40.514476148773156, -3.674447499629994],
         [40.533657515908644, -3.6564230558242317],
         [40.4893175, -3.3418228]]
         #[40.4993175, -3.3418228]]


result=4312

# Cálculo de la tesela
tesela = 500
tesela = 500/30  / 3600


X=[]
Y=[]

for i in range(len(sedes)):
    X.append( int(round(sedes[i][0] / tesela)))
    Y.append(int(round(sedes[i][1] / tesela)))

print(X)
print(Y)

lat = np.poly1d([1])
lon= np.poly1d([1])
for i in X:
    solucion_parcial = np.poly1d([1,-i])
    lat=np.polymul(solucion_parcial, lat)

    
for i in Y:
    solucion_parcial = np.poly1d([1,-i])

    lon=np.polymul(solucion_parcial, lon)

    
num=np.poly1d([result])
lon=lon+num
num=np.poly1d([result])
lat=lat+num
np.savez('ecuaciones',lat,lon)

#print('solucion')
#print(C)
#print(np.matmul(x,C[0]))

