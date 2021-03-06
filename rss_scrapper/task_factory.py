# -*- coding: utf-8 -*-
import logging

import rss_scrapper.tasks.concat
import rss_scrapper.tasks.dummy
import rss_scrapper.tasks.dump
import rss_scrapper.tasks.execute
import rss_scrapper.tasks.fork
import rss_scrapper.tasks.get
import rss_scrapper.tasks.print
import rss_scrapper.tasks.regex
import rss_scrapper.tasks.rss_gen
import rss_scrapper.tasks.selector
import rss_scrapper.tasks.text
import rss_scrapper.tasks.write
import rss_scrapper.tasks.xpath
from rss_scrapper.errors import ConfigurationError

logger = logging.getLogger(__name__)
TASKS = [
    rss_scrapper.tasks.execute.ExecuteTask,
    rss_scrapper.tasks.dummy.DummyTask,
    rss_scrapper.tasks.print.PrintTask,
    rss_scrapper.tasks.dump.DumpTask,
    rss_scrapper.tasks.text.TextTask,
    rss_scrapper.tasks.get.GetTask,
    rss_scrapper.tasks.xpath.XPathTask,
    rss_scrapper.tasks.selector.SelectorTask,
    rss_scrapper.tasks.regex.RegexTask,
    rss_scrapper.tasks.rss_gen.RssGenTask,
    rss_scrapper.tasks.write.WriteTask,
    rss_scrapper.tasks.write.ReadTask,
    rss_scrapper.tasks.concat.ConcatTask,
    rss_scrapper.tasks.fork.ForkTask,
]
TASKS_MAP = {task.name: task for task in TASKS}


def create_task(name, conf=None, parent_task=None):
    if name not in TASKS_MAP:
        raise ConfigurationError("the task '%s' does not exist" % name)
    else:
        task_class = TASKS_MAP[name]
        return task_class(conf=conf, parent_task=parent_task)


def create_tasks(tasks_conf, parent_task=None):
    tasks = []

    if not isinstance(tasks_conf, list):
        logger.error("Expected a task list and got a %s" % type(tasks_conf))
        raise ConfigurationError("no task list found", conf=tasks_conf)

    for task_conf in tasks_conf:
        if isinstance(task_conf, str):
            tasks.append(create_task(task_conf, parent_task=parent_task))

        elif isinstance(task_conf, dict):
            for task_name, task_args in task_conf.items():
                validate_task_name(task_name)

                try:
                    tasks.append(create_task(task_name, task_args,
                                             parent_task=parent_task))
                except ConfigurationError as e:
                    e.conf = task_conf
                    raise e
        else:
            logger.error("Expected a task and got a %s at %s" %
                         (type(task_conf), task_conf))
            raise ConfigurationError("incorrect task definition",
                                     conf=task_conf)

    return tasks


def execute_configuration(conf, dry_run=False):
    if "feeds" not in conf:
        logger.error("The configuration lacks a feeds collection,"
                     " the yaml file should have a 'feeds' dictionary"
                     " at the top level")
        raise ConfigurationError("no feeds found", conf=conf)

    feeds = conf["feeds"]
    if not isinstance(feeds, dict):
        raise ConfigurationError("'feeds' should be a dictionary instead of %s"
                                 % type(feeds))

    logger.debug("Found %d feed(s)" % len(feeds))

    # We create every task before executing any for validation purposes
    tasks = []
    for feed_name, tasks_conf in feeds.items():
        logger.info("Validating feed %s" % feed_name)
        tasks.append((feed_name, create_task('execute', tasks_conf)))

    res = {}
    for (feed_name, task) in tasks:
        if not dry_run:
            logger.info("Executing feed %s" % feed_name)

            task_res = task.execute(None)

            task_res_data = list(task_res)

            if len(task_res_data) == 0:
                logger.info("The feed %s has not returned any data,"
                            " nothing has been generated" % feed_name)

            res[feed_name] = task_res_data
    return res


def validate_task_name(task_name):
    if not isinstance(task_name, str):
        logger.error("Expected a task name and got a %s"
                     % type(task_name))
        if isinstance(task_name, dict):
            logger.error("Is there an indentation problem ? "
                         "The task's arguments should have one more "
                         "indentation level than its name")
        raise ConfigurationError("task name should be a string",
                                 conf=task_name)
