# Despliegue de la aplicación Workshops

## 1. Descripción

La infraestructura de Workshops se administra mediante AWS Serverless Application Model (AWS SAM).

AWS SAM permite definir los recursos de la aplicación mediante Infraestructura como Código (IaC), facilitando la creación reproducible de los ambientes de desarrollo y producción.

El archivo principal de infraestructura es:

`template.yaml`

La configuración de despliegue se encuentra en:

`samconfig.toml`

---

## 2. Ambientes

La aplicación utiliza ambientes independientes:

- `dev`
- `prod`

Los stacks utilizados son:

```text
workshops-iac-dev
workshops-iac-prod
```

Esta separación permite realizar cambios y pruebas en desarrollo antes de utilizar el ambiente de producción.

---

## 3. Recursos administrados mediante SAM

La plantilla de infraestructura crea y configura recursos del backend serverless, incluyendo componentes como:

- AWS Lambda.
- Amazon API Gateway.
- Amazon DynamoDB.
- Roles y permisos IAM.
- CloudWatch Alarm.
- Recursos necesarios para la ejecución del backend.

Los nombres de los recursos se diferencian mediante el ambiente correspondiente.

Ejemplos:

```text
workshops-api-iac-dev
workshops-api-iac-prod

workshops-iac-dev
workshops-iac-prod
```

---

## 4. Requisitos

Para desplegar el proyecto manualmente se requiere:

- Una cuenta de AWS.
- AWS CLI configurado.
- AWS SAM CLI.
- Permisos suficientes para crear los recursos definidos en la plantilla.
- Acceso a la región utilizada por el proyecto.

Región principal:

```text
us-east-1
```

---

## 5. Construcción del proyecto

Desde la raíz del repositorio se puede ejecutar:

```bash
sam build
```

Este comando procesa el archivo `template.yaml`, prepara el código Lambda y genera los artefactos necesarios para el despliegue.

---

## 6. Validación de la plantilla

Antes del despliegue se puede validar la plantilla SAM mediante:

```bash
sam validate
```

Esto permite detectar problemas de sintaxis o configuración antes de crear o actualizar recursos en AWS.

---

## 7. Despliegue guiado

Para realizar el primer despliegue de forma interactiva se puede utilizar:

```bash
sam deploy --guided
```

Durante este proceso SAM solicita parámetros como:

- Nombre del stack.
- Región.
- Confirmación de cambios.
- Permisos para crear roles IAM.
- Parámetros del ambiente.

Una vez guardada la configuración, los siguientes despliegues pueden ejecutarse utilizando `samconfig.toml`.

---

## 8. Despliegue de DEV

El ambiente de desarrollo utiliza:

```text
Environment = dev
Stack = workshops-iac-dev
```

Flujo general:

```text
Código
  |
  v
sam validate
  |
  v
sam build
  |
  v
sam deploy
  |
  v
CloudFormation
  |
  v
workshops-iac-dev
```

El objetivo del ambiente dev es permitir pruebas y validaciones antes de promover cambios hacia producción.

---

## 9. Despliegue de PROD

El ambiente de producción utiliza:

```text
Environment = prod
Stack = workshops-iac-prod
```

La misma plantilla de infraestructura puede reutilizarse cambiando los parámetros del ambiente.

Esto evita mantener configuraciones completamente diferentes para desarrollo y producción.

---

## 10. Parámetros y variables

La plantilla utiliza parámetros para distinguir los recursos entre ambientes.

Ejemplo conceptual:

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues:
      - dev
      - prod
```

Los nombres de los recursos pueden construirse utilizando este parámetro.

Ejemplo:

```yaml
FunctionName: !Sub workshops-api-iac-${Environment}
```

De esta forma, la misma infraestructura puede utilizarse para ambos ambientes.

---

## 11. Etiquetas

Los recursos principales utilizan etiquetas para facilitar su administración.

Etiquetas utilizadas:

```text
Project = Workshops
Env = dev
```

o:

```text
Project = Workshops
Env = prod
```

Estas etiquetas permiten identificar los recursos de cada ambiente y mejorar el control operativo y de costos.

---

# 12. CI/CD mediante GitHub Actions

El repositorio utiliza GitHub Actions para automatizar el proceso de integración y despliegue continuo.

Los workflows se encuentran en:

```text
.github/workflows/
```

El pipeline ejecuta tareas como:

1. Obtener el código del repositorio.
2. Preparar el entorno.
3. Ejecutar pruebas automatizadas.
4. Validar la aplicación.
5. Construir el proyecto con AWS SAM.
6. Autenticarse contra AWS.
7. Ejecutar el despliegue correspondiente.

---

## 13. Autenticación de GitHub con AWS

Para evitar almacenar credenciales AWS permanentes dentro del repositorio, se configuró autenticación mediante OpenID Connect (OIDC).

AWS dispone de un proveedor de identidad para:

```text
token.actions.githubusercontent.com
```

El rol utilizado para GitHub Actions es:

```text
GitHubActionsWorkshopsSAMRole
```

GitHub Actions puede asumir este rol durante la ejecución del pipeline y obtener credenciales temporales.

Esto mejora la seguridad al evitar el almacenamiento de Access Keys permanentes como secretos del repositorio.

---

## 14. Flujo del pipeline

El proceso automatizado puede representarse de la siguiente manera:

```text
Push a GitHub
      |
      v
