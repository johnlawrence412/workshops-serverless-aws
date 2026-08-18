# API REST - Workshops

## 1. Descripción

La aplicación Workshops utiliza Amazon API Gateway para exponer una API REST que permite consultar, crear, actualizar y eliminar talleres, además de registrar estudiantes.

La lógica de negocio es procesada mediante AWS Lambda y los datos son almacenados en Amazon DynamoDB.

Las operaciones protegidas utilizan Amazon Cognito como mecanismo de autenticación y autorización.

---

## 2. Endpoints base

### API mediante Amazon CloudFront

```text
https://d1z6gu4fgp8a7e.cloudfront.net/api
```

Ejemplo:

```text
https://d1z6gu4fgp8a7e.cloudfront.net/api/workshops
```

### API Gateway directa - entorno dev

```text
https://r4w74x1kvd.execute-api.us-east-1.amazonaws.com/dev
```

---

## 3. Contrato de la API

| Método | Ruta | Autenticación | Descripción |
|---|---|---|---|
| GET | `/workshops` | Pública | Obtiene la lista de talleres |
| GET | `/workshops/{id}` | Pública | Obtiene un taller por su identificador |
| POST | `/workshops` | Cognito / Admin | Crea un nuevo taller |
| PUT | `/workshops/{id}` | Cognito / Admin | Actualiza un taller existente |
| DELETE | `/workshops/{id}` | Cognito / Admin | Elimina un taller |
| POST | `/workshops/{id}/register` | Cognito / Student | Registra un estudiante en un taller |

---

## 4. Autenticación

Las operaciones protegidas utilizan Amazon Cognito.

El cliente debe enviar el token correspondiente mediante el encabezado:

```http
Authorization: Bearer <JWT_TOKEN>
```

API Gateway utiliza el authorizer:

```text
WorkshopsCognitoAuthorizer
```

Los roles principales de la aplicación son:

```text
Admin
Student
```

Las operaciones administrativas requieren que el usuario autenticado tenga permisos de administrador.

---

# 5. GET /workshops

Obtiene la lista de talleres disponibles.

## Solicitud

```http
GET /workshops
```

No requiere cuerpo de solicitud.

## Ejemplo mediante CloudFront

```text
https://d1z6gu4fgp8a7e.cloudfront.net/api/workshops
```

## Respuesta de ejemplo

```json
{
  "items": [],
  "count": 0,
  "nextToken": null,
  "lastEvaluatedKey": null
}
```

La API utiliza un formato preparado para paginación mediante `nextToken` y `lastEvaluatedKey`.

## Código esperado

```text
200 OK
```

---

# 6. GET /workshops/{id}

Obtiene la información de un taller específico.

## Solicitud

```http
GET /workshops/123
```

## Respuesta de ejemplo

```json
{
  "workshopId": "123",
  "name": "Taller Serverless AWS",
  "description": "Introducción al desarrollo serverless en AWS",
  "category": "Tecnología",
  "location": "Virtual",
  "startAt": "2026-10-10T10:00:00",
  "endAt": "2026-10-10T12:00:00",
  "status": "scheduled",
  "capacity": 30
}
```

## Códigos posibles

```text
200 OK
404 Not Found
```

---

# 7. POST /workshops

Crea un nuevo taller.

Esta operación está protegida mediante Amazon Cognito.

## Solicitud

```http
POST /workshops
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```

## Cuerpo JSON

```json
{
  "name": "Taller Serverless AWS",
  "description": "Taller sobre arquitectura serverless",
  "category": "Tecnología",
  "location": "Virtual",
  "startAt": "2026-10-10T10:00:00",
  "endAt": "2026-10-10T12:00:00",
  "status": "scheduled",
  "capacity": 30
}
```

`workshopId` puede ser gestionado por la aplicación y no es obligatorio dentro del modelo de creación.

## Modelo de validación

API Gateway utiliza el modelo:

```text
WorkshopRequest
```

Los campos obligatorios son:

```text
name
description
category
location
startAt
endAt
status
capacity
```

## Validación

El método utiliza:

```text
Request Validator = Validar cuerpo
Content-Type = application/json
Model = WorkshopRequest
```

Una solicitud inválida como:

```json
{}
```

es rechazada antes de llegar a AWS Lambda.

Respuesta comprobada:

```json
{
  "message": "Invalid request body"
}
```

Código HTTP:

```text
400 Bad Request
```

---

# 8. PUT /workshops/{id}

Actualiza la información de un taller existente.

Requiere autenticación administrativa.

## Solicitud

```http
PUT /workshops/123
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```

## Ejemplo

```json
{
  "name": "Taller Serverless AWS - Actualizado",
  "description": "Contenido actualizado del taller",
  "category": "Tecnología",
  "location": "Virtual",
  "startAt": "2026-10-10T10:00:00",
  "endAt": "2026-10-10T13:00:00",
  "status": "scheduled",
  "capacity": 40
}
```

## Códigos posibles

```text
200 OK
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
```

---

# 9. DELETE /workshops/{id}

Elimina un taller existente.

