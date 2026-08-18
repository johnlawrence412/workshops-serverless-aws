# Costos y Optimización de la aplicación Workshops

## 1. Descripción

La aplicación Workshops utiliza una arquitectura serverless en Amazon Web Services (AWS).

Este enfoque permite reducir costos operativos debido a que la mayoría de los servicios utilizados funcionan bajo modelos de pago por uso, evitando mantener servidores tradicionales encendidos permanentemente.

El proyecto también utiliza mecanismos de control como AWS Budgets y etiquetas de recursos para facilitar el seguimiento del consumo.

---

## 2. Servicios principales

Los principales servicios utilizados son:

- Amazon S3
- Amazon CloudFront
- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- Amazon Cognito
- Amazon EventBridge
- EventBridge Scheduler
- Amazon SNS
- Amazon SQS
- Amazon CloudWatch
- AWS X-Ray
- AWS WAF
- AWS CloudFormation
- AWS SAM

---

## 3. Estimación general

El proyecto fue diseñado para un escenario académico y de bajo volumen de tráfico.

La estimación general de consumo puede clasificarse de la siguiente manera:

| Servicio | Consumo esperado | Principal factor de costo |
|---|---|---|
| Amazon S3 | Bajo | Almacenamiento y solicitudes |
| CloudFront | Bajo | Transferencia de datos y solicitudes |
| API Gateway | Bajo | Cantidad de solicitudes |
| AWS Lambda | Bajo | Invocaciones y tiempo de ejecución |
| DynamoDB | Bajo | Lecturas y escrituras |
| Cognito | Bajo | Usuarios activos |
| EventBridge | Bajo | Eventos procesados |
| SNS | Bajo | Notificaciones enviadas |
| SQS | Muy bajo | Solicitudes y mensajes |
| CloudWatch | Bajo | Logs, métricas y alarmas |
| X-Ray | Bajo | Trazas procesadas |
| AWS WAF | Controlado | Web ACL, reglas y solicitudes |
| CloudFormation / SAM | Bajo | Administración de infraestructura |

En un entorno académico con pocas solicitudes, el consumo variable de los componentes serverless debería mantenerse reducido.

Los costos reales dependen del número de usuarios, solicitudes, volumen de transferencia de datos, cantidad de logs y tiempo de ejecución de las funciones.

---

## 4. Amazon S3

Amazon S3 almacena el frontend estático de la aplicación.

Los principales factores que pueden generar costos son:

- Cantidad de datos almacenados.
- Número de solicitudes.
- Transferencia de datos.
- Versiones de objetos, si se habilitan.

El frontend del proyecto está compuesto principalmente por archivos HTML y recursos estáticos, por lo que su tamaño es reducido.

### Optimización

Para reducir costos:

- Eliminar archivos que ya no sean necesarios.
- Evitar almacenar múltiples versiones innecesarias.
- Utilizar CloudFront para distribuir el contenido.
- Mantener únicamente los archivos requeridos por la aplicación.

---

## 5. Amazon CloudFront

CloudFront distribuye el frontend y también dirige las solicitudes `/api/*` hacia API Gateway.

Los costos están relacionados principalmente con:

- Transferencia de datos.
- Número de solicitudes.
- Ubicación de los usuarios.
- Configuración de caché.

### Optimización

Se recomienda:

- Utilizar caché para archivos estáticos.
- Configurar correctamente los TTL.
- Evitar invalidaciones innecesarias.
- Comprimir contenido cuando sea posible.
- Mantener archivos estáticos pequeños.

---

## 6. Amazon API Gateway

API Gateway recibe las solicitudes REST de la aplicación.

Ejemplos:

```text
GET /workshops
POST /workshops
PUT /workshops/{id}
DELETE /workshops/{id}
POST /workshops/{id}/register
```

Su consumo aumenta principalmente según el número de solicitudes recibidas.

### Optimización

Para reducir costos:

- Evitar llamadas innecesarias desde el frontend.
- Utilizar CloudFront como punto de acceso.
- Implementar paginación.
- Validar solicitudes antes de ejecutar Lambda.
- Utilizar throttling para limitar tráfico excesivo.

---

## 7. AWS Lambda

AWS Lambda ejecuta la lógica del backend.

El costo depende principalmente de:

- Número de invocaciones.
- Memoria asignada.
- Duración de ejecución.

Función principal:

```text
workshops-api-dev
```

### Optimización

Se recomienda:

- Mantener el código eficiente.
- Evitar operaciones innecesarias.
- Reducir tiempos de ejecución.
- Asignar únicamente la memoria necesaria.
- Utilizar Request Validator en API Gateway para evitar ejecutar Lambda con solicitudes inválidas.
- Supervisar la métrica Duration en CloudWatch.

---

## 8. Amazon DynamoDB

DynamoDB almacena talleres y registros de estudiantes.

La aplicación utiliza claves:

```text
PK
SK
```

