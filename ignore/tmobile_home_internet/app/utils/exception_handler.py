from logging import getLogger, Logger
from traceback import format_exc
from typing import Callable, Optional, Any
from box  import Box
from os import getenv


LOG_PATH = getenv('LOG_PATH') or __file__
LOGGER = getLogger(LOG_PATH)


def exception_handler(
    logger: Logger = LOGGER,
) -> Optional[Any]:
    def wrapper(function: Callable) -> Optional[Any]:
        log = Box({'function': function.__name__})
        def handler(*args, **kwargs) -> Optional[Any]:
            result = None
            log_level = 'info'

            try:
                result = function(*args, **kwargs)
            except Exception as e:
                log_level = 'exception'
                log.inputs = Box({
                    'args': args,
                    'kwargs': kwargs,
                })

                log.exception = Box({
                    'type': type(e).__name__,
                    'description': str(e),
                    'traceback': format_exc().split('\n'),
                })

                error_description = str(e).replace(' ', '+')
                url = f"https://stackoverflow.com/search?q={error_description}"
                log.stackoverflow = url
            
            # log status of function execution
            getattr(logger, log_level)(log)
            return result

        return handler
    return wrapper


if __name__ == '__main__':
    @exception_handler()
    def add(a: int, b: int) -> Optional[int]:
        '''Adds two integers'''
        return a + b

    result = add(1, 1)
    assert result == 2

    result = add(1, None)
    assert result == None