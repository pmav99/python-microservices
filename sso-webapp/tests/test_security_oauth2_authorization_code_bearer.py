from typing import Optional

from fastapi import FastAPI, Security

from .contexts import security
from security.models import OAuth2AuthorizationCodeBearer

from starlette.testclient import TestClient

app = FastAPI()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorization_url="/authorize", token_url="/token", auto_error=True
)


@app.get("/items/")
async def read_items(token: Optional[str] = Security(oauth2_scheme)):
    return {"token": token}


client = TestClient(app)

openapi_schema = {
    "openapi": "3.0.2",
    "info": {"title": "Fast API", "version": "0.1.0"},
    "paths": {
        "/items/": {
            "get": {
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {"application/json": {"schema": {}}},
                    }
                },
                "summary": "Read Items",
                "operationId": "read_items_items__get",
                "security": [{"OAuth2AuthorizationCodeBearer": []}],
            }
        }
    },
    "components": {
        "securitySchemes": {
            "OAuth2AuthorizationCodeBearer": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "/authorize",
                        "tokenUrl": "/token",
                        "scopes": {},
                    }
                },
            }
        }
    },
}


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json() == openapi_schema


def test_no_token():
    response = client.get("/items")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_incorrect_token():
    response = client.get("/items", headers={"Authorization": "Non-existent testtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_token():
    response = client.get("/items", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json() == {"token": "testtoken"}