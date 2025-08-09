import abc
import argparse

import overrides


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
