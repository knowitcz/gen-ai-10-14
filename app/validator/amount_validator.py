from typing import Protocol


class ValidationError(ValueError):
    pass


class ValidationResult:
    def __init__(self, *, success: bool, error_messages: list[str] = None):
        self._success = success
        self._error_messages = error_messages or []

    @classmethod
    def success(cls):
        return cls(success=True)

    @classmethod
    def error(cls, message: str):
        return cls(success=False, error_messages=[message])

    @property
    def is_success(self) -> bool:
        return self._success

    @property
    def error_messages(self) -> list[str]:
        return self._error_messages

    @classmethod
    def join(cls, results: list['ValidationResult']) -> 'ValidationResult':
        if all(result.is_success for result in results):
            return cls.success()
        error_messages = [result.error_messages for result in results if not result.is_success]
        return cls(success=False, error_messages=error_messages)

    def raise_if_error(self):
        if not self.is_success:
            raise ValidationError("Validation failed: " + ", ".join(self.error_messages))


class AmountValidator(Protocol):
    def __call__(self, amount: int) -> ValidationResult:
        ...


def validate_maximum_cash_amount(amount: int) -> ValidationResult:
    if amount > 10000:
        return ValidationResult.error("Amount cannot exceed 10000.")
    return ValidationResult.success()
