import logging.config
import os


def configure_logging(telemetry_path, debug_enabled=False):
    if not os.path.isabs(telemetry_path):
        raise ValueError('Logs path must be absolute')
    os.makedirs(telemetry_path, exist_ok=True)
    logging.config.dictConfig(get_logging_conf(telemetry_path, debug_enabled))


def get_logging_conf(telemetry_path, debug_enabled=False):
    return {
        "version": 1,
        "incremental": False,
        "disable_existing_loggers": False,
        "root": {
            "level": "DEBUG" if debug_enabled else "INFO",
            "handlers": [
                "stdout",
                "srderr"
            ]
        },
        "loggers": {
            "trackme.telemetry": {
                "level": "INFO",
                "handlers": [
                    "telemetry"
                ]
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "srderr": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
                "level": "ERROR"
            },
            "telemetry": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "plain",
                "filename": os.path.join(telemetry_path, "telemetry.txt"),
                "when": "midnight",
                "utc": True
            }
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s %(name)-s[%(process)d]: %(levelname)-8s %(message)s"
            },
            "plain": {
                "format": "%(message)s"
            }
        }
    }
