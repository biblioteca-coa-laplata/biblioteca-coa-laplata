# 📚 Biblioteca Virtual — COA La Plata

¡Bienvenido al repositorio de la Biblioteca Virtual del **Club de Observadores de Aves (COA) de La Plata**! 

Este proyecto aloja un catálogo dinámico, interactivo y de acceso público que centraliza guías de campo, artículos científicos, revistas, fichas técnicas y material didáctico sobre las ciencias naturales, la conservación y la biodiversidad de nuestra región (Punta Lara, Berisso, La Plata, Pereyra Iraola) y de la Argentina en general.

🌍 **Acceso a la plataforma web:** [https://biblioteca-coa-laplata.github.io/biblioteca-coa-laplata/](https://biblioteca-coa-laplata.github.io/biblioteca-coa-laplata/)

---

## 🛠️ Arquitectura del Proyecto

El sistema está diseñado de forma híbrida e inteligente para funcionar de manera ágil a escala local y web sin necesidad de bases de datos pesadas ni servidores pagos:

* **Procesador de Datos (Backend - Python):** Un script indexador inteligente que escanea la estructura física del disco rígido local, clasifica de forma determinista los documentos según su carpeta raíz y enriquece el catálogo generando una matriz de etiquetas cruzadas.
* **Buscador en la Nube (Frontend - HTML5/JS):** Una interfaz web estática (*Single Page Application*) que procesa el catálogo JSON en la memoria del navegador del usuario. Cuenta con un motor de intersección cruzada (Texto libre + Tipo Documental + Alcance Geográfico) y actúa como lanzador para búsquedas en repositorios de revistas externas.

---

## 📂 Flujo y Secuencia de Trabajo para Actualizaciones

Cada vez que se incorpore nuevo material a la biblioteca física y se desee sincronizar con el sitio web, se debe seguir la siguiente secuencia establecida:

### Fase 1: Trabajo de Campo e Ingesta (Manual)
1. Conectar el disco **Seagate Expansion Drive**.
2. Limpiar y renombrar los nuevos archivos PDF/imágenes utilizando el divisor `;` para separar múltiples coautores si los hubiera.
3. Subir las copias de los nuevos documentos a sus carpetas correspondientes en la cuenta institucional de **Google Drive**.

### Fase 2: Primera Pasada Local (VSCodium)
1. Abrir la carpeta `deploy_web/scripts` en VSCodium.
2. Ejecutar la primera pasada del script en la terminal integrada para registrar los nuevos archivos locales:
   ```bash
   python3 indexador_biblioteca_coa_v_2_python_2.py

(Nota: La terminal advertirá que no se detectó el CSV de URLs, generando un índice temporal con valores nulos para Drive).

### Fase 3: Extracción y Sincronización de URLs (Google Colab)
Abrir el cuaderno de Jupyter extraer_urls_biblioteca.ipynb en VSCodium.

Conectar el Kernel a Colab (Select Kernel -> Colab -> Auto Connect) y ejecutar las celdas en orden (autenticación, mapeo de Drive y generación del reporte).

Descargar el archivo generado drive_urls_biblioteca.csv y moverlo a la carpeta un nivel superior en el disco:
👉 /media/ignacio/Seagate Expansion Drive/deploy_web/

### Fase 4: Segunda Pasada y Fusión Matriz (Consola)
Regresar a la terminal integrada de VSCodium (parada en scripts) y volver a ejecutar el indexador:
    python3 indexador_biblioteca_coa_v_2_python_2.py
El script detectará el nuevo CSV, cruzará las rutas del disco físico con los enlaces de Google Drive e inyectará la matriz de etiquetas acumulativas escribiendo el archivo definitivo catalogo_v2.json en deploy_web/.

### Fase 5: Despliegue en Producción
Ingresar a la interfaz web de GitHub en el repositorio de la biblioteca.

Arrastrar y soltar el archivo catalogo_v2.json actualizado para confirmar los cambios (commit). GitHub Pages actualizará la biblioteca online automáticamente en minutos.

🔧 Mantenimiento Técnico de la Base de Datos
El script indexador realiza una clasificación ortogonal en tres dimensiones independientes dentro de catalogo_v2.json:

Tema Principal: Determinado de forma estricta por la carpeta raíz física del disco (Aves, Flora Nativa, etc.).

Tipo Documental: Forzado rígidamente si el archivo vive en la carpeta Material Didáctico para alimentar correctamente los filtros del sitio web, o deducido por heurística de texto para otros formatos (Guías, Artículos, Revistas).

Etiquetas Cruzadas (etiquetas): Array acumulativo que almacena la ubicación física, palabras clave científicas detectadas y marcas geográficas territoriales (Punta Lara, Berisso), garantizando que un documento didáctico sobre peces sea intersectado con éxito al buscar en cualquier dimensión.


🌐 PARTE 2: Funcionamiento del Frontend (index.html) y Sistema de Búsquedas
La interfaz web está diseñada bajo el paradigma de una Single Page Application (SPA) sin dependencias externas (Vanilla JavaScript). Funciona procesando el JSON generado por Python de forma dinámica en la memoria del navegador.

1. El Motor de Intersección Cruzada (ejecutarBusqueda())
El núcleo de la interactividad web reside en la función de filtrado. No realiza búsquedas aisladas, sino que aplica una intersección lógica (AND) sobre tres variables en tiempo real:

Resultado Final = Match de Texto AND Match de Tipo AND Match de Alcance Geográfico

Cada vez que el usuario escribe o mueve un desplegable, el script realiza el siguiente escaneo sobre el array global de la biblioteca:

Filtro de Texto Libre: Normaliza y busca la cadena del usuario dentro de cinco campos simultáneos del ítem: título, autor, tema_principal, ruta_local y el array de etiquetas.

Filtro por Tipo Documental: Cruza el valor del elemento select (#filtroTipo) directamente contra el campo tipo del JSON.

Filtro por Alcance Geográfico: Cruza el valor del select (#filtroGeo) contra la sigla del campo alcance_geografico (como ARG, BSAS, LOC).

Este diseño es lo que permite que al escribir "aves" y seleccionar el tipo "MATERIAL DIDÁCTICO", la interfaz reduzca la vista únicamente a la intersección exacta de ambos mundos.

🔌 PARTE 3: El Doble Rol de la Barra de Búsqueda y Botones Externos
Una de las características más avanzadas de tu interfaz es que la barra de búsqueda central (#searchBar) y los botones superiores de emojis no solo manipulan la base de datos local, sino que actúan como un controlador de consultas para repositorios y revistas externas.

1. Comportamiento de los Botones de Exploración Rápida (Emojis)
Cuando hacés clic en un botón de categoría (ej. 🦅 Aves, 🌿 Flora nativa, 🎒 Material didáctico), la web ejecuta la función buscarCategoria(categoria, event). Esta rutina realiza dos acciones en paralelo:

Inyecta el texto del filtro (ej: "didactico" o "aves") directamente dentro de la caja de texto visible del usuario (searchBar.value = categoria).

Dispara la búsqueda local inmediatamente para mostrar los archivos que tenés guardados en tu repositorio de GitHub.

2. El Enlace con las Revistas y Buscadores Externos
Al dejar el término de búsqueda escrito en la caja de texto central (#searchBar), la interfaz aprovecha ese estado de la memoria para redirigir al usuario hacia plataformas externas con la consulta ya armada.

En los eventos asignados a los botones de abajo (btnEbird, btnHornero, btnNuestrasAves), el código JavaScript lee el valor actual de la barra de búsqueda mediante searchBar.value.trim().

Si la barra está vacía, abre la página de inicio del repositorio externo (ej. la sección de archivos de la revista).

Si la barra contiene texto (por ejemplo, el nombre de una especie o un autor), el script intercepta ese valor y construye dinámicamente una URL de consulta usando encodeURIComponent(t).

De este modo, cuando el usuario hace clic, se le abre una pestaña nueva en el navegador que impacta directamente en el motor de búsqueda interno de la Revista El Hornero, Nuestras Aves o Google Search (filtrado para eBird) con la palabra clave ya ingresada

🦅 Proyecto desarrollado para la gestión de contenidos biológicos del COA La Plata. Desarrollado en entornos libres (Debian Stable / VSCodium).
