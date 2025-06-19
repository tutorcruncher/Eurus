import logging
from app.utils.settings import get_settings
import logfire


class Logger:
    def __init__(self, name: str = 'eurus'):
        self.settings = get_settings()
        self.name = name
        self.use_logfire = not self.settings.dev and self.settings.logfire_token

        if self.use_logfire:
            if not hasattr(logfire, '_configured'):
                logfire.configure(service_name='eurus')
                logfire._configured = True
        else:
            self.logger = logging.getLogger(name)
            if not self.logger.handlers:
                self.logger.setLevel(logging.INFO)
                handler = logging.StreamHandler()
                handler.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

    def _format_message(self, message: str, **kwargs) -> str:
        if kwargs:
            context = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
            return f'{message} | {context}'
        return message

    def info(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.info(message, **kwargs)
        else:
            self.logger.info(self._format_message(message, **kwargs))

    def debug(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.debug(message, **kwargs)
        else:
            self.logger.debug(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.warning(message, **kwargs)
        else:
            self.logger.warning(self._format_message(message, **kwargs))

    def warn(self, message: str, **kwargs) -> None:
        self.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.error(message, **kwargs)
        else:
            self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.critical(message, **kwargs)
        else:
            self.logger.critical(self._format_message(message, **kwargs))

    def exception(self, message: str, **kwargs) -> None:
        if self.use_logfire:
            logfire.exception(message, **kwargs)
        else:
            self.logger.exception(self._format_message(message, **kwargs))


logger = Logger()
