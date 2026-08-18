import json
import os
import base64
import uuid
from decimal import Decimal
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


# ============================================================
# CONFIGURACION
# ============================================================

TABLE_NAME = os.environ.get("TABLE_NAME", "workshops")
EVENT_BUS_NAME = os.environ.get(
    "EVENT_BUS_NAME",
    "workshops-events-dev"
)
INDEX_NAME = os.environ.get("INDEX_NAME", "GSI1")


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

eventbridge = boto3.client("events")


# ============================================================
# CORS
# ============================================================

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":
        "Content-Type,Authorization",
    "Access-Control-Allow-Methods":
        "GET,POST,PUT,DELETE,OPTIONS",
    "Content-Type": "application/json"
}


# ============================================================
# UTILIDADES
# ============================================================

class DecimalEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, Decimal):

            if obj % 1 == 0:
                return int(obj)

            return float(obj)

        return super().default(obj)


def response(status_code, body):

    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(
            body,
            cls=DecimalEncoder,
            ensure_ascii=False
        )
    }


def now_iso():

    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_body(event):

    body = event.get("body")

    if not body:
        return {}

    if event.get("isBase64Encoded"):

        body = base64.b64decode(
            body
        ).decode("utf-8")

    if isinstance(body, dict):
        return body

    try:

        return json.loads(body)

    except json.JSONDecodeError:

        raise ValueError(
            "El cuerpo no contiene JSON valido"
        )


# ============================================================
# COGNITO
# ============================================================

def get_claims(event):

    authorizer = (
        event
        .get("requestContext", {})
        .get("authorizer", {})
    )

    claims = authorizer.get("claims")

    if claims:
        return claims

    # Compatibilidad adicional
    return (
        authorizer
        .get("jwt", {})
        .get("claims", {})
    )


def get_groups(claims):

    groups = claims.get(
        "cognito:groups",
        []
    )

    if isinstance(groups, list):
        return groups

    if not groups:
        return []

    text = str(groups).strip()

    text = text.strip("[]")

    return [
        item
        .strip()
        .strip('"')
        .strip("'")

        for item in text.split(",")

        if item.strip()
    ]


def require_role(event, role):

    claims = get_claims(event)

    groups = get_groups(claims)

    if role not in groups:

        return None, response(
            403,
            {
                "message":
                    f"Acceso denegado. "
                    f"Se requiere el rol {role}"
            }
        )

    return claims, None


# ============================================================
# WORKSHOP ID
# ============================================================

def get_workshop_id(item):

    if item.get("workshopId"):
        return str(item["workshopId"])

    pk = item.get("PK", "")

    if pk.startswith("WORKSHOP#"):

        return pk.replace(
            "WORKSHOP#",
            "",
            1
        )

    return ""


def normalize_workshop(item):

    if not item:
        return item

    result = dict(item)

    result["workshopId"] = (
        get_workshop_id(result)
    )

    return result


# ============================================================
# GET /workshops
# ============================================================

def list_workshops(event):

    parameters = (
        event.get("queryStringParameters")
        or {}
    )

    try:

        limit = int(
            parameters.get(
                "limit",
                50
            )
        )

    except ValueError:

        limit = 50

    limit = max(
        1,
        min(limit, 100)
    )

    # Intentamos primero mediante GSI1
    try:

        result = table.query(

            IndexName=INDEX_NAME,

            KeyConditionExpression=
                Key("GSI1PK").eq(
                    "WORKSHOP#ALL"
                ),

            Limit=limit,

            ScanIndexForward=True
        )

        items = [
            normalize_workshop(item)

            for item in result.get(
                "Items",
                []
            )
        ]

    except ClientError as error:

        print(
            "No fue posible usar GSI1:",
            str(error)
        )

        # Fallback para que la API siga funcionando
        result = table.scan(

            FilterExpression=
                Attr("SK").eq("META"),

            Limit=limit
        )

        items = [
            normalize_workshop(item)

            for item in result.get(
                "Items",
                []
            )
        ]

        items.sort(
            key=lambda item:
                item.get("startAt", "")
        )

    return response(
        200,
        {
            "items": items,
            "count": len(items),
            "nextToken": None,
            "lastEvaluatedKey":
                result.get(
                    "LastEvaluatedKey"
                )
        }
    )