Requiere autenticación administrativa.

## Solicitud

```http
DELETE /workshops/123
Authorization: Bearer <JWT_TOKEN>
```

## Códigos posibles

```text
200 OK
401 Unauthorized
403 Forbidden
404 Not Found
```

---

# 10. POST /workshops/{id}/register

Permite que un estudiante autenticado se registre en un taller.

## Solicitud

```http
POST /workshops/789/register
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
```

La identidad del estudiante se obtiene del usuario autenticado mediante Amazon Cognito.

## Flujo

```text
Student
   |
   v
Amazon Cognito
   |
   v
API Gateway
   |
   v
AWS Lambda
   |
   v
Amazon DynamoDB
   |
   v
Amazon EventBridge
   |
   v
Amazon SNS
```

Después de registrar al estudiante, la aplicación puede generar el evento:

```text
STUDENT_REGISTERED
```

Este evento es enviado a Amazon EventBridge y posteriormente procesado para generar una notificación mediante Amazon SNS.

---

# 11. Prevención de registros duplicados

La lógica de AWS Lambda verifica si el estudiante ya se encuentra registrado en el taller.

Esto permite que la operación de registro sea idempotente y evita crear registros duplicados para el mismo usuario y taller.

---

# 12. CORS

API Gateway tiene configurado CORS para permitir solicitudes desde el frontend.

Los métodos `OPTIONS` están disponibles en las rutas correspondientes.

Entre los encabezados permitidos se encuentran:

```text
Content-Type
Authorization
X-Amz-Date
X-Api-Key
X-Amz-Security-Token
```

Los métodos permitidos incluyen:

```text
DELETE
GET
HEAD
OPTIONS
PATCH
POST
PUT
```

La configuración comprobada utiliza:

```text
Access-Control-Allow-Origin: *
```

---

# 13. Registros de acceso

API Gateway envía registros de acceso hacia Amazon CloudWatch.

Grupo de registros:

```text
/aws/apigateway/workshops-rest-api-dev-access
```

El formato registra información como:

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

Esto permite verificar las solicitudes recibidas y sus códigos de respuesta.

---

# 14. Códigos HTTP principales

| Código | Significado |
|---|---|
| 200 | Operación completada correctamente |
| 201 | Recurso creado correctamente, cuando corresponda |
| 400 | Solicitud inválida |
| 401 | Usuario no autenticado |
| 403 | Usuario autenticado sin permisos suficientes |
| 404 | Recurso no encontrado |
| 409 | Conflicto, por ejemplo registro duplicado cuando corresponda |
| 500 | Error interno del servidor |

---

# 15. OpenAPI

A continuación se presenta una versión resumida del contrato OpenAPI de la aplicación.

```yaml
openapi: 3.0.3

info:
  title: Workshops API
  version: 1.0.0
  description: API REST para la gestión de talleres de formación profesional.

servers:
  - url: https://d1z6gu4fgp8a7e.cloudfront.net/api
    description: CloudFront
  - url: https://r4w74x1kvd.execute-api.us-east-1.amazonaws.com/dev
    description: API Gateway DEV

paths:

  /workshops:

    get:
      summary: Obtener talleres
      responses:
        '200':
          description: Lista de talleres obtenida correctamente

    post:
      summary: Crear un taller
      security:
        - CognitoAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkshopRequest'
      responses:
        '200':
          description: Taller creado correctamente
        '400':
          description: Solicitud inválida
        '401':
          description: No autenticado
        '403':
          description: Acceso denegado

  /workshops/{id}:

    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string

    get:
      summary: Obtener un taller
      responses:
        '200':
          description: Taller encontrado
        '404':
          description: Taller no encontrado

    put:
      summary: Actualizar un taller
      security:
        - CognitoAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkshopRequest'
      responses:
        '200':
          description: Taller actualizado

    delete:
      summary: Eliminar un taller
      security:
        - CognitoAuth: []
      responses:
        '200':
          description: Taller eliminado

  /workshops/{id}/register:

    post:
      summary: Registrar estudiante en un taller
      security:
        - CognitoAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Registro procesado correctamente
        '400':
          description: Solicitud inválida
        '401':
          description: No autenticado

components:

  securitySchemes:

    CognitoAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:

    WorkshopRequest:
      type: object
      required:
        - name
        - description
        - category
        - location
        - startAt
        - endAt
        - status
        - capacity
      properties:

        workshopId:
          type: string

        name:
          type: string

        description:
          type: string

        category:
          type: string

        location:
          type: string

        startAt:
          type: string

        endAt:
          type: string

        status:
          type: string

        capacity:
          type: number
```

---

# 16. Resumen

La API REST de Workshops proporciona las operaciones necesarias para gestionar talleres y registros de estudiantes.

Amazon API Gateway actúa como punto de entrada del backend, Amazon Cognito protege las operaciones que requieren autenticación y AWS Lambda procesa la lógica de negocio.

La integración con Request Validator, CORS, CloudWatch Logs, DynamoDB y EventBridge permite disponer de una API segura, observable y desacoplada.
