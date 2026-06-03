from pathlib import Path
import csv
import json
import re
import unicodedata

# =========================================================
# BIBLIOTECA VIRTUAL — COA LA PLATA
# Indexador v2 (Optimizado para Doble Pasada: Curación + URLs)
# =========================================================

# =========================================================
# CONFIGURACIÓN
# =========================================================

RUTA_BIBLIOTECA = Path(
    "/media/ignacio/Seagate Expansion Drive/Biblioteca COA La Plata"
)

SALIDA_JSON = "/media/ignacio/Seagate Expansion Drive/deploy_web/catalogo_v2.json"
CSV_URLS_DRIVE = Path(
    "/media/ignacio/Seagate Expansion Drive/deploy_web/drive_urls_biblioteca.csv"
)

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
# DICCIONARIOS DE DETECCIÓN (TEMAS, TIPOS, ETC.)
# =========================================================

TEMAS = {
    "aves": ["ave", "aves", "bird", "ornitologia", "ornitología"],
    "flora nativa": ["flora", "planta", "plantas", "nativa", "botanica", "botánica"],
    "entomología": ["entomologia", "entomología", "insecto", "insectos", "mariposa", "mariposas", "lepidoptero", "coleópteros", "lepidóptero", "lepidopteros", "lepidópteros", "chinches", "arañas","tarántulas"],
    "hongos": ["hongo", "hongos", "fungi", "funga"],
    "mamíferos": ["mamifero", "mamífero", "mamiferos", "mamíferos", "ballenas", "cetáceos", "cetaceos", "roedores", "murcielagos", "murciélagos", "xenartros", "aguará guazú"],
    "anfibios": ["anfibio", "herpetologia", "herpetología", "ranas", "sapos", "anfibios", "anphibians"],
    "reptiles": ["herpetología", "herpetologia", "serpientes", "culebras", "lagartos", "lagartijas", "reptil", "reptiles"],
    "peces": ["pez", "peces"],
    "legislación ambiental": ["ley", "legislacion", "legislación", "normativa", "ordenanza", "ambiente"],
    "destinos y áreas protegidas": ["__carpeta_destinos__"],
}

TIPOS = {
    "guía": ["guia", "guide", "guía", "field guide"],
    "artículo": ["paper", "journal", "articulo", "artículo", "scientific", "congreso", "ponencia", "articulo cientifico", "artículo científico"],
    "revista": ["revista", "boletin", "boletín"],
    "ficha": ["ficha", "fichas"],
    "lámina": ["lamina", "lámina", "afiche", "poster", "póster"],
    "manual": ["manual"],
    "material didáctico": ["didactico", "didáctico", "actividad", "juego"],
    "libro": ["libro"],
    "cartilla": ["cartilla"],
    "monografía": ["monografía", "monografia"],
    "inventario": ["inventario", "catalogo", "catálogo"],
    "listado": ["listado", "lista"]
}

ETIQUETAS_GEOGRAFICAS = {
    "Punta Lara": ["punta lara"],
    "Berisso": ["berisso"],
    "Pereyra Iraola": ["pereyra", "iraola"]
}

ETIQUETAS_CARPETAS = {
    "mariposas": "Mariposas",
    "revista fauna argentina ceal": "Fauna Argentina CEAL",
    "revista garganchillo": "El Garganchillo",
    "guias": "Guías",
    "fichas": "Fichas",
    "material didactico": "Material Didáctico",
    "destinos y areas protegidas": "Destinos y Áreas Protegidas"  # <- ¡Agregamos esta línea!
}

ALCANCE_GEOGRAFICO = {
    "LOC": "Local / Regional",
    "SAM": "Sudamérica",
    "ARG": "Argentina",
    "BSAS": "Buenos Aires",
    "MUN": "Mundial"
}

COLECCIONES = {
    "El Garganchillo": ["garganchillo"],
    "Bandera Argentina": ["bandera argentina"],
    "Fichas de Nativas": ["fichas"]
}

AUTORES = {
    "Narosky": ["narosky"],
    "Chebez": ["chebez"],
    "Haene": ["haene"],
    "Canevari": ["canevari"],
    "Bertonatti": ["bertonatti"],
    "Aprile": ["aprile"]
}

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def limpiar_titulo(nombre_archivo):
    nombre = nombre_archivo.stem
    nombre = nombre.replace("_", " ")
    nombre = nombre.replace("-", " ")
    nombre = re.sub(r"\s+", " ", nombre)
    return nombre.strip()

def detectar_tema(texto):
    texto = normalizar(texto)
    for tema, palabras in TEMAS.items():
        for palabra in palabras:
            if palabra in texto:
                return tema
    return "sin clasificar"

def detectar_tipo(texto):
    texto = normalizar(texto)
    for tipo, palabras in TIPOS.items():
        for palabra in palabras:
            if palabra in texto:
                return tipo
    return "documento"

