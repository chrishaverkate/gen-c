#! /bin/python3

import argparse
from git import Repo, Submodule
import os
import re
import shutil


def print_error(message):
    print(f"** Error: {message}")


def print_info(message):
    print(f"! Info: {message}")


class SourceFiles(object):
    @staticmethod
    def app():
        return """#include <iostream>
#include <#PROJECT_NAME#/message.h>

int main (int argc, char** argv) {
	Message msg;
	printf("%s\\n", msg.get_hello()->c_str());
	return 0;
}
"""

    @staticmethod
    def include_message_h():
        return """#pragma once

#include <memory>
#include <string>

class Message {
public:
	[[nodiscard]] std::unique_ptr<std::string> get_hello() const;
};
"""

    @staticmethod
    def src_message_cpp():
        return """#include <#PROJECT_NAME#/message.h>

using std::make_unique;
using std::string;
using std::unique_ptr;

unique_ptr<string> Message::get_hello() const {
	return make_unique<string>("Hello World!");
}
"""

    @staticmethod
    def tests_unit():
        return """#include <gtest/gtest.h>

#include <#PROJECT_NAME#/message.h>

TEST(MessageTests, get_hello) {
	Message m;
	ASSERT_STREQ("Hello World!", m.get_hello()->c_str());
}
"""

    @staticmethod
    def tests_benchmark():
        return """#include <benchmark/benchmark.h>

#include <#PROJECT_NAME#/message.h>

static void get_hello(benchmark::State& state) {
	Message m;
	for (auto _ : state)
		auto hello = m.get_hello();
}

BENCHMARK(get_hello);
"""


class CmakeFiles(object):
    @staticmethod
    def top_level():
        return """cmake_minimum_required(VERSION 3.18)

project(#PROJECT_NAME#
	LANGUAGES C CXX ASM
	VERSION 0.1.0
)

add_subdirectory(app)
add_subdirectory(extern)
add_subdirectory(include)
add_subdirectory(src)
add_subdirectory(tests)
"""

    @staticmethod
    def app():
        return """set(target_name ${CMAKE_PROJECT_NAME}_cli)

add_executable(${target_name}
	main.cpp
)

target_link_libraries(${target_name}
	PUBLIC

	${CMAKE_PROJECT_NAME}_includes
	${CMAKE_PROJECT_NAME}_lib
)

set_target_properties(${target_name}
	PROPERTIES
		C_STANDARD 11
		CXX_STANDARD 17
)

"""

    @staticmethod
    def includes():
        return """set(target_name ${CMAKE_PROJECT_NAME}_includes)

add_library(
	${target_name}
	INTERFACE
)

target_include_directories(
	${target_name}
	INTERFACE
	$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
)
"""

    @staticmethod
    def src():
        return """set(target_name ${CMAKE_PROJECT_NAME}_lib)

add_library(${target_name}
	OBJECT
	message.cpp
)

target_link_libraries(
	${target_name}
	PUBLIC

	${CMAKE_PROJECT_NAME}_includes
)

set_target_properties(${target_name}
	PROPERTIES
		C_STANDARD 11
		CXX_STANDARD 17
)
"""

    @staticmethod
    def tests():
        return """include(GoogleTest)
enable_testing()

include_directories("${CMAKE_SOURCE_DIR}/src")

add_subdirectory(benchmark)
add_subdirectory(unit)
"""

    @staticmethod
    def extern():
        return """add_subdirectory(googletest)
add_subdirectory(benchmark)
"""

    @staticmethod
    def tests_unit():
        return """set(target_name tests-unit)

add_executable(${target_name}
	message_tests.cpp
)

set_target_properties(${target_name}
	PROPERTIES
		C_STANDARD 11
		CXX_STANDARD 17
)

target_link_libraries(${target_name}
	${CMAKE_PROJECT_NAME}_lib
	${CMAKE_PROJECT_NAME}_includes
	gtest_main
)

gtest_discover_tests(${target_name})
"""

    @staticmethod
    def tests_benchmark():
        return """set(target_name tests-perf)

add_executable(${target_name}
	message_perf.cpp
)

set_target_properties(${target_name}
	PROPERTIES
		C_STANDARD 11
		CXX_STANDARD 17
)

target_link_libraries(${target_name}
	${CMAKE_PROJECT_NAME}_lib
	${CMAKE_PROJECT_NAME}_includes
	benchmark::benchmark_main
)
"""


class SupportFiles(object):
    @staticmethod
    def readme():
        return """# Overview
*Add high-level description about project*

# Dependencies
*Describe the things needed to build/use this project*

# Resources
*Provide some notes, links, etc. that help understand the context*
"""

    @staticmethod
    def clang_format():
        return """---
Language: Cpp
Standard: c++17

# Alignment
AlignAfterOpenBracket: Align
AlignEscapedNewlines: Left
AlignOperands: AlignAfterOperator
AllowShortIfStatementsOnASingleLine: Never
PointerAlignment: Left
SpaceBeforeParens: ControlStatements
SpaceBeforeAssignmentOperators: true

# Tabs & Indent
UseTab: ForIndentation
TabWidth: 4
IndentWidth: 4
ContinuationIndentWidth: 4
AccessModifierOffset: -4
NamespaceIndentation: None
SpacesBeforeTrailingComments: 2

# Line breaks
ColumnLimit: 0
AllowShortBlocksOnASingleLine: Never
AllowShortFunctionsOnASingleLine: None
BinPackArguments: false
BinPackParameters: false
ReflowComments: false
ConstructorInitializerAllOnOneLineOrOnePerLine: true
BreakConstructorInitializersBeforeComma: true
BreakBeforeBinaryOperators: NonAssignment
BreakBeforeBraces: Custom
BraceWrapping:
  AfterClass: false
  AfterControlStatement: Never
  AfterEnum: false
  AfterFunction: false
  AfterNamespace: false
  AfterStruct: false
  AfterExternBlock: false
  BeforeCatch: false
  BeforeElse: false
  IndentBraces: false
...

"""


