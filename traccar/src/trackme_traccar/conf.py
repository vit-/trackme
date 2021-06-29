import logging.config


def configure_logging(debug_enabled=False):
    logging.config.dictConfig(get_logging_conf(debug_enabled))


def get_logging_conf(debug_enabled=False):
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
