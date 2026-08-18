# Workshops Serverless AWS

Aplicación web serverless para la gestión de talleres de formación profesional, desarrollada utilizando servicios de Amazon Web Services (AWS).

El proyecto permite consultar talleres, crear y administrar actividades, registrar estudiantes y gestionar usuarios mediante autenticación y autorización basada en roles.

---

## Arquitectura

La solución utiliza una arquitectura serverless compuesta principalmente por:

- Amazon S3 para alojamiento del frontend.
- Amazon CloudFront como CDN y punto de acceso público.
- Amazon API Gateway para exponer la API REST.
- AWS Lambda para la lógica de negocio.
- Amazon DynamoDB para almacenamiento de talleres y registros.
- Amazon Cognito para autenticación y autorización.
- Amazon EventBridge para gestión de eventos.
- Amazon SNS para notificaciones.
- Amazon SQS como Dead Letter Queue (DLQ).
- AWS WAF para protección del frontend.
- Amazon CloudWatch para logs, métricas, alarmas y monitoreo.
- AWS X-Ray para trazabilidad.
- AWS SAM para Infraestructura como Código.
- GitHub Actions para CI/CD.

---

## URLs públicas

### Frontend

https://d1z6gu4fgp8a7e.cloudfront.net/

### API mediante CloudFront

https://d1z6gu4fgp8a7e.cloudfront.net/api/workshops

---

## Repositorio

https://github.com/johnlawrence412/workshops-serverless-aws

---

## Estructura del proyecto

```text
workshops-serverless-aws/
│
├── .github/
│   └── workflows/
│
├── frontend/
│   └── index.html
│
├── src/
│   └── Código de AWS Lambda
│
├── tests/
│   └── Pruebas automatizadas
│
├── docs/
│   └── Documentación del proyecto
│
├── template.yaml
├── samconfig.toml
└── README.md

Funcionalidades principales
Consulta de talleres disponibles.
Consulta individual de talleres.
Creación de talleres por administradores.
Actualización de talleres.
Eliminación de talleres.
Registro de estudiantes en talleres.
Prevención de registros duplicados.
Consulta de los talleres registrados por cada estudiante.
Autenticación mediante Amazon Cognito.
Roles de administrador y estudiante.
Notificaciones mediante Amazon SNS.
Eventos mediante Amazon EventBridge.
Recordatorios programados.
Manejo de eventos fallidos mediante SQS DLQ.
Seguridad

La aplicación incorpora diferentes mecanismos de seguridad:

Autenticación con Amazon Cognito.
Cognito Authorizer en API Gateway.
Políticas IAM con principio de mínimo privilegio.
Protección mediante AWS WAF.
CORS configurado en API Gateway.
Validación de solicitudes mediante Request Validator.
HTTPS mediante Amazon CloudFront.
Bucket S3 privado servido mediante CloudFront.
Observabilidad

El proyecto utiliza:

Amazon CloudWatch Logs.
Access Logs de API Gateway.
Alarmas de CloudWatch.
Dashboard de monitoreo.
AWS X-Ray.
Retención de logs.
Métricas de AWS Lambda.
AWS Budgets para control de costos.
Infraestructura como Código

La infraestructura está definida mediante AWS Serverless Application Model (AWS SAM).

El archivo principal de infraestructura es:

template.yaml

La configuración de despliegue se encuentra en:

samconfig.toml

Se implementaron ambientes separados de desarrollo y producción.

CI/CD

El repositorio utiliza GitHub Actions para automatizar:

Validación del código.
Ejecución de pruebas.
Construcción del proyecto.
Despliegue de infraestructura AWS SAM.

Los workflows se encuentran en:

.github/workflows/

Pruebas

El proyecto incluye pruebas automatizadas almacenadas en:

tests/

También se realizaron pruebas funcionales sobre API Gateway para validar:

Solicitudes correctas.
CORS.
Registro de acceso.
Validación del cuerpo JSON.
Respuestas HTTP.
Manejo de solicitudes inválidas.
Despliegue

Para construir el proyecto con AWS SAM:

sam build

Para realizar un despliegue guiado:

sam deploy --guided

El despliegue también puede ejecutarse automáticamente mediante GitHub Actions.

Documentación

La documentación complementaria del proyecto se encuentra en la carpeta:

/docs

Incluye:

arquitectura.md
api.md
despliegue.md
operacion.md
costos.md


John Roa

Proyecto Final – Desarrollo de Aplicación Web Serverless para la Gestión de Talleres de Formación Profesional.