# ============================================================
# GET /workshops/{id}
# ============================================================

def get_workshop(workshop_id):

    result = table.get_item(

        Key={
            "PK":
                f"WORKSHOP#{workshop_id}",

            "SK":
                "META"
        }
    )

    item = result.get("Item")

    if not item:

        return response(
            404,
            {
                "message":
                    "Taller no encontrado"
            }
        )

    return response(
        200,
        normalize_workshop(item)
    )


# ============================================================
# POST /workshops
# ADMIN
# ============================================================

def create_workshop(event):

    claims, error = require_role(
        event,
        "Admin"
    )

    if error:
        return error

    try:

        body = parse_body(event)

    except ValueError as error:

        return response(
            400,
            {"message": str(error)}
        )

    workshop_id = str(
        body.get(
            "workshopId",
            ""
        )
    ).strip()

    # Si el administrador no escribe ID,
    # se genera uno automaticamente.
    if not workshop_id:

        workshop_id = (
            uuid.uuid4()
            .hex[:8]
        )

    try:

        capacity = int(
            body.get(
                "capacity",
                30
            )
        )

    except Exception:

        return response(
            400,
            {
                "message":
                    "La capacidad no es valida"
            }
        )

    if capacity <= 0:

        return response(
            400,
            {
                "message":
                    "La capacidad debe ser mayor que cero"
            }
        )

    date = now_iso()

    item = {

        "PK":
            f"WORKSHOP#{workshop_id}",

        "SK":
            "META",

        "workshopId":
            workshop_id,

        "name":
            body.get(
                "name",
                ""
            ),

        "description":
            body.get(
                "description",
                ""
            ),

        "category":
            body.get(
                "category",
                ""
            ),

        "location":
            body.get(
                "location",
                ""
            ),

        "startAt":
            body.get(
                "startAt",
                ""
            ),

        "endAt":
            body.get(
                "endAt",
                ""
            ),

        "status":
            body.get(
                "status",
                "scheduled"
            ),

        "capacity":
            capacity,

        "createdAt":
            date,

        "updatedAt":
            date,

        "GSI1PK":
            "WORKSHOP#ALL",

        "GSI1SK":
            body.get(
                "startAt",
                ""
            )
    }

    try:

        table.put_item(

            Item=item,

            ConditionExpression=(
                "attribute_not_exists(PK) "
                "AND attribute_not_exists(SK)"
            )
        )

    except ClientError as error:

        code = (
            error.response
            .get("Error", {})
            .get("Code")
        )

        if (
            code
            ==
            "ConditionalCheckFailedException"
        ):

            return response(
                409,
                {
                    "message":
                        "Ya existe un taller con ese ID"
                }
            )

        raise

    return response(
        201,
        {
            "message":
                "Taller creado correctamente",

            "workshop":
                item
        }
    )


# ============================================================
# PUT /workshops/{id}
# ADMIN
# ============================================================

def update_workshop(
    event,
    workshop_id
):

    claims, error = require_role(
        event,
        "Admin"
    )

    if error:
        return error

    try:

        body = parse_body(event)

    except ValueError as error:

        return response(
            400,
            {"message": str(error)}
        )

    existing = table.get_item(

        Key={
            "PK":
                f"WORKSHOP#{workshop_id}",

            "SK":
                "META"
        }
    ).get("Item")

    if not existing:

        return response(
            404,
            {
                "message":
                    "Taller no encontrado"
            }
        )

    allowed_fields = [

        "name",
        "description",
        "category",
        "location",
        "startAt",
        "endAt",
        "status",
        "capacity"
    ]

    for field in allowed_fields:

        if field in body:

            existing[field] = (
                body[field]
            )

    if "capacity" in body:

        try:

            existing["capacity"] = int(
                body["capacity"]
            )

        except Exception:

            return response(
                400,
                {
                    "message":
                        "La capacidad no es valida"
                }
            )

    existing["updatedAt"] = (
        now_iso()
    )

    existing["GSI1PK"] = (
        "WORKSHOP#ALL"
    )

    existing["GSI1SK"] = (
        existing.get(
            "startAt",
            ""
        )
    )

    existing["workshopId"] = (
        str(workshop_id)
    )

    table.put_item(
        Item=existing
    )

    return response(
        200,
        {
            "message":
                "Taller actualizado correctamente",

            "workshop":
                normalize_workshop(
                    existing
                )
        }
    )


