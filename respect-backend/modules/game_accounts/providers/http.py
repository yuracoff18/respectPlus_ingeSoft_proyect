import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class IntegrationError(Exception):
    def __init__(self, message, status="error"):
        self.status = status
        super().__init__(message)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get_json(url, headers=None):
    """Fixed provider hosts only; redirects cannot forward API credentials."""
    try:
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "RespectPlus/3.0", **(headers or {})})
        with build_opener(NoRedirect).open(request, timeout=4) as response:
            body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise IntegrationError("La respuesta del proveedor es demasiado grande.")
            return json.loads(body)
    except HTTPError as error:
        with error:
            if error.code in (401, 403):
                raise IntegrationError("El proveedor rechazó el acceso. Revisa la clave y los permisos de la aplicación.") from None
            if error.code == 404:
                raise IntegrationError("No encontramos esa cuenta. Revisa el identificador y la región.") from None
            if error.code == 429:
                raise IntegrationError("El proveedor alcanzó su límite de consultas. Inténtalo más tarde.") from None
            raise IntegrationError("El proveedor no pudo completar la consulta.") from None
    except (URLError, TimeoutError, ValueError, OSError):
        raise IntegrationError("No fue posible obtener los rangos del proveedor. Inténtalo más tarde.") from None
