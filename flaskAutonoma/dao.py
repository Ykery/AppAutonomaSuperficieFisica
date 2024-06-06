from clases import *


class ExperimentoDAO:
    """
    Data Access Object (DAO) para la clase Experimento.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'experimentos' de la base de datos.

    Métodos:
    --------
    crear(experimento):
        Crea un nuevo experimento en la base de datos y devuelve el último experimento creado.
    obtener_por_id(id):
        Obtiene un experimento por su ID.
    obtener_todos():
        Obtiene todos los experimentos de la base de datos.
    obtener_ultimo():
        Obtiene el último experimento creado en la base de datos.
    actualizar(experimento):
        Actualiza un experimento existente en la base de datos.
    eliminar(experimento):
        Elimina un experimento de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear un nuevo experimento
        nuevo_experimento = Experimento(descripcion="Nuevo experimento", rutaCsv="ruta/al/archivo.csv", tipo="Tipo de experimento")
        ExperimentoDAO.crear(nuevo_experimento)

        # Obtener un experimento por ID
        experimento = ExperimentoDAO.obtener_por_id(1)

        # Obtener todos los experimentos
        experimentos = ExperimentoDAO.obtener_todos()

        # Actualizar un experimento
        experimento.descripcion = "Descripción actualizada"
        ExperimentoDAO.actualizar(experimento)

        # Eliminar un experimento
        ExperimentoDAO.eliminar(experimento)
    """

    def crear(experimento):
        """
        Crea un nuevo experimento en la base de datos y devuelve el último experimento creado.

        :param experimento: El objeto Experimento a ser creado.
        :type experimento: Experimento
        :return: El último experimento creado.
        :rtype: Experimento
        """
        session = Conexion.getConexion()
        session.add(experimento)
        session.commit()
        session.close()
        return ExperimentoDAO.obtener_ultimo()

    def obtener_por_id(id):
        """
        Obtiene un experimento por su ID.

        :param id: El ID del experimento a obtener.
        :type id: int
        :return: El experimento con el ID especificado.
        :rtype: Experimento
        """
        session = Conexion.getConexion()
        experimento = session.query(Experimento).filter(Experimento.id == id).first()
        session.close()
        return experimento

    def obtener_todos():
        """
        Obtiene todos los experimentos de la base de datos.

        :return: Una lista de todos los experimentos.
        :rtype: list[Experimento]
        """
        session = Conexion.getConexion()
        experimentos = session.query(Experimento).all()
        session.close()
        return experimentos

    def obtener_ultimo():
        """
        Obtiene el último experimento creado en la base de datos.

        :return: El último experimento creado.
        :rtype: Experimento
        """
        session = Conexion.getConexion()
        experimento = session.query(Experimento).order_by(Experimento.id.desc()).first()
        session.close()
        return experimento

    def actualizar(experimento):
        """
        Actualiza un experimento existente en la base de datos.

        :param experimento: El objeto Experimento a ser actualizado.
        :type experimento: Experimento
        """
        session = Conexion.getConexion()
        session.add(experimento)
        session.commit()
        session.close()

    def eliminar(experimento):
        """
    Elimina un experimento y todas sus configuraciones y resultados asociados de la base de datos.

    :param experimento: El experimento a eliminar.
    :type experimento: Experimento
    :return: True si el experimento se eliminó con éxito, False en caso contrario.
    :rtype: bool
    """
        if experimento is None:
            return False
        if experimento.tipo.lower() == "teas":
            configuracion = ConfiguracionTeasDAO.obtener_por_id(experimento.id)
            ConfiguracionTeasDAO.eliminar(configuracion)
            resultados = ResultadoTeasDAO.obtener_por_id_experimento(experimento.id)
            for resultado in resultados:
                ResultadoTeasDAO.eliminar(resultado)
        elif experimento.tipo.lower() == "moke":
            configuracion = ConfiguracionMokeDAO.obtener_por_id(experimento.id)
            ConfiguracionMokeDAO.eliminar(configuracion)
            resultados = ResultadoMokeDAO.obtener_por_id_experimento(experimento.id)
            for resultado in resultados:
                ResultadoMokeDAO.eliminar(resultado)
        marcadores = MarcadorDAO.obtener_por_id_experimento(experimento.id)
        for marcador in marcadores:
            MarcadorDAO.eliminar(marcador)
        session = Conexion.getConexion()
        session.delete(experimento)
        session.commit()
        session.close()
        return True