GitHub Actions
      |
      v
Pruebas automatizadas
      |
      v
SAM Validate
      |
      v
SAM Build
      |
      v
Autenticación OIDC
      |
      v
SAM Deploy
      |
      v
AWS CloudFormation
      |
      v
Recursos DEV / PROD
```

---

## 15. Pruebas automatizadas

El repositorio contiene una carpeta:

```text
tests/
```

Las pruebas se ejecutan como parte del proceso CI/CD para detectar errores antes del despliegue.

Esto permite validar el comportamiento del código antes de actualizar la infraestructura.

---

## 16. Infraestructura creada mediante CloudFormation

AWS SAM utiliza AWS CloudFormation para crear y administrar los recursos definidos en la plantilla.

Los stacks pueden visualizarse desde:

```text
AWS Console
→ CloudFormation
→ Stacks
```

En el proyecto se verificaron los stacks:

```text
workshops-iac-dev
workshops-iac-prod
```

Esto demuestra la separación de ambientes mediante Infraestructura como Código.

---

## 17. Actualizaciones

Cuando se realiza una modificación en `template.yaml` o en el código Lambda, el despliegue actualiza únicamente los recursos necesarios.

Flujo:

```text
Cambio de código
      |
      v
Commit / Push
      |
      v
GitHub Actions
      |
      v
Pruebas
      |
      v
Construcción
      |
      v
CloudFormation Change Set
      |
      v
Actualización de recursos
```

Esto permite mantener la infraestructura versionada junto con el código fuente.

---

## 18. Versionado y despliegue gradual de Lambda

La aplicación utiliza versiones y alias de AWS Lambda para controlar los cambios del backend.

Se verificó una distribución gradual de tráfico tipo Canary:

```text
Versión estable = 90 %
Nueva versión   = 10 %
```

Esta estrategia permite enviar inicialmente una pequeña parte del tráfico hacia una nueva versión.

Si el comportamiento es correcto, posteriormente puede aumentarse el porcentaje de tráfico dirigido a la nueva versión.

---

## 19. Rollback

En caso de detectar problemas después de una actualización, se puede regresar a una versión estable de Lambda modificando el alias o revirtiendo el despliegue.

CloudFormation también permite controlar las actualizaciones de los recursos administrados mediante el stack.

Una estrategia básica consiste en:

1. Detectar el error mediante CloudWatch.
2. Identificar la versión afectada.
3. Redirigir el alias hacia la versión estable.
4. Revisar los logs.
5. Corregir el código.
6. Ejecutar nuevamente las pruebas.
7. Realizar un nuevo despliegue.

---

## 20. Frontend

El frontend de Workshops está almacenado en:

```text
frontend/index.html
```

En AWS, los archivos estáticos se almacenan en Amazon S3 y son distribuidos mediante Amazon CloudFront.

URL pública:

```text
https://d1z6gu4fgp8a7e.cloudfront.net/
```

CloudFront también contiene el comportamiento:

```text
/api/*
```

que dirige las solicitudes del frontend hacia Amazon API Gateway.

---

## 21. Verificación posterior al despliegue

Después de un despliegue se recomienda realizar las siguientes comprobaciones:

- Abrir el frontend mediante CloudFront.
- Ejecutar `GET /api/workshops`.
- Verificar autenticación con Cognito.
- Crear un taller con un usuario administrador.
- Registrar un estudiante.
- Consultar CloudWatch Logs.
- Revisar alarmas.
- Confirmar que EventBridge y SNS funcionen correctamente.
- Verificar que no existan mensajes inesperados en la DLQ.

Ejemplo de comprobación pública:

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

---

## 22. Archivos relacionados con el despliegue

Los principales archivos del repositorio relacionados con el despliegue son:

```text
template.yaml
samconfig.toml
README_DEPLOY.txt
.github/workflows/
src/
tests/
```

---

## 23. Ventajas del enfoque utilizado

El uso de AWS SAM y GitHub Actions proporciona:

- Infraestructura versionada.
- Separación entre dev y prod.
- Despliegues reproducibles.
- Reducción de configuraciones manuales.
- Automatización de pruebas.
- Uso de credenciales temporales mediante OIDC.
- Mayor facilidad para realizar actualizaciones.
- Posibilidad de rollback.
- Trazabilidad mediante Git y CloudFormation.

---

## 24. Resumen

El proceso de despliegue de Workshops combina AWS SAM, AWS CloudFormation y GitHub Actions.

La infraestructura se mantiene como código mediante `template.yaml`, mientras que `samconfig.toml` facilita la configuración de despliegue.

Los ambientes `dev` y `prod` están separados mediante stacks independientes y el pipeline CI/CD permite validar, construir y desplegar cambios de manera automatizada.

La integración con OIDC evita almacenar credenciales AWS permanentes en GitHub y la estrategia de versiones y alias de Lambda permite realizar actualizaciones de forma controlada.
