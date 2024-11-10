def calcular_resiliencia(ruta, fallas_infra, tipos_amenazas, multiplicadores_amenazas, penalizacion_adicional=1.5):
    """
    Calcula las métricas de resiliencia para una ruta dada, considerando los elementos afectados por distintos tipos de amenazas,
    con una penalización adicional significativamente mayor para calles cerradas y problemas de seguridad.

    Args:
        ruta (list): Lista de tuplas representando la ruta con el formato (edge_id, cost).
        fallas_infra (list): Lista de IDs de infraestructura afectados por amenazas activas.
        tipos_amenazas (dict): Diccionario con los IDs de infraestructura como claves y el tipo de amenaza como valor.
        multiplicadores_amenazas (dict): Diccionario con el tipo de amenaza como clave y su peso como valor.
        penalizacion_adicional (float): Factor adicional de penalización para elementos afectados por amenazas.

    Returns:
        dict: Diccionario con las métricas de resiliencia calculadas.
    """
    # Ajustar multiplicadores específicamente para cierre de calle y seguridad
    penalizacion_cierre_calle = 10  # Penalización muy alta para calles cerradas
    penalizacion_seguridad = 5      # Penalización alta para problemas de seguridad

    # Identificar elementos afectados y calcular el costo afectado basado en el tipo de amenaza
    elementos_afectados = []
    costo_total = sum(cost for _, cost in ruta)
    costo_afectado = 0

    for edge_id, cost in ruta:
        if edge_id in fallas_infra:
            elementos_afectados.append(edge_id)
            # Obtener el tipo de amenaza y aplicar la penalización correspondiente
            tipo_amenaza = tipos_amenazas.get(edge_id, None)
            if tipo_amenaza == 'cierre_calle':
                multiplicador = penalizacion_cierre_calle
            elif tipo_amenaza == 'seguridad':
                multiplicador = penalizacion_seguridad
            else:
                multiplicador = multiplicadores_amenazas.get(tipo_amenaza, 1) * penalizacion_adicional
            
            costo_afectado += cost * multiplicador
        else:
            costo_afectado += cost

    # Número de elementos afectados y porcentaje de elementos afectados
    num_elementos_afectados = len(elementos_afectados)
    porcentaje_afectado = num_elementos_afectados / len(ruta) if ruta else 0

    # Calcular métricas de resiliencia
    resiliencia_costo = costo_total / costo_afectado if costo_afectado else 1
    resiliencia_impacto = 1 - porcentaje_afectado
    
    return {
        "resiliencia_costo": resiliencia_costo,
        "resiliencia_impacto": resiliencia_impacto,
        "elementos_afectados": elementos_afectados
    }