class ResultadoTeasDAO:
    """
    Data Access Object (DAO) para la clase ResultadoTeas.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'resultados_teas' de la base de datos.

    Métodos:
    --------
    crear(resultado):
        Crea un nuevo resultado TEAS en la base de datos.
    obtener_por_id(id):
        Obtiene un resultado TEAS por su ID.
    obtener_por_id_experimento(id_experimento):
        Obtiene todos los resultados TEAS asociados a un experimento específico.
    obtener_todos():
        Obtiene todos los resultados TEAS de la base de datos.
    actualizar(resultado):
        Actualiza un resultado TEAS existente en la base de datos.
    eliminar(resultado):
        Elimina un resultado TEAS de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear un nuevo resultado TEAS
        nuevo_resultado = ResultadoTeas(id_experimento=1, time=10.0, intensity=100.0)
        ResultadoTeasDAO.crear(nuevo_resultado)

        # Obtener un resultado TEAS por ID
        resultado = ResultadoTeasDAO.obtener_por_id(1)

        # Obtener todos los resultados TEAS de un experimento
        resultados = ResultadoTeasDAO.obtener_por_id_experimento(1)

        # Obtener todos los resultados TEAS
        todos_resultados = ResultadoTeasDAO.obtener_todos()

        # Actualizar un resultado TEAS
        resultado.intensity = 150.0
        ResultadoTeasDAO.actualizar(resultado)

        # Eliminar un resultado TEAS
        ResultadoTeasDAO.eliminar(resultado)
    """

    def crear(resultado):
        """
        Crea un nuevo resultado TEAS en la base de datos.

        :param resultado: El objeto ResultadoTeas a ser creado.
        :type resultado: ResultadoTeas
        """

        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()

    def obtener_por_id(id):
        """
        Obtiene un resultado TEAS por su ID.

        :param id: El ID del resultado TEAS a obtener.
        :type id: int
        :return: El resultado TEAS con el ID especificado.
        :rtype: ResultadoTeas
        """
        session = Conexion.getConexion()
        resultado = (
            session.query(ResultadoTeas)
            .filter(ResultadoTeas.id_resultado_exp == id)
            .first()
        )
        session.close()
        return resultado

    def obtener_por_id_experimento(id_experimento):
        """
        Obtiene todos los resultados TEAS asociados a un experimento específico.

        :param id_experimento: El ID del experimento cuyos resultados TEAS se desean obtener.
        :type id_experimento: int
        :return: Una lista de resultados TEAS asociados al experimento especificado.
        :rtype: list[ResultadoTeas]
        """
        session = Conexion.getConexion()
        resultados = (
            session.query(ResultadoTeas)
            .filter(ResultadoTeas.id_experimento == id_experimento)
            .all()
        )
        session.close()
        return resultados

    def obtener_todos():
        """
        Obtiene todos los resultados TEAS de la base de datos.

        :return: Una lista de todos los resultados TEAS.
        :rtype: list[ResultadoTeas]
        """
        session = Conexion.getConexion()
        resultados = session.query(ResultadoTeas).all()
        session.close()
        return resultados

    def actualizar(resultado):
        """
        Actualiza un resultado TEAS existente en la base de datos.

        :param resultado: El objeto ResultadoTeas a ser actualizado.
        :type resultado: ResultadoTeas
        """
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()

    def eliminar(resultado):
        """
        Elimina un resultado TEAS de la base de datos.

        :param resultado: El objeto ResultadoTeas a ser eliminado.
        :type resultado: ResultadoTeas
        """
        session = Conexion.getConexion()
        session.delete(resultado)
        session.commit()
        session.close()


