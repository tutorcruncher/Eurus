from unittest.mock import MagicMock
import logging

from app.utils.logging import Logger


def test_logger_debug_and_error(monkeypatch):
    # Disable logfire
    monkeypatch.setattr('app.utils.logging.logfire', None, raising=False)
    import types

    monkeypatch.setattr(
        'app.utils.logging.get_settings',
        lambda: types.SimpleNamespace(dev=False, logfire_token=''),
    )

    lg = Logger('debug_logger')
    mock_std = MagicMock(spec=logging.Logger)
    lg.logger = mock_std

    lg.debug('Processing', step=1)
    lg.error('Failed', code=500)

    # Ensure both methods were forwarded.
    mock_std.debug.assert_called_once()
    mock_std.error.assert_called_once()

    # Check formatting contains context.
    debug_msg = mock_std.debug.call_args.args[0]
    error_msg = mock_std.error.call_args.args[0]

    assert 'step=1' in debug_msg
    assert 'code=500' in error_msg
