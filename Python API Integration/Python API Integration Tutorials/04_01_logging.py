# 4_01_logging.py — Python Logging: Loggers, Handlers, Formatters, and Configuration

import logging
from logging import LogRecord
import sys

# =============================================
# LOGGER HIERARCHY
# =============================================
# Loggers are organized in a tree — child loggers propagate to parent by default.
# root is the top-level ancestor; all named loggers descend from it.
root_logger = logging.getLogger()
# print(f"Root Logger: name={root_logger.name}, Level={logging.getLevelName(root_logger.level)}")

app_logger = logging.getLogger("app")
# print(f"App Logger: name={app_logger.name}, Level={logging.getLevelName(app_logger.level)}, Parent={app_logger.parent}")

# "app.network" is a child of "app" — inherits its level if not explicitly set
network_logger = logging.getLogger("app.network")
# print(f"Network Logger: name={network_logger.name}, Level={logging.getLevelName(network_logger.level)}, Parent={network_logger.parent.name}")


# =============================================
# LOGRECORD
# =============================================
# LogRecord is the internal object created each time a log call is made.
# Understanding its fields helps when writing custom formatters or filters.
record = LogRecord(
    name="app.network",
    level=logging.ERROR,
    pathname="/path/to/file.py",
    lineno=43,
    msg="My Log Message",
    args=(),
    exc_info=None
)

# print("LogRecord contents:")

# for attr in ("name","levelname","pathname","msg"):
#     print(f" {attr}=> {getattr(record, attr)}")



# =============================================
# HANDLERS
# =============================================
# Handlers decide where log output goes — terminal, file, network, etc.
# A logger can have multiple handlers, each with its own level.
demo_logger = logging.getLogger("handler_demo")

demo_logger.setLevel(logging.DEBUG)  # Logger gate — only messages >= DEBUG reach handlers

# Check the handler [] means no handler yet
# print(demo_logger.handlers)

# print(logging.getLevelName(demo_logger.level))

# StreamHandler — output goes to terminal via sys.stdout
stream_handler = logging.StreamHandler(sys.stdout)

# FileHandler — output written to file; "w" overwrites on each run
file_handler = logging.FileHandler("./Tutorial/process.log","w")

# Handler-level gates — each handler filters independently
stream_handler.setLevel(logging.WARNING)  # WARNING and above levels → terminal
file_handler.setLevel(logging.INFO)       # INFO and above levels → file

demo_logger.addHandler(stream_handler)
demo_logger.addHandler(file_handler)

# print(demo_logger.handlers)

# demo_logger.debug("Debug Message: Dropped")          # below both handler levels — silent
# demo_logger.warning("Warning Message: File and Stream both")
# demo_logger.error("Error Message: File and Stream both")
# demo_logger.info("Info Message: File Only")           # below stream threshold


# =============================================
# FORMATTER
# =============================================
# Formatters control the final string shape of each log line.
# %(asctime)s adds a human-readable timestamp.
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

stream_handler.setFormatter(formatter)

# demo_logger.warning("Formatted warning")


# =============================================
# FILEHANDLER — APPEND MODE
# =============================================
# "a" mode appends to the existing file — useful for persistent logs across runs.
print("basic logging with FileHandler")
print("___\n")

basic_logger = logging.getLogger("file.basic")
basic_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("./Tutorial/process.log","a")  # "a" = append, not overwrite
file_handler.setLevel(logging.INFO)

basic_logger.addHandler(file_handler)

# basic_logger.info("INFO: will append to file")

# Skipping for Now udemy video 100, 101
# print("basic logging with RotatingFileHandler")
# print("___\n")

# print("basic logging with TimeRotatingFileHandler")
# print("___\n")


# =============================================
# STRUCTURED LOGGING — python-json-logger
# =============================================
# Outputs logs as JSON — easier to parse in log aggregators (e.g. Datadog, ELK).
# rename_fields maps default key names to custom ones in the JSON output.
print("Configuring python-json-logger")
print("___\n")