class ResultadoMokeDAO:
    """
    Data Access Object (DAO) para la clase ResultadoMoke.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'resultados_moke' de la base de datos.

    Métodos:
    --------
    crear(resultado):
        Crea un nuevo resultado MOKE en la base de datos.
    obtener_por_id(id):
        Obtiene un resultado MOKE por su ID.
    obtener_por_id_experimento(id_experimento):
        Obtiene todos los resultados MOKE asociados a un experimento específico.
    obtener_todos():
        Obtiene todos los resultados MOKE de la base de datos.
    actualizar(resultado):
        Actualiza un resultado MOKE existente en la base de datos.
    eliminar(resultado):
        Elimina un resultado MOKE de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear un nuevo resultado MOKE
        nuevo_resultado = ResultadoMoke(id_experimento=1, magnetic_field=1.0, intensity=100.0)
        ResultadoMokeDAO.crear(nuevo_resultado)

        # Obtener un resultado MOKE por ID
        resultado = ResultadoMokeDAO.obtener_por_id(1)

        # Obtener todos los resultados MOKE de un experimento
        resultados = ResultadoMokeDAO.obtener_por_id_experimento(1)

        # Obtener todos los resultados MOKE
        todos_resultados = ResultadoMokeDAO.obtener_todos()

        # Actualizar un resultado MOKE
        resultado.intensity = 150.0
        ResultadoMokeDAO.actualizar(resultado)

        # Eliminar un resultado MOKE
        ResultadoMokeDAO.eliminar(resultado)
    """

    def crear(resultado):
        """
        Crea un nuevo resultado MOKE en la base de datos.

        :param resultado: El objeto ResultadoMoke a ser creado.
        :type resultado: ResultadoMoke
        """
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()

    def obtener_por_id(id):
        """
        Obtiene un resultado MOKE por su ID.

        :param id: El ID del resultado MOKE a obtener.
        :type id: int
        :return: El resultado MOKE con el ID especificado.
        :rtype: ResultadoMoke
        """
        session = Conexion.getConexion()
        resultado = (
            session.query(ResultadoMoke)
            .filter(ResultadoMoke.id_resultado_exp == id)
            .first()
        )
        session.close()
        return resultado

    def obtener_por_id_experimento(id_experimento):
        """
        Obtiene todos los resultados MOKE asociados a un experimento específico.

        :param id_experimento: El ID del experimento cuyos resultados MOKE se desean obtener.
        :type id_experimento: int
        :return: Una lista de resultados MOKE asociados al experimento especificado.
        :rtype: list[ResultadoMoke]
        """
        session = Conexion.getConexion()
        resultados = (
            session.query(ResultadoMoke)
            .filter(ResultadoMoke.id_experimento == id_experimento)
            .all()
        )
        session.close()
        return resultados

    def obtener_todos():
        """
        Obtiene todos los resultados MOKE de la base de datos.

        :return: Una lista de todos los resultados MOKE.
        :rtype: list[ResultadoMoke]
        """
        session = Conexion.getConexion()
        resultados = session.query(ResultadoMoke).all()
        session.close()
        return resultados

    def actualizar(resultado):
        """
        Actualiza un resultado MOKE existente en la base de datos.

        :param resultado: El objeto ResultadoMoke a ser actualizado.
        :type resultado: ResultadoMoke
        """
        session = Conexion.getConexion()
        session.add(resultado)
        session.commit()
        session.close()

    def eliminar(resultado):
        """
        Elimina un resultado MOKE de la base de datos.

        :param resultado: El objeto ResultadoMoke a ser eliminado.
        :type resultado: ResultadoMoke
        """
        session = Conexion.getConexion()
        session.delete(resultado)
        session.commit()
        session.close()


