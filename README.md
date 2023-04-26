# CppMagic
A Python script to help build C/C++ project cross-platform using whatever desired simple editor.

---

**The primary objective of the script is to, based on some Json configuration files, mount command lines for the C/C++ compiler and run it.**

The current version supports [GCC](https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html), [Clang](https://clang.llvm.org/) and [MSVC](https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-by-category) compilers on Linux, MacOS and Windows platforms.
The script depends on the Python [Colorama](https://pypi.org/project/colorama/) library.

---

The script currently can create a simple console project to start with, identify the compilers available on the current OS and call the compiler with parameterized data to build the project. Plus, to configure some basic parameters for [Visual Studio Code](https://code.visualstudio.com/) ([c_cpp_properties.json](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference), [launch.json](https://code.visualstudio.com/docs/cpp/launch-json-reference) and [tasks.json](https://code.visualstudio.com/docs/editor/tasks)) based on the project.


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
|-d|Directory|Specify a project directory to process.|
|-j|Project|Specify a project configuration file (.json).|
|-u|Publish|Specify a directory to copy the out file.|
