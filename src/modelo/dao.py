from .clases import *

class ExperimentoDAO():

    # 'experimento' es un objeto de la clase Experimento
    def crear(experimento):
        session = Conexion.getConexion()
        session.add(experimento)
        session.commit()
        session.close()
        return ExperimentoDAO.obtener_ultimo()

    def obtener_por_id(id):
        session = Conexion.getConexion()
        experimento = session.query(Experimento).filter(Experimento.id == id).first()
        session.close()
        return experimento

    def obtener_todos():
        session = Conexion.getConexion()
        experimentos = session.query(Experimento).all()
        session.close()
        return experimentos
    
    def obtener_ultimo():
        session = Conexion.getConexion()
        experimento = session.query(Experimento).order_by(Experimento.id.desc()).first()
        session.close()
        return experimento

    def actualizar(experimento):
        session = Conexion.getConexion()
        session.add(experimento)
        session.commit()
        session.close()


    def eliminar(experimento):
        session = Conexion.getConexion()
        session.delete(experimento)
        session.commit()
        session.close()


class ResultadoTeasDAO():
    
    def crear(resultado):    
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        resultado = session.query(ResultadoTeas).filter(ResultadoTeas.id_resultado_exp == id).first()
        session.close()
        return resultado
    
    def obtener_por_id_experimento(id_experimento):
        session = Conexion.getConexion()
        resultados = session.query(ResultadoTeas).filter(ResultadoTeas.id_experimento == id_experimento).all()
        session.close()
        return resultados
    
    def obtener_todos():    
        session = Conexion.getConexion()
        resultados = session.query(ResultadoTeas).all()
        session.close()
        return resultados
    
    def actualizar(resultado):    
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()
    
    def eliminar(resultado):    
        session = Conexion.getConexion()
        session.delete(resultado)
        session.commit()
        session.close()


class ResultadoMokeDAO():
    
    def crear(resultado):    
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        resultado = session.query(ResultadoMoke).filter(ResultadoMoke.id_resultado_exp == id).first()
        session.close()
        return resultado
    
    def obtener_por_id_experimento(id_experimento):
        session = Conexion.getConexion()
        resultados = session.query(ResultadoMoke).filter(ResultadoMoke.id_experimento == id_experimento).all()
        session.close()
        return resultados
    
    def obtener_todos():    
        session = Conexion.getConexion()
        resultados = session.query(ResultadoMoke).all()
        session.close()
        return resultados
    
    def actualizar(resultado):    
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()
    
    def eliminar(resultado):    
        session = Conexion.getConexion()
        session.delete(resultado)
        session.commit()
        session.close()


class ConfiguracionTeasDAO():
    
    # 'configuracion' es un objeto de la clase ConfiguracionTeas
    def crear(configuracion):    
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        configuracion = session.query(ConfiguracionTeas).filter(ConfiguracionTeas.id_experimento == id).first()
        session.close()
        return configuracion
    
    def obtener_todos():    
        session = Conexion.getConexion()
        configuraciones = session.query(ConfiguracionTeas).all()
        session.close()
        return configuraciones
    
    def actualizar(configuracion):    
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()
    
    def eliminar(configuracion):    
        session = Conexion.getConexion()
        session.delete(configuracion)
        session.commit()
        session.close()


class ConfiguracionMokeDAO():
    
    def crear(configuracion):    
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        configuracion = session.query(ConfiguracionMoke).filter(ConfiguracionMoke.id_experimento == id).first()
        session.close()
        return configuracion
    
    def obtener_todos():    
        session = Conexion.getConexion()
        configuraciones = session.query(ConfiguracionMoke).all()
        session.close()
        return configuraciones
    
    def actualizar(configuracion):    
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()
    
    def eliminar(configuracion):    
        session = Conexion.getConexion()
        session.delete(configuracion)
        session.commit()
        session.close()


class MarcadorDAO():
    
    def crear(marcador):    
        session = Conexion.getConexion()
        session.add(marcador)
        session.commit()
        #session.refresh(marcador)
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        marcador = session.query(Marcador).filter(Marcador.id == id).first()
        session.close()
        return marcador
    
    def obtener_por_id_experimento(id_experimento):
        session = Conexion.getConexion()
        marcadores = session.query(Marcador).filter(Marcador.id_experimento == id_experimento).all()
        session.close()
        return marcadores
    
    def obtener_todos():    
        session = Conexion.getConexion()
        marcadores = session.query(Marcador).all()
        session.close()
        return marcadores
    
    def actualizar(marcador):    
        session = Conexion.getConexion()
        session.add(marcador)
        session.commit()
        session.close()
    
    def eliminar(marcador):    
        session = Conexion.getConexion()
        session.delete(marcador)
        session.commit()
        session.close()