class ConfiguracionTeasDAO:
    """
    Data Access Object (DAO) para la clase ConfiguracionTeas.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'configuracion_teas' de la base de datos.

    Métodos:
    --------
    crear(configuracion):
        Crea una nueva configuración TEAS en la base de datos.
    obtener_por_id(id):
        Obtiene una configuración TEAS por su ID.
    obtener_todos():
        Obtiene todas las configuraciones TEAS de la base de datos.
    actualizar(configuracion):
        Actualiza una configuración TEAS existente en la base de datos.
    eliminar(configuracion):
        Elimina una configuración TEAS de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear una nueva configuración TEAS
        nueva_configuracion = ConfiguracionTeas(dac_input_intensity="1", dac_teas_voltaje_range="20 V", ...)
        ConfiguracionTeasDAO.crear(nueva_configuracion)

        # Obtener una configuración TEAS por ID
        configuracion = ConfiguracionTeasDAO.obtener_por_id(1)

        # Obtener todas las configuraciones TEAS
        todas_configuraciones = ConfiguracionTeasDAO.obtener_todos()

        # Actualizar una configuración TEAS
        configuracion.dac_input_intensity = "2"
        ConfiguracionTeasDAO.actualizar(configuracion)

        # Eliminar una configuración TEAS
        ConfiguracionTeasDAO.eliminar(configuracion)
    """

    def crear(configuracion):
        """
        Crea una nueva configuración TEAS en la base de datos.

        :param configuracion: El objeto ConfiguracionTeas a ser creado.
        :type configuracion: ConfiguracionTeas
        """
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()

    def obtener_por_id(id):
        """
        Obtiene una configuración TEAS por su ID.

        :param id: El ID de la configuración TEAS a obtener.
        :type id: int
        :return: La configuración TEAS con el ID especificado.
        :rtype: ConfiguracionTeas
        """
        session = Conexion.getConexion()
        configuracion = (
            session.query(ConfiguracionTeas)
            .filter(ConfiguracionTeas.id_experimento == id)
            .first()
        )
        session.close()
        return configuracion

    def obtener_todos():
        """
        Obtiene todas las configuraciones TEAS de la base de datos.

        :return: Una lista de todas las configuraciones TEAS.
        :rtype: list[ConfiguracionTeas]
        """
        session = Conexion.getConexion()
        configuraciones = session.query(ConfiguracionTeas).all()
        session.close()
        return configuraciones

    def actualizar(configuracion):
        """
        Actualiza una configuración TEAS existente en la base de datos.

        :param configuracion: El objeto ConfiguracionTeas a ser actualizado.
        :type configuracion: ConfiguracionTeas
        """
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()

    def eliminar(configuracion):
        """
        Elimina una configuración TEAS de la base de datos.

        :param configuracion: El objeto ConfiguracionTeas a ser eliminado.
        :type configuracion: ConfiguracionTeas
        """
        session = Conexion.getConexion()
        session.delete(configuracion)
        session.commit()
        session.close()


class ConfiguracionMokeDAO:
    """
    Data Access Object (DAO) para la clase ConfiguracionMoke.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'configuracion_moke' de la base de datos.

    Métodos:
    --------
    crear(configuracion):
        Crea una nueva configuración MOKE en la base de datos.
    obtener_por_id(id):
        Obtiene una configuración MOKE por su ID.
    obtener_todos():
        Obtiene todas las configuraciones MOKE de la base de datos.
    actualizar(configuracion):
        Actualiza una configuración MOKE existente en la base de datos.
    eliminar(configuracion):
        Elimina una configuración MOKE de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear una nueva configuración MOKE
        nueva_configuracion = ConfiguracionMoke(dac_input_intensity="1", dac_voltaje_range="20 V", ...)
        ConfiguracionMokeDAO.crear(nueva_configuracion)

        # Obtener una configuración MOKE por ID
        configuracion = ConfiguracionMokeDAO.obtener_por_id(1)

        # Obtener todas las configuraciones MOKE
        todas_configuraciones = ConfiguracionMokeDAO.obtener_todos()

        # Actualizar una configuración MOKE
        configuracion.dac_input_intensity = "2"
        ConfiguracionMokeDAO.actualizar(configuracion)

        # Eliminar una configuración MOKE
        ConfiguracionMokeDAO.eliminar(configuracion)
    """

    def crear(configuracion):
        """
        Crea una nueva configuración MOKE en la base de datos.

        :param configuracion: El objeto ConfiguracionMoke a ser creado.
        :type configuracion: ConfiguracionMoke
        """
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()

    def obtener_por_id(id):
        """
        Obtiene una configuración MOKE por su ID.

        :param id: El ID de la configuración MOKE a obtener.
        :type id: int
        :return: La configuración MOKE con el ID especificado.
        :rtype: ConfiguracionMoke
        """
        session = Conexion.getConexion()
        configuracion = (
            session.query(ConfiguracionMoke)
            .filter(ConfiguracionMoke.id_experimento == id)
            .first()
        )
        session.close()
        return configuracion

    def obtener_todos():
        """
        Obtiene todas las configuraciones MOKE de la base de datos.

        :return: Una lista de todas las configuraciones MOKE.
        :rtype: list[ConfiguracionMoke]
        """
        session = Conexion.getConexion()
        configuraciones = session.query(ConfiguracionMoke).all()
        session.close()
        return configuraciones

    def actualizar(configuracion):
        """
        Actualiza una configuración MOKE existente en la base de datos.

        :param configuracion: El objeto ConfiguracionMoke a ser actualizado.
        :type configuracion: ConfiguracionMoke
        """
        session = Conexion.getConexion()
        session.add(configuracion)
        session.commit()
        session.close()

    def eliminar(configuracion):
        """
        Elimina una configuración MOKE de la base de datos.

        :param configuracion: El objeto ConfiguracionMoke a ser eliminado.
        :type configuracion: ConfiguracionMoke
        """
        session = Conexion.getConexion()
        session.delete(configuracion)
        session.commit()
        session.close()


