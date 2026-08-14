"""Prueba de carga autenticada para el flujo principal de reservas.

Lee LOAD_TEST_USERNAME, LOAD_TEST_PASSWORD y LOAD_TEST_RESOURCE_ID desde
.env.locust. Usa exclusivamente una base de datos de pruebas.
"""

from locust import HttpUser, between, task
from locust.exception import StopUser
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoadTestSettings(BaseSettings):
    """Configuración local del escenario de carga."""

    LOAD_TEST_USERNAME: str = ""
    LOAD_TEST_PASSWORD: str = ""
    LOAD_TEST_RESOURCE_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env.locust", env_file_encoding="utf-8", extra="ignore"
    )


load_test_settings = LoadTestSettings()


class ReservationUser(HttpUser):
    """Usuario que consulta recursos y reservas, y crea reservas no solapadas."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.username = self._required_setting(load_test_settings.LOAD_TEST_USERNAME)
        self.password = self._required_setting(load_test_settings.LOAD_TEST_PASSWORD)
        self.resource_id = self._required_setting(
            load_test_settings.LOAD_TEST_RESOURCE_ID
        )

        with self.client.post(
            "/auth/login",
            data={"username": self.username, "password": self.password},
            name="POST /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"No se pudo iniciar sesión: {response.status_code}")
                raise StopUser()

            auth_token = response.cookies.get("auth_token")
            if not auth_token:
                response.failure("El inicio de sesión no devolvió auth_token")
                raise StopUser()

            # La API marca la cookie como Secure; Locust apunta al backend local por HTTP.
            self.client.headers["Cookie"] = f"auth_token={auth_token}"

    @staticmethod
    def _required_setting(value: str) -> str:
        if not value:
            raise StopUser("Completa las variables requeridas en .env.locust")
        return value

    @task(4)
    def list_resources(self) -> None:
        self.client.get("/resources/?start=0&limit=10", name="GET /resources/")

    @task(3)
    def list_reservations(self) -> None:
        self.client.get("/reservations/?start=0&limit=10", name="GET /reservations/")
