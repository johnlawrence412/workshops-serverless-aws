# Operación y Monitoreo de la aplicación Workshops

## 1. Descripción

La operación de Workshops se apoya principalmente en Amazon CloudWatch, AWS X-Ray, Amazon SQS, Amazon EventBridge y AWS Budgets.

Estos servicios permiten supervisar la aplicación, detectar errores, revisar solicitudes, analizar trazas y responder ante fallos de procesamiento.

---

## 2. CloudWatch Logs

AWS Lambda genera registros automáticamente en Amazon CloudWatch Logs.

Grupo principal del backend:

```text
/aws/lambda/workshops-api-dev
```

También existen grupos de logs asociados a las funciones administradas mediante IaC para los ambientes dev y prod.

Los registros permiten revisar:

- Solicitudes recibidas.
- Errores de ejecución.
- Excepciones.
- Tiempos de procesamiento.
- Información útil para depuración.

---

## 3. Retención de logs

Los grupos de logs principales utilizan una política de retención de:

```text
30 días
```

Esto evita mantener registros indefinidamente y ayuda a controlar costos.

---

## 4. Access Logs de API Gateway

Amazon API Gateway envía registros de acceso a CloudWatch.

Grupo configurado:

```text
/aws/apigateway/workshops-rest-api-dev-access
```

El formato de registro incluye datos como:

```json
{
  "requestId": "$context.requestId",
  "extendedRequestId": "$context.extendedRequestId",
  "ip": "$context.identity.sourceIp",
  "requestTime": "$context.requestTime",
  "httpMethod": "$context.httpMethod",
  "resourcePath": "$context.resourcePath",
  "status": "$context.status",
  "responseLength": "$context.responseLength"
}
```

Esto permite identificar qué solicitudes llegan a la API y qué código HTTP generan.

---

## 5. Ejemplo de acceso registrado

Se verificó una solicitud real:

```text
GET /workshops
```

con estado:

```text
200
```

Esto confirmó que API Gateway está enviando correctamente los registros hacia Amazon CloudWatch.

---

## 6. CloudWatch Alarm

La aplicación utiliza una alarma para detectar errores en AWS Lambda.

Nombre:

```text
workshops-lambda-errors-dev
```

Configuración:

```text
Métrica: Errors
Función: workshops-api-dev
Estadística: Sum
Periodo: 5 minutos
Umbral: >= 1 error
Datapoints: 1 de 1
```

Cuando la alarma detecta uno o más errores, puede generar una notificación mediante Amazon SNS.

---

## 7. Amazon SNS

Topic utilizado para notificaciones:

```text
workshops-notifications-dev
```

SNS se utiliza para:

- Notificaciones de eventos.
- Recordatorios programados.
- Notificaciones de alarmas.
- Comunicación por correo electrónico.

---

## 8. Dashboard de CloudWatch

Se creó un dashboard para visualizar el estado de la función Lambda.

Nombre:

```text
workshops-monitoring-dev
```

El dashboard incluye métricas como:

- Invocations.
- Errors.
- Duration.

Esto permite revisar rápidamente el comportamiento del backend.

---

## 9. AWS X-Ray

AWS X-Ray está habilitado para proporcionar trazabilidad en el backend.

Permite visualizar el flujo de una solicitud entre los distintos componentes y analizar:

- Latencia.
- Errores.
- Dependencias.
- Tiempo de ejecución.

Se verificó el mapa de trazas correspondiente a:

```text
Cliente
   |
   v
AWS Lambda
   |
   v
workshops-api-dev
```

---

## 10. Amazon SQS DLQ

La aplicación utiliza una Dead Letter Queue para almacenar eventos que no puedan procesarse correctamente después de los reintentos.

Nombre:

```text
workshops-events-dlq-dev
```

La DLQ está asociada al procesamiento de eventos del proyecto.

Su objetivo es evitar la pérdida silenciosa de eventos y permitir análisis posteriores.

---

## 11. EventBridge y reintentos

Amazon EventBridge procesa eventos generados por la aplicación.

Bus principal:

```text
workshops-events-dev
```

Regla utilizada:

```text
student-registration-notification-dev
```

Evento principal:

```text
STUDENT_REGISTERED
```

EventBridge aplica políticas de reintento antes de enviar un evento fallido a la DLQ.