class MarcadorDAO:
    """
    Data Access Object (DAO) para la clase Marcador.

    Esta clase proporciona métodos para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    en la tabla 'marcadores' de la base de datos.

    Métodos:
    --------
    crear(marcador):
        Crea un nuevo marcador en la base de datos.
    obtener_por_id(id):
        Obtiene un marcador por su ID.
    obtener_por_id_experimento(id_experimento):
        Obtiene todos los marcadores asociados a un experimento por su ID.
    obtener_todos():
        Obtiene todos los marcadores de la base de datos.
    actualizar(marcador):
        Actualiza un marcador existente en la base de datos.
    eliminar(marcador):
        Elimina un marcador de la base de datos.

    Ejemplo de uso:

    .. code-block:: python

        # Crear un nuevo marcador
        nuevo_marcador = Marcador(eje_x_id=1, id_experimento=1, descripcion="Nuevo marcador")
        MarcadorDAO.crear(nuevo_marcador)

        # Obtener un marcador por ID
        marcador = MarcadorDAO.obtener_por_id(1)

        # Obtener todos los marcadores asociados a un experimento
        marcadores_experimento = MarcadorDAO.obtener_por_id_experimento(1)

        # Obtener todos los marcadores
        todos_marcadores = MarcadorDAO.obtener_todos()

        # Actualizar un marcador
        marcador.descripcion = "Descripción actualizada"
        MarcadorDAO.actualizar(marcador)

        # Eliminar un marcador
        MarcadorDAO.eliminar(marcador)
    """

    def crear(marcador):
        """
        Crea un nuevo marcador en la base de datos.

        :param marcador: El objeto Marcador a ser creado.
        :type marcador: Marcador
        """
        session = Conexion.getConexion()
        session.add(marcador)
        session.commit()
        session.close()

    def obtener_por_id(id):
        """
        Obtiene un marcador por su ID.

        :param id: El ID del marcador a obtener.
        :type id: int
        :return: El marcador con el ID especificado.
        :rtype: Marcador
        """
        session = Conexion.getConexion()
        marcador = session.query(Marcador).filter(Marcador.id == id).first()
        session.close()
        return marcador

    def obtener_por_id_experimento(id_experimento):
        """
        Obtiene un marcador por su ID.

        :param id: El ID del marcador a obtener.
        :type id: int
        :return: El marcador con el ID especificado.
        :rtype: Marcador
        """
        session = Conexion.getConexion()
        marcadores = (
            session.query(Marcador)
            .filter(Marcador.id_experimento == id_experimento)
            .all()
        )
        session.close()
        return marcadores

    def obtener_todos():
        """
        Obtiene todos los marcadores de la base de datos.

        :return: Una lista de todos los marcadores.
        :rtype: list[Marcador]
        """
        session = Conexion.getConexion()
        marcadores = session.query(Marcador).all()
        session.close()
        return marcadores

    def actualizar(marcador):
        """
        Actualiza un marcador existente en la base de datos.

        :param marcador: El objeto Marcador a ser actualizado.
        :type marcador: Marcador
        """
        session = Conexion.getConexion()
        session.add(marcador)
        session.commit()
        session.close()

    def eliminar(marcador):
        """
        Elimina un marcador de la base de datos.

        :param marcador: El objeto Marcador a ser eliminado.
        :type marcador: Marcador
        """
        session = Conexion.getConexion()
        session.delete(marcador)
        session.commit()
        session.close()

