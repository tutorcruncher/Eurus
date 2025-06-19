from unittest.mock import MagicMock

import logging

from app.utils.logging import Logger


def test_logger_format_and_info(monkeypatch):
    """Verify that the custom ``Logger`` properly formats contextual messages and delegates to the underlying stdlib logger."""

    # Ensure ``logfire`` is disabled so that the logger falls back to stdlib logging.
    monkeypatch.setattr('app.utils.logging.logfire', None, raising=False)
    import types

    monkeypatch.setattr(
        'app.utils.logging.get_settings',
        lambda: types.SimpleNamespace(dev=False, logfire_token=''),
    )

    custom_logger = Logger('test_logger')

    # Replace the underlying stdlib logger with a mock so we can verify the call.
    mocked_std_logger = MagicMock(spec=logging.Logger)
    custom_logger.logger = mocked_std_logger

    # Send a message with contextual kwargs (ordering of kwargs is not important).
    custom_logger.info('User login', user='alice', action='login')

    # Ensure the stdlib ``info`` method was called exactly once.
    mocked_std_logger.info.assert_called_once()

    # Extract the formatted message that was sent to the stdlib logger.
    called_message = mocked_std_logger.info.call_args.args[0]

    assert 'User login' in called_message
    # The formatted context should be included in the message.
    assert 'user=alice' in called_message
    assert 'action=login' in called_message
