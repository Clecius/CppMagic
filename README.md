# **CppMagic**
**A Python script to help build C/C++ project cross-platform using whatever desired simple editor.**

---

**The primary objective of the script is to, based on some Json configuration files, mount command lines for the C/C++ compiler and run it.**

>The current version supports [GCC](https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html) (GNU Compiler Collection), [Clang](https://clang.llvm.org/) (LLVM native C/C++/Objective-C compiler), [MSVC](https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-by-category) (Microsoft C++ compiler) and [EMCC](https://emscripten.org/docs/tools_reference/emcc.html) (Emscripten Compiler Frontend) compilers on Linux, MacOS, Windows and Web (WASM) platforms.

>The script depends on the Python [Colorama](https://pypi.org/project/colorama/) library.

---

## **The Script**
>The script currently can create a simple console project to start with, identify the compilers available on the current OS and call the compiler with parameterized data to build the project. Plus, to configure some basic parameters for [Visual Studio Code](https://code.visualstudio.com/) ([c_cpp_properties.json](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference), [launch.json](https://code.visualstudio.com/docs/cpp/launch-json-reference) and [tasks.json](https://code.visualstudio.com/docs/editor/tasks)) based on the project.


`cppmagic.py prepare`
 - Try to discover all available compilers;
 - Generate a basic C++ structure project;
 - Generate Visual Studio Code Json files in .vscode directory.

`cppmagic.py prepare -e vscode`
 - Create or update Json files for Visual Studio Code.

`cppmagic.py build -m gcc -p x64 -c debug`
 - Build project using GCC for X64 in Debug.

|Command|Description|
|---|---|
|build|Generate C++ binaries.|
|rebuild|Generate C++ binaries compiling entire project.|
|clean|Erase C++ binaries.|
|prepare|Prepare environments.|
|discover|Try to locate C++ compilers available.|
|host|Start a Python web server.|

|Option|Name|Description|
|---|---|---|
|-m|MODE|Set compiler to use. (gcc, clang, msvc or emcc)|
|-p|PLATFORM|Set platfomr to use. (arm, arm64, x64, x86 or wasm)|
|-c|CONFIG|Set configuration. (debug or release)|
|-e|ENVIRONMENT|Set environment to prepare. (simple or vscode)|
|||simple   - Prepare a simple C++ project structure.|
|||vscode   - Prepare Json files for Visual Studio Code.|
|-r|Run|Execute binary product of build on the end.|
|-d|Directory|Project directory to process.|
|-j|Project|Project configuration file (.json).|
|-u|Publish|Directory to copy the out file.|
|-o|HostDir|Directory to host in http server.|
|-t|HostPort|Port to host in http server.|
|-s|StartPage|Start page file in host.|

---
<br>

## **Configuration**
>All project configuration is based on Json files.
>>Basically the CppMagic script mix all Json files needed for the compiler and platform specific and based on the mixed Json content mounts 2 command lines; one to turn all the source files on objects (compile) and another to turn the object files on the final binary / assets (link).

### project.json
>This Json file contains the basic information and generic parameters for the project, like Project Name (output binary name), project related includes and preprocessors, source files list, etc.

### compiler_platform.json
>The compiler and platform specific options. In this file is informed all specific options needed for the use of the compiler, specific platform libraries, compiler and linker options, etc.

<br>

---
<br>

## Simple GCC Project on Linux
You will need a Linux system with Python 3 (and Colorama) and essential building tools installed, no need for Make Utilities nor Autotools.

>This command will create a very simple project structure.
```
cppmagic.py prepare -m gcc -e simple
```

```
.
├── cppmagic
│   ├── gcc-linux.json  <- GCC options for Linux
│   └── project.json    <- Project configuration
├── include
├── library
│   └── gcc-linux
│       └── x64
│           └── debug
└── source
    └── main.cpp        <- Sample source file
```
>Now lets compile it with debugging information.
```
cppmagic.py build -m gcc -p x64 -c debug
```
```
.
├── build
│   ├── gcc-linux
│   │   └── x64
│   │       └── debug
│   │           ├── Example         <- Generated final binary file
│   │           └── intermediate
│   │               └── Example
│   │                   └── main.o  <- Object file from source code
│   └── run
├── cppmagic
│   ├── gcc-linux.json
│   └── project.json
├── include
├── library
│   └── gcc-linux
│       └── x64
│           └── debug
├── source
│   └── main.cpp
└── temp
    └── gcc
        ├── config.json      <- Big Json file (mix from project and gcc-linux)
        ├── gcc-gpp.par      <- Compile command line
        ├── gcc-header.json  <- ( CppMagic build control file )
        └── gcc-lnk.par      <- Link command line
```

<br>

---
<br>

## Simple MSVC Project on Windows
You will need a Windows system with Python 3 (and Colorama) and MSVC Compiler/Linker command line, but intalling entire Visual Studio solution works the same way.

>This command will create a very simple project structure.
```
cppmagic.py prepare -m gcc -e simple
```
```
.
├── cppmagic
│   ├── msvc.json      <- MSVC options for Windows
│   └── project.json   <- Project configuration
├── include
├── library
│   └── msvc-windows
│       └── x64
│           └── debug
└── source
    └── main.cpp       <- Sample source file
```
>Now lets compile it with debugging information.
```
cppmagic.py build -m msvc -p x64 -c debug
```
**DO NOT FORGET TO SET THE SPECIAL VARIABLES (in msvc.json) TO INFORM THE MSVC COMPILER WICH INSTALLED LIBRARY VERSION TO USE.**

E.g.
``` json
  "var": {
    "winsdk_version": "10.0.19041.0",
    "vc_version": "14.33"
  },
```
```
.
├── build
│   ├── msvc-windows
│   │   └── x64
│   │       └── debug
│   │           ├── Example.exe         <- Generated final binary file
│   │           ├── Example.ilk
│   │           ├── Example.pdb
│   │           └── intermediate
│   │               └── Example
│   │                   ├── main.obj    <- Object file from source code
│   │                   └── vc140.pdb
│   └── run
├── cppmagic
│   ├── msvc.json
│   └── project.json
├── include
├── library
│   └── msvc-windows
│       └── x64
│           └── debug
├── source
│   └── main.cpp
└── temp
    └── msvc
        ├── config.json       <- Big Json file (mix from project.json and msvc.json)
        ├── msvc-header.json  <- ( CppMagic build control file )
        └── msvc-lnk.par      <- Linker command line
```

<br>

---
<br>

## Simple Clang Project on macOS
You will need a macOS system with Python 3 (and Colorama) and essential building tools installed, no need for Make Utilities nor Autotools.

>This command will create a very simple project structure.
```
cppmagic.py prepare -m clang -e simple
```

```
.
├── cppmagic
│   ├── clang-darwin.json  <- Clang options for macOS
│   └── project.json       <- Project configuration
├── include
├── library
│   └── clang-darwin
│       └── x64
│           └── debug
└── source
    └── main.cpp           <- Sample source file
```
>Now lets compile it with debugging information.
```
cppmagic.py build -m clang -p x64 -c debug
```
```
.
├── build
│   ├── clang-darwin
│   │   └── x64
│   │       └── debug
│   │           ├── Example         <- Generated final binary file
│   │           └── intermediate
│   │               └── Example
│   │                   └── main.o  <- Object file from source code
│   └── run
├── cppmagic
│   ├── clang-darwin.json
│   └── project.json
├── include
├── library
│   └── clang-darwin
│       └── x64
│           └── debug
├── source
│   └── main.cpp
└── temp
    └── clang
        ├── clang-header.json  <- ( CppMagic build control file )
        ├── clang-lnk.par      <- Link command line
        ├── clang-lpp.par      <- Compile command line
        └── config.json        <- Big Json file (mix from project.json and clang-darwin.json)
```

<br>

---
<br>

## Cross Platform - Let's put all things together
Share a directory between all desired SO and run the commands on each one.

>On Linux
```
cppmagic.py prepare -m gcc -e simple
```
>On Windows
```
cppmagic.py prepare -m msvc -e simple
```
>On macOS
```
cppmagic.py prepare -m clan -e simple
```
```
.
├── cppmagic
│   ├── clang-darwin.json  <- Clang options for macOS
│   ├── gcc-linux.json     <- GCC options for Linux
│   ├── msvc.json          <- MSVC options for Windows
│   └── project.json       <- Project configuration
├── include
├── library
│   ├── clang-darwin
│   │   └── x64
│   │       └── debug
│   ├── gcc-linux
│   │   └── x64
│   │       └── debug
│   └── msvc-windows
│       └── x64
│           └── debug
└── source
    └── main.cpp           <- Sample source file
```
Now compiling.
>On Linux
```
cppmagic.py build -m gcc -p x64 -c debug
```
>On Windows
```
cppmagic.py build -m msvc -p x64 -c debug
```
>On macOS
```
cppmagic.py build -m clang -p x64 -c debug
```
```
.
├── build
│   ├── clang-darwin
│   │   └── x64
│   │       └── debug
│   │           ├── Example              <- Generated final binary file
│   │           └── intermediate
│   │               └── Example
│   │                   └── main.o
│   ├── gcc-linux
│   │   └── x64
│   │       └── debug
│   │           ├── Example              <- Generated final binary file
│   │           └── intermediate
│   │               └── Example
│   │                   └── main.o
│   ├── msvc-windows
│   │   └── x64
│   │       └── debug
│   │           ├── Example.exe         <- Generated final binary file
│   │           ├── Example.ilk
│   │           ├── Example.pdb
│   │           └── intermediate
│   │               └── Example
│   │                   ├── main.obj
│   │                   └── vc140.pdb
│   └── run
├── cppmagic
│   ├── clang-darwin.json
│   ├── gcc-linux.json
│   ├── msvc.json
│   └── project.json
├── include
├── library
│   ├── clang-darwin
│   │   └── x64
│   │       └── debug
│   ├── gcc-linux
│   │   └── x64
│   │       └── debug
│   └── msvc-windows
│       └── x64
│           └── debug
├── source
│   └── main.cpp
└── temp
    ├── clang
    │   ├── clang-header.json
    │   ├── clang-lnk.par
    │   ├── clang-lpp.par
    │   └── config.json
    ├── gcc
    │   ├── config.json
    │   ├── gcc-gpp.par
    │   ├── gcc-header.json
    │   └── gcc-lnk.par
    └── msvc
        ├── config.json
        ├── msvc-cpl.par
        ├── msvc-header.json
        └── msvc-lnk.par
```

<br>

---
<br>

## Visual Studio Code
If you want to use Visual Studio Code editor, CppMagic helps to create some Json files for VSCode based on project configurations.

>Just execute:
```
cppmagic.py prepare -e vscode
```
>The script will create the **c_cpp_properties.json**, **launch.json** and **tasks.json** files.

>The above command will be put in **tasks.json**, so every time you change the project configuration just execute the task *'CppMagic - Prepare Visual Studio Code'* to update the Json files.

``` json
    {
      "type": "shell",
      "command": "cppmagic.py",
      "label": "CppMagic - Prepare Visual Studio Code",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      },
      "problemMatcher": [],
      "args": [
        "prepare",
        "-e",
        "vscode"
      ]
    },
```
