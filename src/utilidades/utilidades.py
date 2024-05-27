from ..modelo.dao import ExperimentoDAO, ConfiguracionTeasDAO, ConfiguracionMokeDAO, ResultadoTeasDAO, ResultadoMokeDAO
from ..vista.teasGraph import Plot
from docxtpl import DocxTemplate, InlineImage
from docx2pdf import convert
from os import remove
import sys
from io import BytesIO
from PyQt6 import Qwt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice

def crear_pdf_experimento(id, pdf_path):
    docx_path = crear_docx_experimento(id)
    convertir_docx_pdf(docx_path, pdf_path)

def crear_docx_experimento(id, docx_path = "./experimento.docx"): 
    # Definir la ruta por defecto para crear el documento en la carpeta raiz del proyecto
    TEMPLATE_PATH = "src/resources/plantilla_experimento.docx"
    
    # Obtener el experimento de la base de datos
    experimento = ExperimentoDAO.obtener_por_id(id)    
    # Si no existe el experimento, retornar False
    if experimento is None:
        return False
    datos_x = []
    datos_y = []
    configuracion = ""
    # Crear los datos de la grafica
    if experimento.tipo.lower() == "teas":
        configuracion = ConfiguracionTeasDAO.obtener_por_id(experimento.id)
        resultados = ResultadoTeasDAO.obtener_por_id_experimento(experimento.id)
        for resultado in resultados:
            datos_x.append(resultado.time)
            datos_y.append(resultado.intensity)
    elif experimento.tipo.lower() == "moke":
        configuracion = ConfiguracionMokeDAO.obtener_por_id(experimento.id)
        resultados = ResultadoMokeDAO.obtener_por_id_experimento(experimento.id)
        for resultado in resultados:
            datos_x.append(resultado.magnetic_field)
            datos_y.append(resultado.intensity)
    # Si no existe la configuracion, retornar None
    if configuracion is None:
        configuracion = "No existe configuracion asociada al experimento"
        
    # Crear el documento de Word
    doc = DocxTemplate(TEMPLATE_PATH)
    # Crear la imagen de la grafica
    plot_experimento = Plot()
    plot_experimento.resize(350,300)
    plot_experimento.showData(datos_x, datos_y)
    printer : QPixmap = plot_experimento.grab()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.ReadWrite)
    printer.save(buffer, 'PNG')
    # Guardar la imagen en un buffer
    image_bytes = buffer.data()
    image_stream = BytesIO(image_bytes)
    # Crear la imagen en el documento usando el buffer
    inline_image : InlineImage = InlineImage(doc, image_stream)
    # Crear el contexto del documento
    context = {"nombre_exp" : None,"descripcion_exp" : None, "configuracion_exp" : None,  "grafica_exp" : None}
    context["nombre_exp"] = experimento.rutaCsv.split("/")[-1].split(".")[0]
    context["descripcion_exp"] = experimento.descripcion
    context["configuracion_exp"] = str(configuracion)
    context["grafica_exp"] = inline_image
    doc.render(context)
    # Save doc to pdf
    doc.save(docx_path)
    return docx_path

def convertir_docx_pdf(docx_path, pdf_path):
    convert(docx_path, pdf_path)
    remove(docx_path)

def mostrar_pdf(path):
    import os
    os.system("start " + path)
