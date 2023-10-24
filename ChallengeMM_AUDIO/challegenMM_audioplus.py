import librosa
import numpy as np
import os
from pathlib import Path
#import easygui
from tkinter import messagebox
import lock
from pydub import AudioSegment
import soundfile as sf

# variables globales

props_dict={} 
DEBUG_MODE=True
SAMPLING_RATE = 44100

def init(props):
    global props_dict
    print("Python: Enter in init")
    
    #props es un diccionario
    props_dict= props

    # retornamos un cero como si fuese ok, porque
    # no vamos a ejecutar ahora el challenge
    return 0 # si init va mal retorna -1 else retorna 0

def calculateF0(filename):
    #print("Fichero de captura", filename, " encontrado")
    wav_data, sr = librosa.load(filename, sr= SAMPLING_RATE, mono=True)
    
    # Calcular la STFT del audio
    espectrograma = np.abs(librosa.stft(wav_data))
    
    # Encontrar el índice del pico de frecuencia más prominente en cada frame
    indices_picos = np.argmax(espectrograma, axis=0)
    
    # Convertir el índice del pico en frecuencia
    frecuencias = librosa.fft_frequencies(sr=sr)
    
    # Obtener las frecuencias fundamentales correspondientes a los índices de pico
    frecuencias_fundamentales = frecuencias[indices_picos]
    
    # Tomar la frecuencia fundamental promedio de todos los frames
    frecuencia_fundamental = np.mean(frecuencias_fundamentales)

    print("Frecuencia fundamental:", frecuencia_fundamental, "Hz")
    return frecuencia_fundamental

def mix(captured_audio):
    audio_nokia = props_dict["NetworkAudio"]
    audio1, sr1 = librosa.load(captured_audio, sr=None)
    audio2, sr2 = librosa.load(audio_nokia, sr=None)

    min_length = min(len(audio1), len(audio2))

    audio1 = audio1[:min_length]
    audio2 = audio2[:min_length]

    mix = audio1 + audio2
    mixed_audio = "mixed_audio.wav"
    sf.write(mixed_audio, mix, sr1)

    return mixed_audio

def returnKey(frequency):
    if (frequency == 0):
        key = frequency
        key_size = 0
    else:
        cad="%d%d"%(frequency,frequency)
        key = bytes(cad,'utf-8')
        key_size = len(key)
    result = (key, key_size)
    print ("result:",result)
    return result

def fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio):
    if os.path.exists(filename):
        audio = mix(filename)
        f0 = calculateF0(audio)
        lock.lockOUT("AUDIO")
        return f0
    
    elif os.path.exists(filename_mp3):
        print ("Fichero de captura",filename_mp3," encontrado")
        sound = AudioSegment.from_file(filename_mp3)
        sound.export(converted_audio, format="wav")
        
        audio = mix(converted_audio)
        f0 = calculateF0(audio)
        lock.lockOUT("AUDIO")
        return f0

    elif os.path.exists(filename_m4a):
        print ("Fichero de captura",filename_m4a," encontrado")
        sound = AudioSegment.from_file(filename_m4a)
        sound.export(converted_audio, format="wav")
        
        audio = mix(converted_audio)
        f0 = calculateF0(audio)
        lock.lockOUT("AUDIO")
        return f0
    
    elif os.path.exists(filename_aac):
        print ("Fichero de captura",filename_aac," encontrado")
        sound = AudioSegment.from_file(filename_aac)
        sound.export(converted_audio, format="wav")

        audio = mix(converted_audio)
        f0 = calculateF0(audio)
        return f0
        
    else:
        print ("ERROR: el fichero de captura",filename," no existe")
        return 0
    
        #mecanismo de lock END
        lock.lockOUT("AUDIO")
    
def executeChallenge():
    print("Starting execute")
    folder=os.environ['SECUREMIRROR_CAPTURES']
    print ("storage folder is :",folder)

    #mecanismo de lock BEGIN
    lock.lockIN("AUDIO")

    # lectura del audio
    #-------------------------------
    # se supone que el usuario ha depositado un .wav usando bluetooth
    # el nombre del audio puede ser siempre el mismo, fijado por el proxy bluetooth.
    # aqui vamos a "forzar" el nombre del fichero para pruebas

    filename = os.path.join(folder, "capture.wav")
    filename_mp3 = os.path.join(folder, "capture.mp3")
    filename_m4a = os.path.join(folder, "capture.m4a")
    filename_aac = os.path.join(folder, "capture.aac")
    converted_audio = os.path.join(folder, "converted_audio.wav")

    if (DEBUG_MODE==True):
        filename="test.wav"
        filename_mp3="test.mp3"
        filename_m4a="test.m4a"
        filename_aac="test.aac"
        converted_audio="converted_audio.wav"

        f0 = fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio)

    else:
        # pregunta si el usuario tiene movil con capacidad para grabar audio
        conexion=messagebox.askyesno('challenge MM: AUDIO','¿Tienes un movil con bluetooth activo y emparejado a tu PC con capacidad para grabar un audio?')
        
        #Si el usuario responde que no ha emparejado móvil y PC, devolvemos clave y longitud 0
        if (conexion==False):
            print ("ERROR: el móvil no se ha emparejado")
            lock.lockOUT("AUDIO")
            return returnKey(0)

        else:      
            # popup msgbox pidiendo interaccion
            sent=conexion=messagebox.askyesno('challenge MM: AUDIO',props_dict['interactionText'])
            
            #Si el usuario responde que no ha enviado la imagen, devolvemos clave y longitud 0
            if (sent== False):
                print ("ERROR: la imagen no se ha enviado")
                lock.lockOUT("AUDIO")
                return returnKey(0)

            else:
                f0 = fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio)

                if os.path.exists(filename):    
                    os.remove(filename)
                if os.path.exists(filename_mp3):    
                    os.remove(filename_mp3)
                if os.path.exists(filename_m4a):    
                    os.remove(filename_m4a)
                if os.path.exists(filename_aac):    
                    os.remove(filename_aac)
                if os.path.exists(converted_audio):    
                    os.remove(converted_audio)

    # construccion de la respuesta
    return returnKey(f0)

    
if __name__ == "__main__":
    midict={"interactionText": '¿Has enviado el audio desde el móvil a tu PC?', "param2":3, "NetworkAudio":"nokia.mp3"}
    init(midict)
    executeChallenge()
