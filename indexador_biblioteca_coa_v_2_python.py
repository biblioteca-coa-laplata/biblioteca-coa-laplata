from pathlib import Path
import json
import re
import unicodedata

# =========================================================
# BIBLIOTECA DEL NATURALISTA — COA LA PLATA
# Indexador v2
# =========================================================
#
# OBJETIVOS:
# - Recorrer biblioteca local
# - Generar catálogo JSON
# - Detectar temas preliminares
# - Detectar tipos documentales
# - Preparar catálogo para HTML
#
# Este script NO depende de la estructura exacta
# de carpetas.
#
# =========================================================

# =========================================================
# CONFIGURACIÓN
# =========================================================

RUTA_BIBLIOTECA = Path(
    "/media/ignaciot/Seagate Expansion Drive/Biblioteca COA La Plata"
)

SALIDA_JSON = "catalogo_v2.json"

EXTENSIONES_VALIDAS = {
    ".pdf",
    ".epub",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".jpg",
    ".jpeg",
    ".png"
}

# =========================================================
# TEMAS PRINCIPALES
# =========================================================

TEMAS = {
    "aves": [
        "ave",
        "aves",
        "bird",
        "ornitologia",
        "ornitología"
    ],

    "flora nativa": [
        "flora",
        "planta",
        "plantas",
        "nativa",
        "botanica",
        "botánica"
    ],

    "entomología": [
        "entomologia",
        "entomología",
        "insecto",
        "insectos",
        "mariposa",
        "mariposas",
        "lepidoptero",
        "lepidóptero",
        "lepidopteros",
        "lepidópteros"
    ],
    
    "hongos": [
        "hongo",
        "hongos",
        "fungi",
        "funga"
    ],

    "mamíferos": [
    "mamifero",
    "mamífero",
    "mamiferos",
    "mamíferos"
    ],

    "anfibios": [
    "anfibio",
    "herpetologia",
    "herpetología",
    "ranas",
    "sapos",
    "anfibios"
],

"reptiles": [
    "herpetología",
    "herpetologia",
    "serpeintes",
    "culebras",
    "lagartos",
    "lagartijas",
    "reptil",
    "reptiles"
    ],

    "peces": [
        "pez",
        "peces"
    ],

    "legislación ambiental": [
        "ley",
        "legislacion",
        "legislación",
        "normativa",
        "ordenanza",
        "ambiente"
    ]
}

# =========================================================
# TIPOS DOCUMENTALES
# =========================================================

TIPOS = {
    "guía": ["guia", "guide", "guía", "field guide"],

    "artículo": [
        "paper",
        "journal",
        "articulo",
        "artículo",
        "scientific",
        "congreso",
        "ponencia",
        "articulo cientifico",
        "artículo científico"
    ],
    "revista": [
        "revista",
        "boletin",
        "boletín"
        ],

    "ficha": ["ficha", "fichas"],

    "lámina": ["lamina", "lámina", "afiche", "poster", "póster"],

    "manual": ["manual"],

    "material didáctico": [
        "didactico",
        "didáctico",
        "actividad",
        "juego",
    ],

    "libro": ["libro"],

    "cartilla": ["cartilla"],

    "monografía": ["monografía", "monografia"],

    "inventario": ["inventario", "catalogo", "catálogo"],

    "listado": ["listado", "lista"]
}

# =========================================================
# ETIQUETAS GEOGRÁFICAS
# =========================================================

ETIQUETAS_GEOGRAFICAS = {
    "Punta Lara": [
        "punta lara"
    ],

    "Berisso": [
        "berisso"
    ],

    "Pereyra Iraola": [
        "pereyra",
        "iraola"
    ]
}


# =========================================================
# ETIQUETAS POR CARPETA
# =========================================================

ETIQUETAS_CARPETAS = {

    "mariposas": "Mariposas",

    "revista fauna argentina ceal": "Fauna Argentina CEAL",

    "revista garganchillo": "El Garganchillo",

    "guias": "Guías",

    "fichas": "Fichas",

    "material didactico": "Material Didáctico"
}


