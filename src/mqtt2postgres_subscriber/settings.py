from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping

from mqtt2postgres_subscriber.logging import DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL
from mqtt2postgres_subscriber.models import (
    DEFAULT_DB_INGEST_FUNCTION,
    SubscriberSettings,
    SubscriberSettingsError,
)


def resolve_subscriber_settings(
    settings_path: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> SubscriberSettings:
    env = dict(os.environ if environ is None else environ)
    file_settings = load_subscriber_settings_file(settings_path) if settings_path else {}

    mqtt_host = _settings_text(file_settings, "mqtt_host") or _env_text(env, "MQTT_HOST") or "127.0.0.1"
    mqtt_port = _settings_int(file_settings, "mqtt_port") or _int_env(env, "MQTT_PORT", 1883)
    mqtt_qos = (
        _settings_int(file_settings, "mqtt_qos")
        if _settings_int(file_settings, "mqtt_qos") is not None
        else _int_env(env, "MQTT_QOS", 0)
    )
    mqtt_username = _settings_text(file_settings, "mqtt_username") or _env_text(env, "MQTT_USERNAME")
    mqtt_password = _settings_text(file_settings, "mqtt_password") or _env_text(env, "MQTT_PASSWORD")
    if mqtt_username and not mqtt_password:
        raise SubscriberSettingsError(
            "An MQTT password is required when an MQTT username is configured. Set mqtt_password in the settings file or MQTT_PASSWORD."
        )
    if mqtt_password and not mqtt_username:
        raise SubscriberSettingsError(
            "An MQTT username is required when an MQTT password is configured. Set mqtt_username in the settings file or MQTT_USERNAME."
        )

    db_username = _settings_text(file_settings, "db_username") or _env_text(env, "POSTGRES_USERNAME")
    if not db_username:
        raise SubscriberSettingsError("A database username is required. Set db_username in the settings file or POSTGRES_USERNAME.")
    db_password = _settings_text(file_settings, "db_password") or _env_text(env, "POSTGRES_PASSWORD")
    db_sslrootcert = _settings_text(file_settings, "db_sslrootcert") or _env_text(env, "PGSSLROOTCERT")
    db_sslcert = _settings_text(file_settings, "db_sslcert") or _env_text(env, "PGSSLCERT")
    db_sslkey = _settings_text(file_settings, "db_sslkey") or _env_text(env, "PGSSLKEY")
    db_sslmode = _settings_text(file_settings, "db_sslmode") or _env_text(env, "PGSSLMODE")

    if bool(db_sslcert) != bool(db_sslkey):
        raise SubscriberSettingsError(
            "Database client certificate authentication requires both db_sslcert and db_sslkey. "
            "Set both fields in the settings file or PGSSLCERT and PGSSLKEY."
        )
    if not db_password and not (db_sslcert and db_sslkey):
        raise SubscriberSettingsError(
            "A database password or client certificate/key pair is required. "
            "Set db_password/POSTGRES_PASSWORD or db_sslcert and db_sslkey/PGSSLCERT and PGSSLKEY."
        )
    if not db_sslmode and (db_sslrootcert or db_sslcert or db_sslkey):
        db_sslmode = "verify-full"

    raw_topic_filters = _settings_topic_filters(file_settings)
    topic_filters = tuple(parse_topic_filter(raw_filter) for raw_filter in raw_topic_filters)
    if not topic_filters:
        raise SubscriberSettingsError("At least one topic filter is required. Provide topic_filters in the settings file.")
    status_topics = tuple(parse_topic_filter(raw_filter) for raw_filter in _settings_string_list(file_settings, "status_topics"))

    return SubscriberSettings(
        mqtt_host=mqtt_host,
        mqtt_port=mqtt_port,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password,
        mqtt_client_id=_settings_text(file_settings, "mqtt_client_id") or "mqtt2postgres",
        mqtt_qos=mqtt_qos,
        db_host=_settings_text(file_settings, "db_host") or _env_text(env, "POSTGRES_HOST") or "127.0.0.1",
        db_port=_settings_int(file_settings, "db_port") or _int_env(env, "POSTGRES_PORT", 5432),
        db_name=_settings_text(file_settings, "db_name") or _env_text(env, "POSTGRES_DB") or "mqtt",
        db_schema=_settings_text(file_settings, "db_schema") or _env_text(env, "POSTGRES_SCHEMA") or "public",
        db_username=db_username,
        db_password=db_password,
        db_sslmode=db_sslmode,
        db_sslrootcert=db_sslrootcert,
        db_sslcert=db_sslcert,
        db_sslkey=db_sslkey,
        topic_filters=topic_filters,
        status_topics=status_topics,
        db_ingest_function=_settings_text(file_settings, "db_ingest_function")
        or _env_text(env, "MQTT2POSTGRES_DB_INGEST_FUNCTION")
        or DEFAULT_DB_INGEST_FUNCTION,
        log_format=_settings_text(file_settings, "log_format") or _env_text(env, "MQTT2POSTGRES_LOG_FORMAT") or DEFAULT_LOG_FORMAT,
        log_level=_settings_text(file_settings, "log_level") or _env_text(env, "MQTT2POSTGRES_LOG_LEVEL") or DEFAULT_LOG_LEVEL,
    )


def parse_topic_filter(raw_topic_filter: str) -> str:
    topic_filter = raw_topic_filter.strip()
    if not topic_filter:
        raise SubscriberSettingsError("Topic filter must not be empty.")
    return topic_filter


def load_subscriber_settings_file(path: str) -> Mapping[str, object]:
    settings_path = Path(path)
    try:
        raw = json.loads(settings_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SubscriberSettingsError(f"Subscriber settings file does not exist: {settings_path}") from exc
    except json.JSONDecodeError as exc:
        raise SubscriberSettingsError(f"Subscriber settings file is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise SubscriberSettingsError("Subscriber settings root must be a JSON object.")
    return raw


def _settings_text(settings: Mapping[str, object], key: str) -> str | None:
    value = settings.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise SubscriberSettingsError(f"Settings field '{key}' must be a string.")
    text = value.strip()
    return text or None


def _env_text(env: Mapping[str, str], key: str) -> str | None:
    value = env.get(key)
    if value is None:
        return None
    text = value.strip()
    return text or None


def _settings_int(settings: Mapping[str, object], key: str) -> int | None:
    value = settings.get(key)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SubscriberSettingsError(f"Settings field '{key}' must be an integer.") from exc


def _settings_topic_filters(settings: Mapping[str, object]) -> list[str]:
    return _settings_string_list(settings, "topic_filters")


def _settings_string_list(settings: Mapping[str, object], key: str) -> list[str]:
    value = settings.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise SubscriberSettingsError(f"Settings field '{key}' must be an array of strings.")
    filters: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SubscriberSettingsError(f"Settings field '{key}' must contain only strings.")
        filters.append(item)
    return filters


def _int_env(env: Mapping[str, str], name: str, default: int) -> int:
    raw_value = env.get(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise SubscriberSettingsError(f"{name} must be an integer.") from exc
