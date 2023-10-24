from math import log10, sqrt
import cv2
# para instalar la libreria openCV simplemente:
# pip3 install opencv-python
# o bien py -m pip install opencv-python
import numpy as np
import os
from pathlib import Path
import time
#para instalar el modulo easygui simplemente:
#pip3 install easygui
# o bien py -m pip install easygui
#import easygui
from tkinter import messagebox
import lock
import json
import statistics
import math

# variables globales
# ------------------
props_dict={}
DEBUG_MODE=False

def init(props):
    global props_dict
    print("Python: Enter in init")
    
    #props es un diccionario
    props_dict= props
    
    # retornamos un cero como si fuese ok, porque
    # no vamos a ejecutar ahora el challenge
    return 0 # si init va mal retorna -1 else retorna 0
    

def executeChallenge():
    print("Starting execute")
    #for key in os.environ: print(key,':',os.environ[key]) # es para ver variables entorno
    folder=os.environ['SECUREMIRROR_CAPTURES']
    print ("storage folder is :",folder)
    
    # mecanismo de lock BEGIN
    # -----------------------
    lock.lockIN("GPS")

    # pregunta si el usuario tiene movil con capacidad GPS
    # -----------------------------------------------------
    #textos en español, aunque podrian ser parametros adicionales del challenge
    #conexion=easygui.ynbox(msg='¿Tienes un movil con bluetooth activo y emparejado con tu PC con capacidad GPS?', choices=("Yes","Not"))
    conexion=messagebox.askyesno('challenge MM: GPS','¿Tienes un movil con bluetooth activo emparejado a tu PC con capacidad GPS?')
    print (conexion)

    if (conexion==False):
        lock.lockOUT("GPS")
        print ("return key zero and long zero")
        key=0
        key_size=0
        result =(key,key_size)
        print ("result:",result)
        return result # clave cero, longitud cero

    #popup msgbox pidiendo interaccion
    #---------------------------------
    #output = easygui.msgbox(props_dict["interactionText"], "challenge MM: GPS")
    output = messagebox.showinfo("challenge MM: GPS",props_dict["interactionText"])
    # lectura del fichero capture.gps
    #-------------------------------
    # se supone que el usuario ha depositado un .gps usando bluetooth
    # el nombre del fichero puede ser siempre el mismo, fijado por el proxy bluetooth.
    # aqui vamos a "forzar" el nombre del fichero para pruebas
    filename="capture.gps"
    if (DEBUG_MODE==True):
        filename="test.gps"
    print(folder+"/"+filename)
    if os.path.exists(folder+"/"+filename):    
        with open(folder+"/"+filename) as cosa:
            geodata=json.load(cosa)
            print ("Geolocation data")
            print ("  Version:",geodata["version"])
            print ("  GPS:\t",geodata["gps"][0],"\n\t",geodata["gps"][1])
            print ("  Orientation:\t",geodata["orientation"][0],"\n\t\t",geodata["orientation"][1])
    else:
        print ("ERROR: el fichero de captura",filename," no existe")
        key=0
        key_size=0
        result =(key,key_size)
        print ("result:",result)
        lock.lockOUT("GPS")
        return result # clave cero, longitud cero  
   
    
    # una vez consumida, podemos borrar la captura (fichero "capture.gps")
    #----------------------------------------------------------------------luego descomentar lo siguiente
    #if (DEBUG_MODE==False):
    #    if os.path.exists(folder+"/"+filename):    
    #        os.remove(folder+"/"+filename)        
    
    #--------------------------------------------------------------------
    #mecanismo de lock END
    #-----------------------
    lock.lockOUT("GPS")
    
    #procesamiento
    # averigua si la altura esta en un rango concreto
    lon=statistics.mean([geodata["gps"][0]["lon"],geodata["gps"][1]["lon"]])
    lat=statistics.mean([geodata["gps"][0]["lat"],geodata["gps"][1]["lat"]])
    print('a')
    print(lon)
    print(lat)

    #
    tesela = 500/30/ 3600
    #coordenadas lon y lat en teselas 
    lon=int(round(lon / tesela))
    lat=int(round(lat / tesela))
    print(lon)
    print(lat)
    arrays=np.load("ecuaciones.npz")
    ec_lat=np.poly1d(arrays['arr_0'])
    ec_lon=np.poly1d(arrays['arr_1'])

    valor_lon=np.polyval(ec_lon,lon)
    """if valor_lon<0:
        valor_lon=0
    elif valor_lon>20000:
        valor_lon=20000"""
    valor_lat=np.polyval(ec_lat,lat)
    """if valor_lat<0:
        valor_lat=0
    elif valor_lat>20000:
        valor_lat=20000"""
    print(valor_lon)
    print(valor_lat)
    #construccion de la respuesta
    cad="%d%d"%(valor_lon,valor_lat)
    key = bytes(cad,'utf-8')
    key_size = len(key)
    result =(key, key_size)
    print ("result:",result)
    return result


if __name__ == "__main__":
    midict={"interactionText": "Por favor haz una captura de datos de geolocalización."}
    init(midict)
    executeChallenge()

