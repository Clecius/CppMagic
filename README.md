![](https://user-images.githubusercontent.com/7787140/86186364-4719d400-bb0f-11ea-9eaf-686fca7b139f.png)
# CppMagic
A Python 3 script to help build C/C++ projects cross-platform.

---

### Objective
**The primary objective of the script is to, based on some Json configuration files, mount command lines for C/C++ compilers and run it.**
In current version I am using it with [MSVC](https://docs.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-by-category?view=vs-2019) and [GCC](https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html), soon I pretend to implement Clang.
I think this script is intended to advanced C/C++ coders with acknowledge of compilers parameters, since this parameters must be informed on a specific compiler Json configuration file.

---

### Needs
I know there is tons of build systems, but I needed one with simple and direct configurations without have to code the build system too; and working on cross-platform.

---

### The Script
The script currently can create a simple console project to start with, identify the compilers available on the current SO and call the compiler with parameterized data to build the project.
Plus, configure some basic parameters for [Visual Studio Code](https://code.visualstudio.com/) ([c_cpp_properties.json](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference), [launch.json](https://code.visualstudio.com/docs/cpp/launch-json-reference) and [tasks.json](https://code.visualstudio.com/docs/editor/tasks)) based on project.

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
|discover|Try to locate C++ compilers available.|
|prepare|Prepare environments.|

|Option|Name|Description|
|---|---|---|
|-m|MODE|Set compiler to use. (clang, gcc or msvc)|
|-p|PLATFORM|Set platfomr to use. (arm, arm64, x64 or x86)|
|-c|CONFIG|Set configuration. (debug or release)|
|-e|ENVIRONMENT|Set environment to prepare. (simple or vscode)|
|||simple   - Prepare a simple C++ project structure.|
|||vscode   - Prepare Json files for Visual Studio Code.|
|-r|Run|Execute binary product of build on the end.|
|||(uses "project.jsom" options)

---

### Structure
After running the follow commands on Windows and Linux:

**Windows**
`cppmagic.py prepare`

**Linux**
`cppmagic.py discover`

![structure](https://user-images.githubusercontent.com/7787140/86171723-90f4c100-baf3-11ea-9898-5997387e53f4.png)

***After Building***

**Windows**
`cppmagic.py build -m msvc -p x64 -c release`

**Linux**
`cppmagic.py build -m gcc -p x64 -c release`

:exclamation:**Do not forget to set `WinSDKVersion` property on `var` section from `project.json` to correct build on Windows!**

![afterbuild](https://user-images.githubusercontent.com/7787140/86171724-918d5780-baf3-11ea-83b4-922ad5d8bbf5.png)

### Visual Studio Code
To create or update VSCode Json configuration files, run the following command:

`cppmagic.py prepare -e vscode`

Use this after changes to `project.json` file.

The `Run Task...` menu from VSCode will become like this:

![runtask](https://user-images.githubusercontent.com/7787140/86171719-905c2a80-baf3-11ea-93b9-25f6230cb41a.png)


### What next
In the future I intend to finish Clang support and some routines to import projects from other tools.

## Project Sample Configuration
Follow as an example the configuration that I am using on a personal project.

**project.json**
```json
{
  "var": {
    "WinSDKVersion": "10.0.17763.0"
  },
  "project_name": "CPPWS",
  "intellisense": {
    "cStandard": "c11",
    "cppStandard": "c++14"
  },
  "common": {
    "preprocessor": [
      "USE_SQLITE",
      "SQLITE_ENABLE_FTS5",
      "USE_STACK_SIZE=102400",
      "USE_ZLIB",
      "USE_IPV6",
      "USE_WEBSOCKET",
      "USE_SERVER_STATS"
    ]
  },
  "include": [
    "${ProjectDir}source",
    "${ProjectDir}source/application",
    "${ProjectDir}source/loguru",
    "${ProjectDir}source/helper",
    "${ProjectDir}source/dbquery",
    "${ProjectDir}source/civetweb",
    "${ProjectDir}source/webserver",
    "${ProjectDir}source/pugixml",
    "${ProjectDir}source/cajun",
    "${ProjectDir}source/sqlite",
    "${ProjectDir}include/zlib",
    "${ProjectDir}include/cryptopp"
  ],
  "source": {
    "c": [
      "${ProjectDir}source/sqlite/sqlite3.c",
      "${ProjectDir}source/civetweb/civetweb.c"
    ],
    "cpp": [
      "${ProjectDir}source/main.cpp",
      "${ProjectDir}source/console.cpp",
      "${ProjectDir}source/loguru/loguru.cpp",
      "${ProjectDir}source/helper/file.cpp",
      "${ProjectDir}source/helper/network.cpp",
      "${ProjectDir}source/helper/timer.cpp",
      "${ProjectDir}source/helper/configfile.cpp",
      "${ProjectDir}source/helper/memdata.cpp",
      "${ProjectDir}source/helper/process.cpp",
      "${ProjectDir}source/helper/datetime.cpp",
      "${ProjectDir}source/dbquery/dataset.cpp",
      "${ProjectDir}source/dbquery/dbquery.cpp",
      "${ProjectDir}source/pugixml/pugixml.cpp",
      "${ProjectDir}source/civetweb/CivetServer.cpp",
      "${ProjectDir}source/webserver/model.cpp",
      "${ProjectDir}source/webserver/cryptohelper.cpp",
      "${ProjectDir}source/webserver/resource.cpp",
      "${ProjectDir}source/webserver/controller.cpp",
      "${ProjectDir}source/webserver/webserver.cpp",
      "${ProjectDir}source/webserver/webhelper.cpp",
      "${ProjectDir}source/application/webapp.cpp",
      "${ProjectDir}source/application/database.cpp",
      "${ProjectDir}source/application/session.cpp"
    ]
  },
  "run": {
    "cwd": "${ProjectDir}build/run",
    "args": [
      "-l",
      "${ProjectDir}build/run",
      "-c",
      "${ProjectDir}build/run/cppws-${system}.cfg"
    ]
  },
  "out_dir": "${ProjectDir}build/${Mode}-${System}/${Platform}/${Configuration}",
  "int_dir": "${OutDir}intermediate",
  "tmp_dir": "${ProjectDir}temp/${Mode}",
  "lib_dir": [
    "${ProjectDir}library/${Mode}-${System}/${Platform}",
    "${ProjectDir}library/${Mode}-${System}/${Platform}/${Configuration}"
  ]
}
```
**msvc.json**
```json
{
  "import": "project.json",
  "tool_dir": {
    "x64_x64-bat": "C:/program files (x86)/microsoft visual studio/2019/community/VC/Auxiliary/Build/vcvars64.bat",
    "x64_x64-exe": "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.25.28610/bin/Hostx64/x64/cl.exe",
    "x64_x86-bat": "C:/program files (x86)/microsoft visual studio/2019/community/VC/Auxiliary/Build/vcvarsamd64_x86.bat",
    "x64_x86-exe": "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.25.28610/bin/Hostx64/x86/cl.exe",
    "x64_arm64-bat": "C:/program files (x86)/microsoft visual studio/2019/community/VC/Auxiliary/Build/vcvarsamd64_arm64.bat",
    "x64_arm64-exe": "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.25.28610/bin/Hostx64/arm64/cl.exe",
    "x64_arm-bat": "C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/bin/amd64_arm/vcvarsamd64_arm.bat",
    "x64_arm-exe": "C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/bin/amd64_arm/cl.exe"
  },
  "lib": [
    "Iphlpapi.lib",
    "cryptlib.lib",
    "z.lib"
  ],
  "intellisense": {
    "browse": {
      "limitSymbolsToIncludedHeaders": true,
      "databaseFilename": "${workspaceFolder}/.vscode/msvc/browse.vc.db"
    }
  },
  "clean": [
    "*.exe",
    "*.obj",
    "*.pdb",
    "*.ilk",
    "*.pch",
    "*.idb*.iobj",
    "*.ipdb"
  ],
  "out_file": "${OutDir}${ProjectName}.exe",
  "common": {
    "preprocessor": [
      "_WINDOWS",
      "_CONSOLE",
      "_CRT_SECURE_NO_WARNINGS",
      "_CRT_SECURE_NO_DEPRECATE"
    ],
    "compile": [
      "/fp:precise",
      "/GS",
      "/W3",
      "/Zc:wchar_t",
      "/sdl",
      "/Zc:inline",
      "/Zc:forScope",
      "/WX-",
      "/Gd",
      "/FC",
      "/EHsc",
      "/nologo",
      "/diagnostics:classic",
      "/errorReport:none",
      "/Fo:\"${IntDir}\\\"",
      "/Fd:\"${IntDir}\\\"",
      "/MP4",
      "/Zf",
      "/wd4996"
    ],
    "link": [
      "/NXCOMPAT",
      "/NOLOGO",
      "/ERRORREPORT:NONE",
      "/SUBSYSTEM:CONSOLE",
      "/MACHINE:${Platform}",
      "/OUT:\"${OutFile}\""
    ]
  },
  "x64": {
    "debug": {
      "preprocessor": [
        "_DEBUG",
        "DEBUG"
      ],
      "compile": [
        "/RTC1",
        "/JMC",
        "/Od",
        "/MTd",
        "/Zi"
      ],
      "link": [
        "/DEBUG",
        "/INCREMENTAL",
        "/DEBUG:FASTLINK"
      ]
    },
    "release": {
      "preprocessor": [
        "NDEBUG"
      ],
      "compile": [
        "/O2",
        "/Oi",
        "/GL",
        "/Gy",
        "/Ox",
        "/MT"
      ],
      "link": [
        "/LTCG:incremental",
        "/INCREMENTAL:NO"
      ]
    }
  }
}
```
**gcc-linux.json**
```json
{
  "import": "project.json",
  "tool_dir": {
    "gpp": "/usr/bin/g++",
    "gcc": "/usr/bin/gcc"
  },
  "lib": [
    "stdc++",
    "pthread",
    "dl",
    "systemd",
    "cryptopp",
    "z"
  ],
  "intellisense": {
    "browse": {
      "limitSymbolsToIncludedHeaders": true,
      "databaseFilename": "${workspaceFolder}/.vscode/gcc-linux/browse.vc.db"
    }
  },
  "launch": {
    "linux": {
      "MIMode": "gdb",
      "miDebuggerPath": "/usr/bin/gdb",
      "setupCommands": [
        {
          "description": "Enable pretty-printing",
          "text": "-enable-pretty-printing"
        }
      ]
    }
  },
  "clean": [],
  "out_file": "${OutDir}${ProjectName}",
  "common": {
    "preprocessor": [
      "LINUX"
    ],
    "compile": {
      "common": [
        "-Wall",
        "-Wextra",
        "-Wshadow",
        "-Wformat-security",
        "-Winit-self",
        "-fPIC"
      ],
      "gcc": [
        "-Wmissing-prototypes"
      ],
      "gpp": [
        "-std=c++11"
      ]
    },
    "link": [
      "-o${outfile}"
    ]
  },
  "x64": {
    "debug": {
      "preprocessor": [
        "DEBUG",
        "_DEBUG"
      ],
      "compile": {
        "common": [
          "-m64",
          "-g3",
          "-ggdb",
          "-Og"
        ]
      },
      "link": [
        "-m64"
      ]
    },
    "release": {
      "preprocessor": [
        "DNDEBUG"
      ],
      "compile": {
        "common": [
          "-m64",
          "-O2"
        ]
      },
      "link": [
        "-m64"
      ]
    }
  }
}
```

**Project Tree**
![cppwsfiles](https://user-images.githubusercontent.com/7787140/86189242-661c6400-bb17-11ea-89b3-62b66d23130f.png)

**Visual Studio Code for Linux and Windows working side by side using Virtual Box resource of Seamless Mode.**
![seamlessmode](https://user-images.githubusercontent.com/7787140/86189248-6a488180-bb17-11ea-8eb7-9a2c5bb8c452.png)
