import abc
import argparse

import overrides

from core.utils import time as time_utils


class ArgumentsBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def add_arguments(parser: argparse.ArgumentParser):
        """Define arguments here"""

    @classmethod
    def parse(cls):
        """Parse all arguments and return"""
        parser = argparse.ArgumentParser(
            description=f"Configuration for {cls.__name__}",
        )
        cls.add_arguments(parser)
        return parser.parse_args()


class BasicDBTaskArguments(ArgumentsBase):
    @staticmethod
    @overrides.override
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--database",
            type=str,
            required=True,
        )

        parser.add_argument(
            "--write-database",
            type=str,
            default=None,
        )


class BacktestArguments(BasicDBTaskArguments):
    @staticmethod
    @overrides.override
    def add_arguments(parser: argparse.ArgumentParser):
        BasicDBTaskArguments.add_arguments(parser)

        parser.add_argument(
            "--start-date",
            type=time_utils.DateTimeFormatter.DATE.parse,
            required=True,
        )
        parser.add_argument(
            "--window",
            type=int,
            required=True,
        )

        parser.add_argument("--skip-info", action="store_true")
        parser.add_argument("--skip-quote", action="store_true")


class PipelineTaskArguments(BasicDBTaskArguments):
    """PipelineTaskArguments"""

    @staticmethod
    @overrides.override
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--finance-database",
            type=str,
            required=True,
        )

        parser.add_argument(
            "--trade-database",
            type=str,
            required=True,
        )

        parser.add_argument(
            "--top-k",
            type=int,
            default=30,
        )

        parser.add_argument("--skip-info", action="store_true")
        parser.add_argument("--skip-quote", action="store_true")
