import sqlalchemy
from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """
    Clase base para modelos declarativos de SQLAlchemy.

    Esta clase sirve como base para todas las definiciones de modelos en SQLAlchemy.
    Hereda de `DeclarativeBase`, proporcionando la funcionalidad necesaria para la
    creación de tablas y el mapeo de objetos relacionales.

    Ejemplo de uso:

    .. code-block:: python

        from sqlalchemy import Column, Integer, String

        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String)
            email = Column(String)

    Esta clase no contiene métodos ni atributos adicionales, simplemente extiende
    `DeclarativeBase` para permitir la creación de modelos de base de datos.

    """

    pass


class Conexion:
    """
    Clase para gestionar la conexión a la base de datos y la creación de sesiones.

    Esta clase proporciona métodos para inicializar la base de datos y obtener conexiones
    de sesión utilizando SQLAlchemy.

    Atributos de clase:
    -------------------
    engine : sqlalchemy.engine.Engine
        El motor de base de datos utilizado para las conexiones.
    """
    engine = create_engine('mysql://root:root@localhost/aplicacionuam', echo=True) 

    def iniciar_bbdd():
        """
        Inicializa la base de datos creando todas las tablas definidas en los modelos.

        Utiliza el metadata de la clase `Base` para crear todas las tablas en la base de datos
        conectada a través del motor `engine`.

        Ejemplo de uso:

        .. code-block:: python

            Conexion.iniciar_bbdd()
        """
        Base.metadata.create_all(Conexion.engine)

    def getConexion():
        """
        Obtiene una nueva sesión de conexión a la base de datos.

        Crea una nueva sesión utilizando el motor de la clase y la devuelve para su uso
        en operaciones de base de datos.

        :return: Una nueva sesión de SQLAlchemy.
        :rtype: sqlalchemy.orm.session.Session

        Ejemplo de uso:

        .. code-block:: python

            session = Conexion.getConexion()
            # Realizar operaciones de base de datos con la sesión
        """
        Session = sessionmaker(bind=Conexion.engine)
        session = Session()
        return session


class Experimento(Base):
    """
    Modelo de base de datos para representar un experimento en la aplicación.

    Esta clase define la estructura de la tabla `experimentos` en la base de datos,
    incluyendo columnas para la descripción, ruta del archivo CSV, fecha de creación
    y tipo de experimento.

    Atributos:
    ----------
    id : int
        Identificador único del experimento (clave primaria, autoincremental).
    descripcion : str
        Descripción del experimento, opcional.
    rutaCsv : str
        Ruta del archivo CSV asociado con el experimento, obligatorio.
    fecha_creacion : datetime
        Fecha y hora en que se creó el registro, se autogenera al insertar un nuevo registro.
    tipo : str
        Tipo de experimento, obligatorio.
    configuracion : dict
        Diccionario para almacenar configuraciones adicionales del experimento.

    Ejemplo de uso:

    .. code-block:: python

        nuevo_experimento = Experimento(
            descripcion="Descripción del experimento",
            rutaCsv="ruta/al/archivo.csv",
            tipo="Tipo de experimento"
        )
        session.add(nuevo_experimento)
        session.commit()
    """

    __tablename__ = "experimentos"

    id = Column(Integer, autoincrement=True, primary_key=True)
    descripcion = Column(String(255), nullable=True, server_default="---")
    rutaCsv = Column(String(255), nullable=False)
    # Atributo fecha_creacion autogenerado al insertar un nuevo registro
    fecha_creacion = Column(DateTime, default=sqlalchemy.func.now())
    tipo = Column(String(45), nullable=False)

    configuracion = {}

    def __repr__(self):
        """
        Representación en forma de cadena del objeto Experimento.

        :return: Una cadena que representa al objeto Experimento con sus atributos.
        :rtype: str

        Ejemplo de salida:

        .. code-block:: text

            Experimento(id=1,
                        descripcion='Descripción del experimento',
                        rutaCsv='ruta/al/archivo.csv',
                        fecha_creacion='2023-01-01 00:00:00',
                        tipo='Tipo de experimento')
        """
        return f"""Experimento(id={self.id}, 
            descripcion={self.descripcion}, 
            rutaCsv={self.rutaCsv}, 
            fecha_creacion={self.fecha_creacion}, 
            tipo={self.tipo})
            """


