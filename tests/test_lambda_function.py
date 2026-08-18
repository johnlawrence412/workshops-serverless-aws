import os
import sys
import json
import base64
import unittest

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

import lambda_function as app


class TestWorkshopsLambda(unittest.TestCase):

    def test_response_status_and_cors(self):
        result = app.response(
            200,
            {"message": "OK"}
        )

        self.assertEqual(
            result["statusCode"],
            200
        )

        self.assertEqual(
            result["headers"]["Access-Control-Allow-Origin"],
            "*"
        )

        body = json.loads(
            result["body"]
        )

        self.assertEqual(
            body["message"],
            "OK"
        )


    def test_parse_body_valid_json(self):
        event = {
            "body": json.dumps({
                "name": "Taller AWS"
            })
        }

        result = app.parse_body(event)

        self.assertEqual(
            result["name"],
            "Taller AWS"
        )


    def test_parse_body_base64(self):
        payload = json.dumps({
            "name": "Taller Serverless"
        }).encode("utf-8")

        event = {
            "body": base64.b64encode(
                payload
            ).decode("utf-8"),
            "isBase64Encoded": True
        }

        result = app.parse_body(event)

        self.assertEqual(
            result["name"],
            "Taller Serverless"
        )


    def test_parse_body_invalid_json(self):
        event = {
            "body": "{JSON INVALIDO"
        }

        with self.assertRaises(
            ValueError
        ):
            app.parse_body(event)


    def test_get_groups_from_string(self):
        claims = {
            "cognito:groups":
                "[Admin, Student]"
        }

        result = app.get_groups(
            claims
        )

        self.assertIn(
            "Admin",
            result
        )

        self.assertIn(
            "Student",
            result
        )


    def test_require_admin_role_denied(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "cognito:groups":
                            "[Student]"
                    }
                }
            }
        }

        claims, error = app.require_role(
            event,
            "Admin"
        )

        self.assertIsNone(
            claims
        )

        self.assertEqual(
            error["statusCode"],
            403
        )


    def test_options_request(self):
        event = {
            "httpMethod": "OPTIONS",
            "resource": "/workshops",
            "path": "/workshops"
        }

        result = app.lambda_handler(
            event,
            None
        )

        self.assertEqual(
            result["statusCode"],
            200
        )


    def test_unknown_route_returns_404(self):
        event = {
            "httpMethod": "GET",
            "resource": "/unknown",
            "path": "/unknown"
        }

        result = app.lambda_handler(
            event,
            None
        )

        self.assertEqual(
            result["statusCode"],
            404
        )


if __name__ == "__main__":
    unittest.main()
