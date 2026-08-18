# Presentación de SoporteLab en LinkedIn

## Texto sugerido para la sección Proyectos

**SoporteLab — Simulador de mesa de ayuda IT**

Aplicación web personal desarrollada para practicar el ciclo completo de gestión
de incidentes: registro y priorización de tickets, seguimiento de activos,
documentación del diagnóstico, control de vencimientos y creación de una base de
conocimientos. Incluye datos ficticios reproducibles y un script PowerShell de
diagnóstico de Windows.

**Tecnologías:** Python, Django, SQLite, HTML/CSS, JavaScript y PowerShell.

Repositorio: `[agregar URL]`  
Demo o video: `[agregar URL]`

## Publicación sugerida

Terminé **SoporteLab**, un proyecto personal con el que simulé el trabajo diario
de una mesa de ayuda IT.

El sistema permite registrar incidentes y solicitudes, priorizarlos, asociarlos
a equipos del inventario, documentar diagnósticos y resoluciones, controlar
vencimientos y convertir soluciones frecuentes en artículos de conocimiento.
También desarrollé un script PowerShell de solo lectura que genera un informe
del sistema, almacenamiento, red, DNS y conectividad de un equipo Windows.

El objetivo no fue reemplazar una herramienta profesional, sino construir un
entorno acotado para practicar soporte, documentación técnica y desarrollo web
de punta a punta.

Tecnologías utilizadas: Python, Django, SQLite, HTML/CSS, JavaScript y PowerShell.

Código y documentación: `[agregar URL del repositorio]`

#SoporteIT #HelpDesk #Python #Django #PowerShell #DesarrolloDeSoftware

## Guion breve para un video de demostración

1. Presentar el panel y explicar las métricas principales.
2. Abrir un ticket vencido, revisar su activo y agregar una actividad.
3. Completar diagnóstico, causa raíz y resolución.
4. Mostrar cómo una solución queda documentada en la base de conocimientos.
5. Ejecutar el script PowerShell y abrir el JSON generado.
6. Cerrar aclarando que los usuarios, la empresa y los incidentes son ficticios.

Duración recomendada: entre 60 y 90 segundos.

## Cómo describirlo en una entrevista

- Es un proyecto personal con datos simulados, no una implementación para un cliente.
- El alcance se definió alrededor del flujo de soporte: detectar, registrar,
  diagnosticar, resolver y documentar.
- La carga idempotente permite reconstruir siempre el mismo escenario de demo.
- SQLite mantiene la instalación sencilla y suficiente para este objetivo.
- El script PowerShell no corrige ni modifica el equipo: reúne evidencia para
  facilitar el diagnóstico.

## Afirmaciones que conviene evitar

- No decir que estuvo en producción o que fue usado por una empresa real.
- No presentar los tiempos de resolución simulados como métricas laborales.
- No describirlo como un reemplazo de GLPI, Jira Service Management u osTicket.
- No atribuirse experiencia profesional con herramientas o tecnologías que el
  proyecto no utiliza.
