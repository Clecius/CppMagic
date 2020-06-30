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

