import pytest

from demon_cry_base.runner import BaseEntity, ErrorEntity, PluginResult


class SearchHit(BaseEntity):
    title: str
    url: str


def test_empty_build_is_ok():
    assert PluginResult.build().status == "ok"


def test_data_only_is_ok():
    result = PluginResult.build(entities=[SearchHit(title="t", url="u")])
    assert result.status == "ok"


def test_errors_only_is_error():
    result = PluginResult.build(
        errors=[ErrorEntity(code="AUTH_FAILED", message="bad api key")]
    )
    assert result.status == "error"


def test_data_and_errors_is_partial():
    result = PluginResult.build(
        entities=[SearchHit(title="t", url="u")],
        errors=[ErrorEntity(code="HTTP_429", message="rate limited")],
    )
    assert result.status == "partial"


def test_build_defaults_to_empty_lists():
    result = PluginResult.build()
    assert result.entities == []
    assert result.errors == []


def test_direct_ctor_uses_errors_field():
    result = PluginResult(
        entities=[SearchHit(title="t", url="u")],
        errors=[ErrorEntity(code="TIMEOUT", message="timed out")],
    )
    assert result.status == "partial"


def test_dump_includes_status_and_errors():
    result = PluginResult.build(
        entities=[SearchHit(title="t", url="u")],
        errors=[ErrorEntity(code="HTTP_429", message="rl")],
    )
    dumped = result.model_dump()
    assert dumped["status"] == "partial"
    assert dumped["entities"] == [{"title": "t", "url": "u"}]
    assert dumped["errors"] == [{"code": "HTTP_429", "message": "rl", "details": None}]


def test_error_entity_round_trip():
    result = PluginResult.build(
        errors=[ErrorEntity(code="HTTP_429", message="rl", details={"retry_after": 60})]
    )
    restored = PluginResult.model_validate_json(result.model_dump_json())
    assert restored.status == "error"
    assert restored.errors[0].code == "HTTP_429"
    assert restored.errors[0].details == {"retry_after": 60}


def test_entities_serialize_with_subclass_fields():
    result = PluginResult.build(entities=[SearchHit(title="hello", url="http://x")])
    assert result.model_dump()["entities"] == [{"title": "hello", "url": "http://x"}]


@pytest.mark.xfail(
    reason="SerializeAsAny сохраняет поля только при сериализации; "
    "при model_validate entities восстанавливаются как голый BaseEntity "
    "без полей подкласса. Нужен реестр типов / discriminated union.",
    strict=True,
)
def test_entities_polymorphic_round_trip():
    result = PluginResult.build(entities=[SearchHit(title="hello", url="http://x")])
    restored = PluginResult.model_validate_json(result.model_dump_json())
    assert isinstance(restored.entities[0], SearchHit)
    assert restored.entities[0].title == "hello"
