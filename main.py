from fastapi import FastAPI

app = FastAPI(
    title="API de Banca Abierta",
    description="API de prueba para consultar tasas de préstamos",
    version="1.0.0"
)


@app.get("/api/v1/prestamos/tasa")
def obtener_tasa():
    return {
        "tipo_prestamo": "personal",
        "moneda": "UYU",
        "tasa_interes_anual": 35.0,
        "unidad": "porcentaje",
        "tipo_tasa": "nominal"
    }
