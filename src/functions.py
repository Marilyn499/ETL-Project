import pandas as pd
import openpyxl
from selenium import webdriver
import requests as req
from bs4 import BeautifulSoup as bs
import json
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

import warnings   # para quitar warnings
warnings.simplefilter('ignore')

#_______________________________Función para scraping de tabla INE________________________________________#
def scraping():
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get("https://www.ine.es/")    
    escribir = driver.find_element_by_xpath('//input[@id="searchString"]')
    escribir.click()
    time.sleep(2)
    escribir.send_keys('tabaco')

    buscar = driver.find_element_by_xpath('//button[@id="Menu_botonBuscador"]')
    buscar.click()
    time.sleep(2)
    enlace = driver.find_element_by_xpath('//*[@id="tabsResult"]/ul/li[1]/ul/li[1]/a/span[3]')
    enlace.click()

    try:
        driver.switch_to.window(driver.window_handles[1])
        print("ventana cambiada")
        time.sleep(5)
    except:
        time.sleep(5)

    cookies = driver.find_element_by_css_selector('#aceptarCookie')
    cookies.click()
    
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    verTabla = driver.find_element_by_css_selector('#aceptarCookie')
    verTabla.click()

    tabla=driver.find_element_by_tag_name('tbody')
    filas=tabla.find_elements_by_tag_name('tr')

    data=[[e.text for e in f.find_elements_by_tag_name('td')] for f in filas]
    cabeceras=driver.find_element_by_tag_name('thead')
    cabeceras=[c.text for c in cabeceras.find_elements_by_tag_name('th')]

    tablaCompleta = pd.DataFrame(data)
    
    tabla_Completa = tablaCompleta.rename(columns={0:'Porcentaje_Pandemia',
                                1:'Fumador_Diario_Pandemia',
                                2:'Fumador_Ocasional_Pandemia',
                                3:'No_Fumador_Pandemia',
                                4:'Porcentaje_Antes',
                                5:'Fumador_Diario_Antes',
                                6:'Fumador_Ocasional_Antes',
                                7:'No_Fumador_Antes'})

    tabla_Completa.insert(0,"Grupos",['Ambos','Total1','15-44A','45-54A','65+A','Hombres','Total2','15-44H','45-54H','65+H','Mujeres','Total3','15-44M','45-54M','65+M'],True)

    tabla_Completa.drop([0,5,6,7,8,9,10,11,12,13,14],axis=0)

    tabla_Completa.set_index('Grupos', drop=True, inplace=True, verify_integrity=True)

    return tabla_Completa                      


#_______________________________Función obtener datos de API________________________________________#
def datos():
    respuesta = req.get('https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/49159?tip=AM')
    contenido = respuesta.json()

    lista = dict()
    for i in range(0,3):
        anyo = contenido[0]['Data'][i]['Anyo']
        valor = contenido[0]['Data'][i]['Valor']
        lista[anyo] = valor
    return  lista