---

## 12. Flujo de error

El flujo general ante un fallo puede representarse así:

```text
Evento
  |
  v
EventBridge
  |
  v
Intento de entrega
  |
  +---- éxito ----> SNS
  |
  +---- fallo ----> Reintentos
                     |
                     v
                   SQS DLQ
```

---

## 13. Revisión de la DLQ

Para revisar mensajes fallidos:

```text
AWS Console
→ Amazon SQS
→ workshops-events-dlq-dev
```

Si existen mensajes, se debe analizar:

- Fecha.
- Contenido del evento.
- Recurso de origen.
- Motivo del fallo.
- Estado del destino.

Después de corregir la causa del error, el evento puede reprocesarse manualmente si corresponde.

---

## 14. EventBridge Scheduler

Se utiliza EventBridge Scheduler para ejecutar recordatorios programados.

Ejemplo:

```text
workshop-789-reminder-dev
```

El recordatorio envía un mensaje antes del inicio del taller mediante Amazon SNS.

Este mecanismo permite automatizar tareas basadas en fecha y hora.

---

## 15. Request Validator

API Gateway valida el cuerpo de las solicitudes antes de invocar AWS Lambda.

Modelo:

```text
WorkshopRequest
```

Una prueba utilizando:

```json
{}
```

produjo:

```text
HTTP 400
```

con mensaje:

```json
{
  "message": "Invalid request body"
}
```

Esto permite reducir solicitudes inválidas y disminuir procesamiento innecesario en Lambda.

---

## 16. Throttling

La etapa `dev` de API Gateway dispone de límites de tráfico.

Valores observados:

```text
Rate: 10000 solicitudes por segundo
Burst: 5000 solicitudes
```

Estos límites ayudan a proteger la API frente a tráfico excesivo.

---

## 17. CORS

CORS está configurado en API Gateway mediante métodos `OPTIONS`.

Esto permite que el frontend servido por CloudFront pueda comunicarse correctamente con la API.

Los encabezados permiten, entre otros:

```text
Content-Type
Authorization
X-Amz-Date
X-Api-Key
X-Amz-Security-Token
```

---

## 18. AWS WAF

AWS WAF está asociado a la distribución de Amazon CloudFront.

El Web ACL protege el frontend mediante reglas de filtrado de solicitudes.

Esto permite reducir el riesgo de tráfico web malicioso antes de que llegue a la aplicación.

---

## 19. Estado general del sistema

Ante un problema, se recomienda revisar en este orden:

1. CloudFront.
2. API Gateway.
3. CloudWatch Access Logs.
4. AWS Lambda.
5. CloudWatch Logs de Lambda.
6. DynamoDB.
7. EventBridge.
8. SNS.
9. SQS DLQ.
10. Alarmas.
11. X-Ray.

Este orden permite seguir el recorrido lógico de una solicitud.

---

## 20. Runbook - Error HTTP 500

Si la aplicación devuelve:

```text
HTTP 500
```

se recomienda:

1. Revisar CloudWatch Logs de la función Lambda.
2. Buscar excepciones recientes.
3. Confirmar acceso a DynamoDB.
4. Verificar variables de entorno.
5. Revisar permisos IAM.
6. Comprobar la alarma de errores.
7. Utilizar X-Ray para identificar el punto de fallo.
8. Corregir el problema.
9. Ejecutar pruebas.
10. Volver a desplegar.

---

## 21. Runbook - Error de autenticación

Si el usuario recibe:

```text
401 Unauthorized
```

o:

```text
403 Forbidden
```

se debe revisar:

1. Que el usuario exista en Cognito.
2. Que el token JWT sea válido.
3. Que el token no haya expirado.
4. Que API Gateway utilice el authorizer correcto.
5. Que el usuario pertenezca al grupo adecuado.
6. Que la ruta requiera el rol correcto.

---

## 22. Runbook - Error de EventBridge

Si una notificación no se genera:

1. Revisar que Lambda haya publicado el evento.
2. Confirmar el bus `workshops-events-dev`.
3. Revisar la regla `student-registration-notification-dev`.
4. Confirmar el patrón `STUDENT_REGISTERED`.
5. Revisar métricas de EventBridge.
6. Confirmar el destino SNS.
7. Revisar la DLQ.

---

## 23. Runbook - Mensajes en DLQ

