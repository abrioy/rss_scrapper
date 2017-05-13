# -*- coding: utf-8 -*-
import logging
import yaml
from yaml import YAMLError

logger = logging.getLogger(__name__)


def load_yaml_from_path(yaml_path):
    with open(yaml_path, 'r') as yaml_file:
        return load_yaml_file(yaml_file)


def load_yaml_file(yaml_file):
    logger.debug("Loading configuration from: %s" % yaml_file.name)
    try:
        return yaml.load(yaml_file)
    except YAMLError as e:
        logger.error("Error while parsing the configuration file: %s %s"
                     % (type(e).__name__, e))
        raise e


def validate_task_name(task_name):
    if not isinstance(task_name, str):
        logger.error("Expected a task name and got a %s"
                     % type(task_name))
        if isinstance(task_name, dict):
            logger.error("Is there an indentation problem ? "
                         "The task's arguments should have one more "
                         "indentation level than its name")
        raise ConfigurationError("task name should be a string",
                                 task_name)


class ConfigurationError(Exception):
    none = None
    task = None

    def __init__(self, message, node=None, task=None):
        super(ConfigurationError, self).__init__(message)

        self.node = node
        if task is not None:
            self.task = task

    def __str__(self):
        message = ""

        if self.task:
            message += "[task: " + self.task.get_path() + "] "

        message += super(ConfigurationError, self).__str__()

        if self.node is not None:
            message += " - invalid configuration: \n%s" % self.node

        return message
