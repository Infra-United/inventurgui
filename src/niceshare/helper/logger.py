import logging
from logging import Logger

import niceshare


class RelativeSeconds(logging.Formatter):
    def format(self, record):
        record.relativeCreated = record.relativeCreated // 1000
        return super().format(record)


formatter = RelativeSeconds("%(relativeCreated)ds %(levelname)s %(name)s.%(module)s.%(funcName)s: %(message)s")

# Get Logger and set log level
logging.basicConfig()
LOGGER: Logger = logging.getLogger(name=niceshare.__name__)
LOGGER.root.handlers[0].setFormatter(formatter)
