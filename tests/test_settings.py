import json

import pytest

from mqtt2postgres_subscriber.settings import (
    SubscriberSettingsError,
    resolve_subscriber_settings,
)


def base_environ(**overrides):
    env = {
        "POSTGRES_USERNAME": "postgres",
        "POSTGRES_PASSWORD": "postgres",
    }
    env.update(overrides)
    return env


def config_file(tmp_path, **overrides):
    config = {
        "topic_filters": ["sensors/+/temp"],
    }
    config.update(overrides)
    path = tmp_path / "subscriber.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


def test_password_config_still_works(tmp_path):
    settings = resolve_subscriber_settings(
        environ=base_environ(),
        settings_path=config_file(tmp_path),
    )

    assert settings.db_username == "postgres"
    assert settings.db_password == "postgres"
    assert settings.db_sslmode is None
    assert settings.status_topics == ()


def test_missing_password_without_client_cert_pair_fails(tmp_path):
    with pytest.raises(SubscriberSettingsError, match="database password or client certificate/key pair"):
        resolve_subscriber_settings(
            environ={"POSTGRES_USERNAME": "postgres"},
            settings_path=config_file(tmp_path),
        )


def test_client_cert_pair_allows_missing_password(tmp_path):
    settings = resolve_subscriber_settings(
        environ=base_environ(
            POSTGRES_PASSWORD="",
            PGSSLCERT="/pki/client.crt",
            PGSSLKEY="/pki/client.key",
        ),
        settings_path=config_file(tmp_path),
    )

    assert settings.db_password is None
    assert settings.db_sslcert == "/pki/client.crt"
    assert settings.db_sslkey == "/pki/client.key"


def test_cert_without_key_fails(tmp_path):
    with pytest.raises(SubscriberSettingsError, match="db_sslcert and db_sslkey"):
        resolve_subscriber_settings(
            environ=base_environ(
                POSTGRES_PASSWORD="",
                PGSSLCERT="/pki/client.crt",
            ),
            settings_path=config_file(tmp_path),
        )


def test_key_without_cert_fails(tmp_path):
    with pytest.raises(SubscriberSettingsError, match="db_sslcert and db_sslkey"):
        resolve_subscriber_settings(
            environ=base_environ(
                POSTGRES_PASSWORD="",
                PGSSLKEY="/pki/client.key",
            ),
            settings_path=config_file(tmp_path),
        )


def test_certificate_config_defaults_sslmode_to_verify_full(tmp_path):
    settings = resolve_subscriber_settings(
        environ=base_environ(
            PGSSLCERT="/pki/client.crt",
            PGSSLKEY="/pki/client.key",
        ),
        settings_path=config_file(tmp_path),
    )

    assert settings.db_sslmode == "verify-full"


def test_explicit_sslmode_is_preserved(tmp_path):
    settings = resolve_subscriber_settings(
        environ=base_environ(
            PGSSLMODE="verify-ca",
            PGSSLROOTCERT="/pki/ca.crt",
        ),
        settings_path=config_file(tmp_path),
    )

    assert settings.db_sslmode == "verify-ca"
    assert settings.db_sslrootcert == "/pki/ca.crt"


def test_status_topics_parse_and_trim_filters(tmp_path):
    settings = resolve_subscriber_settings(
        environ=base_environ(),
        settings_path=config_file(tmp_path, status_topics=[" shellies/+/relay/0 "]),
    )

    assert settings.status_topics == ("shellies/+/relay/0",)


def test_non_array_status_topics_fails(tmp_path):
    with pytest.raises(SubscriberSettingsError, match="status_topics"):
        resolve_subscriber_settings(
            environ=base_environ(),
            settings_path=config_file(tmp_path, status_topics="shellies/+/relay/0"),
        )


def test_non_string_status_topics_item_fails(tmp_path):
    with pytest.raises(SubscriberSettingsError, match="status_topics"):
        resolve_subscriber_settings(
            environ=base_environ(),
            settings_path=config_file(tmp_path, status_topics=["shellies/+/relay/0", 42]),
        )