def detectar_etiquetas(texto):
    etiquetas = []
    texto_normalizado = normalizar(texto)
    for etiqueta, palabras in ETIQUETAS_GEOGRAFICAS.items():
        for palabra in palabras:
            if palabra in texto_normalizado:
                etiquetas.append(etiqueta)
                break
    if "mariposa" in texto_normalizado or "lepidopter" in texto_normalizado:
        etiquetas.append("mariposas")
    if "migr" in texto_normalizado:
        etiquetas.append("migración")
    for carpeta, etiqueta in ETIQUETAS_CARPETAS.items():
        if carpeta in texto_normalizado:
            etiquetas.append(etiqueta)
    return sorted(list(set(etiquetas)))

def detectar_coleccion(texto):
    texto = normalizar(texto)
    for coleccion, palabras in COLECCIONES.items():
        for palabra in palabras:
            if palabra in texto:
                return coleccion
    return None

def detectar_autores(texto):
    tipos_reservados = set()
    for tipo, variantes in TIPOS.items():
        tipos_reservados.add(normalizar(tipo))
        for variante in variantes:
            tipos_reservados.add(normalizar(variante))

    if " - " in texto:
        parte_autores = texto.split(" - ")[0]
        autores = [autor.strip() for autor in re.split(r"[;,]", parte_autores)]
        autores = [autor for autor in autores if autor]

        if autores:
            autores_normalizados = [normalizar(a) for a in autores]
            if all(a in tipos_reservados for a in autores_normalizados):
                return []
            return autores

    autores_detectados = []
    texto_normalizado = normalizar(texto)
    for autor, variantes in AUTORES.items():
        for variante in variantes:
            if variante in texto_normalizado:
                autores_detectados.append(autor)
                break
    return autores_detectados

# =========================================================
# CIRCUITO DE PROCESAMIENTO (Doble Pasada Seguro)
# =========================================================

# 1. CARGA SEGURO DEL CSV (Si no existe, no explota)
urls_drive = {}
if CSV_URLS_DRIVE.exists():
    try:
        with open(CSV_URLS_DRIVE, encoding="utf-8") as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            for fila in lector:
                # Usamos .strip() por si Colab mete espacios invisibles en los nombres
                if "ruta_local" in fila and "url_drive" in fila:
                    urls_drive[fila["ruta_local"].strip()] = fila["url_drive"].strip()
        print(f"✅ [Pasada 2] Mapeo de URLs cargado con éxito. Se encontraron {len(urls_drive)} enlaces de Drive.")
    except Exception as e:
        print(f"⚠️ Alerta: Se encontró el CSV de Drive pero tiene un problema de formato: {e}")
else:
    print("ℹ️ [Pasada 1] No se detectó el CSV de URLs de Drive. Se generará el índice preliminar con 'url_drive': null.")

catalogo = []
contador = 1

# Recorremos la biblioteca local actualizada por los curadores
for archivo in RUTA_BIBLIOTECA.rglob("*"):
    if not archivo.is_file():
        continue

    if archivo.suffix.lower() not in EXTENSIONES_VALIDAS:
        continue

    ruta_relativa = archivo.relative_to(RUTA_BIBLIOTECA)
    texto_analisis = " ".join(ruta_relativa.parts)

    # Detectar alcance geográfico
    alcance_geografico = None
    for sigla in ALCANCE_GEOGRAFICO:
        if f"[{sigla}]" in texto_analisis:
            alcance_geografico = sigla
            break

    # Extracción de metadatos heurísticos
    titulo = limpiar_titulo(archivo)
    tema = detectar_tema(texto_analisis)
    tipo = detectar_tipo(texto_analisis)
    etiquetas = detectar_etiquetas(texto_analisis)
    coleccion = detectar_coleccion(texto_analisis)
    autores = detectar_autores(archivo.stem)
    extension = archivo.suffix.lower()

    # Configuración de Acceso según peso
    acceso = "visor_drive"
    if archivo.stat().st_size > 100 * 1024 * 1024:
        acceso = "descarga"

    # Cruce seguro con el diccionario de URLs (Soporta null implícito)
    # Si no lo encuentra en el CSV, el valor por defecto queda en None (null en JSON)
    url_detectada = urls_drive.get(str(ruta_relativa), None)

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
        "ruta_local": str(ruta_relativa),
        "url_drive": url_detectada
    }

    catalogo.append(registro)
    contador += 1

# =========================================================
# EXPORTACIÓN DEL ARCHIVO CATÁLOGO JSON
# =========================================================

# Asegurar que la carpeta de destino exista antes de guardar
Path(SALIDA_JSON).parent.mkdir(parents=True, exist_ok=True)

with open(SALIDA_JSON, "w", encoding="utf-8") as archivo_json:
    json.dump(
        catalogo,
        archivo_json,
        ensure_ascii=False,
        indent=2
    )

# =========================================================
# PANEL DE CONTROL FIN DE PROCESO
# =========================================================

print()
print("==================================================")
print("             INDEXACIÓN COMPLETADA                ")
print("==================================================")
print(f" Archivos procesados con éxito: {len(catalogo)}")
print(f" Ubicación del catálogo final:  {SALIDA_JSON}")
print("--------------------------------------------------")
if urls_drive:
    vinculados = sum(1 for x in catalogo if x["url_drive"] is not None)
    print(f" 🔗 Documentos vinculados a Drive:  {vinculados} de {len(catalogo)}")
else:
    print(" 📂 Modo Curación: Todos los campos 'url_drive' se setearon en 'null'.")
print("==================================================")
print()
