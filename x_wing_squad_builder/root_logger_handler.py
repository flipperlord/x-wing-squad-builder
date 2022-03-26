import logging
from PySide6.QtCore import Signal, QObject


class RootLoggerHandler(logging.Handler):
    def __init__(self, **kwargs):
        super().__init__()
        self.sigLog = Log()
        format_ = kwargs.pop('format', "%(asctime)s - %(levelname)s - %(message)s")
        self.setFormatter(logging.Formatter(format_))
        logging.basicConfig(format=format_, **kwargs)
        self.logger.addHandler(self)

    def emit(self, record):
        msg = self.format(record)
        self.sigLog.signal.emit(msg)

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger()


class Log(QObject):
    signal = Signal(str)

    def __init__(self):
        super().__init__()
