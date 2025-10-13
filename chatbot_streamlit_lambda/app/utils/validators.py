import sys
import os
import re
from data.glossary import GLOSARIO

def validar_mensaje(texto):
    errores = []

    # WIP
    for match in re.findall(r"\bWIP\s+(\d+)\b", texto, re.IGNORECASE):
        try:
            n = int(match)
            if not (GLOSARIO["wip"]["min"] <= n <= GLOSARIO["wip"]["max"]):
                errores.append(f"WIP {n} fuera de rango (10001-65535)")
        except ValueError:
            errores.append(f"WIP {match} no es un número válido")

    # Cuentas
    cuentas = re.findall(r"\b[IE]\d{6}\b", texto)
    for cuenta in cuentas:
        if cuenta not in GLOSARIO["cuentas_validas"]:
            errores.append(f"Cuenta {cuenta} no válida")

    # Líneas
    lineas = []
    for linea in re.findall(r"\bZZ[A-Z0-9]+\b", texto, re.IGNORECASE):
        linea_upper = linea.upper()
        if linea_upper not in GLOSARIO["lineas_validas"]:
            errores.append(f"Línea {linea} no reconocida")
        lineas.append(linea_upper)

    # PdV
    pdvs = []

    pattern = re.compile(
        r"\b(?:pdv|punto de venta)\b(?:\s+de)?[:\s\-]*([A-Za-z0-9]{2})\b",
        re.IGNORECASE
    )
    for pdv_match in pattern.findall(texto):
        if pdv_match not in GLOSARIO["pdv_validos"]:
            errores.append(f"Punto de venta {pdv_match} no válido")
        pdvs.append(pdv_match)

    incompleto_pattern = re.compile(
        r"\b(?:pdv|punto de venta)\b(?!\s+(?:de\s+)?[A-Za-z0-9]{2}\b)",
        re.IGNORECASE
    )
    for m in incompleto_pattern.finditer(texto):
        errores.append("Se menciona 'punto de venta' pero no se especificó. Debes especificar el punto de venta para ayudarte de mejor manera")

    # Compatibilidades
    for regla in GLOSARIO["incompatibilidades"]:
        if regla["linea"] in lineas:
            for c in cuentas:
                if c.startswith(regla["cuentas_prohibidas_prefijo"]):
                    errores.append(f"Línea {regla['linea']} incompatible con cuenta {c}")

    return errores