class Project(object):
    def __init__(self, args):
        self._args = args

    @property
    def name(self):
        return self._args.name

    @property
    def name_for_folder(self):
        name = self._args.name
        # change PascalCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return name

    @property
    def dir(self):
        return self._args.dir

    @property
    def include_tests(self):
        return self._args.tests

    @property
    def include_benchmark(self):
        return self._args.benchmark

    @property
    def delete_existing(self):
        return self._args.delete


class Generate(object):
    def __init__(self, project_details):
        self._project = project_details
        self._repo = None

    def print_summary_pre(self):
        print("==================================\nPre-action summary of options:\n")
        print(f"Project name: {self._project.name}")
        print(f"Project base directory: {self._project.dir}")
        print(f"Include Google Test: {self._project.include_tests}")
        print(f"Include Google Benchmark: {self._project.include_benchmark}")
        print(f"Delete existing project: {self._project.delete_existing}")
        print('==================================\n')

    def print_summary_post(self):
        # Print a summary of what was created and the tree structure (if possible)
        pass

    def go(self):
        # Let's use exceptions to bail out on failures and send a message out
        self.initialize_folder_structure()
        self.initialize_git_repo()
        self.build_folder_structure()
        self.create_source_files()
        self.build_cmake_structure()
        self.clone_external_dependencies()
        self.add_supporting_files()

    def initialize_folder_structure(self):
        if os.path.isdir(self._project.dir):
            if self._project.delete_existing:
                shutil.rmtree(self._project.dir)
            else:
                print_error("Directory already exists... aborting")
                raise FileExistsError

        os.mkdir(self._project.dir)

        print_info('Project directory created.')

    def initialize_git_repo(self):
        self._repo = Repo.init(self._project.dir)
        git = self._repo.git
        git.checkout(b='main')

    def build_folder_structure(self):
        folders = ['app', 'docs', 'extern', 'include', f"include/{self._project.name_for_folder}", 'src', 'tests', 'tests/benchmark', 'tests/unit']
        for folder in folders:
            os.mkdir(f"{self._project.dir}/{folder}")

        print_info("Basic folder structure created.")

    def create_source_files(self):
        source_files = [("app/main.cpp", SourceFiles.app()),
                        (f"include/{self._project.name_for_folder}/message.h", SourceFiles.include_message_h()),
                        ("src/message.cpp", SourceFiles.src_message_cpp()),
                        ("tests/unit/message_tests.cpp", SourceFiles.tests_unit()),
                        ("tests/benchmark/message_perf.cpp", SourceFiles.tests_benchmark())]

        for (file, content) in source_files:
            with open(f"{self._project.dir}/{file}", 'w') as w:
                w.write(content.replace('#PROJECT_NAME#', self._project.name_for_folder))

        print_info('Source files created.')

    def build_cmake_structure(self):
        cmake_files = [("", CmakeFiles.top_level().replace('#PROJECT_NAME#', self._project.name)),
                       ("app/", CmakeFiles.app()),
                       ("include/", CmakeFiles.includes()),
                       ("src/", CmakeFiles.src()),
                       ("tests/", CmakeFiles.tests()),
                       ("extern/", CmakeFiles.extern()),
                       ("tests/", CmakeFiles.tests()),
                       ("tests/unit/", CmakeFiles.tests_unit()),
                       ("tests/benchmark/", CmakeFiles.tests_benchmark())]

        for (folder, content) in cmake_files:
            with open(f"{self._project.dir}/{folder}/CMakeLists.txt", 'w') as w:
                w.write(content)

        print_info('CMake Files created.')
        pass

    def clone_external_dependencies(self):
        if self._project.include_tests:
            Submodule.add(self._repo, 'googletest', 'extern/googletest', 'https://github.com/google/googletest.git')
            print_info('Cloned Google Test.')

        if self._project.include_benchmark:
            Submodule.add(self._repo, 'benchmark', 'extern/benchmark', 'https://github.com/google/benchmark.git')
            print_info('Cloned Google Benchmark.')

    def add_supporting_files(self):
        files = [("readme.md", SupportFiles.readme()),
                 (".clang-format", SupportFiles.clang_format())]

        for (file, content) in files:
            with open(f"{self._project.dir}/{file}", 'w') as w:
                w.write(content)

        print_info('Supporting files created.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--benchmark', action='store_true', default=True, help="Include Google Benchmark framework")
    parser.add_argument('-d', '--dir', required=True, help="New project's base directory. Will be created if it doesn't exist")
    parser.add_argument('-n', '--name', required=True, help="Name of the new project.")
    parser.add_argument('-t', '--tests', action='store_true', default=True, help="Include Google Test framework")
    parser.add_argument('-D', '--delete', action='store_true', default=False, help="Delete existing folder")

    args = parser.parse_args()

    project = Project(args)
    g = Generate(project)
    g.print_summary_pre()

    # todo confirm? pause for cancel...?

    try:
        g.go()
    except Exception as e:
        print(f"Exiting with error. Project was not fully created. Exception:\n {e}")