# ============================================================
# DELETE /workshops/{id}
# ADMIN
# ============================================================

def delete_workshop(
    event,
    workshop_id
):

    claims, error = require_role(
        event,
        "Admin"
    )

    if error:
        return error

    pk = (
        f"WORKSHOP#{workshop_id}"
    )

    existing = table.get_item(

        Key={
            "PK": pk,
            "SK": "META"
        }
    ).get("Item")

    if not existing:

        return response(
            404,
            {
                "message":
                    "Taller no encontrado"
            }
        )

    # Obtiene taller y registros asociados
    result = table.query(

        KeyConditionExpression=
            Key("PK").eq(pk)
    )

    while True:

        with table.batch_writer() as batch:

            for item in result.get(
                "Items",
                []
            ):

                batch.delete_item(

                    Key={
                        "PK":
                            item["PK"],

                        "SK":
                            item["SK"]
                    }
                )

        if not result.get(
            "LastEvaluatedKey"
        ):
            break

        result = table.query(

            KeyConditionExpression=
                Key("PK").eq(pk),

            ExclusiveStartKey=
                result[
                    "LastEvaluatedKey"
                ]
        )

    return response(
        200,
        {
            "message":
                "Taller eliminado correctamente"
        }
    )


# ============================================================
# EVENTBRIDGE
# ============================================================

def publish_student_registered(
    workshop,
    workshop_id,
    claims,
    participant_name,
    registered_at
):

    detail = {

        "workshopId":
            str(workshop_id),

        "workshopName":
            workshop.get(
                "name",
                ""
            ),

        "startAt":
            workshop.get(
                "startAt",
                ""
            ),

        "location":
            workshop.get(
                "location",
                ""
            ),

        "userId":
            claims.get(
                "sub",
                ""
            ),

        "email":
            claims.get(
                "email",
                ""
            ),

        "name":
            participant_name,

        "registeredAt":
            registered_at
    }

    result = eventbridge.put_events(

        Entries=[
            {
                "Source":
                    "workshops.app",

                "DetailType":
                    "STUDENT_REGISTERED",

                "Detail":
                    json.dumps(
                        detail,
                        ensure_ascii=False
                    ),

                "EventBusName":
                    EVENT_BUS_NAME
            }
        ]
    )

    print(
        "EVENTBRIDGE RESULT:",
        json.dumps(
            result,
            default=str
        )
    )

    if (
        result.get(
            "FailedEntryCount",
            0
        )
        >
        0
    ):

        print(
            "ERROR AL PUBLICAR EVENTO"
        )

        return None

    entries = result.get(
        "Entries",
        []
    )

    if entries:

        return entries[0].get(
            "EventId"
        )

    return None


# ============================================================
# POST /workshops/{id}/register
# STUDENT
# ============================================================

