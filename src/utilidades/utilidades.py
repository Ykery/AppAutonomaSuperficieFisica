from src.modelo.dao import ExperimentoDAO, ConfiguracionTeasDAO, ConfiguracionMokeDAO, ResultadoTeasDAO, ResultadoMokeDAO, MarcadorDAO
from src.vista.componentes.grafica import Plot
from docxtpl import DocxTemplate, InlineImage
from docx2pdf import convert
from os import remove
import sys
from io import BytesIO
from PyQt6 import Qwt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtWidgets import QFileDialog
from threading import Thread

def crear_pdf_experimento(id, pdf_path):
    docx_path = crear_docx_experimento(id)
    convertir_docx_pdf(docx_path, pdf_path)

def crear_docx_experimento(id, docx_path = "./experimento.docx"): 
    """
    Crea un documento de Word a partir de un experimento en la base de datos.

    :param id: Identificador del experimento en la base de datos.
    :type id: int
    :param docx_path: Ruta del documento de Word a crear, defaults to "./experimento.docx"
    :type docx_path: str, optional
    :return: Ruta del documento de Word creado.
    :rtype: str
    
    """
    # Definir la ruta por defecto para crear el documento en la carpeta raiz del proyecto
    TEMPLATE_PATH = "src/resources/plantilla_experimento.docx"
    
    # Obtener el experimento de la base de datos
    experimento = ExperimentoDAO.obtener_por_id(id)    
    # Si no existe el experimento, retornar False
    if experimento is None:
        return False
    marcadores = MarcadorDAO.obtener_por_id_experimento(experimento.id)
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
    context["marcadores_exp"] = marcadores
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

def exportar_mostrar_pdf(id_experimento, pdf_path):
    crear_pdf_experimento(id_experimento, pdf_path)
    mostrar_pdf(pdf_path)
    
def pedir_ruta_exportar_pdf(parent, id_experimento):
    pdf_path = QFileDialog.getSaveFileName(parent, "Guardar PDF", "", "PDF Files (*.pdf)")
    if pdf_path[0] == "":
        return
    hilo = Thread(target=exportar_mostrar_pdf, args=(id_experimento, pdf_path[0])) # pdf_path[0] es la ruta del pdf
    hilo.start()
    
    
def escribir_csv(path, valor_x, valor_y):
    with open(path, "a") as file:
        file.write(f"{valor_x},{valor_y}\n")