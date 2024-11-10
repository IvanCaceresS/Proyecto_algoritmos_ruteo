import json

def calcular_resiliencia(ruta, fallas_infra, multiplicador_afectado=2):
    """
    Calcula las métricas de resiliencia para una ruta dada, considerando los elementos afectados.
    
    Args:
        ruta (list): Lista de tuplas representando la ruta con el formato (edge_id, cost).
        fallas_infra (list): Lista de IDs de infraestructura afectados por amenazas activas.
        multiplicador_afectado (int, optional): Factor de aumento del costo para elementos afectados. Default es 2.
    
    Returns:
        dict: Diccionario con las métricas de resiliencia calculadas.
    """
    # Identificar elementos afectados
    elementos_afectados = [edge_id for edge_id, _ in ruta if edge_id in fallas_infra]
    
    # Calcular costo total y costo afectado
    costo_total = sum(cost for _, cost in ruta)
    costo_afectado = sum(cost * multiplicador_afectado for edge_id, cost in ruta if edge_id in fallas_infra)
    
    # Número de elementos afectados y porcentaje de elementos afectados
    num_elementos_afectados = len(elementos_afectados)
    porcentaje_afectado = num_elementos_afectados / len(ruta) if ruta else 0

    # Calcular métricas de resiliencia
    resiliencia_costo = (costo_total - costo_afectado) / costo_total if costo_total else 1
    resiliencia_impacto = 1 - porcentaje_afectado
    
    return {
        "resiliencia_costo": resiliencia_costo,
        "resiliencia_impacto": resiliencia_impacto,
        "elementos_afectados": elementos_afectados
    }
