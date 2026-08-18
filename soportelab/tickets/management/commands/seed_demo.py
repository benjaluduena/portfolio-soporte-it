"""Carga un escenario ficticio y reproducible para demostrar SoporteLab."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from assets.models import Asset
from knowledge.models import KnowledgeArticle
from tickets.models import Category, Ticket, TicketActivity


DEMO_PASSWORD = "Demo2026!"
ADMIN_PASSWORD = "SoporteLab2026!"


class Command(BaseCommand):
    help = "Crea o actualiza los datos ficticios usados en la demostración."

    @transaction.atomic
    def handle(self, *args, **options):
        users = self._seed_users()
        categories = self._seed_categories()
        assets = self._seed_assets(users)
        tickets = self._seed_tickets(users, categories, assets)
        self._seed_activities(users, tickets)
        self._seed_articles(users, categories, tickets)

        self.stdout.write(
            self.style.SUCCESS(
                "Escenario demo listo: 4 usuarios, 8 categorías, 12 activos, "
                "18 tickets y 8 artículos."
            )
        )
        self.stdout.write("Administrador: admin / SoporteLab2026!")
        self.stdout.write("Otros usuarios: contraseña Demo2026!")

    def _seed_users(self):
        User = get_user_model()
        definitions = (
            {
                "username": "admin",
                "first_name": "Administración",
                "last_name": "SoporteLab",
                "email": "admin@soportelab.example.invalid",
                "is_staff": True,
                "is_superuser": True,
                "password": ADMIN_PASSWORD,
            },
            {
                "username": "tecnico.ana",
                "first_name": "Ana",
                "last_name": "Torres",
                "email": "ana@soportelab.example.invalid",
                "is_staff": True,
                "is_superuser": False,
                "password": DEMO_PASSWORD,
            },
            {
                "username": "tecnico.martin",
                "first_name": "Martín",
                "last_name": "Rojas",
                "email": "martin@soportelab.example.invalid",
                "is_staff": True,
                "is_superuser": False,
                "password": DEMO_PASSWORD,
            },
            {
                "username": "solicitante",
                "first_name": "Sofía",
                "last_name": "Gómez",
                "email": "sofia@soportelab.example.invalid",
                "is_staff": False,
                "is_superuser": False,
                "password": DEMO_PASSWORD,
            },
        )

        users = {}
        for definition in definitions:
            password = definition.pop("password")
            username = definition.pop("username")
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={**definition, "is_active": True},
            )
            user.set_password(password)
            user.save(update_fields=["password"])
            users[username] = user
        return users

    def _seed_categories(self):
        definitions = (
            ("Accesos y cuentas", "Altas, bloqueos, permisos y credenciales."),
            ("Hardware", "Fallas y solicitudes relacionadas con componentes físicos."),
            ("Software", "Instalación, configuración y errores de aplicaciones."),
            ("Red y conectividad", "Conexión local, Internet, Wi-Fi, DNS y VPN."),
            ("Correo y colaboración", "Correo electrónico y herramientas colaborativas."),
            ("Impresión", "Impresoras, colas, controladores y consumibles."),
            ("Seguridad", "Eventos sospechosos y medidas preventivas."),
            ("Solicitudes generales", "Consultas y pedidos que no corresponden a otra categoría."),
        )
        categories = {}
        for name, description in definitions:
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"description": description, "is_active": True},
            )
            categories[name] = category
        return categories

    def _seed_assets(self, users):
        definitions = (
            ("PC-001", "Puesto Administración 01", "desktop", "Dell", "OptiPlex 7090", "SL-PC-001", "active", "solicitante", "Administración", "Windows 11 Pro", "Equipo principal del área administrativa."),
            ("NB-002", "Notebook Comercial 02", "laptop", "Lenovo", "ThinkPad E14", "SL-NB-002", "active", "solicitante", "Comercial", "Windows 11 Pro", "Uso híbrido oficina/remoto."),
            ("PC-003", "Puesto Depósito 01", "desktop", "HP", "ProDesk 400 G7", "SL-PC-003", "active", None, "Depósito", "Windows 10 Pro", "Conectado a lector de códigos."),
            ("PC-004", "Puesto Recepción", "desktop", "Dell", "OptiPlex 3080", "SL-PC-004", "maintenance", None, "Recepción", "Windows 10 Pro", "En revisión por fallas intermitentes de disco."),
            ("NB-005", "Notebook Gerencia", "laptop", "HP", "ProBook 440 G9", "SL-NB-005", "active", None, "Gerencia", "Windows 11 Pro", "Cifrado del dispositivo habilitado."),
            ("NB-006", "Notebook Soporte", "laptop", "Lenovo", "ThinkPad L14", "SL-NB-006", "active", "tecnico.ana", "Sistemas", "Windows 11 Pro", "Equipo de diagnóstico."),
            ("PRN-001", "Impresora Administración", "printer", "Brother", "MFC-L8900CDW", "SL-PRN-001", "active", None, "Administración", "", "Impresora de red compartida."),
            ("PRN-002", "Impresora Depósito", "printer", "Zebra", "ZD421", "SL-PRN-002", "active", None, "Depósito", "", "Impresión de etiquetas."),
            ("NET-001", "Switch principal", "network", "Ubiquiti", "USW-24", "SL-NET-001", "active", None, "Sala técnica", "UniFi Network", "Switch de acceso principal."),
            ("NET-002", "Punto de acceso oficina", "network", "Ubiquiti", "U6-Lite", "SL-NET-002", "active", None, "Oficina abierta", "UniFi Network", "Punto de acceso del primer piso."),
            ("MOB-001", "Teléfono guardia", "mobile", "Samsung", "Galaxy A33", "SL-MOB-001", "active", "tecnico.martin", "Sistemas", "Android", "Dispositivo para guardias simuladas."),
            ("PC-012", "Puesto legado", "desktop", "Banghó", "Pro T", "SL-PC-012", "retired", None, "Depósito técnico", "Windows 10 Pro", "Retirado del servicio; conservado como registro histórico."),
        )

        assets = {}
        for (
            asset_tag,
            name,
            asset_type,
            brand,
            model,
            serial_number,
            status,
            assigned_username,
            location,
            operating_system,
            notes,
        ) in definitions:
            asset, _ = Asset.objects.update_or_create(
                asset_tag=asset_tag,
                defaults={
                    "name": name,
                    "asset_type": asset_type,
                    "brand": brand,
                    "model": model,
                    "serial_number": serial_number,
                    "status": status,
                    "assigned_to": users.get(assigned_username),
                    "location": location,
                    "operating_system": operating_system,
                    "notes": notes,
                },
            )
            assets[asset_tag] = asset
        return assets

    def _seed_tickets(self, users, categories, assets):
        now = timezone.now()
        definitions = (
            ("INC-0001", "Sin acceso a la cuenta después de varios intentos", "La cuenta quedó bloqueada luego de ingresar una contraseña incorrecta.", "incident", "Accesos y cuentas", "high", "closed", "solicitante", "tecnico.ana", "PC-001", 28, -27, "La cuenta figura bloqueada en el registro de autenticación.", "Bloqueo automático por intentos fallidos.", "Se validó la identidad del usuario, se desbloqueó la cuenta y se recomendó actualizar la contraseña."),
            ("INC-0002", "La impresora de Administración aparece sin conexión", "No se imprimen facturas desde los puestos del sector.", "incident", "Impresión", "high", "resolved", "solicitante", "tecnico.martin", "PRN-001", 18, -17, "La impresora responde en red, pero la cola del servidor quedó pausada.", "Cola de impresión detenida luego de un trabajo con error.", "Se eliminó el trabajo dañado, se reanudó la cola y se verificó una página de prueba."),
            ("INC-0003", "Poco espacio disponible en disco", "Windows muestra avisos de almacenamiento insuficiente.", "incident", "Hardware", "medium", "in_progress", "solicitante", "tecnico.ana", "PC-001", 3, None, "La unidad del sistema tiene menos del 8 % de espacio libre.", "", ""),
            ("INC-0004", "No resuelve nombres de sitios internos", "Hay conectividad por IP, pero no abren los recursos por nombre.", "incident", "Red y conectividad", "critical", "assigned", "solicitante", "tecnico.martin", "NB-002", 1, None, "La interfaz recibió un DNS externo en lugar del DNS interno esperado.", "", ""),
            ("INC-0005", "Wi-Fi inestable en la oficina abierta", "La conexión se interrumpe por momentos durante videollamadas.", "incident", "Red y conectividad", "high", "pending", "solicitante", "tecnico.martin", "NET-002", 4, None, "Se detectan variaciones de señal y alta ocupación del canal.", "", ""),
            ("INC-0006", "Aplicación contable no inicia", "La aplicación se cierra inmediatamente después de abrirla.", "incident", "Software", "high", "closed", "solicitante", "tecnico.ana", "PC-001", 22, -20, "El archivo local de configuración estaba dañado.", "Cierre inesperado durante una actualización de preferencias.", "Se respaldó y regeneró la configuración local; la aplicación inició correctamente."),
            ("INC-0007", "Lentitud al iniciar sesión", "El escritorio tarda más de diez minutos en quedar disponible.", "incident", "Software", "medium", "open", "solicitante", None, "PC-003", 2, None, "", "", ""),
            ("INC-0008", "Correo con adjunto sospechoso", "Se recibió un mensaje inesperado que solicita abrir un archivo comprimido.", "incident", "Seguridad", "critical", "resolved", "solicitante", "tecnico.ana", "NB-002", 8, -8, "El remitente y el dominio no guardan relación con proveedores conocidos.", "Campaña simulada de phishing.", "Se aisló el mensaje, se revisó el equipo y se documentaron indicadores sin abrir el adjunto."),
            ("INC-0009", "Etiquetas impresas desalineadas", "La información queda desplazada en las etiquetas del depósito.", "incident", "Impresión", "medium", "in_progress", "solicitante", "tecnico.martin", "PRN-002", 5, None, "El tamaño configurado en el controlador no coincide con el rollo instalado.", "", ""),
            ("INC-0010", "Pantalla azul en puesto de recepción", "El equipo se reinició dos veces mostrando un error del sistema.", "incident", "Hardware", "critical", "pending", "solicitante", "tecnico.ana", "PC-004", 2, None, "La prueba SMART registra advertencias en la unidad del sistema.", "Posible degradación del almacenamiento.", ""),
            ("INC-0011", "No conecta la VPN desde red doméstica", "La conexión remota queda esperando y finaliza por tiempo agotado.", "incident", "Red y conectividad", "high", "resolved", "solicitante", "tecnico.martin", "NB-002", 12, -10, "El perfil conservaba una dirección antigua del servicio.", "Perfil VPN desactualizado.", "Se importó el perfil vigente y se validó acceso al recurso de prueba."),
            ("INC-0012", "Audio no disponible en videollamada", "La aplicación no detecta el micrófono integrado.", "incident", "Hardware", "low", "closed", "solicitante", "tecnico.ana", "NB-002", 31, -30, "El acceso al micrófono estaba deshabilitado en privacidad de Windows.", "Permiso de privacidad desactivado.", "Se habilitó el permiso y se realizó una llamada de prueba."),
            ("REQ-0013", "Instalar lector de PDF", "Se solicita una aplicación aprobada para consultar documentación en PDF.", "request", "Software", "low", "closed", "solicitante", "tecnico.ana", "PC-003", 16, -14, "Solicitud estándar validada.", "No aplica: solicitud de servicio.", "Se instaló la aplicación aprobada y se verificó la apertura de un documento."),
            ("REQ-0014", "Preparar acceso para usuario nuevo", "Crear los accesos básicos para una incorporación simulada.", "request", "Accesos y cuentas", "medium", "in_progress", "solicitante", "tecnico.martin", None, 1, None, "Solicitud aprobada; faltan confirmar permisos de una carpeta.", "", ""),
            ("REQ-0015", "Cambiar ubicación de impresora", "Se solicita mover la impresora del sector a otra boca de red.", "request", "Impresión", "medium", "open", "solicitante", None, "PRN-001", 0, None, "", "", ""),
            ("REQ-0016", "Reemplazar notebook por batería degradada", "La autonomía del equipo es menor a treinta minutos.", "request", "Hardware", "medium", "assigned", "solicitante", "tecnico.ana", "NB-002", 6, None, "El informe de batería indica una capacidad actual muy inferior a la de diseño.", "", ""),
            ("REQ-0017", "Configurar firma de correo", "Actualizar la firma con los datos del área.", "request", "Correo y colaboración", "low", "resolved", "solicitante", "tecnico.martin", "PC-001", 7, -5, "Solicitud estándar con plantilla aprobada.", "No aplica: solicitud de servicio.", "Se aplicó la plantilla y se comprobó el formato en un mensaje de prueba."),
            ("INC-0018", "Sin conexión en puesto de depósito", "El equipo no obtiene dirección IP y no accede a los sistemas.", "incident", "Red y conectividad", "high", "open", "solicitante", None, "PC-003", 3, None, "", "", ""),
        )

        tickets = {}
        for definition in definitions:
            (
                code, title, description, ticket_type, category_name, priority,
                status, requester_name, assignee_name, asset_tag, age_days,
                resolved_days, diagnosis, root_cause, resolution,
            ) = definition
            created_at = now - timedelta(days=age_days)
            due_at = created_at + timedelta(hours=Ticket.SLA_HOURS[priority])
            resolved_at = (
                now + timedelta(days=resolved_days) if resolved_days is not None else None
            )
            closed_at = resolved_at if status == Ticket.Status.CLOSED else None
            ticket, _ = Ticket.objects.update_or_create(
                code=code,
                defaults={
                    "title": title,
                    "description": description,
                    "ticket_type": ticket_type,
                    "category": categories[category_name],
                    "priority": priority,
                    "status": status,
                    "requester": users[requester_name],
                    "assignee": users.get(assignee_name),
                    "asset": assets.get(asset_tag),
                    "diagnosis": diagnosis,
                    "root_cause": root_cause,
                    "resolution": resolution,
                    "due_at": due_at,
                    "resolved_at": resolved_at,
                    "closed_at": closed_at,
                },
            )
            Ticket.objects.filter(pk=ticket.pk).update(
                created_at=created_at,
                updated_at=resolved_at or created_at + timedelta(hours=2),
            )
            ticket.refresh_from_db()
            tickets[code] = ticket
        return tickets

    def _seed_activities(self, users, tickets):
        definitions = (
            ("INC-0001", "tecnico.ana", "diagnosis", "Se verificó el bloqueo de la cuenta y la identidad de la persona solicitante."),
            ("INC-0001", "tecnico.ana", "comment", "Acceso recuperado y recomendaciones comunicadas."),
            ("INC-0002", "tecnico.martin", "diagnosis", "La impresora responde al ping; se revisó la cola de trabajos."),
            ("INC-0003", "tecnico.ana", "diagnosis", "Se adjuntó el detalle de ocupación del disco y carpetas de mayor tamaño."),
            ("INC-0004", "tecnico.martin", "assignment", "Ticket crítico tomado para validar la configuración DNS."),
            ("INC-0005", "tecnico.martin", "comment", "Pendiente de una medición adicional fuera del horario de mayor uso."),
            ("INC-0008", "tecnico.ana", "diagnosis", "El adjunto no fue ejecutado; se registraron remitente y dominio para revisión."),
            ("INC-0009", "tecnico.martin", "diagnosis", "Se comparó el tamaño del papel configurado con el rollo instalado."),
            ("INC-0010", "tecnico.ana", "comment", "Se indicó no utilizar el equipo hasta completar el respaldo preventivo."),
            ("INC-0011", "tecnico.martin", "comment", "Prueba remota exitosa luego de renovar el perfil."),
            ("REQ-0014", "tecnico.martin", "comment", "Cuenta principal creada; se espera confirmación del responsable del área."),
            ("REQ-0016", "tecnico.ana", "diagnosis", "Capacidad máxima observada por debajo del 35 % de la capacidad de diseño."),
            ("INC-0018", "solicitante", "comment", "El indicador de red del puesto permanece apagado."),
        )
        for code, author_name, activity_type, message in definitions:
            TicketActivity.objects.get_or_create(
                ticket=tickets[code],
                author=users[author_name],
                activity_type=activity_type,
                message=message,
                defaults={"old_value": "", "new_value": ""},
            )

    def _seed_articles(self, users, categories, tickets):
        definitions = (
            ("Desbloqueo seguro de una cuenta", "desbloqueo-seguro-cuenta", "Accesos y cuentas", "Validaciones mínimas antes de recuperar el acceso de un usuario.", "1. Confirmar la identidad por el procedimiento autorizado.\n2. Revisar el motivo del bloqueo.\n3. Desbloquear la cuenta sin solicitar la contraseña.\n4. Pedir al usuario que pruebe el acceso.\n5. Registrar el resultado y recomendar una contraseña única.", "published", "tecnico.ana", ("INC-0001",)),
            ("Cola de impresión detenida", "cola-impresion-detenida", "Impresión", "Diagnóstico básico cuando una impresora de red figura sin conexión.", "1. Comprobar alimentación y conectividad.\n2. Verificar respuesta por red.\n3. Revisar trabajos con error.\n4. Reiniciar únicamente la cola afectada.\n5. Imprimir una página de prueba y documentar el resultado.", "published", "tecnico.martin", ("INC-0002",)),
            ("Diagnóstico de poco espacio en Windows", "diagnostico-poco-espacio-windows", "Hardware", "Reunir evidencia antes de liberar espacio de almacenamiento.", "1. Registrar capacidad total y disponible.\n2. Identificar carpetas de mayor tamaño con herramientas aprobadas.\n3. No eliminar archivos personales sin autorización.\n4. Revisar temporales y políticas de retención.\n5. Documentar el espacio recuperado.", "published", "tecnico.ana", ("INC-0003",)),
            ("Comprobaciones básicas de DNS", "comprobaciones-basicas-dns", "Red y conectividad", "Distinguir una falla de nombres de una pérdida general de conectividad.", "1. Registrar la configuración IP.\n2. Probar la puerta de enlace.\n3. Comparar acceso por IP y por nombre.\n4. Consultar el servidor DNS configurado.\n5. Escalar si la respuesta no coincide con la configuración esperada.", "published", "tecnico.martin", ("INC-0004", "INC-0018")),
            ("Reporte inicial de correo sospechoso", "reporte-inicial-correo-sospechoso", "Seguridad", "Qué datos preservar sin interactuar con enlaces o adjuntos.", "No abrir enlaces ni adjuntos. Registrar remitente, asunto y hora. Usar el canal interno de reporte y seguir las instrucciones del equipo responsable. Si hubo interacción, informarlo con claridad y desconectar el equipo de la red solo cuando el procedimiento lo indique.", "published", "tecnico.ana", ("INC-0008",)),
            ("Revisión de un perfil VPN", "revision-perfil-vpn", "Red y conectividad", "Puntos de control ante un perfil remoto desactualizado.", "Confirmar conexión a Internet, fecha y hora del equipo, versión del cliente y dirección configurada. Comparar el perfil con la fuente oficial. No desactivar controles de seguridad para forzar la conexión.", "published", "tecnico.martin", ("INC-0011",)),
            ("Preparación de accesos para una incorporación", "preparacion-accesos-incorporacion", "Accesos y cuentas", "Lista de verificación para altas con permisos mínimos.", "Validar la solicitud y su aprobación, crear la identidad, aplicar permisos de mínimo privilegio, registrar vencimientos cuando correspondan y solicitar una prueba de acceso. Los permisos excepcionales deben quedar justificados.", "draft", "tecnico.martin", ("REQ-0014",)),
            ("Recolección de diagnóstico con PowerShell", "recoleccion-diagnostico-powershell", "Solicitudes generales", "Uso responsable del script incluido en SoporteLab.", "Ejecutar tools/Get-SystemDiagnostic.ps1 sin elevación. Revisar el JSON antes de adjuntarlo porque puede incluir nombres de equipo, usuario, dominio y direcciones IP. El script reúne información; no aplica correcciones ni cambia la configuración.", "published", "tecnico.ana", ("INC-0003", "INC-0004")),
        )

        for (
            title, slug, category_name, summary, content, status, author_name,
            related_codes,
        ) in definitions:
            article, _ = KnowledgeArticle.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": categories[category_name],
                    "summary": summary,
                    "content": content,
                    "status": status,
                    "author": users[author_name],
                },
            )
            article.related_tickets.set(tickets[code] for code in related_codes)
