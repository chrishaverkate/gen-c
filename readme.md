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

# Usage
Create a new project named AwesomePrj in the /tmp/awesome-prj folder

_Caution_: gen-c expects to create the project folder and will initialize a Git repo. 

```
python3 gen-c.py -n AwesomePrj -d /tmp/awesome-prj
```

Output:  
```
==================================
Pre-action summary of options:

Project name: AwesomePrj
Project base directory: /tmp/awesome-prj
Include Google Test: True
Include Google Benchmark: True
Delete existing project: False
==================================

----------------------------------
Running...
! Info: Project directory created.
! Info: Basic folder structure created.
! Info: Source files created.
! Info: CMake Files created.
! Info: Cloned Google Test.
! Info: Cloned Google Benchmark.
! Info: Supporting files created.
Finished!
----------------------------------

==================================
Generation Report:

awesome-prj/
├── .clang-format
├── .gitmodules
├── app/
│   ├── CMakeLists.txt
│   └── main.cpp
├── CMakeLists.txt
├── docs/
├── extern/
│   └── CMakeLists.txt
├── include/
│   ├── awesome_prj/
│   │   └── message.h
│   └── CMakeLists.txt
├── readme.md
├── src/
│   ├── CMakeLists.txt
│   └── message.cpp
└── tests/
    ├── CMakeLists.txt
    └── unit/
        ├── CMakeLists.txt
        └── message_tests.cpp

==================================
```

