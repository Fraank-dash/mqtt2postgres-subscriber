from mqtt2postgres_subscriber import runtime
from mqtt2postgres_subscriber.models import SubscriberSettings


def make_settings(**overrides):
    values = {
        "mqtt_host": "mqtt-broker",
        "mqtt_port": 1883,
        "mqtt_username": "subscriber",
        "mqtt_password": "subscriber-secret",
        "mqtt_client_id": "mqtt2postgres",
        "mqtt_qos": 0,
        "db_host": "postgres",
        "db_port": 5432,
        "db_name": "mqtt",
        "db_schema": "public",
        "db_username": "postgres",
        "db_password": "postgres",
        "db_sslmode": None,
        "db_sslrootcert": None,
        "db_sslcert": None,
        "db_sslkey": None,
        "topic_filters": ("sensors/+/temp",),
        "status_topics": (),
        "db_ingest_function": "mqtt_ingest.ingest_message",
        "log_format": "json",
        "log_level": "INFO",
    }
    values.update(overrides)
    return SubscriberSettings(**values)


def test_database_connect_args_include_ssl_options():
    settings = make_settings(
        db_sslmode="verify-full",
        db_sslrootcert="/pki/ca.crt",
        db_sslcert="/pki/client.crt",
        db_sslkey="/pki/client.key",
    )

    assert runtime.build_database_connect_args(settings) == {
        "sslmode": "verify-full",
        "sslrootcert": "/pki/ca.crt",
        "sslcert": "/pki/client.crt",
        "sslkey": "/pki/client.key",
    }


def test_create_database_engine_passes_ssl_options_to_sqlalchemy(monkeypatch):
    captured = {}

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(runtime, "create_engine", fake_create_engine)
    settings = make_settings(
        db_password=None,
        db_sslmode="verify-full",
        db_sslrootcert="/pki/ca.crt",
        db_sslcert="/pki/client.crt",
        db_sslkey="/pki/client.key",
    )

    runtime.create_database_engine(settings)

    assert captured["url"].password is None
    assert captured["kwargs"]["future"] is True
    assert captured["kwargs"]["connect_args"] == {
        "sslmode": "verify-full",
        "sslrootcert": "/pki/ca.crt",
        "sslcert": "/pki/client.crt",
        "sslkey": "/pki/client.key",
    }


def test_subscription_filters_include_status_topics_and_deduplicate():
    service = object.__new__(runtime.MQTTToPostgresService)
    service.config = make_settings(
        topic_filters=("shellies/+/relay/0/power", "shellies/+/relay/0"),
        status_topics=("shellies/+/relay/0",),
    )

    assert service.subscription_filters() == (
        "shellies/+/relay/0",
        "shellies/+/relay/0/power",
    )


def test_status_topic_match_wins_over_measurement_match():
    service = object.__new__(runtime.MQTTToPostgresService)
    service.config = make_settings(
        topic_filters=("shellies/+/relay/0",),
        status_topics=("shellies/+/relay/0",),
    )

    assert service.matched_topic_filter("shellies/device/relay/0") == (
        "shellies/+/relay/0",
        runtime.TOPIC_KIND_STATUS,
    )


def test_measurement_match_uses_measurement_kind():
    service = object.__new__(runtime.MQTTToPostgresService)
    service.config = make_settings(
        topic_filters=("shellies/+/relay/0/power",),
        status_topics=("shellies/+/relay/0",),
    )

    assert service.matched_topic_filter("shellies/device/relay/0/power") == (
        "shellies/+/relay/0/power",
        runtime.TOPIC_KIND_MEASUREMENT,
    )


def test_message_metadata_includes_topic_kind():
    message = type(
        "Message",
        (),
        {
            "payload": b"on",
            "qos": 0,
            "retain": False,
            "mid": 0,
        },
    )()
    trace = runtime.parse_trace_payload("on")

    metadata = runtime.build_message_metadata(
        message,
        trace=trace,
        topic_filter="shellies/+/relay/0",
        topic_kind=runtime.TOPIC_KIND_STATUS,
    )

    assert metadata["topic_filter"] == "shellies/+/relay/0"
    assert metadata["topic_kind"] == "status"