Si aparecen mensajes en:

```text
workshops-events-dlq-dev
```

se debe:

1. Revisar el contenido del mensaje.
2. Identificar el recurso que falló.
3. Consultar CloudWatch Logs.
4. Corregir el problema.
5. Confirmar permisos IAM.
6. Confirmar disponibilidad del destino.
7. Reprocesar el evento si es necesario.

---

## 24. Backup de DynamoDB

Para recuperación de datos se recomienda utilizar mecanismos de respaldo de Amazon DynamoDB.

Entre las opciones disponibles se encuentran:

- Backups bajo demanda.
- Point-in-time recovery, si se habilita.

Para un respaldo manual:

```text
AWS Console
→ DynamoDB
→ Tables
→ workshops
→ Backups
→ Create backup
```

Nombre sugerido:

```text
workshops-backup-YYYY-MM-DD
```

---

## 25. Restore de DynamoDB

Para recuperar una tabla desde un backup:

```text
AWS Console
→ DynamoDB
→ Backups
→ Seleccionar backup
→ Restore
```

La restauración crea una nueva tabla a partir del respaldo seleccionado.

Antes de utilizarla en producción, se debe validar:

- Cantidad de registros.
- Claves PK y SK.
- Índices.
- Permisos IAM.
- Configuración de la aplicación.

---

## 26. Operación de Lambda

Para revisar la función principal:

```text
AWS Console
→ Lambda
→ workshops-api-dev
```

Se recomienda comprobar:

- Estado.
- Última modificación.
- Variables de entorno.
- Permisos.
- Logs.
- Versiones.
- Alias.
- Métricas.
- Trazabilidad.

---

## 27. Canary y rollback

La aplicación utiliza versiones y alias de Lambda para despliegues graduales.

Distribución comprobada:

```text
Versión estable: 90 %
Nueva versión:   10 %
```

Si la nueva versión presenta errores:

1. Revisar CloudWatch.
2. Identificar el aumento de errores.
3. Modificar el alias.
4. Redirigir el 100 % del tráfico a la versión estable.
5. Corregir la nueva versión.
6. Ejecutar pruebas nuevamente.
7. Volver a realizar el despliegue gradual.

---

## 28. Verificación funcional

Una prueba sencilla del backend puede realizarse mediante:

```text
https://d1z6gu4fgp8a7e.cloudfront.net/api/workshops
```

Una respuesta válida puede ser:

```json
{
  "items": [],
  "count": 0,
  "nextToken": null,
  "lastEvaluatedKey": null
}
```

Esto confirma la comunicación:

```text
CloudFront
→ API Gateway
→ Lambda
→ DynamoDB
```

---

## 29. AWS Budgets

Se utiliza AWS Budgets para supervisar el gasto del proyecto.

Presupuesto configurado:

```text
Workshops-Zero-Spend-Budget
```

Las alertas permiten detectar consumo inesperado y actuar antes de que los costos aumenten.

---

## 30. Etiquetas

Los recursos principales utilizan etiquetas:

```text
Project = Workshops
Env = dev
```

o:

```text
Project = Workshops
Env = prod
```

Esto facilita:

- Búsqueda de recursos.
- Organización.
- Seguimiento operativo.
- Análisis de costos.
- Separación entre ambientes.

---

## 31. Recomendaciones de operación

Se recomienda:

- Revisar periódicamente las alarmas.
- Mantener controlada la retención de logs.
- Revisar mensajes de la DLQ.
- Comprobar AWS Budgets.
- Mantener los permisos IAM mínimos.
- Probar los cambios primero en dev.
- Utilizar despliegue gradual para cambios importantes.
- Mantener actualizada la documentación.
- Revisar logs después de cada despliegue.
- Eliminar recursos de prueba que ya no sean necesarios.

---

## 32. Resumen

La operación de Workshops se basa en mecanismos de monitoreo, trazabilidad y tolerancia a fallos proporcionados por AWS.

CloudWatch permite supervisar logs, métricas y alarmas; X-Ray ayuda a analizar trazas; SQS funciona como DLQ; EventBridge gestiona reintentos y eventos; y AWS Budgets ayuda a controlar costos.

Estos mecanismos permiten detectar problemas rápidamente, analizar su causa y aplicar acciones correctivas de forma controlada.
