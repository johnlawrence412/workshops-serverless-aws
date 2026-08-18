WORKSHOPS - AWS SAM MULTIENV
==============================

Contenido:
- template.yaml: infraestructura parametrizada para dev/prod.
- samconfig.toml: configuraciones separadas de despliegue.
- src/lambda_function.py: codigo real exportado de workshops-api-dev.

La plantilla crea recursos separados con sufijo iac-dev o iac-prod para NO
sobrescribir la aplicacion manual que ya esta funcionando.

VALIDACION
----------
sam validate --lint
sam build

DESPLIEGUE DEV
--------------
sam deploy --config-env dev

DESPLIEGUE PROD
---------------
sam deploy --config-env prod

NOTA
----
Los User Pools se crean sin usuarios. Los grupos Admin y Student se crean,
pero los usuarios de prueba se agregan despues si se desea probar autenticacion.
