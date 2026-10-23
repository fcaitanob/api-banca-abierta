import os

import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app = FastAPI(
    title="API de Banca Abierta",
    description="API de prueba para consultar tasas y ofertas de préstamos",
    version="1.1.0",
)

# Configuración de Auth0
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_AUDIENCE = "https://api-banca-abierta.onrender.com"
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"

JWKS_URL = f"{AUTH0_ISSUER}.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL)

bearer_scheme = HTTPBearer(auto_error=False)


def verificar_token(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="Se requiere un token Bearer de acceso",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credenciales.credentials

    try:
        clave = jwks_client.get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            clave,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
            options={"require": ["exp", "iat", "iss", "aud"]},
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="No se pudo validar el token",
        )

    permisos = payload.get("scope", "").split()

    if "read:prestamos" not in permisos:
        raise HTTPException(
            status_code=403,
            detail="El token no tiene el permiso read:prestamos",
        )

    return payload


@app.get("/api/v1/prestamos/tasa")
def obtener_tasa():
    return {
        "tipo_prestamo": "personal",
        "moneda": "UYU",
        "tasa_interes_anual": 35.0,
        "unidad": "porcentaje",
        "tipo_tasa": "nominal",
    }


@app.get("/api/v1/prestamos/oferta")
def obtener_oferta(
    token: dict = Depends(verificar_token),
):
    return {
        "tipo_prestamo": "personal",
        "moneda": "UYU",
        "monto_maximo": 200000,
        "plazo_maximo_meses": 48,
        "tasa_interes_anual": 35.0,
        "unidad": "porcentaje",
        "tipo_tasa": "nominal",
    }
