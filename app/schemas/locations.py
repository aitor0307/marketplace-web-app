from typing import Annotated

from pydantic import AfterValidator

# Spain's 50 provinces plus the autonomous cities of Ceuta and Melilla, by
# their official (INE) names. Stored as-is in User.state; the React app keeps
# a copy as SPAIN_PROVINCES in frontend/src/config/constants.ts.
SPAIN_PROVINCES = (
    "A Coruña",
    "Albacete",
    "Alicante/Alacant",
    "Almería",
    "Araba/Álava",
    "Asturias",
    "Ávila",
    "Badajoz",
    "Barcelona",
    "Bizkaia",
    "Burgos",
    "Cáceres",
    "Cádiz",
    "Cantabria",
    "Castellón/Castelló",
    "Ceuta",
    "Ciudad Real",
    "Córdoba",
    "Cuenca",
    "Gipuzkoa",
    "Girona",
    "Granada",
    "Guadalajara",
    "Huelva",
    "Huesca",
    "Illes Balears",
    "Jaén",
    "La Rioja",
    "Las Palmas",
    "León",
    "Lleida",
    "Lugo",
    "Madrid",
    "Málaga",
    "Melilla",
    "Murcia",
    "Navarra",
    "Ourense",
    "Palencia",
    "Pontevedra",
    "Salamanca",
    "Santa Cruz de Tenerife",
    "Segovia",
    "Sevilla",
    "Soria",
    "Tarragona",
    "Teruel",
    "Toledo",
    "Valencia/València",
    "Valladolid",
    "Zamora",
    "Zaragoza",
)


def _validate_province(value: str) -> str:
    if value not in SPAIN_PROVINCES:
        raise ValueError("Unknown province")
    return value


Province = Annotated[str, AfterValidator(_validate_province)]
