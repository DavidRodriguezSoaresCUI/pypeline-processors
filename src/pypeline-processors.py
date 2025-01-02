"""Collection of built-in processors
"""
import logging
from time import time
from typing import Any
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from DRSlib.execute import execute
from pypeline.activity import (
    Activity,
    ActivityData,
    ExitState,
)
from pypeline.processor import Processor


@dataclass
class ActivityArchivalActivity(ActivityData):
    """Dumb class, needs to be JSON serializable"""

    processed_activities_path: str
    """Where processed activities are located"""
    archive_dir_path: str
    """Where to put archives"""


class ActivityArchivalProcessor(Processor):
    """Uses a bot to post messages on Telegram
    Expects activity to contain a serialized TelegramMessages object
    """

    INPUT_ACTIVITY_TYPE = "ArchiveActivities"
    OUTPUT_ACTIVITY_TYPES: set[str] = set()

    @classmethod
    def execute(cls, activity: Activity, log: logging.Logger) -> ExitState:
        """Reads TelegramMessages from activity and post messages to target chat as bot"""
        activity_data = ActivityArchivalActivity.from_json(activity.data)

        processed_activities_path = Path(activity_data.processed_activities_path)
        if (
            not processed_activities_path.exists()
            or not processed_activities_path.is_dir()
        ):
            log.error(
                "Invalid path given for processed activities directory '%s'",
                processed_activities_path,
            )
            return ExitState.error(f"Invalid path '{processed_activities_path}'")
        archive_dir_path = Path(activity_data.archive_dir_path)
        if not archive_dir_path.exists():
            archive_dir_path.mkdir()
        elif not archive_dir_path.is_dir():
            log.error(
                "Invalid path given for archived activities directory '%s'",
                archive_dir_path,
            )
            return ExitState.error(f"Invalid path '{archive_dir_path}'")

        processed_activity_files = list(processed_activities_path.glob("activity.*"))
        if not processed_activity_files:
            log.info("No activity found in '%s'", processed_activities_path)
            return ExitState.success("Nothing to do", actual_work_was_done=False)

        timestamp = datetime.now().isoformat().replace(":", "-")
        archive_path = archive_dir_path / f"activities.{timestamp}.zip"
        log.info(
            "Writing %s files to archive file '%s'",
            len(processed_activity_files),
            archive_path,
        )

        with zipfile.ZipFile(
            archive_path, mode="w", compression=zipfile.ZIP_BZIP2, compresslevel=4
        ) as archive:
            for _file in processed_activity_files:
                archive.write(_file)
                _file.unlink()

        return ExitState.success()


@dataclass
class CmdExecuteActivity(ActivityData):
    """Dumb class, needs to be JSON serializable"""

    command_parts: list[Any]
    """If true, files with CRC32 tag will be included"""
    expected_output: list[str]
    """If not empty, one of the text listed must be found in standard output streams,
    otherwise the activity will go into definitive error and push a message to telegram"""
    unexpected_output: list[str]
    """If not empty, if one of the text listed is found in standard output streams,
    then the activity will go into definitive error and push a message to telegram"""


class CmdExecuteProcessor(Processor):
    """Verifies file integrity by computing file's hashes and comparing to the CRC32 tag in file name"""

    INPUT_ACTIVITY_TYPE = "CmdExecute"
    OUTPUT_ACTIVITY_TYPES = set()

    @classmethod
    def execute(cls, activity: Activity, log: logging.Logger) -> ExitState:
        """Activity contains details about the verification to do"""
        _activity = CmdExecuteActivity.from_json(activity.data)
        cmd = _activity.command_parts
        log.info("Will execute command %s", cmd)
        t0 = time()
        std_output = execute(cmd)
        log.info("Command executed in %.1fs; output is %s", time() - t0, std_output)

        # Check ouput streams
        expected_output = _activity.expected_output
        unexpected_output = _activity.unexpected_output
        if expected_output and (
            not any(
                expected in stream
                for expected in expected_output
                for stream in std_output.values()
            )
            or any(
                unexpected in stream
                for unexpected in unexpected_output
                for stream in std_output.values()
            )
        ):
            return ExitState.error(f"Execution failed: {std_output=}")

        return ExitState.success()