# =========================================================
# ALCANCE GEOGRÁFICO
# =========================================================

ALCANCE_GEOGRAFICO = {
    "LOC": "Local / Regional",
    "SAM": "Sudamérica",
    "ARG": "Argentina",
    "BSAS": "Buenos Aires",
    "MUN": "Mundial"
}



# =========================================================
# COLECCIONES
# =========================================================

COLECCIONES = {
    "El Garganchillo": [
        "garganchillo"
    ],

    "Bandera Argentina": [
        "bandera argentina"
    ],

    "Fichas de Nativas": [
        "fichas"
    ]
}

# =========================================================
# AUTORES FRECUENTES
# =========================================================
#
# Esto puede crecer con el tiempo.
#
# =========================================================

AUTORES = {
    "Narosky": ["narosky"],
    "Chebez": ["chebez"],
    "Haene": ["haene"],
    "Canevari": ["canevari"],
    "Bertonatti": ["bertonatti"],
    "Aprile": ["aprile"]
}

# =========================================================
# FUNCIONES
# =========================================================


def normalizar(texto):
    """
    Convierte texto a minúsculas sin acentos.
    """

    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto


# ---------------------------------------------------------


def limpiar_titulo(nombre_archivo):
    """
    Produce títulos más legibles.
    """

    nombre = nombre_archivo.stem

    nombre = nombre.replace("_", " ")
    nombre = nombre.replace("-", " ")

    nombre = re.sub(r"\s+", " ", nombre)

    return nombre.strip()


# ---------------------------------------------------------


def detectar_tema(texto):
    """
    Detecta tema principal.
    """

    texto = normalizar(texto)

    for tema, palabras in TEMAS.items():
        for palabra in palabras:
            if palabra in texto:
                return tema

    return "sin clasificar"


# ---------------------------------------------------------


def detectar_tipo(texto):
    """
    Detecta tipo documental.
    """

    texto = normalizar(texto)

    for tipo, palabras in TIPOS.items():
        for palabra in palabras:
            if palabra in texto:
                return tipo

    return "documento"


# ---------------------------------------------------------


def detectar_etiquetas(texto):
    """
    Detecta etiquetas preliminares.
    """

    etiquetas = []

    texto_normalizado = normalizar(texto)

    # -----------------------------------------------------
    # Geográficas
    # -----------------------------------------------------

    for etiqueta, palabras in ETIQUETAS_GEOGRAFICAS.items():
        for palabra in palabras:
            if palabra in texto_normalizado:
                etiquetas.append(etiqueta)
                break

    # -----------------------------------------------------
    # Lepidópteros
    # -----------------------------------------------------

    if (
        "mariposa" in texto_normalizado
        or "lepidopter" in texto_normalizado
    ):
        etiquetas.append("mariposas")

    # -----------------------------------------------------
    # Migración
    # -----------------------------------------------------

    if "migr" in texto_normalizado:
        etiquetas.append("migración")

    # -----------------------------------------------------
    # Etiquetas por carpeta
    # -----------------------------------------------------

    for carpeta, etiqueta in ETIQUETAS_CARPETAS.items():

        if carpeta in texto_normalizado:

            etiquetas.append(etiqueta)

    return sorted(list(set(etiquetas)))

# ---------------------------------------------------------


def detectar_coleccion(texto):
    """
    Detecta colección.
    """

    texto = normalizar(texto)

    for coleccion, palabras in COLECCIONES.items():
        for palabra in palabras:
            if palabra in texto:
                return coleccion

    return None


# ---------------------------------------------------------