y un índice secundario global para facilitar consultas.

El consumo depende de:

- Número de lecturas.
- Número de escrituras.
- Tamaño de los datos.
- Índices secundarios.

### Optimización

Se recomienda:

- Utilizar consultas por PK/SK.
- Evitar escaneos completos de tabla.
- Utilizar paginación.
- Mantener los elementos pequeños.
- Crear únicamente los índices necesarios.
- Utilizar capacidad bajo demanda cuando sea adecuada al nivel de tráfico.

---

## 9. Amazon Cognito

Cognito administra la autenticación de usuarios.

La aplicación utiliza grupos:

```text
Admin
Student
```

El consumo depende principalmente del número de usuarios activos y las funciones adicionales utilizadas.

### Optimización

Para un proyecto académico, mantener únicamente los usuarios necesarios para las pruebas.

También se recomienda eliminar usuarios de prueba que ya no sean utilizados.

---

## 10. Amazon EventBridge

EventBridge administra eventos de la aplicación.

Bus:

```text
workshops-events-dev
```

Evento utilizado:

```text
STUDENT_REGISTERED
```

Los costos dependen principalmente del número de eventos procesados.

### Optimización

- Publicar únicamente eventos necesarios.
- Utilizar patrones de eventos específicos.
- Evitar reglas duplicadas.
- Eliminar reglas de prueba que ya no sean utilizadas.

---

## 11. EventBridge Scheduler

Scheduler se utiliza para programar recordatorios antes de los talleres.

Ejemplo:

```text
workshop-789-reminder-dev
```

### Optimización

- Eliminar schedules antiguos.
- Configurar ejecuciones únicas cuando corresponda.
- Evitar crear recordatorios duplicados.

---

## 12. Amazon SNS

SNS se utiliza para enviar notificaciones relacionadas con talleres, eventos y alarmas.

Topic:

```text
workshops-notifications-dev
```

### Optimización

- Mantener únicamente las suscripciones necesarias.
- Evitar notificaciones repetidas.
- Eliminar topics que ya no se utilicen.
- Utilizar filtros cuando existan múltiples tipos de eventos.

---

## 13. Amazon SQS

La cola:

```text
workshops-events-dlq-dev
```

funciona como Dead Letter Queue.

Normalmente debería recibir poco o ningún tráfico mientras la aplicación funcione correctamente.

### Optimización

- Revisar periódicamente la DLQ.
- Resolver la causa de los mensajes fallidos.
- Eliminar mensajes antiguos después de analizarlos.
- Mantener una política de retención apropiada.

---

## 14. Amazon CloudWatch

CloudWatch puede generar costos mediante:

- Logs almacenados.
- Métricas.
- Alarmas.
- Dashboards.
- Consultas de logs.

La aplicación utiliza una retención de:

```text
30 días
```

para los principales grupos de registros.

### Optimización

Se recomienda:

- Mantener políticas de retención.
- Evitar almacenar logs indefinidamente.
- No habilitar logging excesivamente detallado sin necesidad.
- Eliminar dashboards de prueba.
- Mantener únicamente alarmas útiles.
- Evitar registrar información innecesaria.

---

## 15. AWS X-Ray

X-Ray proporciona trazabilidad de las solicitudes.

El consumo depende del número de trazas procesadas y almacenadas.

### Optimización

En ambientes con tráfico elevado puede utilizarse muestreo para evitar generar trazas para todas las solicitudes.

---

## 16. AWS WAF

AWS WAF protege la distribución de CloudFront.

El costo depende de la configuración del Web ACL, las reglas utilizadas y el número de solicitudes analizadas.

### Optimización

- Mantener únicamente reglas necesarias.
- Evitar crear Web ACL duplicados.
- Revisar periódicamente las reglas.
- Eliminar configuraciones de prueba que ya no sean necesarias.

---

## 17. Infraestructura como Código

AWS SAM y CloudFormation permiten administrar los recursos mediante código.

Stacks:

```text
workshops-iac-dev
workshops-iac-prod
```

Una ventaja importante es que los stacks permiten identificar fácilmente qué recursos pertenecen a cada ambiente.

### Optimización

Cuando un ambiente ya no sea necesario se puede eliminar su stack para evitar mantener recursos innecesarios.

Antes de eliminar un stack se debe verificar que no contenga información que deba conservarse.

---

## 18. Separación DEV y PROD

Los ambientes están identificados mediante:

```text
Env = dev
Env = prod
```

Esto facilita identificar qué recursos pertenecen a desarrollo y cuáles pertenecen a producción.

El entorno de desarrollo debe utilizarse para realizar pruebas antes de modificar producción.

### Reducción de costos

Si el proyecto deja de utilizarse:

- Eliminar recursos temporales de dev.
- Mantener únicamente los recursos requeridos para la entrega.
- Eliminar stacks de prueba duplicados.
- Revisar funciones Lambda adicionales.
- Revisar tablas DynamoDB adicionales.
- Revisar APIs duplicadas.

