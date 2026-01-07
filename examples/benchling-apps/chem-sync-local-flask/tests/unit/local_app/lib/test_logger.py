import logging

from local_app.lib.logger import get_logger


class TestLogger:
    def test_logger_with_name(self) -> None:
        logger = get_logger("test-logger")
        assert logger.name == "test-logger"
        assert logger.level == logging.INFO

    def test_logger_with_level(self, monkeypatch) -> None:
        with monkeypatch.context() as context:
            context.setenv("BENCHLING_APP_LOG_LEVEL", "DEBUG")
            logger = get_logger()
        assert logger.name == "benchling-app"
        assert logger.level == logging.DEBUG