def detectar_autores(texto):
    """
    Detecta autores usando:
    1. Norma COA (antes del guion)
    2. Diccionario heurístico (fallback)
    """

    import re

    # -------------------------------------------------
    # Construir lista de tipos documentales reservados
    # -------------------------------------------------

    tipos_reservados = set()

    for tipo, variantes in TIPOS.items():

        tipos_reservados.add(normalizar(tipo))

        for variante in variantes:

            tipos_reservados.add(normalizar(variante))

    # -------------------------------------------------
    # Intentar detectar por estructura:
    # Autor1, Autor2 - Título
    # -------------------------------------------------

    if " - " in texto:

        parte_autores = texto.split(" - ")[0]

        autores = [
            autor.strip()
            for autor in re.split(r"[;,]", parte_autores)
        ]

        autores = [
            autor
            for autor in autores
            if autor
        ]

        # ---------------------------------------------
        # Si lo que está antes del guión es un tipo
        # documental, NO es autor
        # ---------------------------------------------

        if autores:

            autores_normalizados = [
                normalizar(a)
                for a in autores
            ]

            if all(
                a in tipos_reservados
                for a in autores_normalizados
            ):
                return []

            return autores

    # -------------------------------------------------
    # Fallback heurístico
    # -------------------------------------------------

    autores_detectados = []

    texto_normalizado = normalizar(texto)

    for autor, variantes in AUTORES.items():

        for variante in variantes:

            if variante in texto_normalizado:

                autores_detectados.append(autor)

                break

    return autores_detectados
    # -------------------------------------------------
    # Fallback heurístico
    # -------------------------------------------------

    autores_detectados = []

    texto_normalizado = normalizar(texto)

    for autor, variantes in AUTORES.items():

        for variante in variantes:

            if variante in texto_normalizado:

                autores_detectados.append(autor)

                break

    return autores_detectados


# =========================================================
# INDEXACIÓN
# =========================================================

catalogo = []

contador = 1

for archivo in RUTA_BIBLIOTECA.rglob("*"):

    if not archivo.is_file():
        continue

    if archivo.suffix.lower() not in EXTENSIONES_VALIDAS:
        continue

    ruta_relativa = archivo.relative_to(RUTA_BIBLIOTECA)

    texto_analisis = " ".join(ruta_relativa.parts)

    #-----------------------------------------------------
    #Detectar alcance geografico
    #-----------------------------------------------------
    alcance_geografico = None
    for sigla in ALCANCE_GEOGRAFICO:
        if f"[{sigla}]" in texto_analisis:
            alcance_geografico = sigla
            break

    titulo = limpiar_titulo(archivo)

    tema = detectar_tema(texto_analisis)

    tipo = detectar_tipo(texto_analisis)

    etiquetas = detectar_etiquetas(texto_analisis)

    coleccion = detectar_coleccion(texto_analisis)

    autores = detectar_autores(archivo.stem)

    extension = archivo.suffix.lower()

    # -----------------------------------------------------
    # Acceso preliminar
    # -----------------------------------------------------

    acceso = "visor_drive"

    if archivo.stat().st_size > 100 * 1024 * 1024:
        acceso = "descarga"

    # -----------------------------------------------------
    # Registro
    # -----------------------------------------------------

    registro = {
        "id": f"{contador:05}",

        "titulo": titulo,

        "autor": autores,

        "tema_principal": tema,

        "tipo": tipo,

        "etiquetas": etiquetas,

        "coleccion": coleccion,

        "fuente": "local",

        "acceso": acceso,

        "alcance_geografico": alcance_geografico,

        "extension": extension,

        "ruta_local": str(ruta_relativa)
    }

    catalogo.append(registro)

    contador += 1

# =========================================================
# EXPORTACIÓN JSON
# =========================================================

with open(SALIDA_JSON, "w", encoding="utf-8") as archivo_json:

    json.dump(
        catalogo,
        archivo_json,
        ensure_ascii=False,
        indent=2
    )

# =========================================================
# RESUMEN
# =========================================================

print()
print("========================================")
print("INDEXACIÓN FINALIZADA")
print("========================================")
print()
print(f"Archivos indexados: {len(catalogo)}")
print(f"JSON generado: {SALIDA_JSON}")
print()
