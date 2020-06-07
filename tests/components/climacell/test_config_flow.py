"""Test the ClimaCell config flow."""
import logging

from pyclimacell.pyclimacell import (
    CantConnectException,
    InvalidAPIKeyException,
    RateLimitedException,
)

from homeassistant import config_entries, data_entry_flow
from homeassistant.components.climacell import SCHEMA
from homeassistant.components.climacell.config_flow import _get_config_schema
from homeassistant.components.climacell.const import (
    CONF_AQI_COUNTRY,
    CONF_FORECAST_FREQUENCY,
    DAILY,
    DEFAULT_NAME,
    DOMAIN,
    HOURLY,
    USA,
)
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType

from .const import API_KEY, MIN_CONFIG, MockRequestInfo

from tests.async_mock import patch

_LOGGER = logging.getLogger(__name__)


async def test_user_flow_minimum_fields(hass: HomeAssistantType,) -> None:
    """Test user config flow with minimum fields."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_hourly",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_daily",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_get_config_schema(hass, MIN_CONFIG)(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == DEFAULT_NAME
        assert result["data"][CONF_NAME] == DEFAULT_NAME
        assert result["data"][CONF_API_KEY] == API_KEY
        assert result["data"][CONF_FORECAST_FREQUENCY] == DAILY
        assert result["data"][CONF_LATITUDE] == hass.config.latitude
        assert result["data"][CONF_LONGITUDE] == hass.config.longitude
        assert result["data"][CONF_AQI_COUNTRY] == USA


async def test_user_flow_cannot_connect(hass: HomeAssistantType,) -> None:
    """Test user config flow when ClimaCell can't connect."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        side_effect=CantConnectException,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_get_config_schema(hass, MIN_CONFIG)(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_api(hass: HomeAssistantType,) -> None:
    """Test user config flow when API key is invalid."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        side_effect=InvalidAPIKeyException(MockRequestInfo(), None),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_get_config_schema(hass, MIN_CONFIG)(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["errors"] == {CONF_API_KEY: "invalid_api_key"}


async def test_user_flow_rate_limited(hass: HomeAssistantType,) -> None:
    """Test user config flow when API key is rate limited."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        side_effect=RateLimitedException(MockRequestInfo(), None),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_get_config_schema(hass, MIN_CONFIG)(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["errors"] == {"base": "rate_limited"}


async def test_user_flow_rate_unknown(hass: HomeAssistantType,) -> None:
    """Test user config flow when unknown error occurs."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        side_effect=Exception,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_get_config_schema(hass, MIN_CONFIG)(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["errors"] == {"base": "unknown"}


async def test_import_flow_minimum_fields(hass: HomeAssistantType,) -> None:
    """Test import config flow with minimum fields."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_hourly",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_daily",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=SCHEMA(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == DEFAULT_NAME
        assert result["data"][CONF_NAME] == DEFAULT_NAME
        assert result["data"][CONF_API_KEY] == API_KEY
        assert result["data"][CONF_FORECAST_FREQUENCY] == DAILY
        assert CONF_LATITUDE not in result["data"]
        assert CONF_LONGITUDE not in result["data"]
        assert result["data"][CONF_AQI_COUNTRY] == USA


async def test_import_flow_already_exists(hass: HomeAssistantType,) -> None:
    """Test import config flow when entry already exists."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_hourly",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_daily",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=SCHEMA(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == DEFAULT_NAME
        assert result["data"][CONF_NAME] == DEFAULT_NAME
        assert result["data"][CONF_API_KEY] == API_KEY
        assert result["data"][CONF_FORECAST_FREQUENCY] == DAILY
        assert CONF_LATITUDE not in result["data"]
        assert CONF_LONGITUDE not in result["data"]
        assert result["data"][CONF_AQI_COUNTRY] == USA

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=SCHEMA(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_ABORT
        assert result["reason"] == "already_configured_account"


async def test_import_flow_update_entry(hass: HomeAssistantType,) -> None:
    """Test import config flow when config is updated."""
    with patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.realtime",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_hourly",
        return_value=True,
    ), patch(
        "homeassistant.components.climacell.config_flow.ClimaCell.forecast_daily",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=SCHEMA(MIN_CONFIG),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == DEFAULT_NAME
        assert result["data"][CONF_NAME] == DEFAULT_NAME
        assert result["data"][CONF_API_KEY] == API_KEY
        assert result["data"][CONF_FORECAST_FREQUENCY] == DAILY
        assert CONF_LATITUDE not in result["data"]
        assert CONF_LONGITUDE not in result["data"]
        assert result["data"][CONF_AQI_COUNTRY] == USA

        config = MIN_CONFIG.copy()
        config[CONF_FORECAST_FREQUENCY] = HOURLY
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=SCHEMA(config),
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_ABORT
        assert result["reason"] == "updated_entry"
