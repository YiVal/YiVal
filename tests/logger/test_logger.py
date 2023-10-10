from yival.logger.token_logger import TokenLogger


def test_singleton_property():
    logger1 = TokenLogger()
    logger2 = TokenLogger()
    assert logger1 is logger2


def test_log_tokens():
    logger = TokenLogger()
    logger.reset()  # Resetting to start with a clean slate
    logger.log(10)
    assert logger.get_current_usage() == 10
    logger.log(5)
    assert logger.get_current_usage() == 15


def test_get_current_usage():
    logger = TokenLogger()
    logger.reset()  # Resetting to start with a clean slate
    assert logger.get_current_usage() == 0
    logger.log(25)
    assert logger.get_current_usage() == 25


def test_reset():
    logger = TokenLogger()
    logger.log(50)
    logger.reset()
    assert logger.get_current_usage() == 0
