#   -*- coding: utf-8 -*-
#
#   This file is part of PyBuilder
#
#   Copyright 2011-2020 PyBuilder Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from unittest import TestCase

from pybuilder.core import Project, Logger
from pybuilder.errors import BuildFailedException
from pybuilder.plugins.python.pylint_plugin import (check_pylint_availability,
                                                    init_pylint,
                                                    execute_pylint,
                                                    DEFAULT_PYLINT_OPTIONS)
from test_utils import Mock, patch, ANY

PYLINT_ERROR_OUTPUT = [
    '************* Module mode.file',
    'src/main/python/module/file.py:34:0: C0301: Line too long (365/100) (line-too-long)',
    'src/main/python/module/file.py:34:0: R1705: Unnecessary "else" after "return" (no-else-return)',
    'Your code has been rated at 9.79/10 (previous run: 9.79/10, +0.00)',
    ''
]

PYLINT_NORMAL_OUTPUT = [
    'Your code has been rated at 9.79/10 (previous run: 9.79/10, +0.00)',
    ''
]


class PylintPluginTests(TestCase):
    def setUp(self):
        self.project = Project("basedir")
        self.project.set_property("dir_source_main_python", "source")
        self.project.set_property("dir_reports", "reports")

        self.reactor = Mock()
        self.reactor.python_env_registry = {}
        self.reactor.python_env_registry["pybuilder"] = pyb_env = Mock()
        pyb_env.environ = {}
        self.reactor.pybuilder_venv = pyb_env

    def test_should_check_that_pylint_can_be_executed(self):
        mock_logger = Mock(Logger)

        check_pylint_availability(self.project, mock_logger, self.reactor)

        self.reactor.pybuilder_venv.verify_can_execute.assert_called_with(['pylint'], 'pylint', 'plugin python.pylint')

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_NORMAL_OUTPUT)
    def test_should_run_pylint_with_default_options(self, *_):
        init_pylint(self.project)

        execute_pylint(self.project, Mock(Logger), self.reactor)

        self.reactor.pybuilder_venv.execute_command.assert_called_with(["pylint"] + DEFAULT_PYLINT_OPTIONS, ANY,
                                                                       env=ANY)

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_NORMAL_OUTPUT)
    def test_should_run_pylint_with_custom_options(self, *_):
        init_pylint(self.project)
        self.project.set_property("pylint_options", ["--test", "-f", "--x=y"])

        execute_pylint(self.project, Mock(Logger), self.reactor)

        self.reactor.pybuilder_venv.execute_command.assert_called_with(["pylint", "--test", "-f", "--x=y"], ANY,
                                                                       env=ANY)

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_ERROR_OUTPUT)
    @patch('pybuilder.plugins.python.pylint_plugin.execute_tool_on_modules')
    def test_should_break_build_when_warnings_and_set(self, *_):
        init_pylint(self.project)
        self.project.set_property("pylint_break_build", True)

        with self.assertRaises(BuildFailedException):
            execute_pylint(self.project, Mock(Logger), self.reactor)

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_ERROR_OUTPUT)
    @patch('pybuilder.plugins.python.pylint_plugin.execute_tool_on_modules')
    def test_should_not_break_build_when_warnings_and_not_set(self, *_):
        init_pylint(self.project)
        self.project.set_property("pylint_break_build", False)

        execute_pylint(self.project, Mock(Logger), self.reactor)

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_NORMAL_OUTPUT)
    @patch('pybuilder.plugins.python.pylint_plugin.execute_tool_on_modules')
    def test_should_not_break_build_when_no_warnings_and_set(self, *_):
        init_pylint(self.project)
        self.project.set_property("pylint_break_build", True)

        execute_pylint(self.project, Mock(Logger), self.reactor)

    @patch('pybuilder.plugins.python.pylint_plugin.read_file', return_value=PYLINT_NORMAL_OUTPUT)
    @patch('pybuilder.plugins.python.pylint_plugin.execute_tool_on_modules')
    def test_should_not_break_build_when_no_warnings_and_not_set(self, *_):
        init_pylint(self.project)
        self.project.set_property("pylint_break_build", False)

        execute_pylint(self.project, Mock(Logger), self.reactor)