class ResultadoTeas(Base):
    """
    Modelo de base de datos para representar un resultado TEAS en la aplicación.

    Esta clase define la estructura de la tabla `resultados_teas` en la base de datos,
    incluyendo columnas para el identificador del resultado, el identificador del experimento
    asociado, el tiempo y la intensidad.

    Atributos:
    ----------
    id_resultado_exp : int
        Identificador único del resultado del experimento (clave primaria, autoincremental).
    id_experimento : int
        Identificador del experimento al que pertenece este resultado (clave foránea).
    time : decimal
        Tiempo asociado al resultado, con precisión y escala definidas.
    intensity : decimal
        Intensidad asociada al resultado, con precisión y escala definidas.

    Ejemplo de uso:

    .. code-block:: python

        nuevo_resultado = ResultadoTeas(
            id_experimento=1,
            time=12.34,
            intensity=56.78
        )
        session.add(nuevo_resultado)
        session.commit()
    """

    __tablename__ = "resultados_teas"

    id_resultado_exp = Column(Integer, autoincrement=True, primary_key=True)
    id_experimento = Column(Integer, ForeignKey("experimentos.id"), nullable=False)
    time = Column(DECIMAL(precision=10, scale=2), nullable=False)
    intensity = Column(DECIMAL(precision=10, scale=2), nullable=False)

    def __repr__(self):
        """
        Representación en forma de cadena del objeto ResultadoTeas.

        :return: Una cadena que representa al objeto ResultadoTeas con sus atributos.
        :rtype: str

        Ejemplo de salida:

        .. code-block:: text

            ResultadoTeas(id_resultado_exp=1,
                          id_experimento=1,
                          time=12.34,
                          intensity=56.78)
        """
        return f"""ResultadoTeas(id_resultado_exp={self.id_resultado_exp},
            id_experimento={self.id_experimento},
            time={self.time},
            intensity={self.intensity})
            """


class ResultadoMoke(Base):
    """
    Representa un resultado del experimento MOKE almacenado en la base de datos.

    Esta clase mapea a la tabla "resultados_moke" en la base de datos y contiene
    los campos necesarios para almacenar los resultados de un experimento MOKE.

    Atributos:
    ----------
    id_resultado_exp : int
        Identificador único autoincremental del resultado del experimento.
    id_experimento : int
        Identificador del experimento al que pertenece este resultado.
    magnetic_field : decimal
        Campo magnético medido durante el experimento (precisión de 10, escala de 2).
    intensity : decimal
        Intensidad medida durante el experimento (precisión de 10, escala de 2).

    Ejemplo de uso:

    .. code-block:: python

        resultado = ResultadoMoke(
            id_experimento=1,
            magnetic_field=5.75,
            intensity=3.42
        )
    """

    __tablename__ = "resultados_moke"

    id_resultado_exp = Column(Integer, autoincrement=True, primary_key=True)
    id_experimento = Column(Integer, ForeignKey("experimentos.id"), nullable=False)
    magnetic_field = Column(DECIMAL(precision=10, scale=2), nullable=False)
    intensity = Column(DECIMAL(precision=10, scale=2), nullable=False)

    def __repr__(self):

        return f"""ResultadoMoke(id_resultado_exp={self.id_resultado_exp},
            id_experimento={self.id_experimento},
            magnetic_field={self.magnetic_field},
            intensity={self.intensity})
            """


