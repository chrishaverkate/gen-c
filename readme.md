# Overview
C++ and CMake Project structure generator.

## Problem
Starting a CMake based C++ project has a lot of structure. Yes, there are some good 
"Template repos" out there, but I wish I could just wave a wand and have a new project.
One that is ready to go, compiling with tests and proper formatting... after all, home is
where the .clang-format file is.

## Solution
An easy-to-use Python script that takes a name and folder path and generates a project.
The output is:
* A C++ CLI application
* Using [Modern CMake](https://cliutils.gitlab.io/modern-cmake/) structure and style
* With [Google Test](https://github.com/google/googletest) and a working unit test
* With [Google Benchmark](https://github.com/google/benchmark) and a working performance test
* A simple readme.md
* Clang-format file

All of this is bundled in a freshly initialized Git repo.