---

## 19. Etiquetas de costos

Los principales recursos utilizan:

```text
Project = Workshops
```

y:

```text
Env = dev
```

o:

```text
Env = prod
```

Estas etiquetas permiten:

- Identificar recursos.
- Filtrar recursos del proyecto.
- Separar ambientes.
- Facilitar análisis de costos.
- Detectar recursos olvidados.

---

## 20. AWS Budgets

Se configuró AWS Budgets como mecanismo preventivo de control de costos.

Presupuesto:

```text
Workshops-Zero-Spend-Budget
```

El objetivo es recibir alertas cuando se detecte consumo asociado al proyecto.

AWS Budgets permite supervisar el gasto y actuar antes de que se produzca un aumento inesperado.

---

## 21. Estrategias para reducir costos

Las principales estrategias aplicadas o recomendadas son:

1. Utilizar arquitectura serverless.
2. Evitar servidores EC2 permanentes.
3. Utilizar DynamoDB bajo demanda.
4. Mantener el frontend estático en S3.
5. Distribuir el frontend mediante CloudFront.
6. Configurar retención de CloudWatch Logs.
7. Eliminar recursos de prueba.
8. Utilizar etiquetas `Project` y `Env`.
9. Mantener AWS Budgets activo.
10. Utilizar Request Validator para evitar invocaciones Lambda innecesarias.
11. Utilizar paginación en consultas.
12. Revisar periódicamente la DLQ.
13. Evitar reglas EventBridge duplicadas.
14. Eliminar schedules vencidos.
15. Revisar funciones y APIs duplicadas.
16. Deshabilitar o eliminar ambientes que ya no sean necesarios.

---

## 22. Recursos que deben revisarse al finalizar el proyecto

Al terminar las pruebas se recomienda revisar:

```text
Lambda
API Gateway
DynamoDB
S3
CloudFront
Cognito
EventBridge
EventBridge Scheduler
SNS
SQS
CloudWatch
X-Ray
WAF
CloudFormation
```

El objetivo es detectar recursos de laboratorio o pruebas que hayan quedado activos accidentalmente.

---

## 23. Recursos que no requieren servidores permanentes

La arquitectura evita utilizar servidores tradicionales para el backend.

El flujo principal utiliza:

```text
CloudFront
     |
     v
API Gateway
     |
     v
AWS Lambda
     |
     v
DynamoDB
```

Esto permite que los recursos de procesamiento sean utilizados principalmente cuando existen solicitudes.

---

## 24. Estimación por escenario

### Escenario académico

Características:

```text
Pocos usuarios
Pocas solicitudes diarias
Pocas notificaciones
Base de datos pequeña
Frontend estático pequeño
```

Costo esperado:

```text
Bajo
```

---

### Escenario de mayor uso

Si la aplicación aumenta su cantidad de usuarios, los componentes que deben supervisarse principalmente son:

```text
CloudFront Data Transfer
API Gateway Requests
Lambda Invocations
Lambda Duration
DynamoDB Reads/Writes
CloudWatch Logs
AWS WAF Requests
SNS Notifications
```

El monitoreo mediante CloudWatch y AWS Budgets permitirá identificar estos incrementos.

---

## 25. Cost Governance

La estrategia de gobierno de costos del proyecto utiliza:

```text
AWS Budgets
+
Etiquetas Project/Env
+
Arquitectura Serverless
+
Retención de Logs
+
Eliminación de recursos innecesarios
```

Esto proporciona mayor control sobre los recursos desplegados y facilita detectar gastos inesperados.

---

## 26. Recomendaciones finales

Para mantener los costos controlados:

- Revisar AWS Budgets periódicamente.
- Mantener las alertas por correo activas.
- Revisar el Billing Dashboard.
- Utilizar etiquetas en todos los recursos posibles.
- Eliminar recursos de prueba.
- Revisar CloudWatch Logs.
- Evitar datos innecesarios en DynamoDB.
- Eliminar objetos S3 obsoletos.
- Revisar reglas WAF.
- Eliminar schedules vencidos.
- Verificar que no existan stacks temporales.
- Eliminar recursos una vez finalizado el proyecto si ya no serán utilizados.

---

## 27. Resumen

Workshops fue diseñado utilizando una arquitectura serverless con el objetivo de mantener un modelo de costos flexible y basado principalmente en el uso.

AWS Lambda, API Gateway, DynamoDB, S3 y otros servicios administrados evitan la necesidad de mantener servidores tradicionales encendidos permanentemente.

AWS Budgets, las etiquetas `Project` y `Env`, la retención de CloudWatch Logs y la revisión periódica de recursos proporcionan mecanismos adicionales para controlar los gastos.

La combinación de estas estrategias permite mantener el proyecto organizado, identificar consumo inesperado y reducir recursos innecesarios.
