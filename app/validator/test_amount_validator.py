import pytest

from app.validator.amount_validator import (
    ValidationError,
    ValidationResult,
    validate_maximum_cash_amount,
)

# Creation tests

def test_validation_result_creation_with_success():
    result = ValidationResult(success=True)
    assert result.is_success is True
    assert result.error_messages == []


def test_validation_result_creation_with_error():
    result = ValidationResult(success=False, error_messages=["Invalid amount"])
    assert result.is_success is False
    assert result.error_messages == ["Invalid amount"]


def test_validation_result_creation_with_error_multiple_messages():
    messages = ["Amount too large", "Amount must be positive"]
    result = ValidationResult(success=False, error_messages=messages)
    assert result.is_success is False
    assert result.error_messages == messages


# success() classmethod tests

def test_validation_result_success_classmethod():
    result = ValidationResult.success()
    assert result.is_success is True
    assert result.error_messages == []


# error() classmethod tests

def test_validation_result_error_classmethod():
    result = ValidationResult.error("Amount cannot exceed 10000.")
    assert result.is_success is False
    assert result.error_messages == ["Amount cannot exceed 10000."]


# raise_if_error() tests

def test_raise_if_error_does_not_raise_on_success():
    result = ValidationResult.success()
    result.raise_if_error()  # Should not raise


def test_raise_if_error_raises_on_error():
    result = ValidationResult.error("Amount is invalid")
    with pytest.raises(ValidationError) as exc_info:
        result.raise_if_error()
    assert "Validation failed: Amount is invalid" in str(exc_info.value)


def test_raise_if_error_raises_with_multiple_errors():
    result = ValidationResult(
        success=False,
        error_messages=["Error 1", "Error 2"]
    )
    with pytest.raises(ValidationError) as exc_info:
        result.raise_if_error()
    assert "Error 1" in str(exc_info.value)
    assert "Error 2" in str(exc_info.value)


# join() tests

def test_join_all_successful():
    results = [
        ValidationResult.success(),
        ValidationResult.success(),
        ValidationResult.success()
    ]
    joined = ValidationResult.join(results)
    assert joined.is_success is True
    assert joined.error_messages == []


def test_join_some_successful_some_unsuccessful():
    results = [
        ValidationResult.success(),
        ValidationResult.error("First error"),
        ValidationResult.success(),
        ValidationResult.error("Second error")
    ]
    joined = ValidationResult.join(results)
    assert joined.is_success is False
    assert len(joined.error_messages) == 2
    assert ["First error"] in joined.error_messages
    assert ["Second error"] in joined.error_messages


def test_join_all_unsuccessful():
    results = [
        ValidationResult.error("Error 1"),
        ValidationResult.error("Error 2"),
        ValidationResult.error("Error 3")
    ]
    joined = ValidationResult.join(results)
    assert joined.is_success is False
    assert len(joined.error_messages) == 3
    assert ["Error 1"] in joined.error_messages
    assert ["Error 2"] in joined.error_messages
    assert ["Error 3"] in joined.error_messages


def test_join_empty_list():
    results = []
    joined = ValidationResult.join(results)
    assert joined.is_success is True
    assert joined.error_messages == []


def test_join_single_successful():
    results = [ValidationResult.success()]
    joined = ValidationResult.join(results)
    assert joined.is_success is True
    assert joined.error_messages == []


def test_join_single_unsuccessful():
    results = [ValidationResult.error("Single error")]
    joined = ValidationResult.join(results)
    assert joined.is_success is False
    assert ["Single error"] in joined.error_messages


def test_amount_validator_raises_on_too_large():
    result = validate_maximum_cash_amount(20000)
    assert result.is_success is False
    assert "Amount cannot exceed 10000." in result.error_messages


def test_amount_validator_ok():
    result = validate_maximum_cash_amount(5000)
    assert result.is_success is True
    assert result.error_messages == []
