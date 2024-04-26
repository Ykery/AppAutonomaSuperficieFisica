# Ejemplo de declaracion de una clase usuario de una base de datos utilizando sqlalchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker


class Base(DeclarativeBase):
    pass

# Clase para crear una conexion a la base de datos
class Conexion():
    # Crear un motor de base de datos
    engine = create_engine('mysql://root:root@localhost/aplicacionuam', echo=True)

    def iniciar_bbdd():
        Base.metadata.create_all(Conexion.engine)

    def getConexion():
        Session = sessionmaker(bind=Conexion.engine)
        session = Session()
        return session
    

class Experimento(Base):
    __tablename__ = 'experimentos'
   
    id = Column(Integer, autoincrement=True, primary_key=True)
    descripcion = Column(String(45), nullable=False)
    rutaCsv = Column(String(45), nullable=False)
    # Atributo fecha_creacion autogenerado al insertar un nuevo registro
    fecha_creacion = Column(DateTime, default=sqlalchemy.func.now())
    tipo =Column(String(45), nullable=False)

    configuracion = {}
    def __repr__(self):
        return f"""Experimento(id={self.id}, 
            descripcion={self.descripcion}, 
            rutaCsv={self.rutaCsv}, 
            fecha_creacion={self.fecha_creacion}, 
            tipo={self.tipo})
            """


class ResultadoTeas(Base):
    __tablename__ = 'resultados_teas'
    
    id_resultado_exp = Column(Integer, autoincrement=True, primary_key=True)
    id_experimento = Column(Integer, ForeignKey('experimentos.id'), nullable=False)
    time = Column(DECIMAL, nullable=False)
    intensity = Column(DECIMAL, nullable=False)
    
    def __repr__(self):
        return f"""ResultadoTeas(id_resultado_exp={self.id_resultado_exp},
            id_experimento={self.id_experimento},
            time={self.time},
            intensity={self.intensity})
            """


class ResultadoMoke(Base):
    __tablename__ = 'resultados_moke'
    
    id_resultado_exp = Column(Integer, autoincrement=True, primary_key=True)
    id_experimento = Column(Integer, ForeignKey('experimentos.id'), nullable=False)
    magnetic_field = Column(DECIMAL, nullable=False)
    intensity = Column(DECIMAL, nullable=False)
    
    def __repr__(self):
        return f"""ResultadoMoke(id_resultado_exp={self.id_resultado_exp},
            id_experimento={self.id_experimento},
            magnetic_field={self.magnetic_field},
            intensity={self.intensity})
            """


class ConfiguracionTeas(Base):
    __tablename__ = 'configuracion_teas'
    
    id_experimento = Column(Integer, ForeignKey('experimentos.id'), primary_key=True, nullable=False)
    dac_input_intensity = Column(String(45), nullable=False)
    dac_teas_voltaje_range = Column(String(45), nullable=False)
    dac_input_temperature = Column(String(45), nullable=False)
    dac_temperature_voltaje_range = Column(String(45), nullable=False)
    dac_sampling_rate = Column(DECIMAL, nullable=False)
    aml_input_pressure = Column(String(45), nullable=False)
    aml_voltage_range = Column(String(45), nullable=False)
    aml_sensitivity = Column(String(45), nullable=False)
    aml_presure_units = Column(String(45), nullable=False)
    aml_emission_current = Column(String(45), nullable=False)
    configuracion_teascol = Column(String(45), nullable=False)
    lock_sensitivity = Column(String(45), nullable=False)
    lock_time_constant = Column(String(45), nullable=False)
    integration_time = Column(DECIMAL, nullable=False)
    channeltron_voltage = Column(String(45), nullable=False)
    description = Column(String(45), nullable=False)
    
    
    
    
    def __repr__(self):
        return f"""ConfiguracionTeas(id_experimento={self.id_experimento},
            dac_input_intensity={self.dac_input_intensity},
            dac_teas_voltaje_range={self.dac_teas_voltaje_range},
            dac_input_temperature={self.dac_input_temperature},
            dac_temperature_voltaje_range={self.dac_temperature_voltaje_range},
            dac_sampling_rate={self.dac_sampling_rate},
            aml_input_pressure={self.aml_input_pressure},
            aml_voltage_range={self.aml_voltage_range},
            aml_sensitivity={self.aml_sensitivity},
            aml_presure_units={self.aml_presure_units},
            aml_emission_current={self.aml_emission_current},
            configuracion_teascol={self.configuracion_teascol},
            lock_sensitivity={self.lock_sensitivity},
            lock_time_constant={self.lock_time_constant},
            integration_time={self.integration_time},
            channeltron_voltage={self.channeltron_voltage},
            description={self.description})
            """


class ConfiguracionMoke(Base):
    __tablename__ = 'configuracion_moke'
    
    id_experimento = Column(Integer, ForeignKey('experimentos.id'), primary_key=True,nullable=False)
    dac_input_intensity = Column(String(45), nullable=False)
    dac_voltaje_range = Column(String(45), nullable=False)
    dac_input_temperature = Column(String(45), nullable=False)
    dac_temperature_voltaje_range = Column(String(45), nullable=False)
    dac_sampling_rate = Column(DECIMAL, nullable=False)
    dac_dc_level = Column(String(45), nullable=False)
    dac_dc_voltage_range = Column(String(45), nullable=False)
    dac_field_driving_current = Column(String(45), nullable=False)
    lock_sensitivity = Column(String(45), nullable=False)
    lock_time_constant = Column(String(45), nullable=False)
    integration_time = Column(DECIMAL, nullable=False)
    dwell_time = Column(DECIMAL, nullable=False)
    magnetic_field = Column(DECIMAL, nullable=False)
    points_per_loop = Column(DECIMAL, nullable=False)
    number_of_sweeps = Column(DECIMAL, nullable=False)
    geometry = Column(String(45), nullable=False)
    description = Column(String(45), nullable=True)
    
    
    
    def __repr__(self):
        return f"""ConfiguracionMoke(id_experimento={self.id_experimento},
            dac_input_intensity={self.dac_input_intensity},
            dac_voltaje_range={self.dac_voltaje_range},
            dac_input_temperature={self.dac_input_temperature},
            dac_temperature_voltaje_range={self.dac_temperature_voltaje_range},
            dac_sampling_rate={self.dac_sampling_rate},
            dac_dc_level={self.dac_dc_level},
            dac_dc_voltage_range={self.dac_dc_voltage_range},
            dac_field_driving_current={self.dac_field_driving_current},
            lock_sensitivity={self.lock_sensitivity},
            lock_time_constant={self.lock_time_constant},
            integration_time={self.integration_time},
            dwell_time={self.dwell_time},
            magnetic_field={self.magnetic_field},
            points_per_loop={self.points_per_loop},
            number_of_sweeps={self.number_of_sweeps},
            geometry={self.geometry},
            description={self.description})
            """