class ConfiguracionTeas(Base):
    """
    Representa la configuración de un experimento TEAS almacenado en la base de datos.

    Esta clase mapea a la tabla "configuracion_teas" en la base de datos y contiene
    los campos necesarios para almacenar la configuración de un experimento TEAS.

    Atributos:
    ----------
    id_experimento : int
        Identificador del experimento al que pertenece esta configuración (clave primaria).
    dac_input_intensity : str
        Intensidad de entrada DAC.
    dac_teas_voltaje_range : str
        Rango de voltaje DAC para TEAS.
    dac_input_temperature : str
        Temperatura de entrada DAC.
    dac_temperature_voltaje_range : str
        Rango de voltaje de temperatura DAC.
    dac_sampling_rate : decimal
        Tasa de muestreo DAC (precisión de 10, escala de 2).
    aml_input_pressure : str
        Presión de entrada AML.
    aml_voltage_range : str
        Rango de voltaje AML.
    aml_sensitivity : str
        Sensibilidad AML.
    aml_presure_units : str
        Unidades de presión AML.
    aml_emission_current : str
        Corriente de emisión AML.
    lock_sensitivity : str
        Sensibilidad del lock-in.
    lock_time_constant : str
        Constante de tiempo del lock-in.
    integration_time : decimal
        Tiempo de integración (precisión de 10, escala de 2).
    channeltron_voltage : str
        Voltaje del Channeltron.

    Ejemplo de uso:

    .. code-block:: python

        configuracion = ConfiguracionTeas(
            id_experimento=1,
            dac_input_intensity="10V",
            dac_teas_voltaje_range="5V",
            dac_input_temperature="25C",
            dac_temperature_voltaje_range="10V",
            dac_sampling_rate=1000.0,
            aml_input_pressure="1 atm",
            aml_voltage_range="5V",
            aml_sensitivity="High",
            aml_presure_units="Pa",
            aml_emission_current="0.5A",
            lock_sensitivity="10mV",
            lock_time_constant="1s",
            integration_time=0.5,
            channeltron_voltage="1000V"
        )
    """

    __tablename__ = "configuracion_teas"

    id_experimento = Column(
        Integer,
        ForeignKey("experimentos.id"),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    dac_input_intensity = Column(String(45), nullable=False)
    dac_teas_voltaje_range = Column(String(45), nullable=False)
    dac_input_temperature = Column(String(45), nullable=False)
    dac_temperature_voltaje_range = Column(String(45), nullable=False)
    dac_sampling_rate = Column(
        DECIMAL(precision=10, scale=2), nullable=False, default=0
    )
    aml_input_pressure = Column(String(45), nullable=False)
    aml_voltage_range = Column(String(45), nullable=False)
    aml_sensitivity = Column(String(45), nullable=False)
    aml_presure_units = Column(String(45), nullable=False)
    aml_emission_current = Column(String(45), nullable=False)
    lock_sensitivity = Column(String(45), nullable=False)
    lock_time_constant = Column(String(45), nullable=False)
    integration_time = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    channeltron_voltage = Column(String(45), nullable=False)

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
            lock_sensitivity={self.lock_sensitivity},
            lock_time_constant={self.lock_time_constant},
            integration_time={self.integration_time},
            channeltron_voltage={self.channeltron_voltage})
            """


class ConfiguracionMoke(Base):
    """
    Representa la configuración de un experimento MOKE almacenado en la base de datos.

    Esta clase mapea a la tabla "configuracion_moke" en la base de datos y contiene
    los campos necesarios para almacenar la configuración de un experimento MOKE.

    Atributos:
    ----------
    id_experimento : int
        Identificador del experimento al que pertenece esta configuración (clave primaria).
    dac_input_intensity : str
        Intensidad de entrada DAC.
    dac_voltaje_range : str
        Rango de voltaje DAC.
    dac_input_temperature : str
        Temperatura de entrada DAC.
    dac_temperature_voltaje_range : str
        Rango de voltaje de temperatura DAC.
    dac_sampling_rate : decimal
        Tasa de muestreo DAC (precisión de 10, escala de 2).
    dac_dc_level : str
        Nivel de DC del DAC.
    dac_dc_voltage_range : str
        Rango de voltaje de DC del DAC.
    dac_field_driving_current : str
        Corriente de conducción de campo del DAC.
    lock_sensitivity : str
        Sensibilidad del lock-in.
    lock_time_constant : str
        Constante de tiempo del lock-in.
    integration_time : decimal
        Tiempo de integración (precisión de 10, escala de 2).
    dwell_time : decimal
        Tiempo de permanencia (precisión de 10, escala de 2).
    magnetic_field : decimal
        Campo magnético (precisión de 10, escala de 2).
    points_per_loop : decimal
        Puntos por bucle (precisión de 10, escala de 2).
    number_of_sweeps : decimal
        Número de barridos (precisión de 10, escala de 2).
    geometry : str
        Geometría del experimento.

    """

    __tablename__ = "configuracion_moke"

    id_experimento = Column(
        Integer, ForeignKey("experimentos.id"), primary_key=True, nullable=False
    )
    dac_input_intensity = Column(String(45), nullable=False)
    dac_voltaje_range = Column(String(45), nullable=False)
    dac_input_temperature = Column(String(45), nullable=False)
    dac_temperature_voltaje_range = Column(String(45), nullable=False)
    dac_sampling_rate = Column(
        DECIMAL(precision=10, scale=2), nullable=False, default=0
    )
    dac_dc_level = Column(String(45), nullable=False)
    dac_dc_voltage_range = Column(String(45), nullable=False)
    dac_field_driving_current = Column(String(45), nullable=False)
    lock_sensitivity = Column(String(45), nullable=False)
    lock_time_constant = Column(String(45), nullable=False)
    integration_time = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    dwell_time = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    magnetic_field = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    points_per_loop = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    number_of_sweeps = Column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    geometry = Column(String(45), nullable=False)

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
            geometry={self.geometry})
            """


class Marcador(Base):
    """
    Representa un marcador asociado a un experimento almacenado en la base de datos.

    Esta clase mapea a la tabla "marcadores" en la base de datos y contiene
    los campos necesarios para almacenar la información de un marcador.

    Atributos:
    ----------
    eje_x_id : int
        Identificador del eje X del marcador (parte de la clave primaria compuesta).
    id_experimento : int
        Identificador del experimento al que pertenece este marcador (parte de la clave primaria compuesta).
    descripcion : str
        Descripción del marcador.

    Ejemplo de uso:

    .. code-block:: python

        marcador = Marcador(
            eje_x_id=1,
            id_experimento=101,
            descripcion="Marcador de referencia inicial"
        )
    """

    __tablename__ = "marcadores"

    # 'eje_x_id' y 'id_experimento' son claves primarias compuestas
    eje_x_id = Column(Integer, primary_key=True, nullable=False)
    id_experimento = Column(
        Integer, ForeignKey("experimentos.id"), primary_key=True, nullable=False
    )
    descripcion = Column(String(255), nullable=False)

    def __repr__(self):
        return f"""Marcadores(eje_x_id={self.eje_x_id},
            id_experimento={self.id_experimento},
            descripcion={self.descripcion})
            """
