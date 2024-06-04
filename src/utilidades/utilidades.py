import sys
from io import BytesIO
from os import remove
from threading import Thread

from docx2pdf import convert
from docxtpl import DocxTemplate, InlineImage
from PyQt6 import Qwt
from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog

from src.modelo.dao import (ConfiguracionMokeDAO, ConfiguracionTeasDAO,
                            ExperimentoDAO, MarcadorDAO, ResultadoMokeDAO,
                            ResultadoTeasDAO)
from src.vista.componentes.grafica import Plot


def crear_pdf_experimento(id, pdf_path):
    """
    Crea un archivo PDF a partir de un documento de Word (docx) generado para un experimento.

    Este método genera un archivo PDF utilizando un documento de Word previamente creado para un experimento específico.

    :param id: El identificador único del experimento.
    :type id: int
    :param pdf_path: La ruta donde se guardará el archivo PDF generado.
    :type pdf_path: str
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Crear un archivo PDF a partir del documento de Word para un experimento con ID 1
        crear_pdf_experimento(1, "experimento.pdf")

    """
    docx_path = crear_docx_experimento(id)
    convertir_docx_pdf(docx_path, pdf_path)

def crear_docx_experimento(id, docx_path = "./experimento.docx"):
    """
    Crea un documento de Word (docx) para un experimento específico.

    Este método genera un documento de Word que contiene información sobre un experimento, incluida una descripción, 
    configuración, gráfico de resultados y marcadores asociados.

    :param id: El identificador único del experimento.
    :type id: int
    :param docx_path: La ruta donde se guardará el documento de Word generado. Por defecto, "./experimento.docx".
    :type docx_path: str, optional
    :return: La ruta del archivo del documento de Word generado si se crea correctamente, False si el experimento no existe.
    :rtype: str or bool

    Ejemplo de uso:

    .. code-block:: python

        # Crear un documento de Word para un experimento con ID 1
        ruta_documento = crear_docx_experimento(1)

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
    if experimento.tipo.lower() == "teas":
        plot_experimento = Plot("TEAS Timescan", "Time[sec]", "Intensity [arb. un.]", None)
    elif experimento.tipo.lower() == "moke":
        plot_experimento = Plot(
            "Moke Loop Graph",
            "Magnetic field (Oe)",
            "Intensity [arb. un.]",
            None,
            color=QColor(131, 25, 70),
        )
    plot_experimento.resize(270,270)
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
    """
    Convierte un archivo de Word (docx) en un archivo PDF y elimina el archivo de Word original.

    Este método toma un archivo de Word en formato docx, lo convierte a PDF y luego elimina el archivo de Word original.

    :param docx_path: La ruta del archivo de Word (docx) que se convertirá a PDF.
    :type docx_path: str
    :param pdf_path: La ruta donde se guardará el archivo PDF generado.
    :type pdf_path: str
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Convertir un archivo de Word a PDF y eliminar el archivo de Word original
        convertir_docx_pdf("documento.docx", "documento.pdf")

    """
    convert(docx_path, pdf_path)
    remove(docx_path)

def mostrar_pdf(path):
    """
    Abre el archivo PDF en el visor de PDF predeterminado del sistema operativo.

    Este método abre el archivo PDF especificado en el visor de PDF predeterminado del sistema operativo.

    :param path: La ruta del archivo PDF que se abrirá.
    :type path: str
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Abrir un archivo PDF en el visor de PDF predeterminado del sistema operativo
        mostrar_pdf("documento.pdf")

    """
    import os
    os.system("start " + path)

def exportar_mostrar_pdf(id_experimento, pdf_path):
    """
    Exporta el experimento a un archivo PDF y luego lo muestra.

    Este método exporta el experimento con el ID especificado a un archivo PDF en la ubicación especificada
    y luego abre el archivo PDF en el visor de PDF predeterminado del sistema operativo.

    :param id_experimento: El ID del experimento a exportar.
    :type id_experimento: int
    :param pdf_path: La ruta donde se guardará el archivo PDF exportado.
    :type pdf_path: str
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Exportar el experimento con ID 123 a un archivo PDF y mostrarlo
        exportar_mostrar_pdf(123, "experimento.pdf")

    """
    crear_pdf_experimento(id_experimento, pdf_path)
    mostrar_pdf(pdf_path)
    
def pedir_ruta_exportar_pdf(parent, id_experimento):
    """
    Abre un cuadro de diálogo para seleccionar la ruta de exportación y luego exporta el experimento a un archivo PDF.

    Este método abre un cuadro de diálogo para que el usuario seleccione la ruta y el nombre del archivo PDF de destino.
    Luego, exporta el experimento con el ID especificado a ese archivo PDF.

    :param parent: El widget principal padre del cuadro de diálogo.
    :type parent: QWidget
    :param id_experimento: El ID del experimento a exportar.
    :type id_experimento: int
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Pedir al usuario que seleccione la ruta y el nombre del archivo PDF y luego exportar el experimento
        pedir_ruta_exportar_pdf(parent_widget, 123)

    """
    pdf_path = QFileDialog.getSaveFileName(parent, "Guardar PDF", "", "PDF Files (*.pdf)")
    if pdf_path[0] == "":
        return
    hilo = Thread(target=exportar_mostrar_pdf, args=(id_experimento, pdf_path[0])) # pdf_path[0] es la ruta del pdf
    hilo.start()
    
    
def escribir_csv(path, valor_x, valor_y):
    """
    Escribe un par de valores en formato CSV en un archivo especificado.

    Este método escribe un par de valores (valor_x, valor_y) en formato CSV en el archivo especificado por la ruta.

    :param path: La ruta del archivo CSV donde se escribirán los valores.
    :type path: str
    :param valor_x: El valor correspondiente al eje X que se va a escribir en el archivo CSV.
    :type valor_x: float or int
    :param valor_y: El valor correspondiente al eje Y que se va a escribir en el archivo CSV.
    :type valor_y: float or int
    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        # Escribir un par de valores en un archivo CSV
        escribir_csv("datos.csv", 10.5, 20.3)

    """
    with open(path, "a") as file:
        file.write(f"{valor_x},{valor_y}\n")