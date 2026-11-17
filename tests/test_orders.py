import json
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from orders import OrderStatus, order_to_dict, order_to_json, parse_order

VALID = {"id": 1, "customer_email": "user@example.com", "total": "99.90", "status": "paid"}


def test_valid_order_from_dict():
    order = parse_order(VALID)
    assert order.total == Decimal("99.90")
    assert order.status is OrderStatus.PAID


def test_default_status_is_new():
    data = {k: v for k, v in VALID.items() if k != "status"}
    assert parse_order(data).status is OrderStatus.NEW


def test_status_is_normalized():
    assert parse_order({**VALID, "status": "  SHIPPED "}).status is OrderStatus.SHIPPED


@pytest.mark.parametrize("email", ["not-an-email", "a@", "@b.com", ""])
def test_invalid_email(email):
    with pytest.raises(ValidationError):
        parse_order({**VALID, "customer_email": email})


@pytest.mark.parametrize("total", [0, -5, "-0.01"])
def test_total_must_be_positive(total):
    with pytest.raises(ValidationError):
        parse_order({**VALID, "total": total})


def test_total_too_many_decimals():
    with pytest.raises(ValidationError):
        parse_order({**VALID, "total": "1.999"})


def test_invalid_status():
    with pytest.raises(ValidationError):
        parse_order({**VALID, "status": "refunded"})


def test_invalid_id():
    with pytest.raises(ValidationError):
        parse_order({**VALID, "id": 0})


def test_validation_error_is_value_error_subclass():
    with pytest.raises(ValueError):
        parse_order({**VALID, "total": 0})


def test_from_orm_object():
    row = SimpleNamespace(id=7, customer_email="db@example.com", total=Decimal("10.00"), status="new")
    assert parse_order(row).id == 7


def test_serialization():
    order = parse_order(VALID)
    as_dict = order_to_dict(order)
    assert as_dict["status"] is OrderStatus.PAID
    payload = json.loads(order_to_json(order))
    assert payload["status"] == "paid"
    assert payload["customer_email"] == "user@example.com"
