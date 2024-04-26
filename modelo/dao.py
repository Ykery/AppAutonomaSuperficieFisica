from clases import *

class ExperimentoDAO():

    def crear(experimento):
        session = Conexion.getConexion()
        session.add(experimento)
        session.commit()
        session.close()

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
        resultado = session.query(ResultadoTeas).filter(ResultadoTeas.id == id).first()
        session.close()
        return resultado
    
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
        resultado = session.query(ResultadoMoke).filter(ResultadoMoke.id == id).first()
        session.close()
        return resultado
    
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
    
    def crear(configuracion):    
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()
    
    def obtener_por_id(id):    
        session = Conexion.getConexion()
        configuracion = session.query(ConfiguracionTeas).filter(ConfiguracionTeas.id == id).first()
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
        configuracion = session.query(ConfiguracionMoke).filter(ConfiguracionMoke.id == id).first()
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


