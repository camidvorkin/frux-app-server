import datetime
import logging
from traceback import format_exception

from graphql.execution.utils import ExecutionContext
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


log_handler = logging.StreamHandler()

formatter = jsonlogger.JsonFormatter()
log_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


class LoggingMiddleware(object):
    def on_error(self, info):
        def f(error):
            logger.warning('%s - %s', info.path[0], error)
            raise error

        return f

    def resolve(self, nextn, root, info, **args):
        if not root:
            logger.info(info.path[0])
            logger.debug(info.context.data)  # full request
        return nextn(root, info, **args).catch(self.on_error(info))


def new_report_error(self, error, traceback=None):
    if not (hasattr(error, "original_error")):
        exception = format_exception(
            type(error), error, getattr(error, "stack", None) or traceback
        )
        logger.error("".join(exception))

    self.errors.append(error)


# Monkey patch report_error method from ExecutionContext class
ExecutionContext.report_error = new_report_error