def register_student(
    event,
    workshop_id
):

    claims, error = require_role(
        event,
        "Student"
    )

    if error:
        return error

    user_id = str(
        claims.get(
            "sub",
            ""
        )
    ).strip()

    email = str(
        claims.get(
            "email",
            ""
        )
    ).strip()

    if not user_id:

        return response(
            401,
            {
                "message":
                    "No se pudo identificar al usuario"
            }
        )

    try:

        body = parse_body(event)

    except ValueError as error:

        return response(
            400,
            {"message": str(error)}
        )

    participant_name = str(
        body.get(
            "name",
            ""
        )
    ).strip()

    if not participant_name:

        return response(
            400,
            {
                "message":
                    "El nombre completo es obligatorio"
            }
        )

    workshop = table.get_item(

        Key={
            "PK":
                f"WORKSHOP#{workshop_id}",

            "SK":
                "META"
        }
    ).get("Item")

    if not workshop:

        return response(
            404,
            {
                "message":
                    "Taller no encontrado"
            }
        )

    registered_at = (
        now_iso()
    )

    registration = {

        "PK":
            f"WORKSHOP#{workshop_id}",

        "SK":
            f"REG#USER#{user_id}",

        "workshopId":
            str(workshop_id),

        "userId":
            user_id,

        "email":
            email,

        "name":
            participant_name,

        "registeredAt":
            registered_at,

        # Permite consultar registros
        # del estudiante usando GSI1
        "GSI1PK":
            f"USER#{user_id}",

        "GSI1SK":
            registered_at
    }

    try:

        table.put_item(

            Item=registration,

            ConditionExpression=(
                "attribute_not_exists(PK) "
                "AND attribute_not_exists(SK)"
            )
        )

    except ClientError as error:

        code = (
            error.response
            .get("Error", {})
            .get("Code")
        )

        if (
            code
            ==
            "ConditionalCheckFailedException"
        ):

            return response(
                409,
                {
                    "message":
                        "El usuario ya esta registrado en este taller"
                }
            )

        raise

    # ========================================================
    # PUBLICAR EVENTO STUDENT_REGISTERED
    # ========================================================

    event_id = None

    try:

        event_id = (
            publish_student_registered(

                workshop=
                    workshop,

                workshop_id=
                    workshop_id,

                claims=
                    claims,

                participant_name=
                    participant_name,

                registered_at=
                    registered_at
            )
        )

    except Exception as error:

        # No eliminamos el registro si EventBridge falla.
        # El error queda visible en CloudWatch.
        print(
            "ERROR EVENTBRIDGE:",
            repr(error)
        )

    return response(
        201,
        {
            "message":
                "Registro realizado correctamente",

            "registration":
                registration,

            "eventId":
                event_id
        }
    )


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(
    event,
    context
):

    print(
        "EVENT:",
        json.dumps(
            event,
            default=str
        )
    )

    method = (
        event.get(
            "httpMethod",
            ""
        )
        .upper()
    )

    resource = event.get(
        "resource",
        ""
    )

    path = event.get(
        "path",
        ""
    )

    parameters = (
        event.get(
            "pathParameters"
        )
        or {}
    )

    workshop_id = (
        parameters.get("id")
        or
        parameters.get(
            "workshopId"
        )
    )

    try:

        # OPTIONS
        if method == "OPTIONS":

            return response(
                200,
                {"message": "OK"}
            )

        # GET /workshops
        if (
            method == "GET"
            and
            (
                resource
                ==
                "/workshops"

                or

                path.rstrip("/")
                ==
                "/workshops"
            )
        ):

            return list_workshops(
                event
            )

        # POST /workshops
        if (
            method == "POST"
            and
            (
                resource
                ==
                "/workshops"

                or

                path.rstrip("/")
                ==
                "/workshops"
            )
        ):

            return create_workshop(
                event
            )

        # POST /workshops/{id}/register
        if (
            method == "POST"
            and
            workshop_id
            and
            (
                resource
                ==
                "/workshops/{id}/register"

                or

                path.endswith(
                    "/register"
                )
            )
        ):

            return register_student(
                event,
                workshop_id
            )

        # GET /workshops/{id}
        if (
            method == "GET"
            and
            workshop_id
        ):

            return get_workshop(
                workshop_id
            )

        # PUT /workshops/{id}
        if (
            method == "PUT"
            and
            workshop_id
        ):

            return update_workshop(
                event,
                workshop_id
            )

        # DELETE /workshops/{id}
        if (
            method == "DELETE"
            and
            workshop_id
        ):

            return delete_workshop(
                event,
                workshop_id
            )

        return response(
            404,
            {
                "message":
                    "Ruta no encontrada",

                "method":
                    method,

                "resource":
                    resource,

                "path":
                    path
            }
        )


    except ClientError as error:

        print(
            "AWS ERROR:",
            repr(error)
        )

        return response(
            500,
            {
                "message":
                    "Error al procesar la solicitud",

                "error":
                    (
                        error.response
                        .get(
                            "Error",
                            {}
                        )
                        .get(
                            "Code",
                            "ClientError"
                        )
                    )
            }
        )


    except Exception as error:

        print(
            "ERROR:",
            repr(error)
        )

        return response(
            500,
            {
                "message":
                    "Error interno del servidor",

                "error":
                    str(error)
            }
        )