json_logger = logging.getLogger("demo.json")
json_logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)

# instead of using %(asctime)s we use {} style
json_formatter = json.JsonFormatter(
    "{asctime}{levelname}{message}",
    style="{",
    json_indent=4,
    rename_fields={"asctime":"timestamp","levelname":"level"}
)

stream_handler.setFormatter(json_formatter)

json_logger.addHandler(stream_handler)

# json_logger.info("Structered logging initialized")


# =============================================
# EXTRA CONTEXT IN LOG MESSAGES
# =============================================
# Pass a dict via extra= to attach structured fields to a log record.
# Keys in extra must not clash with built-in LogRecord attributes.
print("___\n")
print("Logging with Extra Context")
print("___\n")

extra_context = {
    "user_id": "devops1",
    "request_id": "request-1234ac",
    "source_ip": "10.0.0.5"
}

# Nested under "context_data" to avoid key conflicts with LogRecord attributes
extra_context_2 = {
    "context_data": {
        "user_id": "devops1",
        "request_id": "request-1234ac",
        "source_ip": "10.0.0.5"
    }
}

# json_logger.warning(
#     "Request took longet than 5s to complete",
#     extra=extra_context
# )

# json_logger.error(
#     "Request took longet than 5s to complete",
#     extra=extra_context_2
# )

# =============================================
# LOGGING EXCEPTIONS AS JSON
# =============================================
# .exception() logs at ERROR level and automatically attaches the full traceback.
print("___\n")
print("Logging Exception as JSON")
print("___\n")

# try:
#     result = 1/0
# except ZeroDivisionError:
#     json_logger.exception("unexpected calculation error", extra={"operation":"division"})

# =============================================
# DECLARATIVE CONFIG — dictConfig
# =============================================
# Define the entire logging setup as a dict — cleaner than scattered basicConfig calls.
# disable_existing_loggers=False keeps loggers created before this config intact.
print("___\n")
print("Declarative Logging Configuration using dictConfig")
print("___\n")

import logging
import logging.config

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,  # keeps loggers already created
    "formatters": {
        "simple": {
            "format": "%(levelname)-8s - %(message)s"  # left-aligned 8-char level name
        }
    },
    "handlers":
    {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"  # ext:// references Python objects by dotted path
        }
    },
    "loggers":
    {
        "config.dict": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }
}

# logging.config.dictConfig(dict_config)
# config_logger = logging.getLogger("config.dict")

# config_logger.debug("dictConfig setup successfully")
# config_logger.info("Info goes to console")


# =============================================
# DECLARATIVE CONFIG — JSON file
# =============================================
# Same structure as dictConfig but loaded from an external file — keeps config out of code.
print("___\n")
print("Declarative Logging Configuration using JSON file")
print("___\n")

import json

config_path = "./Tutorial/logging_conf.json"
with open(config_path,"r") as config_file:
    json_config = json.load(config_file)

# logging.config.dictConfig(json_config)

# config_logger = logging.getLogger("config.json")

# config_logger.debug("Json Config setup successfully")
# config_logger.info("Info goes to console")


# =============================================
# DYNAMIC CONFIG BUILDING
# =============================================
# Build the config dict programmatically — useful when handler setup depends on runtime flags.
print("___\n")
print("Dynamically Building Config.")
print("___\n")

base_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {},
    "handlers":{},
    "loggers": {}
}

# adding values dynamically
base_config["formatters"]["simple"] = {"format": "%(levelname)-8s - %(message)s"}
base_config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }

def is_debug():
    return True

base_config["loggers"]["config.dynamic"] = {
            "level": "WARNING",
            "handlers": ["console"]
        }

# can add loops to loop through all the loggers and to change their level
if is_debug():
    base_config["loggers"]["config.dynamic"]["level"] = "DEBUG"

logging.config.dictConfig(base_config)

config_logger = logging.getLogger("config.dynamic")

config_logger.debug("Dynamic Config setup successfully")
config_logger.info("Info goes to console")