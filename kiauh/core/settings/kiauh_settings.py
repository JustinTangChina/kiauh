# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #
from __future__ import annotations

from core.logger import DialogType, Logger
from core.submodules.simple_config_parser.src.simple_config_parser.simple_config_parser import (
    NoOptionError,
    NoSectionError,
    SimpleConfigParser,
)
from utils.sys_utils import kill

from kiauh import PROJECT_ROOT

DEFAULT_CFG = PROJECT_ROOT.joinpath("default.kiauh.cfg")
CUSTOM_CFG = PROJECT_ROOT.joinpath("kiauh.cfg")


class AppSettings:
    def __init__(self) -> None:
        self.backup_before_update = None


class KlipperSettings:
    def __init__(self) -> None:
        self.repo_url = None
        self.branch = None


class MoonrakerSettings:
    def __init__(self) -> None:
        self.repo_url = None
        self.branch = None


class MainsailSettings:
    def __init__(self) -> None:
        self.port = None
        self.unstable_releases = None


class FluiddSettings:
    def __init__(self) -> None:
        self.port = None
        self.unstable_releases = None


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class KiauhSettings:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "KiauhSettings":
        if cls._instance is None:
            cls._instance = super(KiauhSettings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "__initialized"):
            self.__initialized = False
        if self.__initialized:
            return
        self.__initialized = True
        self.config = SimpleConfigParser()
        self.kiauh = AppSettings()
        self.klipper = KlipperSettings()
        self.moonraker = MoonrakerSettings()
        self.mainsail = MainsailSettings()
        self.fluidd = FluiddSettings()

        self.kiauh.backup_before_update = None
        self.klipper.repo_url = None
        self.klipper.branch = None
        self.moonraker.repo_url = None
        self.moonraker.branch = None
        self.mainsail.port = None
        self.mainsail.unstable_releases = None
        self.fluidd.port = None
        self.fluidd.unstable_releases = None

        self._load_config()

    def get(self, section: str, option: str) -> str | int | bool:
        """
        Get a value from the settings state by providing the section and option name as strings.
        Prefer direct access to the properties, as it is usually safer!
        :param section: The section name as string.
        :param option: The option name as string.
        :return: The value of the option as string, int or bool.
        """

        try:
            section = getattr(self, section)
            value = getattr(section, option)
            return value  # type: ignore
        except AttributeError:
            raise

    def set(self, section: str, option: str, value: str | int | bool) -> None:
        """
        Set a value in the settings state by providing the section and option name as strings.
        Prefer direct access to the properties, as it is usually safer!
        :param section: The section name as string.
        :param option: The option name as string.
        :param value: The value to set as string, int or bool.
        """
        try:
            section = getattr(self, section)
            section.option = value  # type: ignore
        except AttributeError:
            raise

    def save(self) -> None:
        self._set_config_options()
        self.config.write(CUSTOM_CFG)
        self._load_config()

    def _load_config(self) -> None:
        if not CUSTOM_CFG.exists() and not DEFAULT_CFG.exists():
            self._kill()

        cfg = CUSTOM_CFG if CUSTOM_CFG.exists() else DEFAULT_CFG
        self.config.read(cfg)

        self._validate_cfg()
        self._read_settings()

    def _validate_cfg(self) -> None:
        try:
            self._validate_bool("kiauh", "backup_before_update")

            self._validate_str("klipper", "repo_url")
            self._validate_str("klipper", "branch")

            self._validate_int("mainsail", "port")
            self._validate_bool("mainsail", "unstable_releases")

            self._validate_int("fluidd", "port")
            self._validate_bool("fluidd", "unstable_releases")

        except ValueError:
            err = f"Invalid value for option '{self._v_option}' in section '{self._v_section}'"
            Logger.print_error(err)
            kill()
        except NoSectionError:
            err = f"Missing section '{self._v_section}' in config file"
            Logger.print_error(err)
            kill()
        except NoOptionError:
            err = f"Missing option '{self._v_option}' in section '{self._v_section}'"
            Logger.print_error(err)
            kill()

    def _validate_bool(self, section: str, option: str) -> None:
        self._v_section, self._v_option = (section, option)
        bool(self.config.getboolean(section, option))

    def _validate_int(self, section: str, option: str) -> None:
        self._v_section, self._v_option = (section, option)
        int(self.config.getint(section, option))

    def _validate_str(self, section: str, option: str) -> None:
        self._v_section, self._v_option = (section, option)
        v = self.config.get(section, option)
        if v.isdigit() or v.lower() == "true" or v.lower() == "false":
            raise ValueError

    def _read_settings(self) -> None:
        self.kiauh.backup_before_update = self.config.getboolean(
            "kiauh", "backup_before_update"
        )
        self.klipper.repo_url = self.config.get("klipper", "repo_url")
        self.klipper.branch = self.config.get("klipper", "branch")
        self.moonraker.repo_url = self.config.get("moonraker", "repo_url")
        self.moonraker.branch = self.config.get("moonraker", "branch")
        self.mainsail.port = self.config.getint("mainsail", "port")
        self.mainsail.unstable_releases = self.config.getboolean(
            "mainsail", "unstable_releases"
        )
        self.fluidd.port = self.config.getint("fluidd", "port")
        self.fluidd.unstable_releases = self.config.getboolean(
            "fluidd", "unstable_releases"
        )

    def _set_config_options(self) -> None:
        self.config.set(
            "kiauh",
            "backup_before_update",
            str(self.kiauh.backup_before_update),
        )
        self.config.set("klipper", "repo_url", self.klipper.repo_url)
        self.config.set("klipper", "branch", self.klipper.branch)
        self.config.set("moonraker", "repo_url", self.moonraker.repo_url)
        self.config.set("moonraker", "branch", self.moonraker.branch)
        self.config.set("mainsail", "port", str(self.mainsail.port))
        self.config.set(
            "mainsail",
            "unstable_releases",
            str(self.mainsail.unstable_releases),
        )
        self.config.set("fluidd", "port", str(self.fluidd.port))
        self.config.set(
            "fluidd", "unstable_releases", str(self.fluidd.unstable_releases)
        )

    def _kill(self) -> None:
        Logger.print_dialog(
            DialogType.ERROR,
            [
                "No KIAUH configuration file found! Please make sure you have at least "
                "one of the following configuration files in KIAUH's root directory:",
                "● default.kiauh.cfg",
                "● kiauh.cfg",
            ],
        )
        kill()
