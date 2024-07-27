#!/usr/bin/python3
# coding=utf-8

#+-------
#| CppMagic - Deoclecio Freire 2019-2023
#|
#| A Python 3 script to help build C/C++ project cross-platform using whatever desired simple editor.
#|
#| https://github.com/Clecius/CppMagic.git
#|

# pylint: disable=E1101

VERSION = '0.9.995'

import platform
import os
import sys
import shutil
import argparse
import pkgutil
clrma = pkgutil.find_loader('colorama')
if clrma:
  from colorama import init
  init(autoreset=True)
  from colorama import Fore, Back, Style
import json
import fnmatch
import glob
import http.server
import socketserver
import webbrowser
from subprocess import PIPE, Popen
from threading import Thread
from timeit import default_timer as timer

# === Magic Behavior ===
RSlash = True # Use right slash in Windows
VscGen = ['x64', 'x86', 'arm', 'wasm'] # Platforms to gerenerate Visual Studio Code Tasks and Launchers
ConfigBak = False
# ===

JVar = {}

DEF_CONFIG_DIR = 'cppmagic'
DEF_CONFIG_PRJ = 'project'

CMD_BUILD = 'build'
CMD_REBUILD = 'rebuild'
CMD_CLEAN = 'clean'
CMD_PREPARE = 'prepare'
CMD_DISCOVER = 'discover'
CMD_INSTALL = 'install'
CMD_HOST = 'host'

MODE_ALL = 'all'
MODE_MSVC = 'msvc'
MODE_GCC = 'gcc'
MODE_CLANG = 'clang'
MODE_EMCC = 'emcc'

ENV_SIMPLE = 'simple'
ENV_VSCODE = 'vscode'

PROJECT_NAME = 'project_name'
INCLUDE = 'include'
SOURCE = 'source'
INSTALL = 'install'
PREFIX = 'prefix'
OUTPUT = 'output'
CLEAN = 'clean'
OUT_DIR = 'out_dir'
OUT_FILE = 'out_file'
SHELL_FILE = 'shell_file'
SETTINGS = 'settings'
LSETTINGS = 'link_settings'
EMBED_FILE = 'embed_file'
PRELOAD_FILE = 'preload-file'
INT_DIR = 'int_dir'
TMP_DIR = 'tmp_dir'
LIB_DIR = 'lib_dir'
RTLIB_DIR = 'rtlib_dir'
INTELLISENSE = 'intellisense'
LAUNCH = 'launch'
RUN = 'run'
CWD = 'cwd'
ARGS = 'args'

JVAR = 'var'
IMPORT = 'import'
TOOL_DIR = 'tool_dir'
LIB = 'lib'

COMMON = 'common'
GCC = 'gcc'
GPP = 'gpp'
LCC = 'clang'
LPP = 'clangpp'
ECC = 'emcc'
EPP = 'em++'
EAR = 'emar'
ERANLIB = 'emranlib'
X86 = 'x86'
X64 = 'x64'
ARM = 'arm'
ARM64 = 'arm64'
WASM = 'wasm'
DEBUG = 'debug'
RELEASE = 'release'
PREPROC = 'preprocessor'
COMPILE = 'compile'
LINK = 'link'
GENLIB = 'genlib'
AR = 'ar'
RANLIB = 'ranlib'
MODULES = 'modules'
PKGCONF = 'pkg-config'

MSVC_CFG = 'msvc.json'
MSVC_RUN = 'msvc.bat'
MSVC_CPL = 'msvc-cpl.par'
MSVC_LNK = 'msvc-lnk.par'
MSVC_HDR = 'msvc-header.json'

GCC_CFG = 'gcc.json'
GCC_GCC = 'gcc-gcc.par'
GCC_GPP = 'gcc-gpp.par'
GCC_LNK = 'gcc-lnk.par'
GCC_HDR = 'gcc-header.json'

CLANG_CFG = 'clang.json'
CLANG_LCC = 'clang-lcc.par'
CLANG_LPP = 'clang-lpp.par'
CLANG_LNK = 'clang-lnk.par'
CLANG_HDR = 'clang-header.json'

EMCC_CFG = 'emcc.json'
EMCC_LCC = 'emcc-lcc.par'
EMCC_LPP = 'emcc-lpp.par'
EMCC_LNK = 'emcc-lnk.par'
EMCC_HDR = 'emcc-header.json'

BuildCmd = []
BuildDef = []
BuildInc = []
ErrorLst = []
DumpMsgLst = {}
DML_Err = 'error'
DML_CMg = 'cppmag'

Command = ""
Mode = ""
Platform = ""
Configuration = ""
Host = ""
ProjectDir = ""
ConfigDir = ""
ProjectJson = ""
PrjJsonLoaded = False
ProjectName = ""
TmpDir = ""
OutDir = ""
RunDir = ""
OutFile = ""
IntDir = ""
PubDir = ""

MainCPP = """#include <iostream>
int main(int argc, char *argv[])
{
  std::cout << "Hello CppMagic!" << std::endl;
}"""
GitIgnore = """.vscode
build
temp"""

OsResp = ''
OsOut = ''
OsError = ''

def DumpMessages():
  global DumpMsgLst
  CMgLst = DumpMsgLst[DML_CMg]
  if len(CMgLst) > 0:
    print(Fore.MAGENTA + "CppMagic messages:" + Fore.RESET)
    for e in CMgLst:
      print(e)
    print(Fore.RESET)
  ErrLst = DumpMsgLst[DML_Err]
  if len(ErrLst) > 0:
    print(Fore.RED + "Errors list:" + Fore.RESET)
    for e in ErrLst:
      print(e)
    print(Fore.RESET)

def FixSlash(value, force = None):
  V = os.path.normpath(value)
  slash = RSlash
  if force != None:
    slash = force
  if slash:
    V = V.replace('\\', '/')
  else:
    V = V.replace('/', '\\')
  if platform.system() == 'Windows' and (V[1] == ':'):
    # Life obligation: Work around to fix other's bullshit.
    # Capital drive letter on windows.
    V = '{0}{1}'.format(V[0].upper(),V[1:])
  return V

def FullMergeDict(D1, D2):
  for key, value in D1.items():
    if key in D2:
      if type(value) is dict:
        FullMergeDict(D1[key], D2[key])
      else:
        if type(value) in (int, float, str):
          D1[key] = [value]
        if type(D2[key]) is list:
          D1[key].extend(D2[key])
        else:
          D1[key].append(D2[key])
  for key, value in D2.items():
    if key not in D1:
      D1[key] = value

def Mkd(value):
  if value and (not os.path.exists(value)):
    os.makedirs(value)
  return value

def OsCmd(cmd, wait = True):
  global OsResp
  global OsOut
  global OsError
  OsResp = ''
  OsOut = ''
  OsError = ''
  Posix = 'posix' in sys.builtin_module_names
  Shell = ''
  if Posix:
    Shell = '/bin/sh'
    OsProc = Popen(Shell, shell=True, encoding='utf-8', bufsize=-1, close_fds=Posix, stdout=PIPE, stderr=PIPE, stdin=PIPE)
  else:
    Shell = 'cmd.exe'
    OsProc = Popen(Shell, shell=True, universal_newlines=True, bufsize=-1, close_fds=Posix, stdout=PIPE, stderr=PIPE, stdin=PIPE)
  if wait:
    OsOut, OsError = OsProc.communicate(cmd)
    if len(OsError) > 0:
      OsResp = OsOut + '\n' + OsError
    else:
      OsResp = OsOut
  else:
    OsProc.stdin.write(cmd)
    OsProc.stdin.flush()
  Ret = OsProc.returncode
  return Ret

def OsList(showerrors):
  global DumpMsgLst
  EWN = 0
  Sqg = -1
  for l in OsResp.split('\n'):
    if (showerrors):
      Normal = True
      if Mode == MODE_MSVC:
        for x in [[': fatal', 3, Fore.RED], [': error', 1, Fore.RED], [': warning', 2, Fore.YELLOW], [': note', 3, Fore.CYAN]]:
          W = l.lower().find(x[0])
          if (W > -1):
            S1 = l.find(':', W +1)
            Normal = False
            PLin = l[:W + 1] + x[2] + l[W + 1:S1 + 1].upper() + Fore.RESET + l[S1 + 1:]
            print(PLin)
            if (x[2] == Fore.RED):
              DumpMsgLst[DML_Err].append(PLin)
      else:
        for x in [[' error: ', 1, Fore.RED], [' warning: ', 2, Fore.YELLOW], [' note: ', 3, Fore.CYAN]]:
          W = l.lower().find(x[0])
          if (W > -1):
            S1 = l.find(':', 0, W)
            S2 = -1
            if (S1 > -1):
              S2 = l.find(':', S1 + 1, W)
              if (S2 > -1):
                EWN = x[1]
                Normal = False
                Sqg = 3
                PLin = l[:W] + x[2] + x[0].upper() + Fore.RESET + l[W + len(x[0]):]
                print(PLin)
                if (x[2] == Fore.RED):
                  DumpMsgLst[DML_Err].append(PLin)
                break
        if Sqg > -1:
          Sqg -= 1
          if (Sqg == 0):
            if (l.strip()[:1] == '^') or (l.strip()[:1] == '~'):
              Normal = False
              if EWN == 1:
                print(Fore.RED + l)
              elif EWN == 2:
                print(Fore.YELLOW + l)
              elif EWN == 3:
                print(Fore.CYAN + l)
      if Normal:
        print(l)
    else:
      print (l)

def RemoveDict(dlist, dprop, dvalue):
  Found = True
  while Found:
    Count = 0
    Found = False
    for Conf in dlist:
      PValue = Conf.get(dprop, '-novalue-')
      if PValue == dvalue:
        Found = True
        break
      Count += 1
    if Found:
      del dlist[Count]

def Splt(value, sep):
  S = []
  if ',' in value:
    S = value.split(sep)
  else:
    S.append(value)
  return S

def versionvalue(version):
  l = [int(x, 10) for x in version.split('.')]
  l.reverse()
  return sum(x * (100 ** i) for i, x in enumerate(l))

def which(pgm):
  path = os.getenv('PATH')
  Bin = pgm
  if platform.system() == 'Windows':
    Bin = pgm + '.exe'
  for p in path.split(os.path.pathsep):
    x = os.path.join(p, Bin)
    if os.path.exists(p) and os.access(x, os.X_OK):
      return os.path.join(p, Bin)


def LoadJson(file):
  with open(file) as J:
    lines = J.readlines()
  JText = ''
  for l in lines:
    t = l.strip()
    if len(t) > 0:
      p = t.find('//')
      if not p == 0:
        JText += t
  return json.loads(JText)

def MsvcDiscover():
  BinPath = {}
  VsDir = []
  print (Fore.MAGENTA + 'Discovering MSVC...')
  ProgDir = []
  ProgDir.append(os.environ.get('ProgramFiles')) # Uses default PF directory.
  ProgDir.append(os.environ.get('ProgramFiles(x86)')) # Uses x86 specific PF directory.
  for pd in ProgDir:
    for f in os.listdir(pd): # Cycle through all directorys in PF;
      if 'visual studio' in f.lower(): # If path contains VS stuff,
        for root, _, files in os.walk(os.path.join(pd, f)): # Check files within;
          if 'cl.exe' in files: # If compiler found,
            VsDir.append(root) # Store path for analysis.
    if len(VsDir) > 0:
      break

  COpt = {}
  if len(VsDir) > 0: # If something to analysis,
    for v in VsDir: # Cycle through stored path;
      vd = v.lower() # To lower case for better comparison.
      Batch = ''
      cdir = os.path.split(vd) # Compiler directory AKA TARGET compiler.
      hdir = os.path.split(cdir[0]) # Upper directory AKA HOST compiler.
      if 'host' in hdir[1]: # Check if new Visual Studio installation schema,
        bdir = os.path.split(hdir[0]) # Get current directory.
        hdir = hdir[1][-3:] # Set HOST compiler.
        while bdir[1] != 'vc' and bdir[1] != '': #Seek up directories for VC;
          bdir = os.path.split(bdir[0])
        if bdir[1] != '': # If VC found, build Batch name.
          h = hdir # Host
          t = cdir[1] # Target
          ht = '' # Combination
          if h == 'x64': # Convert x64 constant to Microsoft's Bullshit 'amd64'. =P
            h = 'amd64'
          if t == 'x64':
            t = 'amd64'
          if t == h: # if Host and Target equals,
            if '86' in h: # Another conversion for Microsoft's Dismantling. XP
              ht = '32'
            else:
              ht = '64'
          else:
            ht = h + '_' + t
          bat = 'vcvars' + ht + '.bat' # Build batch file name
          Batch = os.path.join(bdir[0], 'VC', 'Auxiliary', 'Build', bat) # Batch file localization.
        cdir = cdir[1] # Set TARGET compiler.
      else: # Old Visual Studio installation,
        if "_" in cdir[1]: # Is TARGET and HOST in directory name?
          hdir = cdir[1].split("_")[0] # Set HOST compiler.
          cdir = cdir[1].split("_")[1] # Set TARGET compiler.
        else: # Assume boot TARGET and HOST equals.
          hdir = cdir[1]
          cdir = cdir[1]
        if hdir == 'amd64': # Unbullshiting Microsoft's Dismantling.
          hdir = 'x64'
        if cdir == 'amd64':
          cdir = 'x64'
        for f in os.listdir(v): # Find the Batch file,
          if 'vcvars' in f.lower(): # that starts with 'vsvars'
            if not 'phone' in f.lower(): # and not contais 'phone'
              Batch = os.path.join(v, f) # Batch file localization.
              break
      if hdir == Host and os.path.exists(Batch): # If HOST matches system host platform.
        Vers = '0' # Default compiler version. =P
        vdir = os.path.split(v)
        while '.' not in vdir[1] and vdir[1] != '': # Try to find some version within directory path.
          vdir = os.path.split(vdir[0])
        if vdir[1] != '':
          if ' ' in vdir[1]: # If thers is words amid version number.
            for w in vdir[1].split(' '):
              if '.' in w:
                vdir = w
                break
          else:
            vdir = vdir[1]
          vdir = vdir.split('.')
          Vers = vdir[0] + (vdir[1] + '000')[:3]
        Exec = os.path.join(v, 'cl.exe')
        hd = hdir + '_' + cdir
        if hd in COpt:
          if COpt[hd][0] < Vers:
            COpt[hd] = [Vers, FixSlash(Batch), FixSlash(Exec)]
        else:
          COpt[hd] = [Vers, FixSlash(Batch), FixSlash(Exec)]
  if COpt:
    for o in COpt:
      BinPath[o + '-bat'] = COpt[o][1]
      BinPath[o + '-exe'] = COpt[o][2]
  else:
    print (Fore.RED + 'No MSVC compiler found!')
  return BinPath

def GCCDiscover():
  BinPath = {}
  print (Fore.MAGENTA + 'Discovering GCC...')
  Cmd = which('g++')
  if Cmd:
    BinPath[GPP] = Cmd
  Cmd = which('gcc')
  if Cmd:
    BinPath[GCC] = Cmd
  Cmd = which('ar')
  if Cmd:
    BinPath[AR] = Cmd
  Cmd = which('ranlib')
  if Cmd:
    BinPath[RANLIB] = Cmd
  Cmd = which(PKGCONF)
  if Cmd:
    BinPath[PKGCONF] = Cmd
  return BinPath

def ClangDiscover():
  BinPath = {}
  print (Fore.MAGENTA + 'Discovering CLANG...')
  Cmd = which('clang++')
  if Cmd:
    BinPath[LPP] = Cmd
  Cmd = which('clang')
  if Cmd:
    BinPath[LCC] = Cmd
  Cmd = which('ar')
  if Cmd:
    BinPath[AR] = Cmd
  Cmd = which('ranlib')
  if Cmd:
    BinPath[RANLIB] = Cmd
  Cmd = which(PKGCONF)
  if Cmd:
    BinPath[PKGCONF] = Cmd
  return BinPath

def EmsdkDiscover():
  BinPath = {}
  print (Fore.MAGENTA + 'Discovering Emscripten...')
  Cmd = which(EPP)
  if Cmd:
    BinPath[EPP] = Cmd
  Cmd = which(ECC)
  if Cmd:
    BinPath[ECC] = Cmd
  Cmd = which(EAR)
  if Cmd:
    BinPath[EAR] = Cmd
  Cmd = which(ERANLIB)
  if Cmd:
    BinPath[ERANLIB] = Cmd
  return BinPath

def MacroResolve(data):
  Ret = data
  B = Ret.find('${')
  while B >= 0:
    E = Ret.find('}', B)
    if E >= 0:
      Id = Ret[B+2:E].lower()
      Value = ''
      if Id[:4] == JVAR + ':':
        Id = Ret[B+2:E][4:]
        Value = JVar.get(Id, '')
        if len(Value) > 0:
          if Id[-3:].lower() == 'dir':
            Value = FixSlash(Value) + ('/' if RSlash else os.path.sep)
        else:
          Value = '{var:?}'
      else:
        if Id == 'command':
          Value = Command
        elif Id == 'mode':
          Value = Mode
        elif Id == 'platform':
          Value = Platform
        elif Id == 'configuration':
          Value = Configuration
        elif Id == 'system':
          Value = platform.system().lower()
        elif Id == 'host':
          Value = Host
        elif Id == 'projectdir':
          Value = ProjectDir
        elif Id == 'configdir':
          Value = ConfigDir
        elif Id == 'tempdir':
          Value = TmpDir
        elif Id == 'outdir':
          Value = OutDir
        elif Id == 'rundir':
          Value = RunDir
        elif Id == 'outfile':
          Value = OutFile
        elif Id == 'intdir':
          Value = IntDir
        elif Id == 'projectname':
          Value = ProjectName
        elif Id == 'sep':
          Value = os.path.sep
        if Value and len(Value) > 0:
          if Id[-3:] == 'dir':
            Value = FixSlash(Value) + ('/' if RSlash else os.path.sep)
        else:
          Value = '{?}'
      Ret = Ret[:B] + Value + Ret[E+1:]
      B = Ret.find('${')
    else:
      B = Ret.find('${', B + 1)
  return Ret

def ProcessJsonImport(data):
  global PrjJsonLoaded
  Ret = True
  Impts = []
  for key, value in data.items():
    if key == IMPORT:
      if type(value) is list:
        Impts.extend(value)
      elif type(value) is str:
        if ',' in value:
          Impts = value.split(',')
        else:
          Impts.append(value)
      break
  data.pop(IMPORT, '')
  for i in Impts:
    i = MacroResolve(i)
    TDat = []
    if os.path.isfile(i):
      if i == ProjectJson:
        PrjJsonLoaded = True
      TDat = LoadJson(i)
      if len(TDat) > 0:
        FullMergeDict(data, TDat)
    else:
      print (Fore.RED + 'Cannot import non existent configuration file: ' + i)
  if not PrjJsonLoaded:
    if os.path.isfile(ProjectJson):
      TDat = LoadJson(ProjectJson)
      if len(TDat) > 0:
        FullMergeDict(data, TDat)
        PrjJsonLoaded = True
  if Ret:
    if IMPORT in data:
      Ret = ProcessJsonImport(data)
  return Ret

def ProcessJVar(data):
  if data.get(JVAR, {}):
    for k, v in data[JVAR].items():
      if type(v) is str:
        JVar[k] = v

def ListHeader(data, source, ccpp, object):
  Ret = []
  Cmd = ''
  Ppd = ''
  Inc = ''
  Tag = 'including file:'
  if Mode == MODE_MSVC:
    for v in BuildDef:
      Ppd += '/D"{0}" '.format(v)
    for v in BuildInc:
      Inc += '/I"{0}" '.format(v)
    if ccpp == 0:
      Cmd = '"{0}" /c /EP /w /showIncludes {1} {2} /Tc"{3}" & exit\n'.format(BuildCmd[1], Ppd, Inc, source)
    else:
      Cmd = '"{0}" /c /EP /w /showIncludes {1} {2} /Tp"{3}" & exit\n'.format(BuildCmd[1], Ppd, Inc, source)
    OsCmd(Cmd)
    if len(OsResp) > 0:
      for l in OsResp.split('\n'):
        if (l.lower().find(Tag) > -1):
          l = FixSlash(l)
          P = l.lower().find(':/')
          if (P > -1):
            l = l[P-1:]
            for v in BuildInc:
              B = v.lower()
              D = l.lower()
              if D.find(B) == 0:
                Ret.append(l)
                break
  elif Mode == MODE_GCC:
    for v in BuildDef:
      Ppd += '-D"{0}" '.format(v)
    for v in BuildInc:
      Inc += '-I"{0}" '.format(v)
    BCmd = ''
    if ccpp == 0:
      BCmd = BuildCmd[0]
    else:
      BCmd = BuildCmd[1]
    Cmd = '"{0}" -c -MM {1} {2} {3}\n'.format(BCmd, Ppd, Inc, source)
    OsCmd(Cmd)
    S = 0
    if len(OsOut) > 0:
      while True:
        S = OsOut.find(' /', S)
        if S >= 0:
          E = S
          while True:
            E = OsOut.find(' ', E + 1)
            if E >= 0:
              if OsOut[E-1] != '\\':
                f = OsOut[S+1:E]
                if not f.endswith(os.path.basename(source)):
                  Ret.append(f)
                S = E
                break
            else:
              f = OsOut[S+1:].rstrip()
              if not f.endswith(os.path.basename(source)):
                Ret.append(f)
              S = E
              break
        else:
          break
  return Ret

def ListSource(data, rebuild, lstcomp, lstlink):
  SrcCode = {}
  ObjExt = ''
  HdrFile = ''
  if Mode == MODE_MSVC:
    ObjExt = '.obj'
    HdrFile = MSVC_HDR
  elif Mode == MODE_GCC:
    ObjExt = '.o'
    HdrFile = GCC_HDR
  elif Mode == MODE_CLANG:
    ObjExt = '.o'
    HdrFile = CLANG_HDR
  elif Mode == MODE_EMCC:
    ObjExt = '.o'
    HdrFile = EMCC_HDR
  if data.get(SOURCE, {}):
    for v in data[SOURCE].get('c', []):
      Sg = glob.glob(FixSlash(MacroResolve(v.strip())))
      if len(Sg) > 0:
        for s in glob.glob(FixSlash(MacroResolve(v.strip()))):
          SrcCode[FixSlash(s)] = 0
      else:
        DmlMsg = Fore.YELLOW + "Nothing found for: " + v
        print (DmlMsg)
        DumpMsgLst[DML_CMg].append(DmlMsg)
    for v in data[SOURCE].get('cpp', []):
      Sg = glob.glob(FixSlash(MacroResolve(v.strip())))
      if len(Sg) > 0:
        for s in Sg:
          SrcCode[FixSlash(s)] = 1
      else:
        DmlMsg = Fore.YELLOW + "Nothing found for: " + v
        print (DmlMsg)
        DumpMsgLst[DML_CMg].append(DmlMsg)
  HdrFile = FixSlash(os.path.join(TmpDir, HdrFile))
  JHdr = {}
  if os.path.exists(HdrFile):
    JHdr = LoadJson(HdrFile)
  BDef = ''
  for v in BuildDef:
    if len(BDef) > 0:
      BDef += ','
    BDef += v

  if not JHdr.get(Platform, {}):
    JHdr.update({Platform: {Configuration: {PREPROC: ''}}})
  elif not JHdr[Platform].get(Configuration, {}):
    JHdr[Platform].update({Configuration: {PREPROC: ''}})
  elif not JHdr[Platform][Configuration].get(PREPROC, {}):
    JHdr[Platform][Configuration].update({PREPROC: ''})

  if not rebuild:
    if not JHdr[Platform][Configuration].get(INCLUDE, {}):
      rebuild = True
    else:
      JDef = JHdr[Platform][Configuration][PREPROC]
      rebuild = (JDef != BDef)

  JInc = {}
  if not rebuild:
    JInc = JHdr[Platform][Configuration][INCLUDE]
    for s in SrcCode:
      if os.path.exists(s):
        if not JInc.get(s, {}):
          JInc.update({s : []})
        o = os.path.join(IntDir, os.path.basename(s[:s.rfind('.')] + ObjExt))
        lstlink.append(o)
        DoComp = False
        if os.path.exists(o):
          if (os.path.getmtime(s) > os.path.getmtime(o)):
            DoComp = True
          else:
            if len(JInc) > 0:
              for h in JInc[s]:
                if (not os.path.exists(h)) or (os.path.getmtime(h) > os.path.getmtime(o)):
                  DoComp = True
                  break
            else:
              DoComp = True
        else:
          DoComp = True
        if DoComp:
          if SrcCode[s] == 0:
            print ('Build: (C  ) ' + s)
          else:
            print ('Build: (C++) ' + s)
          lstcomp[s] = SrcCode[s]
          JInc[s] = ListHeader(data, s, SrcCode[s], o)
  else:
    JHdr[Platform][Configuration].update({PREPROC: BDef})
    for s in SrcCode:
      if os.path.exists(s):
        if SrcCode[s] == 0:
          print ('Rebuild: (C  ) ' + s)
        else:
          print ('Rebuild: (C++) ' + s)
        o = os.path.join(IntDir, os.path.basename(s[:s.rfind('.')] + ObjExt))
        lstlink.append(o)
        lstcomp[s] = SrcCode[s]
        JInc.update({s : ListHeader(data, s, SrcCode[s], o)})

  JHdr[Platform][Configuration].update({INCLUDE: JInc})
  with open(HdrFile, 'w') as Hdr:
    json.dump(JHdr, Hdr, indent=2)

def PkgConfig(data):
  PkgCfg = {'Pre':[],'Inc':[],'Bld':[],'Lpt':[],'Lib':[],'Lnk':[]}
  if data.get(PKGCONF, []):
    Cmd = FixSlash(data[TOOL_DIR].get(PKGCONF, ''))
    if os.path.exists(Cmd):
      Ok = 1
      MList = ''
      for m in data[PKGCONF]:
        if OsCmd('"{0}" --exists {1}'.format(Cmd, m)) != 0:
          DmlMsg = Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' ' + PKGCONF + ' module [' + m + '] not exist! ' + Back.YELLOW + ' '
          print (DmlMsg)
          DumpMsgLst[DML_CMg].append(DmlMsg)
          Ok = 0
          break
        else:
          MList += m + ' '
      if Ok == 1:
        if OsCmd('"{0}" --cflags {1}'.format(Cmd, MList)) == 0:
          for o in OsResp.split(' '):
            if o.startswith('-D'):
              PkgCfg['Pre'].append(o[2:]) # Preprocessors
            elif o.startswith('-I'):
              PkgCfg['Inc'].append(o[2:]) # Include path
            else:
              PkgCfg['Bld'].append(o) # Build option
        if OsCmd('"{0}" --libs {1}'.format(Cmd, MList)) == 0:
          for o in OsResp.split(' '):
            if o.startswith('-L'):
              PkgCfg['Lpt'].append(o[2:]) # Library path
            elif o.startswith('-l'):
              PkgCfg['Lib'].append(o[2:]) # Libraries
            else:
              PkgCfg['Lnk'].append(o) # Link options
    else:
      DmlMsg = Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' No ' + PKGCONF + ' found! ' + Back.YELLOW + ' '
      print (DmlMsg)
      DumpMsgLst[DML_CMg].append(DmlMsg)
  return PkgCfg

def DefaultProject():
  PDat = {
      JVAR: {'ExampleVar': '${ProjectDir}source/platform/example'},
      PROJECT_NAME: os.path.basename(os.getcwd()),
      INTELLISENSE: {
        'cStandard': 'c11',
        'cppStandard': 'c++17'
        },
      COMMON: {
        PREPROC: ['USE_IN_ALL_PLATFORMS']
      },
      INCLUDE: ['${ProjectDir}source',
                '${ProjectDir}include'],
      SOURCE: {
        'c': ['${ProjectDir}source/c_code.c'],
        'cpp': ['${ProjectDir}source/main.cpp']
      },
      RUN: {CWD:'${ProjectDir}build/run', ARGS:['-p', 'parameter']},
      OUT_DIR: '${ProjectDir}build/${Mode}-${System}/${Platform}/${Configuration}',
      INT_DIR: '${OutDir}intermediate/${ProjectName}',
      TMP_DIR: '${ProjectDir}temp/${Mode}',
      LIB_DIR: [
        '${ProjectDir}library/${Mode}-${System}/${Platform}/${Configuration}',
        '${ProjectDir}library/${Mode}-${System}/${Platform}'
      ]
    }
  return PDat

def CheckConfig(force):
  CFile = ''
  if force:
    PFile = os.path.join(ConfigDir, ProjectJson)
    TDat = []
    if not os.path.exists(PFile):
      TDat = DefaultProject()
      with open(PFile, 'w') as Cfg:
        json.dump(TDat, Cfg, indent=2)
  FAll = {
    MODE_CLANG: os.path.join(ConfigDir, CLANG_CFG),
    MODE_EMCC: os.path.join(ConfigDir, EMCC_CFG),
    MODE_GCC: os.path.join(ConfigDir, GCC_CFG),
    MODE_MSVC: os.path.join(ConfigDir, MSVC_CFG)
  }
  if not Mode == MODE_ALL:
    CFile = FAll[Mode]
  else:
    CFile = ''
  for k, v in FAll.items():
    if (Mode == k) or (Mode == MODE_ALL):
      TDat = {}
      if not os.path.exists(v):
        if (k == MODE_MSVC) and (platform.system().lower() == 'windows'):
          TDat = {
            TOOL_DIR: MsvcDiscover(),
            JVAR: {'winsdk_version': '10.0', 'vc_version': '14.0'},
            INCLUDE: ['${var:WinSrcDir}'],
            INTELLISENSE: {
              'browse': {
                  'limitSymbolsToIncludedHeaders': True,
                  'databaseFilename': '${workspaceFolder}/.vscode/msvc/browse.vc.db'
                }
              },
            LIB: ['kernel32.lib','user32.lib','gdi32.lib','winspool.lib','comdlg32.lib',
                  'advapi32.lib','shell32.lib','ole32.lib','oleaut32.lib','uuid.lib',
                  'odbc32.lib','odbccp32.lib'],
            CLEAN: ['*.exe', '*.obj', '*.pdb', '*.ilk', '*.pch', '*.idb' '*.iobj', '*.ipdb'],
            OUT_FILE: '${OutDir}${ProjectName}.exe',
            COMMON: {
              PREPROC: ['_CONSOLE', '_UNICODE', 'UNICODE', '_CRT_SECURE_NO_WARNINGS'],
              COMPILE: ['/fp:precise', '/GS', '/W3', '/Zc:wchar_t', '/sdl', '/Zc:inline', '/Zc:forScope', '/WX-',
                        '/Gd', '/FC', '/EHsc', '/nologo', '/diagnostics:classic', '/errorReport:none',
                        '/Fo:\"${IntDir}\\\"', '/Fd:\"${IntDir}\\\"', '/MP4', '/Zf', '/wd4996'],
              LINK: ['/NXCOMPAT', '/NOLOGO', '/ERRORREPORT:NONE', '/SUBSYSTEM:CONSOLE',
                    '/MACHINE:${Platform}', '/OUT:"${OutFile}"']
            },
            X64:{
              DEBUG: {
                PREPROC: ['_DEBUG', 'DEBUG'],
                COMPILE: ['/RTC1', '/JMC', '/Od', '/MTd', '/Zi'],
                LINK: ['/DEBUG', '/INCREMENTAL', '/DEBUG:FASTLINK']
              },
              RELEASE: {
                PREPROC: ['NDEBUG'],
                COMPILE: ['/O2', '/Oi', '/GL', '/Gy' ,'/Ox', '/MT'],
                LINK: ['/LTCG:incremental', '/INCREMENTAL:NO']
              }
            },
            X86:{
              DEBUG: {
                PREPROC: ['WIN32', '_DEBUG', 'DEBUG'],
                COMPILE: ['/RTC1', '/JMC', '/Od', '/MTd', '/ZI'],
                LINK: ['/DEBUG', '/INCREMENTAL', '/DEBUG:FASTLINK']
              },
              RELEASE: {
                PREPROC: ['WIN32', 'NDEBUG'],
                COMPILE: ['/O2', '/Oi', '/GL', '/Gy' ,'/Ox', '/MT'],
                LINK: ['/LTCG:incremental', '/INCREMENTAL:NO']
              }
            },
            ARM64:{
              DEBUG: {
                PREPROC: ['_DEBUG', 'DEBUG'],
                COMPILE: [],
                LINK: ['/DEBUG']
              },
              RELEASE: {
                PREPROC: ['NDEBUG'],
                COMPILE: ['/Ox'],
                LINK: []
              }
            },
            ARM:{
              DEBUG: {
                PREPROC: ['_DEBUG', 'DEBUG'],
                COMPILE: [],
                LINK: ['/DEBUG']
              },
              RELEASE: {
                PREPROC: ['NDEBUG'],
                COMPILE: ['/Ox'],
                LINK: []
              }
            }
          }
        elif k == MODE_GCC:
          TDat = {
            TOOL_DIR: GCCDiscover(),
            LAUNCH: {
              'linux': {
                'MIMode': 'gdb',
                'miDebuggerPath': '/usr/bin/gdb',
                'setupCommands': [
                  {
                    'description': 'Enable pretty-printing',
                    'text': '-enable-pretty-printing'
                  }
                ]
              }
            },
            INTELLISENSE: {
              'browse': {
                  'limitSymbolsToIncludedHeaders': True,
                  'databaseFilename': '${workspaceFolder}/.vscode/gcc-linux/browse.vc.db'
                }
              },
            LIB: ['stdc++', 'pthread'],
            CLEAN: [],
            OUT_FILE: '${OutDir}${ProjectName}',
            INSTALL: {
              PREFIX: "/somedir/libs/project",
              OUTPUT: [
                {
                  'sub_dir': 'include',
                  'files': [
                    '${ProjectDir}src/header.hpp',
                  ]
                },
                {
                  'sub_dir': 'lib/${Mode}-${System}/${Platform}',
                  'files': [
                    '${OutFile}'
                  ]
                }
              ]
            },
            COMMON: {
              PREPROC: [],
              COMPILE: {
                COMMON: ['-Wall', '-Wextra', '-Wshadow', '-Wformat-security', '-Winit-self', '-fPIC'],
                GCC: ["-Wmissing-prototypes"],
                GPP: ["-std=c++17"],
                GPP: ["-Werror=return-type"]
              },
              LINK: ['-o${outfile}']
            },
            X64:{
              DEBUG: {
                PREPROC: ['DEBUG', '_DEBUG'],
                COMPILE: {
                  COMMON: ['-m64', '-O0', '-g3', '-ggdb3', '-gdwarf', '-gdwarf-4', '-fvar-tracking-assignments']
                },
                LINK: ['-m64']
              },
              RELEASE: {
                PREPROC: ['DNDEBUG'],
                COMPILE: {
                  COMMON: ['-m64', '-O2']
                },
                LINK: ['-m64']
              }
            },
            X86:{
              DEBUG: {
                PREPROC: ['DEBUG', '_DEBUG'],
                COMPILE: {
                  COMMON: ['-m32', '-g', '-Og']
                },
                LINK: ['-m32']
              },
              RELEASE: {
                PREPROC: ['DNDEBUG'],
                COMPILE: {
                  COMMON: ['-m32', '-O2']
                },
                LINK: ['-m32']
              }
            }
          }
        elif k == MODE_CLANG:
          TDat = {
            TOOL_DIR: ClangDiscover(),
            LAUNCH: {
              'linux': {
                'MIMode': 'gdb',
                'miDebuggerPath': '/usr/bin/gdb',
                'setupCommands': [
                  {
                    'description': 'Enable pretty-printing',
                    'text': '-enable-pretty-printing'
                  }
                ]
              }
            },
            INTELLISENSE: {
              'browse': {
                  'limitSymbolsToIncludedHeaders': True,
                  'databaseFilename': '${workspaceFolder}/.vscode/clang-linux/browse.vc.db'
                }
              },
            LIB: ['stdc++', 'pthread'],
            CLEAN: [],
            OUT_FILE: '${OutDir}${ProjectName}',
            COMMON: {
              PREPROC: [],
              COMPILE: {
                COMMON: ['-Wall', '-Wextra', '-Wshadow', '-Wformat-security', '-Winit-self', '-fPIC'],
                GCC: ["-Wmissing-prototypes"],
                GPP: ["-std=c++17"],
                GPP: ["-Werror=return-type"]
              },
              LINK: ['-o${outfile}']
            },
            X64:{
              DEBUG: {
                PREPROC: ['DEBUG', '_DEBUG'],
                COMPILE: {
                  COMMON: ['-m64', '-O0', '-g3', '-ggdb3', '-gdwarf', '-gdwarf-4']
                },
                LINK: ['-m64']
              },
              RELEASE: {
                PREPROC: ['DNDEBUG'],
                COMPILE: {
                  COMMON: ['-m64', '-O2']
                },
                LINK: ['-m64']
              }
            },
            X86:{
              DEBUG: {
                PREPROC: ['DEBUG', '_DEBUG'],
                COMPILE: {
                  COMMON: ['-m32', '-g', '-Og']
                },
                LINK: ['-m32']
              },
              RELEASE: {
                PREPROC: ['DNDEBUG'],
                COMPILE: {
                  COMMON: ['-m32', '-O2']
                },
                LINK: ['-m32']
              }
            }
          }
        elif k == MODE_EMCC:
          TDat = {
            TOOL_DIR: EmsdkDiscover(),
            LIB: ['stdc++', 'pthread'],
            CLEAN: ['*.js', '*.wasm', '*.data'],
            OUT_FILE: '${OutDir}${ProjectName}.html',
            SHELL_FILE: '${ProjectDir}source/shell.html',
            COMMON: {
              PREPROC: [],
              SETTINGS: {
                COMMON: [],
                ECC: [],
                EPP: []
              },
              COMPILE: {
                COMMON: ['-Os', '-Wall'],
                ECC: [],
                EPP: []
              },
              LSETTINGS: [],
              LINK: ['-o${outfile}']
            },
            WASM:{
              DEBUG: {
                PREPROC: ['DEBUG', '_DEBUG'],
                COMPILE: {
                  COMMON: ['-O0', '-g3', '-ggdb3', '-gdwarf', '-gdwarf-4']
                },
                LINK: []
              },
              RELEASE: {
                PREPROC: ['DNDEBUG'],
                COMPILE: {
                  COMMON: ['-O2']
                },
                LINK: []
              }
            }
          }
      else:
        if force:
          TDat = LoadJson(v)
          if k == MODE_MSVC:
            TDat[TOOL_DIR] = MsvcDiscover()
          elif k == MODE_GCC:
            TDat[TOOL_DIR] = GCCDiscover()
          elif k == MODE_CLANG:
            TDat[TOOL_DIR] = ClangDiscover()
      if TDat:
        with open(v, 'w') as Cfg:
          json.dump(TDat, Cfg, indent=2)
  return CFile

def LoadConfig(cfile):
  TDat = {}
  if os.path.exists(cfile):
    TDat = LoadJson(cfile)
    os.chdir(ConfigDir)
    if ProcessJsonImport(TDat):
      ProcessJVar(TDat)
    else:
      TDat = {}
  return TDat

def MakeEnv(cfile, skipmkd = False):
  TDat = LoadConfig(cfile)
  if len(TDat) > 0:
    global ProjectName, OutDir, RunDir, OutFile, IntDir, TmpDir
    ProjectName = MacroResolve(TDat.get(PROJECT_NAME,''))
    if ProjectName == '':
      ProjectName = os.path.basename(os.getcwd())
    OutDir = FixSlash(MacroResolve(TDat.get(OUT_DIR,'')))
    if OutDir == '':
      OutDir = MacroResolve('${ProjectDir}build/${Platform}/${Configuration}')
    if TDat.get(RUN, {}):
      RunDir = MacroResolve(TDat[RUN].get(CWD, OutDir))
    if RunDir == '':
      RunDir = OutDir
    OutFile = FixSlash(MacroResolve(TDat.get(OUT_FILE,'')))
    if OutFile == '':
      Ext = '.out'
      if platform.system() == 'Windows':
        Ext = '.exe'
      OutFile = MacroResolve('${OutDir}${ProjectName}' + Ext)
    IntDir = FixSlash(MacroResolve(TDat.get(INT_DIR,'')))
    if IntDir == '':
      IntDir = MacroResolve('${OutDir}intermediate')
    TmpDir = FixSlash(MacroResolve(TDat.get(TMP_DIR,'')))
    if TmpDir == '':
      TmpDir = MacroResolve('${ProjectDir}temp/${Mode}')
    if not skipmkd:
      Mkd(OutDir)
      Mkd(RunDir)
      Mkd(IntDir)
      Mkd(TmpDir)
  return TDat


def _check_python_version():
  Ret = False
  major_ver = sys.version_info[0]
  if major_ver < 3:
    print ('The python version is %d.%d. But python 3.x is required.\n' % (major_ver, sys.version_info[1]))
  else:
    Ret = True
  return Ret

def _check_modules():
  Ret = False
  if clrma:
    Ret = True
  else:
    print ("Colorama package needed.")
  return Ret

def choicesDescriptions():
  R = Fore.RESET
  M = Fore.MAGENTA
  Y = Fore.YELLOW
  G = Fore.GREEN
  C = Fore.CYAN
  CppMagic = os.path.basename(sys.argv[0])

  Desc = M + "Commands:\n"
  Desc += Y + '  build' + R + ' ...: Generate C++ binaries.\n'
  Desc += Y + '  rebuild' + R + ' .: Generate C++ binaries compiling entire project.\n'
  Desc += Y + '  clean' + R + ' ...: Erase C++ binaries.\n'
  Desc += Y + '  discover' + R + ' : Try to locate C++ compilers available.\n'
  Desc += Y + '  prepare' + R + ' .: Prepare environments.\n'
  Desc += Y + '  install' + R + ' .: Install files to a specific location.\n'
  Desc += Y + '  host' + R + ' ....: Host a webserver.\n'

  Desc += M + "\nOptions:\n"
  Desc += R + '  -m MODE ........: ' + G + 'Set compiler to use. (clang, emcc, gcc or msvc)\n'
  Desc += R + '  -p PLATFORM ....: ' + G + 'Set platfomr to use. (arm, arm64, wasm, x64 or x86)\n'
  Desc += R + '  -c CONFIG ......: ' + G + 'Set configuration. (debug or release)\n'
  Desc += R + '  -e ENVIRONMENT .: ' + G + 'Set environment to prepare. (simple or vscode)\n'
  Desc += G + '                    simple' + R + '   - Prepare a simple C++ project structure.\n'
  Desc += G + '                    vscode' + R + '   - Prepare Json files for Visual Studio Code.\n'
  Desc += R + '  -r Run .........: ' + G + 'Execute binary product of build on the end.\n'
  Desc += G + '                      (uses "project.jsom" options)\n'
  Desc += R + '  -d Directory ...: ' + G + 'Project directory to work within.\n'
  Desc += R + '  -j JsonFile ....: ' + G + 'Project Json condiguration file.\n'
  Desc += R + '  -p Directory ...: ' + G + 'Directory to copy the output file.\n'
  Desc += R + '  -o Directory ...: ' + G + 'Directory to host in http server.\n'
  Desc += R + '  -t Port ........: ' + G + 'Port to host in http server.\n'
  Desc += R + '  -s File ........: ' + G + 'Start page file in host.\n'

  Desc += M + "\nExamples:\n"
  Desc += R + '  ' + CppMagic + Y + ' prepare\n'
  Desc += C + '    *' + R + 'Try to discover all available compilers;\n'
  Desc += C + '    *' + R + 'Generate a basic C++ structure project;\n'
  Desc += C + '    *' + R + 'Generate Visual Studio Code Json files in .vscode directory.\n'

  Desc += R + '  ' + CppMagic + Y + ' prepare ' + R + '-e' + G + ' vscode\n'
  Desc += C + '    *' + R + 'Create or update Json files for Visual Studio Code.\n'

  Desc += R + '  ' + CppMagic + Y + ' build ' + R + '-m' + G + ' gcc ' + R + '-p' + G + ' x64 ' + R + '-c' + G + ' debug\n'
  Desc += C + '    *' + R + 'Build project using GCC for X64 in Debug.\n'

  return Desc

# =================================================================================================
if __name__ == '__main__':

  if not _check_python_version():
    exit(1)
  if not _check_modules():
    exit(1)

  print (Fore.YELLOW + '\nCppMagic - v' + VERSION + Fore.RESET + ' by Deoclecio Freire 2019-2024')

  parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                   epilog=choicesDescriptions())
  parser.add_argument('command', action='store', type= lambda s: s.lower(),
                      choices=[CMD_BUILD, CMD_REBUILD, CMD_CLEAN, CMD_PREPARE, CMD_DISCOVER, CMD_INSTALL, CMD_HOST],
                      help='See commands below.')
  parser.add_argument('-m', '--mode', type= lambda s: s.lower(),
                      choices=[MODE_ALL, MODE_MSVC, MODE_GCC, MODE_CLANG, MODE_EMCC],
                      help='Compiler to use.')
  parser.add_argument('-p', '--platform', type= lambda s: s.lower(),
                      choices=[ARM, ARM64, X64, X86, WASM],
                      help='Building platform.')
  parser.add_argument('-c', '--config', type= lambda s: s.lower(),
                      choices=[DEBUG, RELEASE],
                      help='Building configuration.')
  parser.add_argument('-e', '--environment', type= lambda s: s.lower(),
                      choices=[ENV_SIMPLE, ENV_VSCODE],
                      help='Environmento to prepare.')
  parser.add_argument('-r', '--run', action='store_true', default=False,
                      help='Execute binary after build.')
  parser.add_argument('-d', '--directory', dest='prjdir',
                      help='Project directory to process.')
  parser.add_argument('-j', '--project', dest='prjjson',
                      help='Project configuration file (.json).')
  parser.add_argument('-u', '--publish', dest='pubdir',
                      help='Directory to copy the out file.')

  parser.add_argument('-o', '--hostdir', dest='hostdir',
                      help='Directory to host in http server.')
  parser.add_argument('-t', '--port', dest='hostport',
                      help='Port to host in http server.')
  parser.add_argument('-s', '--startpage', dest='startpage',
                      help='Start page file in host.')

  args = parser.parse_args()

  DumpMsgLst[DML_Err] = []
  DumpMsgLst[DML_CMg] = []

  ShowCustom = False
  ProjectDir = args.prjdir
  if ProjectDir:
    ProjectDir = FixSlash(ProjectDir)
    if not os.path.isdir(ProjectDir):
      print(Fore.RED + 'Directory not found! (-d option)')
      print(Fore.RESET + '[' + ProjectDir + ']')
      exit(1)
    else:
      ShowCustom = True
      os.chdir(ProjectDir)
  else:
    ProjectDir = FixSlash(os.getcwd())

  ConfigDir = Mkd(os.path.join(ProjectDir, DEF_CONFIG_DIR))

  ProjectJson = args.prjjson
  if not ProjectJson:
    ProjectJson = DEF_CONFIG_PRJ
  else:
    ShowCustom = True
  ProjectJson = os.path.splitext(ProjectJson)[0] + '.json'

  PubDir = args.pubdir
  if PubDir:
    PubDir = FixSlash(PubDir)
    if not os.path.isdir(PubDir):
      print(Fore.RED + 'Directory not found! (-u option)')
      print(Fore.RESET + '[' + PubDir + ']')
      exit(1)

  if ShowCustom:
    print (Fore.RESET + '  Project:[{0}] in {1}'.format(ProjectJson, ProjectDir))

  Command = args.command
  Command = Command.lower()
  Mode = args.mode
  if Mode:
    Mode = Mode.lower()
  Platform = args.platform
  if Platform:
    Platform = Platform.lower()
  Configuration = args.config
  if Configuration:
    Configuration = Configuration.lower()
  Host = platform.machine().lower()
  if Host == 'amd64':
    Host = X64

  if Mode == MODE_EMCC:
    Platform = WASM
  if Platform == WASM:
    Mode = MODE_EMCC

  cfg = GCC_CFG.split('.')
  GCC_CFG = cfg[0] + "-" + platform.system().lower() + "." + cfg[1]
  cfg = CLANG_CFG.split('.')
  CLANG_CFG = cfg[0] + "-" + platform.system().lower() + "." + cfg[1]
  cfg = EMCC_CFG.split('.')
  EMCC_CFG = cfg[0] + "-" + WASM + "." + cfg[1]

  Ret = 1 # Error
  tmrProcess = timer()
  if Command == CMD_DISCOVER: # --== DISCOVER ==--
    print (Fore.GREEN + 'Discovering...')
    if not Mode:
      Mode = MODE_ALL
      print(Fore.YELLOW + '(all modes)')
    CheckConfig(True)
    print (Fore.GREEN + 'Done.')
    Ret = 0

  elif Command == CMD_PREPARE: # --== PREPARE ==--
    print (Fore.GREEN + 'Preparing...')
    if not Mode:
      Mode = MODE_ALL
      print(Fore.YELLOW + '(all modes)')
    if not Platform:
      if '64' in Host:
        Platform = X64
      elif '86' in Host:
        Platform = X86
      else:
        Platform = ARM

    if not Configuration:
      Configuration = DEBUG
    MAll = {}
    if (Mode == MODE_ALL) or ((Mode == MODE_MSVC) and (platform.system().lower() == 'windows')):
      MAll.update({MODE_MSVC: FixSlash(os.path.join(ConfigDir, MSVC_CFG))})
    if (Mode == MODE_ALL) or (Mode == MODE_GCC):
      MAll.update({MODE_GCC: FixSlash(os.path.join(ConfigDir, GCC_CFG))})
    if (Mode == MODE_ALL) or (Mode == MODE_CLANG):
      MAll.update({MODE_CLANG: FixSlash(os.path.join(ConfigDir, CLANG_CFG))})
    if (Mode == MODE_ALL) or (Mode == MODE_EMCC):
      MAll.update({MODE_EMCC: FixSlash(os.path.join(ConfigDir, EMCC_CFG))})

    CppMagic = os.path.basename(sys.argv[0])
    Env = args.environment
    DefEnv = False
    if not Env:
      DefEnv = True
      CheckConfig(True)

    if Env == ENV_SIMPLE or DefEnv:
      print (Fore.MAGENTA + 'Simple Project Structure ...')
      if not DefEnv:
        CheckConfig(True)
      PData = DefaultProject()
      SDir = ''
      Tmp = ''

      for k, v in MAll.items():
        Mode = k
        if PData.get(INCLUDE, {}):
          for v in PData[INCLUDE]:
            Mkd(FixSlash(MacroResolve(v)))
        if PData.get(LIB_DIR, {}):
          for v in PData[LIB_DIR]:
            Mkd(FixSlash(MacroResolve(v)))

      SDir = Mkd(os.path.join(ProjectDir, 'source'))
      SDir = os.path.join(SDir, 'main.cpp')
      if not os.path.exists(SDir):
        with open(SDir, 'w') as Cpp:
          Cpp.write(MainCPP)
      SDir = os.path.join(ProjectDir, '.gitignore')
      if not os.path.exists(SDir):
        with open(SDir, 'w') as Cpp:
          Cpp.write(GitIgnore)

    if Env == ENV_VSCODE or DefEnv:
      print (Fore.MAGENTA + 'Visual Studio Code ...')
      VscDir = Mkd(os.path.join(ProjectDir, '.vscode'))

      # C CPP PROPERTIES
      FProp = FixSlash(os.path.join(VscDir, 'c_cpp_properties.json'))
      CProp = {}
      if os.path.exists(FProp):
        CProp = LoadJson(FProp)
      else:
        CProp = {"configurations": [], 'version': 4}
      MLst = MAll
      if not Mode == MODE_ALL:
        MLst = {Mode: MAll[Mode]}
      for k, v in MLst.items():
        if os.path.exists(v):
          PrjJsonLoaded = False
          MDat = LoadConfig(v)

          # if platform.system().lower() == 'linux':
          PkgCfg = PkgConfig(MDat)

          if MDat.get(TOOL_DIR, {}):
            Inte = MDat.get(INTELLISENSE, {})
            IPath = []
            if MDat.get(INCLUDE, {}):
              for i in MDat[INCLUDE]:
                P = FixSlash(MacroResolve(i))
                IPath.append(P)
            if PkgCfg['Inc']:
              for v in PkgCfg['Inc']:
                IPath.append(v)
            if not Inte.get('includePath', {}):
              Inte['includePath'] = IPath
            else:
              Inte['includePath'].extend(IPath)
            PProc = []
            if MDat.get(COMMON, {}):
              if MDat[COMMON].get(PREPROC, {}):
                PProc = MDat[COMMON][PREPROC]
            if PkgCfg['Pre']:
              for v in PkgCfg['Pre']:
                PProc.append(v)
            IMode = k
            IName = 'C++ {0} {1}'.format(k.upper(), platform.system().upper())
            if MDat.get(X64, {}):
              IMode += '-' + X64
              IName += ' ' + X64
              if MDat[X64].get(DEBUG, {}):
                if MDat[X64][DEBUG].get(PREPROC, {}):
                  PProc.extend(MDat[X64][DEBUG][PREPROC])
              elif MDat[X64].get(RELEASE, {}):
                if MDat[X64][RELEASE].get(PREPROC, {}):
                  PProc.extend(MDat[X64][RELEASE][PREPROC])
            elif MDat.get(X86, {}):
              IMode += '-' + X86
              IName += ' ' + X86
              if MDat[X86].get(DEBUG, {}):
                if MDat[X86][DEBUG].get(PREPROC, {}):
                  PProc.extend(MDat[X86][DEBUG][PREPROC])
              elif MDat[X86].get(RELEASE, {}):
                if MDat[X86][RELEASE].get(PREPROC, {}):
                  PProc.extend(MDat[X86][RELEASE][PREPROC])
            elif MDat.get(WASM, {}):
              IMode += '-' + WASM
              IName += ' ' + WASM
              if MDat[WASM].get(DEBUG, {}):
                if MDat[WASM][DEBUG].get(PREPROC, {}):
                  PProc.extend(MDat[WASM][DEBUG][PREPROC])
              elif MDat[WASM].get(RELEASE, {}):
                if MDat[WASM][RELEASE].get(PREPROC, {}):
                  PProc.extend(MDat[WASM][RELEASE][PREPROC])
            else:
              IMode += '-' + X64
              IName += ' ' + X64
            if not Inte.get('name', {}):
              Inte['name'] = IName.upper()
            if not Inte.get('intelliSenseMode', {}):
              Inte['intelliSenseMode'] = IMode.lower()
            if not Inte.get('defines', {}):
              Inte['defines'] = PProc
            else:
              Inte['defines'].extend(PProc)

            if not Inte.get('cStandard', {}):
              Inte['cStandard'] = 'c11'
            if not Inte.get('cppStandard', {}):
              Inte['cppStandard'] = 'c++11'

            if CProp['configurations']:
              RemoveDict(CProp['configurations'], 'name', Inte['name'])
            CProp['configurations'].append(Inte)

      if os.path.exists(FProp) and ConfigBak:
        Bak = FProp + '.bak'
        if os.path.exists(Bak):
          os.remove(Bak)
        os.rename(FProp, Bak)
      with open(FProp, 'w') as Pro:
        json.dump(CProp, Pro, indent=2)

      # TASKS
      FTask = os.path.join(VscDir, 'tasks.json')
      VsTask = {}
      if os.path.exists(FTask):
        VsTask = LoadJson(FTask)
      else:
        VsTask = {'version': '2.0.0', 'tasks': []}
      def AddTsk(label, args, prob = [], group = False):
        RemoveDict(VsTask['tasks'], 'label', label)
        T = {'type': 'shell', 'command': 'cppmagic.py', 'label': label,
             'presentation': {'echo': True, 'reveal': 'always', 'focus': True, 'panel': 'shared'},
             'problemMatcher': prob,
             'args': args}
        if group:
          T['group'] = {'kind': 'build', 'isDefault': True}
        VsTask['tasks'].append(T)
      AddTsk('CppMagic - Discovery', [CMD_DISCOVER])
      AddTsk('CppMagic - Prepare Project', [CMD_PREPARE])

      PrepMode = ''
      if (Mode == MODE_ALL):
        if (platform.system().lower() == 'windows'):
          PrepMode = MODE_MSVC
        else:
          PrepMode = MODE_GCC
      else:
        PrepMode = Mode
      if len(PrepMode) > 0:
        AddTsk('CppMagic - Prepare Visual Studio Code', [CMD_PREPARE, '-e', ENV_VSCODE, '-m', PrepMode])
      else:
        AddTsk('CppMagic - Prepare Visual Studio Code', [CMD_PREPARE, '-e', ENV_VSCODE])

      for m, d in MAll.items():
        PrjJsonLoaded = False
        MDat = LoadConfig(d)
        if MDat.get(TOOL_DIR, {}):
          Prob = ''
          if m == MODE_MSVC:
            Prob = '$msCompile'
          elif m == MODE_GCC:
            Prob = '$gcc'
          elif m == MODE_CLANG:
            Prob = ''
          for p in VscGen:
            if MDat.get(p, {}):
              for c in [DEBUG, RELEASE]:
                Desc = ' ' + m + ' ' + p + ' ' + c
                AddTsk('Build' + Desc, [CMD_BUILD, '-m', m, '-p', p, '-c', c], Prob, True)
                AddTsk('Rebuild' + Desc, [CMD_REBUILD, '-m', m, '-p', p, '-c', c], Prob)
                AddTsk('Clean' + Desc, [CMD_CLEAN, '-m', m, '-p', p, '-c', c])
                AddTsk('Install' + Desc, [CMD_INSTALL, '-m', m, '-p', p, '-c', c])
      if os.path.exists(FTask) and ConfigBak:
        Bak = FTask + '.bak'
        if os.path.exists(Bak):
          os.remove(Bak)
        os.rename(FTask, Bak)
      with open(FTask, 'w') as Task:
        json.dump(VsTask, Task, indent=2)

      # LAUNCH
      FLaunch = os.path.join(VscDir, 'launch.json')
      VsLaunch = {}
      if os.path.exists(FLaunch):
        VsLaunch = LoadJson(FLaunch)
      else:
        VsLaunch = {'version': '0.2.0', 'configurations': []}
      for m, d in MAll.items():
        if os.path.exists(d):
          for p in VscGen:
            Mode = m
            Platform = p
            if Mode == MODE_EMCC:
              Platform = WASM
            if Platform == WASM:
              Mode = MODE_EMCC
            for c in [DEBUG, RELEASE]:
              Configuration = c
              PrjJsonLoaded = False
              MDat = MakeEnv(d, True)
              if MDat.get(TOOL_DIR, {}):
                if MDat.get(p, {}):
                  PreDsc = ' {0} {1} {2}'.format(m, p, c)
                  if m == MODE_MSVC:
                    Desc = PreDsc
                  else:
                    Desc = ' {0} ({1}) {2} {3}'.format(m, platform.system().lower(), p, c)
                  Cwd = OutDir
                  Args = []
                  if MDat.get(RUN, {}):
                    Cwd = MacroResolve(MDat[RUN].get(CWD, OutDir))
                    TArgs = MDat[RUN].get(ARGS, [])
                    if len(TArgs) > 0:
                      for a in TArgs:
                        Args.append(MacroResolve(a))
                  NewL = MDat.get(LAUNCH, {})
                  if m == MODE_EMCC:
                    LName = 'Host' + Desc
                  else:
                    LName = 'Run' + Desc
                  NewL['name'] = LName
                  NewL['request'] = 'launch'

                  if Mode == MODE_EMCC:
                    NewL['program'] = which('cppmagic.py')
                    WsCwd = os.path.dirname(OutFile)
                    NewL['cwd'] = WsCwd
                    WsArgs = ['host', '-o', WsCwd, '-t', '8080', '-s']
                    WsArgs.append(os.path.basename(OutFile))
                    NewL['args'] = WsArgs
                  else:
                    NewL['program'] = OutFile
                    NewL['cwd'] = Cwd
                    NewL['args'] = Args

                  NewL['preLaunchTask'] = 'Build' + PreDsc
                  if not NewL.get('type'):
                    if Mode == MODE_MSVC:
                      NewL['type'] = 'cppvsdbg'
                      NewL.update({'symbolSearchPath': OutDir})
                    elif Mode == MODE_EMCC:
                      NewL['type'] = 'python'
                    else:
                      NewL['type'] = 'cppdbg'
                  if not NewL.get('externalConsole'):
                    NewL['externalConsole'] = False
                  RemoveDict(VsLaunch['configurations'], 'name', LName)
                  VsLaunch['configurations'].append(NewL)

      PDebugName = 'Python CppMagic Debug'
      PDebug = { 'name': PDebugName, 'type': 'python',
        'request': 'launch', 'program': sys.argv[0], #os.path.basename(sys.argv[0]),
        'console': 'integratedTerminal',
        'args': ['prepare', '-e', 'vscode'
        ]}
      RemoveDict(VsLaunch['configurations'], 'name', PDebugName)
      VsLaunch['configurations'].append(PDebug)

      if os.path.exists(FLaunch) and ConfigBak:
        Bak = FLaunch + '.bak'
        if os.path.exists(Bak):
          os.remove(Bak)
        os.rename(FLaunch, Bak)
      with open(FLaunch, 'w') as Launch:
        json.dump(VsLaunch, Launch, indent=2)

    print (Fore.GREEN + 'Done.')
    Ret = 0

  elif Command == CMD_BUILD or Command == CMD_REBUILD or Command == CMD_CLEAN: # --== BUILD ==--
    if not Mode:
      print(Fore.YELLOW + 'Inform a compiler! (-m option)')
      exit(1)
    if Mode == MODE_EMCC:
      Platform = WASM
    if not Platform:
      print(Fore.YELLOW + 'Inform a platform! (-p option)')
      exit(1)
    if Platform == WASM:
      Mode = MODE_EMCC
    if not Configuration:
      print(Fore.YELLOW + 'Inform a configuration! (-c option)')
      exit(1)

    CData = MakeEnv(CheckConfig(False))
    if len(CData) > 0:
      if PrjJsonLoaded:
        if CData.get(SOURCE, {}):
          with open(FixSlash(os.path.join(TmpDir, 'config.json')), 'w') as JAll:
            json.dump(CData, JAll)
        else:
          print(Fore.RED + 'No source file(s) available to compile.' + Fore.RESET)
          exit(1)
      else:
        print(Fore.RED + 'Cannot proceed without a project configuration file.' + Fore.RESET)
        exit(1)
    else:
      print(Fore.RED + 'Cannot proceed with bad or empty configuration file.' + Fore.RESET)
      exit(1)

    Rebuild = (Command == CMD_REBUILD)
    Fcompile = ""
    Fcompile2 = ""
    FLink = ""
    if Mode == MODE_MSVC:
        Fcompile = MSVC_CPL
        FLink = MSVC_LNK
    elif Mode == MODE_GCC:
        Fcompile = GCC_GCC
        Fcompile2 = GCC_GPP
        FLink = GCC_LNK
    elif Mode == MODE_CLANG:
        Fcompile = CLANG_LCC
        Fcompile2 = CLANG_LPP
        FLink = CLANG_LNK
    elif Mode == MODE_EMCC:
        Fcompile = EMCC_LCC
        Fcompile2 = EMCC_LPP
        FLink = EMCC_LNK
    Fcompile = FixSlash(os.path.join(TmpDir, Fcompile))
    Fcompile2 = FixSlash(os.path.join(TmpDir, Fcompile2))
    FLink = FixSlash(os.path.join(TmpDir, FLink))
    if len(CData[TOOL_DIR]) > 0:
      if os.path.isfile(Fcompile):
        os.remove(Fcompile)
      if os.path.isfile(Fcompile2):
        os.remove(Fcompile2)
      if os.path.isfile(FLink):
        os.remove(FLink)
      if CData.get(COMMON, {}):
        for v in CData[COMMON].get(PREPROC, {}):
          BuildDef.append(MacroResolve(v.strip()))
      if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
        for v in CData[Platform][Configuration].get(PREPROC, {}):
          BuildDef.append(MacroResolve(v.strip()))
      if CData.get(INCLUDE, {}):
        for v in CData[INCLUDE]:
          BuildInc.append(FixSlash(MacroResolve(v.strip())))
    else:
      print (Fore.CYAN + '[' + Mode + ' ' + Command + ' ' + Platform + ' ' + Configuration + ']')
      print(Fore.YELLOW + 'No tool configured in json! Try to install a compiler and use discovery command.')
      exit(1)

    #                       === CLEAN ===
    if Command == CMD_CLEAN:
      if os.path.exists(OutDir):
        print (Fore.CYAN + '[' + Mode + ' ' + Command + ' ' + Platform + ' ' + Configuration + ']')
        print (Fore.MAGENTA + 'Cleaning...')
        tmrCounter = timer()
        Count = 0
        CleanMain = []
        if CData.get(CLEAN, {}):
          CleanMain = CData[CLEAN]
        CleanMain.append(os.path.basename(OutFile))
        for r, d, f in os.walk(IntDir):
          for n in fnmatch.filter(f, '*.*'):
            Count += 1
            os.remove(os.path.join(r, n))
        f = os.listdir(OutDir)
        for e in CleanMain:
          for n in fnmatch.filter(f, e):
            Count += 1
            os.remove(os.path.join(OutDir, n))
        print (Fore.YELLOW + '{0} files deleted.'.format(Count))
        print ('(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
        Ret = 0
      else:
        print (Fore.BLACK + Back.RED + 'No directory to clean!')
    else:
      #                    === MSVC ===
      if Mode == MODE_MSVC:
        print (Fore.GREEN + '-= Microsoft Visual C++ =-')
        #https://docs.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-by-category?view=vs-2019
        print (Fore.CYAN + '[' + Command + ' ' + Platform + ' ' + Configuration + ']')
        if platform.system() == 'Windows':
          if len(CData[TOOL_DIR]) > 0:
            BTool = Host + '_' + Platform
            BuildCmd = [''] * 4
            BuildCmd[0] = FixSlash(CData[TOOL_DIR].get(BTool + '-bat', ''), False)
            BuildCmd[1] = FixSlash(CData[TOOL_DIR].get(BTool + '-exe', ''), False)
            BuildCmd[2] = FixSlash(os.path.join(os.path.dirname(BuildCmd[1]), 'link.exe'), False)
            BuildCmd[3] = FixSlash(os.path.join(os.path.dirname(BuildCmd[1]), 'lib.exe'), False)
            if os.path.exists(BuildCmd[0]) and os.path.exists(BuildCmd[1]) and os.path.exists(BuildCmd[2]):
              print (Fore.MAGENTA + 'CppMagic is preparing the arguments...')
              tmrCounter = timer()

              SDK_Ver = MacroResolve('${var:winsdk_version}')
              VC_Ver = MacroResolve('${var:vc_version}')
              PrepCmd = '"' + BuildCmd[0] + '"'
              if SDK_Ver.find('{') >= 0:
                SDK_Ver = ''
              else:
                PrepCmd += ' ' + SDK_Ver
              if VC_Ver.find('{') >= 0:
                VC_Ver = ''
              else:
                PrepCmd += ' -vcvars_ver=' + VC_Ver
              PrepCmd += ' & set\n'
              if OsCmd(PrepCmd) == 0:
                for l in OsResp.split('\n'):
                  if 'not found' in l.lower():
                    print (Fore.YELLOW + l)
                  if '=' in l:
                    v = l.split('=')
                    if v[0].find(' ') < 0:
                      if v[0] in os.environ:
                        if v[1] != os.environ[v[0]]:
                          os.environ[v[0]] = v[1]
                      else:
                        os.environ[v[0]] = v[1]

              #Incremental build
              SrcCompile = {}
              ObjLink = []
              os.chdir(IntDir)
              ListSource(CData, Rebuild, SrcCompile, ObjLink)
              os.chdir(TmpDir)
              RSlash = False

              StaticLib = False
              if CData.get(COMMON, {}) and (GENLIB in CData[COMMON]):
                StaticLib = True
              if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
                StaticLib = True
              if StaticLib:
                if (not OutFile.lower().endswith('.lib')):
                  OutFile += '.lib'
              else:
                if (not OutFile.lower().endswith('.exe')):
                  OutFile += '.exe'

              if SrcCompile:
                with open(Fcompile, 'w') as MsPar:
                  MsPar.write('/c ') # Only compile
                  # Compile parameters
                  if CData.get(COMMON, {}):
                    for v in CData[COMMON].get(COMPILE, {}):
                      MsPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    for v in CData[Platform][Configuration].get(COMPILE, {}):
                      MsPar.write('{0} '.format(MacroResolve(v.strip())))
                  # Preprocessor Definitions
                  for v in BuildDef:
                    MsPar.write('/D"{0}" '.format(v.strip()))
                  # Includes
                  for v in BuildInc:
                    MsPar.write('/I"{0}" '.format(v.strip()))
                  # Source Files
                  for s in SrcCompile:
                    if SrcCompile[s] == 0:
                      MsPar.write('/Tc"{0}" '.format(s))
                    else:
                      MsPar.write('/Tp"{0}" '.format(s))
              if SrcCompile or (not os.path.exists(OutFile)):
                with open(FLink, 'w') as MsPar:
                  # Link parameters
                  if CData.get(COMMON, {}):
                    for v in CData[COMMON].get(LINK, {}):
                      MsPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    for v in CData[Platform][Configuration].get(LINK, {}):
                      MsPar.write('{0} '.format(MacroResolve(v.strip())))
                  # Library Path
                  if CData.get(LIB_DIR, {}):
                    for v in CData[LIB_DIR]:
                      MsPar.write('/LIBPATH:"{0}" '.format(FixSlash(MacroResolve(v.strip()))))
                  CustomMods = False
                  if StaticLib:
                    # TODO: Possivelmente ajustar para alteracao feita no GCC, onde ficou possivel "linkar" .obj(.o) junto com .lib(.a)
                    if CData.get(COMMON, {}) and (GENLIB in CData[COMMON]):
                      CustomMods = True
                      for v in CData[COMMON].get(GENLIB, {}):
                        if (not v.lower().endswith(".obj")):
                          v += ".obj"
                        v = os.path.join(IntDir, v)
                        MsPar.write('"{0}" '.format(MacroResolve(v.strip())))
                    if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
                      CustomMods = True
                      for v in CData[Platform][Configuration].get(GENLIB, {}):
                        if (not v.lower().endswith(".obj")):
                          v += ".obj"
                        v = os.path.join(IntDir, v)
                        MsPar.write('"{0}" '.format(MacroResolve(v.strip())))
                  else:
                    # Library Files
                    if CData.get(LIB, {}):
                      for v in CData[LIB]:
                        MsPar.write('"{0}" '.format(MacroResolve(v.strip())))
                  # Object Files
                  if not CustomMods:
                    for o in ObjLink:
                      MsPar.write('"{0}" '.format(o))

              if os.path.exists(Fcompile) or os.path.exists(FLink):
                print ('(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                print (Fore.MAGENTA + 'Building...')
                tmrCounter = timer()
                Ok = 0
                if os.path.exists(Fcompile):
                  print (Fore.YELLOW + 'MSVC is compiling sources...')
                  Ok = OsCmd('"' + BuildCmd[1] + '" @' + Fcompile + ' & exit\n')
                  OsList(True)
                if Ok == 0:
                  LinkType = 2
                  if StaticLib:
                    LinkType = 3
                    print (Fore.YELLOW + 'MSVC is linking the library...')
                  else:
                    print (Fore.YELLOW + 'MSVC is linking the executable...')
                  Ok = OsCmd('"' + BuildCmd[LinkType] + '" @' + FLink + ' & exit\n')
                  OsList(True)
                if Ok > 0:
                  DumpMessages()
                  print (Back.RED + ' ' + Fore.RED + Back.RESET + ' Build error! ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                else:
                  print (Back.GREEN + ' ' + Fore.GREEN + Back.RESET + ' Build Ok. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                  Ret = 0
              else:
                print (Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' Nothing to build. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                Ret = 0
              if args.run and os.path.exists(OutFile):
                print (Fore.MAGENTA + 'Running...')
                print (OutFile)
                OsCmd(FixSlash(OutFile, False) + '\n', False)
            else:
              print (Fore.WHITE + Back.RED + 'Missing building tools!')
          else:
            print (Fore.WHITE + Back.RED + 'No MSVC compiler found!')
        else:
          print (Fore.BLACK + Back.RED + 'This is not a Windows system!')

      #                     === GCC ===
      elif Mode == MODE_GCC:
        print (Fore.GREEN + '-= GNU Compiler Collection =-')
        #https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html
        print (Fore.CYAN + '[' + Command + ' ' + Platform + ' ' + Configuration + ']')
        if len(CData[TOOL_DIR]) > 0:
          BuildCmd = [''] * 4
          BuildCmd[0] = FixSlash(CData[TOOL_DIR].get(GCC, ''))
          BuildCmd[1] = FixSlash(CData[TOOL_DIR].get(GPP, ''))
          BuildCmd[2] = FixSlash(CData[TOOL_DIR].get(AR, ''))
          BuildCmd[3] = FixSlash(CData[TOOL_DIR].get(RANLIB, ''))
          if os.path.exists(BuildCmd[0]):
            print (Fore.MAGENTA + 'CppMagic is preparing the arguments...')
            tmrCounter = timer()

            #Incremental build
            SrcCompile = {}
            GCCFiles = []
            GPPFiles = []
            ObjLink = []
            os.chdir(IntDir)
            ListSource(CData, Rebuild, SrcCompile, ObjLink)
            os.chdir(TmpDir)
            PkgCfg = PkgConfig(CData)

            if SrcCompile:
              def MkCmd(file, source, compiler):
                with open(file, 'w') as GccPar:
                  GccPar.write('-c ') # Just compile
                  # Compile parameters
                  if CData.get(COMMON, {}):
                    if CData[COMMON].get(COMPILE, {}):
                      for v in CData[COMMON][COMPILE].get(COMMON, {}):
                        GccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[COMMON][COMPILE].get(compiler, {}):
                        GccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    if CData[Platform][Configuration].get(COMPILE, {}):
                      for v in CData[Platform][Configuration][COMPILE].get(COMMON, {}):
                        GccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[Platform][Configuration][COMPILE].get(compiler, {}):
                        GccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Bld']:
                    for v in PkgCfg['Bld']:
                      GccPar.write('{0} '.format(v))
                  # Preprocessor Definitions
                  for v in BuildDef:
                    GccPar.write('-D"{0}" '.format(v.strip()))
                  if PkgCfg['Pre']:
                    for v in PkgCfg['Pre']:
                      GccPar.write('-D{0} '.format(v))
                  # Includes
                  for v in BuildInc:
                    GccPar.write('-I"{0}" '.format(v.strip()))
                  if PkgCfg['Inc']:
                    for v in PkgCfg['Inc']:
                      GccPar.write('-I{0} '.format(v))
                  # Source Files
                  for s in source:
                    GccPar.write('{0} '.format(s))
              for s in SrcCompile:
                if SrcCompile[s] == 0:
                  GCCFiles.append(s)
                else:
                  GPPFiles.append(s)
              if GCCFiles:
                MkCmd(Fcompile, GCCFiles, GCC)
              if GPPFiles:
                MkCmd(Fcompile2, GPPFiles, GPP)

            StaticLib = False
            if CData.get(COMMON, {}) and (GENLIB in CData[COMMON]):
              StaticLib = True
            if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
              StaticLib = True
            if StaticLib:
              if os.path.isfile(OutFile):
                os.remove(OutFile)
              if (not OutFile.lower().endswith('.a')):
                  OutFile += '.a'
              Of = os.path.basename(OutFile)
              Op = os.path.dirname(OutFile)
              if (Of.lower()[:3] != 'lib'):
                  Of = 'lib' + Of
              OutFile = os.path.join(Op, Of)

            if SrcCompile or (not os.path.exists(OutFile)):
              with open(FLink, 'w') as GccPar:
                # Build static library
                if StaticLib:
                  print ('Modules will be archived (static lib):')
                  if (CData.get(COMMON, {}) and (AR in CData[COMMON])):
                    for v in CData[COMMON].get(AR, []):
                      GccPar.write('{0} '.format(v.strip()))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (AR in CData[Platform][Configuration]):
                    for v in CData[Platform][Configuration].get(AR, []):
                      GccPar.write('{0} '.format(v.strip()))
                  GccPar.write('{0} '.format(OutFile))
                  CustomMods = False
                  ModList = []
                  if (CData.get(COMMON, {}) and (GENLIB in CData[COMMON])):
                    CustomMods = True
                    for m in CData[COMMON].get(GENLIB, []):
                      ModList.append(m)
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
                    CustomMods = True
                    for m in CData[Platform][Configuration].get(GENLIB, []):
                      ModList.append(m)
                  if not CustomMods:
                    for o in ObjLink:
                      GccPar.write('{0} '.format(o))
                  else:
                    ModSeek = []
                    ModSeek.append(IntDir)
                    if CData.get(LIB_DIR, {}):
                      for v in CData[LIB_DIR]:
                        ModSeek.append(FixSlash(MacroResolve(v.strip())))
                    for Ml in ModList:
                      MOk = False
                      for Ms in ModSeek:
                        Mfile = os.path.join(Ms, Ml)
                        if os.path.isfile(Mfile):
                          if (Mfile.endswith('.a')):
                            ADir = os.path.join(IntDir, Ml)
                            if os.path.exists(ADir):
                              shutil.rmtree(ADir)
                            Mkd(ADir)
                            CDir = os.path.abspath(os.getcwd())
                            os.chdir(ADir)
                            if OsCmd('"{0}" x {1}'.format(AR, Mfile)) == 0:
                              if OsCmd('"{0}" t {1}'.format(AR, Mfile)) == 0:
                                for o in OsResp.split('\n'):
                                  if len(o) > 0:
                                    MExt = os.path.join(ADir, o)
                                    if os.path.isfile(MExt):
                                      GccPar.write('{0} '.format(MExt))
                                    else:
                                      print (Fore.YELLOW + 'Bad module [' + o + "] extracted from " + Ml + " !")
                            os.chdir(CDir)
                          else:
                            GccPar.write('{0} '.format(Mfile))
                          MOk = True
                          break
                        else:
                          for Ol in ObjLink:
                            if Ol == Mfile:
                              GccPar.write('{0} '.format(Mfile))
                              MOk = True
                              break
                          if MOk:
                            break
                      if not MOk:
                        print (Fore.YELLOW + 'Module [' + Ml + "] not found!")
                else:
                  # Link parameters
                  if CData.get(COMMON, {}):
                    for v in CData[COMMON].get(LINK, {}):
                      GccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    for v in CData[Platform][Configuration].get(LINK, {}):
                      GccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Lnk']:
                    for v in PkgCfg['Lnk']:
                      GccPar.write('{0} '.format(v))
                  # Library Path
                  if CData.get(LIB_DIR, {}):
                    for v in CData[LIB_DIR]:
                      GccPar.write('-L{0} '.format(FixSlash(MacroResolve(v.strip()))))
                  if PkgCfg['Lpt']:
                    for v in PkgCfg['Lpt']:
                      GccPar.write('-L{0} '.format(v))
                  # Object Files
                  for o in ObjLink:
                    GccPar.write('{0} '.format(o))
                  # Library Files
                  if CData.get(LIB, {}):
                    for v in CData[LIB]:
                      GccPar.write('-l{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Lib']:
                    for v in PkgCfg['Lib']:
                      GccPar.write('-l{0} '.format(v))
                  # Runtime library path
                  if CData.get(RTLIB_DIR, {}):
                    for v in CData[RTLIB_DIR]:
                      GccPar.write('-Wl,-rpath,{0}: '.format(MacroResolve(v.strip())))

            if os.path.exists(Fcompile) or os.path.exists(Fcompile2) or os.path.exists(FLink):
              print ('(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              print (Fore.MAGENTA + 'Building...')
              tmrCounter = timer()
              os.chdir(IntDir)
              Ok = 0
              print (Fore.YELLOW + 'GCC is compiling sources...')
              if os.path.exists(Fcompile):
                Ok = OsCmd('"{0}" --pipe @{1}'.format(BuildCmd[0], Fcompile))
                OsList(True)
              if os.path.exists(Fcompile2) and (Ok == 0):
                Ok = OsCmd('"{0}" --pipe @{1}'.format(BuildCmd[1], Fcompile2))
                OsList(True)
              if os.path.exists(FLink) and (Ok == 0):
                if StaticLib:
                  print (Fore.YELLOW + 'GCC is linking the library...')
                  if len(BuildCmd[2]) > 1:
                    Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[2], FLink))
                    OsList(True)
                    if (Ok == 0) and CData.get(COMMON, {}) and (RANLIB in CData[COMMON]):
                      if len(BuildCmd[3]) > 1:
                        RlPar = ''
                        for v in CData[COMMON].get(RANLIB, []):
                          RlPar += '"{0}" '.format(v.strip())
                        Ok = OsCmd('"{0}" {1} "{2}"'.format(BuildCmd[3], RlPar, OutFile))
                        OsList(True)
                      else:
                        print (Fore.YELLOW + 'No RANLIB command found to update symbol table.')
                  else:
                    print (Fore.YELLOW + 'No AR command found to link statically!')
                    Ok =1
                else:
                  print (Fore.YELLOW + 'GCC is linking the binary application...')
                  Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[1], FLink))
                  OsList(True)
              if Ok > 0:
                DumpMessages()
                print (Back.RED + ' ' + Fore.RED + Back.RESET + ' Build error! ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              else:
                print (Back.GREEN + ' ' + Fore.GREEN + Back.RESET + ' Build Ok. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                Ret = 0
            else:
              print (Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' Nothing to build. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              Ret = 0
            if args.run and os.path.exists(OutFile):
              print (Fore.MAGENTA + 'Running...')
              print (OutFile)
              OsCmd(FixSlash(OutFile) + '\n', False)
          else:
            print (Fore.WHITE + Back.RED + 'Missing building tools!')
        else:
          print (Fore.WHITE + Back.RED + 'No GCC compiler found!')

      #                     === CLANG ===
      elif Mode == MODE_CLANG:
        print (Fore.GREEN + '-= LLVM native C C++ Objective-C compiler =-')
        #https://llvm.org/docs/CommandGuide/index.html
        print (Fore.CYAN + '[' + Command + ' ' + Platform + ' ' + Configuration + ']')
        if len(CData[TOOL_DIR]) > 0:
          BuildCmd = [''] * 4
          BuildCmd[0] = FixSlash(CData[TOOL_DIR].get(LCC, ''))
          BuildCmd[1] = FixSlash(CData[TOOL_DIR].get(LPP, ''))
          BuildCmd[2] = FixSlash(CData[TOOL_DIR].get(AR, ''))
          BuildCmd[3] = FixSlash(CData[TOOL_DIR].get(RANLIB, ''))
          if os.path.exists(BuildCmd[0]):
            print (Fore.MAGENTA + 'CppMagic is preparing the arguments...')
            tmrCounter = timer()

            #Incremental build
            SrcCompile = {}
            LCCFiles = []
            LPPFiles = []
            ObjLink = []
            os.chdir(IntDir)
            ListSource(CData, Rebuild, SrcCompile, ObjLink)
            os.chdir(TmpDir)
            PkgCfg = PkgConfig(CData)

            if SrcCompile:
              def MkCmd(file, source, compiler):
                with open(file, 'w') as LccPar:
                  LccPar.write('-c ') # Just compile
                  # Compile parameters
                  if CData.get(COMMON, {}):
                    if CData[COMMON].get(COMPILE, {}):
                      for v in CData[COMMON][COMPILE].get(COMMON, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[COMMON][COMPILE].get(compiler, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    if CData[Platform][Configuration].get(COMPILE, {}):
                      for v in CData[Platform][Configuration][COMPILE].get(COMMON, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[Platform][Configuration][COMPILE].get(compiler, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Bld']:
                    for v in PkgCfg['Bld']:
                      LccPar.write('{0} '.format(v))
                  # Preprocessor Definitions
                  for v in BuildDef:
                    LccPar.write('-D"{0}" '.format(v.strip()))
                  if PkgCfg['Pre']:
                    for v in PkgCfg['Pre']:
                      LccPar.write('-D{0} '.format(v))
                  # Includes
                  for v in BuildInc:
                    LccPar.write('-I"{0}" '.format(v.strip()))
                  if PkgCfg['Inc']:
                    for v in PkgCfg['Inc']:
                      LccPar.write('-I{0} '.format(v))
                  # Source Files
                  for s in source:
                    LccPar.write('{0} '.format(s))
              for s in SrcCompile:
                if SrcCompile[s] == 0:
                  LCCFiles.append(s)
                else:
                  LPPFiles.append(s)
              if LCCFiles:
                MkCmd(Fcompile, LCCFiles, GCC)
              if LPPFiles:
                MkCmd(Fcompile2, LPPFiles, GPP)

            StaticLib = False
            if CData.get(COMMON, {}) and (GENLIB in CData[COMMON]):
              StaticLib = True
            if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
              StaticLib = True
            if StaticLib:
              if os.path.isfile(OutFile):
                os.remove(OutFile)
              if (not OutFile.lower().endswith('.a')):
                  OutFile += '.a'
              Of = os.path.basename(OutFile)
              Op = os.path.dirname(OutFile)
              if (Of.lower()[:3] != 'lib'):
                  Of = 'lib' + Of
              OutFile = os.path.join(Op, Of)

            if SrcCompile or (not os.path.exists(OutFile)):
              with open(FLink, 'w') as LccPar:
                # Build static library
                if StaticLib:
                  print ('Modules will be archived (static lib):')
                  if (CData.get(COMMON, {}) and (AR in CData[COMMON])):
                    for v in CData[COMMON].get(AR, []):
                      LccPar.write('{0} '.format(v.strip()))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (AR in CData[Platform][Configuration]):
                    for v in CData[Platform][Configuration].get(AR, []):
                      LccPar.write('{0} '.format(v.strip()))
                  LccPar.write('{0} '.format(OutFile))
                  CustomMods = False
                  ModList = []
                  if (CData.get(COMMON, {}) and (GENLIB in CData[COMMON])):
                    CustomMods = True
                    for m in CData[COMMON].get(GENLIB, []):
                      ModList.append(m)
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
                    CustomMods = True
                    for m in CData[Platform][Configuration].get(GENLIB, []):
                      ModList.append(m)
                  if not CustomMods:
                    for o in ObjLink:
                      LccPar.write('{0} '.format(o))
                  else:
                    ModSeek = []
                    ModSeek.append(IntDir)
                    if CData.get(LIB_DIR, {}):
                      for v in CData[LIB_DIR]:
                        ModSeek.append(FixSlash(MacroResolve(v.strip())))
                    for Ml in ModList:
                      MOk = False
                      for Ms in ModSeek:
                        Mfile = os.path.join(Ms, Ml)
                        if os.path.isfile(Mfile):
                          if (Mfile.endswith('.a')):
                            ADir = os.path.join(IntDir, Ml)
                            if os.path.exists(ADir):
                              shutil.rmtree(ADir)
                            Mkd(ADir)
                            CDir = os.path.abspath(os.getcwd())
                            os.chdir(ADir)
                            if OsCmd('"{0}" x {1}'.format(AR, Mfile)) == 0:
                              if OsCmd('"{0}" t {1}'.format(AR, Mfile)) == 0:
                                for o in OsResp.split('\n'):
                                  if len(o) > 0:
                                    MExt = os.path.join(ADir, o)
                                    if os.path.isfile(MExt):
                                      LccPar.write('{0} '.format(MExt))
                                    else:
                                      print (Fore.YELLOW + 'Bad module [' + o + "] extracted from " + Ml + " !")
                            os.chdir(CDir)
                          else:
                            LccPar.write('{0} '.format(Mfile))
                          MOk = True
                          break
                        else:
                          for Ol in ObjLink:
                            if Ol == Mfile:
                              LccPar.write('{0} '.format(Mfile))
                              MOk = True
                              break
                          if MOk:
                            break
                      if not MOk:
                        print (Fore.YELLOW + 'Module [' + Ml + "] not found!")
                else:
                  # Link parameters
                  if CData.get(COMMON, {}):
                    for v in CData[COMMON].get(LINK, {}):
                      LccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    for v in CData[Platform][Configuration].get(LINK, {}):
                      LccPar.write('{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Lnk']:
                    for v in PkgCfg['Lnk']:
                      LccPar.write('{0} '.format(v))
                  # Library Path
                  if CData.get(LIB_DIR, {}):
                    for v in CData[LIB_DIR]:
                      LccPar.write('-L{0} '.format(FixSlash(MacroResolve(v.strip()))))
                  if PkgCfg['Lpt']:
                    for v in PkgCfg['Lpt']:
                      LccPar.write('-L{0} '.format(v))
                  # Object Files
                  for o in ObjLink:
                    LccPar.write('{0} '.format(o))
                  # Library Files
                  if CData.get(LIB, {}):
                    for v in CData[LIB]:
                      LccPar.write('-l{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Lib']:
                    for v in PkgCfg['Lib']:
                      LccPar.write('-l{0} '.format(v))
                  # Runtime library path
                  if CData.get(RTLIB_DIR, {}):
                    for v in CData[RTLIB_DIR]:
                      LccPar.write('-Wl,-rpath,{0} '.format(MacroResolve(v.strip())))

            if os.path.exists(Fcompile) or os.path.exists(Fcompile2) or os.path.exists(FLink):
              print ('(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              print (Fore.MAGENTA + 'Building...')
              tmrCounter = timer()
              os.chdir(IntDir)
              Ok = 0
              print (Fore.YELLOW + 'Clang is compiling sources...')
              if os.path.exists(Fcompile):
                Ok = OsCmd('"{0}" --pipe @{1}'.format(BuildCmd[0], Fcompile))
                OsList(True)
              if os.path.exists(Fcompile2) and (Ok == 0):
                Ok = OsCmd('"{0}" --pipe @{1}'.format(BuildCmd[1], Fcompile2))
                OsList(True)
              if os.path.exists(FLink) and (Ok == 0):
                if StaticLib:
                  print (Fore.YELLOW + 'Clang is linking the library...')
                  if len(BuildCmd[2]) > 1:
                    Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[2], FLink))
                    OsList(True)
                    if (Ok == 0) and CData.get(COMMON, {}) and (RANLIB in CData[COMMON]):
                      if len(BuildCmd[3]) > 1:
                        RlPar = ''
                        for v in CData[COMMON].get(RANLIB, []):
                          RlPar += '"{0}" '.format(v.strip())
                        Ok = OsCmd('"{0}" {1} "{2}"'.format(BuildCmd[3], RlPar, OutFile))
                        OsList(True)
                      else:
                        print (Fore.YELLOW + 'No RANLIB command found to update symbol table.')
                  else:
                    print (Fore.YELLOW + 'No AR command found to link statically!')
                    Ok =1
                else:
                  print (Fore.YELLOW + 'Clang is linking the binary application...')
                  Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[1], FLink))
                  OsList(True)
              if Ok > 0:
                DumpMessages()
                print (Back.RED + ' ' + Fore.RED + Back.RESET + ' Build error! ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              else:
                print (Back.GREEN + ' ' + Fore.GREEN + Back.RESET + ' Build Ok. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                Ret = 0
            else:
              print (Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' Nothing to build. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              Ret = 0
            if args.run and os.path.exists(OutFile):
              print (Fore.MAGENTA + 'Running...')
              print (OutFile)
              OsCmd(FixSlash(OutFile) + '\n', False)
          else:
            print (Fore.WHITE + Back.RED + 'Missing building tools!')
        else:
          print (Fore.WHITE + Back.RED + 'No Clang compiler found!')

      #                     === EMCC ===
      elif Mode == MODE_EMCC:
        print (Fore.GREEN + '-= Emscripten Compiler Frontend =-')
        #https://emscripten.org/docs/tools_reference/emcc.html
        print (Fore.CYAN + '[' + Command + ' ' + Platform + ' ' + Configuration + ']')
        if len(CData[TOOL_DIR]) > 0:
          BuildCmd = [''] * 4
          BuildCmd[0] = FixSlash(CData[TOOL_DIR].get(ECC, ''))
          BuildCmd[1] = FixSlash(CData[TOOL_DIR].get(EPP, ''))
          BuildCmd[2] = FixSlash(CData[TOOL_DIR].get(EAR, ''))
          BuildCmd[3] = FixSlash(CData[TOOL_DIR].get(ERANLIB, ''))
          if os.path.exists(BuildCmd[0]):
            print (Fore.MAGENTA + 'CppMagic is preparing the arguments...')
            tmrCounter = timer()

            #Incremental build
            SrcCompile = {}
            ECCFiles = []
            EPPFiles = []
            ObjLink = []
            os.chdir(IntDir)
            ListSource(CData, Rebuild, SrcCompile, ObjLink)
            os.chdir(TmpDir)
            PkgCfg = PkgConfig(CData)

            if SrcCompile:
              def MkCmd(file, source, compiler):
                with open(file, 'w') as LccPar:
                  LccPar.write('-c ') # Just compile
                  # Compile parameters
                  if CData.get(COMMON, {}):
                    if CData[COMMON].get(COMPILE, {}):
                      for v in CData[COMMON][COMPILE].get(COMMON, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[COMMON][COMPILE].get(compiler, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                    if CData[COMMON].get(SETTINGS, {}): # Settings
                      for v in CData[COMMON][SETTINGS].get(COMMON, {}):
                        LccPar.write('-s {0} '.format(MacroResolve(v.strip())))
                      for v in CData[COMMON][SETTINGS].get(compiler, {}):
                        LccPar.write('-s {0} '.format(MacroResolve(v.strip())))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    if CData[Platform][Configuration].get(COMPILE, {}):
                      for v in CData[Platform][Configuration][COMPILE].get(COMMON, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                      for v in CData[Platform][Configuration][COMPILE].get(compiler, {}):
                        LccPar.write('{0} '.format(MacroResolve(v.strip())))
                    if CData[Platform][Configuration].get(SETTINGS, {}): # Settings
                      for v in CData[Platform][Configuration][SETTINGS].get(COMMON, {}):
                        LccPar.write('-s {0} '.format(MacroResolve(v.strip())))
                      for v in CData[Platform][Configuration][SETTINGS].get(compiler, {}):
                        LccPar.write('-s {0} '.format(MacroResolve(v.strip())))

                  if PkgCfg['Bld']:
                    for v in PkgCfg['Bld']:
                      LccPar.write('{0} '.format(v))
                  # Preprocessor Definitions
                  for v in BuildDef:
                    LccPar.write('-D"{0}" '.format(v.strip()))
                  if PkgCfg['Pre']:
                    for v in PkgCfg['Pre']:
                      LccPar.write('-D{0} '.format(v))
                  # Includes
                  for v in BuildInc:
                    LccPar.write('-I"{0}" '.format(v.strip()))
                  if PkgCfg['Inc']:
                    for v in PkgCfg['Inc']:
                      LccPar.write('-I{0} '.format(v))
                  # Source Files
                  for s in source:
                    LccPar.write('{0} '.format(s))
              for s in SrcCompile:
                if SrcCompile[s] == 0:
                  ECCFiles.append(s)
                else:
                  EPPFiles.append(s)
              if ECCFiles:
                MkCmd(Fcompile, ECCFiles, ECC)
              if EPPFiles:
                MkCmd(Fcompile2, EPPFiles, EPP)

            StaticLib = False
            if CData.get(COMMON, {}) and (GENLIB in CData[COMMON]):
              StaticLib = True
            if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
              StaticLib = True
            if StaticLib:
              if os.path.isfile(OutFile):
                os.remove(OutFile)
              if (not OutFile.lower().endswith('.a')):
                  OutFile += '.a'
              Of = os.path.basename(OutFile)
              Op = os.path.dirname(OutFile)
              if (Of.lower()[:3] != 'lib'):
                  Of = 'lib' + Of
              OutFile = os.path.join(Op, Of)

            EmccPacker = False
            if SrcCompile or (not os.path.exists(OutFile)):
              with open(FLink, 'w') as LccPar:
                # Build static library
                if StaticLib:
                  print ('Modules will be archived (static lib):')
                  if (CData.get(COMMON, {}) and (AR in CData[COMMON])):
                    for v in CData[COMMON].get(AR, []):
                      LccPar.write('{0} '.format(v.strip()))
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (AR in CData[Platform][Configuration]):
                    for v in CData[Platform][Configuration].get(AR, []):
                      LccPar.write('{0} '.format(v.strip()))
                  LccPar.write('{0} '.format(OutFile))
                  CustomMods = False
                  ModList = []
                  if (CData.get(COMMON, {}) and (GENLIB in CData[COMMON])):
                    CustomMods = True
                    for m in CData[COMMON].get(GENLIB, []):
                      ModList.append(m)
                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}) and (GENLIB in CData[Platform][Configuration]):
                    CustomMods = True
                    for m in CData[Platform][Configuration].get(GENLIB, []):
                      ModList.append(m)
                  if not CustomMods:
                    for o in ObjLink:
                      LccPar.write('{0} '.format(o))
                  else:
                    ModSeek = []
                    ModSeek.append(IntDir)
                    if CData.get(LIB_DIR, {}):
                      for v in CData[LIB_DIR]:
                        ModSeek.append(FixSlash(MacroResolve(v.strip())))
                    for Ml in ModList:
                      MOk = False
                      for Ms in ModSeek:
                        Mfile = os.path.join(Ms, Ml)
                        if os.path.isfile(Mfile):
                          if (Mfile.endswith('.a')):
                            ADir = os.path.join(IntDir, Ml)
                            if os.path.exists(ADir):
                              shutil.rmtree(ADir)
                            Mkd(ADir)
                            CDir = os.path.abspath(os.getcwd())
                            os.chdir(ADir)
                            if OsCmd('"{0}" x {1}'.format(AR, Mfile)) == 0:
                              if OsCmd('"{0}" t {1}'.format(AR, Mfile)) == 0:
                                for o in OsResp.split('\n'):
                                  if len(o) > 0:
                                    MExt = os.path.join(ADir, o)
                                    if os.path.isfile(MExt):
                                      LccPar.write('{0} '.format(MExt))
                                    else:
                                      print (Fore.YELLOW + 'Bad module [' + o + "] extracted from " + Ml + " !")
                            os.chdir(CDir)
                          else:
                            LccPar.write('{0} '.format(Mfile))
                          MOk = True
                          break
                        else:
                          for Ol in ObjLink:
                            if Ol == Mfile:
                              LccPar.write('{0} '.format(Mfile))
                              MOk = True
                              break
                          if MOk:
                            break
                      if not MOk:
                        print (Fore.YELLOW + 'Module [' + Ml + "] not found!")
                else:
                  # Link parameters
                  if CData.get(COMMON, {}):
                    for v in CData[COMMON].get(LINK, {}):
                      LccPar.write('{0} '.format(MacroResolve(v.strip())))
                    for v in CData[COMMON].get(LSETTINGS, {}): # Settings
                      LccPar.write('-s {0} '.format(MacroResolve(v.strip())))

                  if CData.get(Platform, {}) and CData[Platform].get(Configuration, {}):
                    for v in CData[Platform][Configuration].get(LINK, {}):
                      LccPar.write('{0} '.format(MacroResolve(v.strip())))
                    for v in CData[Platform][Configuration].get(LSETTINGS, {}): # Settings
                      LccPar.write('-s {0} '.format(MacroResolve(v.strip())))

                  if CData.get(SHELL_FILE, {}): # Shell File
                    LccPar.write('--shell-file {0} '.format(MacroResolve(CData.get(SHELL_FILE,''))))
                  if CData.get(EMBED_FILE, {}): # Embed File
                    LccPar.write('--embed-file {0} '.format(MacroResolve(CData.get(EMBED_FILE,''))))
                    EmccPacker = True
                  if CData.get(PRELOAD_FILE, {}): # Preload File
                    LccPar.write('--preload-file {0} '.format(MacroResolve(CData.get(PRELOAD_FILE,''))))
                    EmccPacker = True

                  if PkgCfg['Lnk']:
                    for v in PkgCfg['Lnk']:
                      LccPar.write('{0} '.format(v))
                  # Library Path
                  if CData.get(LIB_DIR, {}):
                    for v in CData[LIB_DIR]:
                      LccPar.write('-L{0} '.format(FixSlash(MacroResolve(v.strip()))))
                  if PkgCfg['Lpt']:
                    for v in PkgCfg['Lpt']:
                      LccPar.write('-L{0} '.format(v))
                  # Object Files
                  for o in ObjLink:
                    LccPar.write('{0} '.format(o))
                  # Library Files
                  if CData.get(LIB, {}):
                    for v in CData[LIB]:
                      LccPar.write('-l{0} '.format(MacroResolve(v.strip())))
                  if PkgCfg['Lib']:
                    for v in PkgCfg['Lib']:
                      LccPar.write('-l{0} '.format(v))
                  # Runtime library path
                  if CData.get(RTLIB_DIR, {}):
                    for v in CData[RTLIB_DIR]:
                      LccPar.write('-Wl,-rpath,{0} '.format(MacroResolve(v.strip())))

            if os.path.exists(Fcompile) or os.path.exists(Fcompile2) or os.path.exists(FLink):
              print ('(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              print (Fore.MAGENTA + 'Building...')
              tmrCounter = timer()
              os.chdir(IntDir)
              Ok = 0
              print (Fore.YELLOW + 'Emcc is compiling sources...')
              if os.path.exists(Fcompile):
                Ok = OsCmd('"{0}" @{1}'.format(BuildCmd[0], Fcompile))
                OsList(True)
              if os.path.exists(Fcompile2) and (Ok == 0):
                Ok = OsCmd('"{0}" @{1}'.format(BuildCmd[1], Fcompile2))
                OsList(True)
              if os.path.exists(FLink) and (Ok == 0):
                if StaticLib:
                  print (Fore.YELLOW + 'Emcc is linking the library...')
                  if len(BuildCmd[2]) > 1:
                    Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[2], FLink))
                    OsList(True)
                    if (Ok == 0) and CData.get(COMMON, {}) and (RANLIB in CData[COMMON]):
                      if len(BuildCmd[3]) > 1:
                        RlPar = ''
                        for v in CData[COMMON].get(RANLIB, []):
                          RlPar += '"{0}" '.format(v.strip())
                        Ok = OsCmd('"{0}" {1} "{2}"'.format(BuildCmd[3], RlPar, OutFile))
                        OsList(True)
                      else:
                        print (Fore.YELLOW + 'No RANLIB command found to update symbol table.')
                  else:
                    print (Fore.YELLOW + 'No AR command found to link statically!')
                    Ok =1
                else:
                  print (Fore.YELLOW + 'Emcc is linking the binary application...')
                  if EmccPacker:
                    os.chdir(RunDir)
                  Ok = OsCmd('"{0}" @"{1}"'.format(BuildCmd[1], FLink))
                  OsList(True)
              if Ok > 0:
                DumpMessages()
                print (Back.RED + ' ' + Fore.RED + Back.RESET + ' Build error! ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              else:
                print (Back.GREEN + ' ' + Fore.GREEN + Back.RESET + ' Build Ok. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
                Ret = 0
            else:
              print (Back.YELLOW + ' ' + Fore.YELLOW + Back.RESET + ' Nothing to build. ' + Fore.RESET + '(Elapsed {:.1f}s)'.format(timer() - tmrCounter))
              Ret = 0
            if args.run and os.path.exists(OutFile):
              print (Fore.MAGENTA + 'Running...')
              print (OutFile)
              OsCmd(FixSlash(OutFile) + '\n', False)
          else:
            print (Fore.WHITE + Back.RED + 'Missing building tools!')
        else:
          print (Fore.WHITE + Back.RED + 'No Clang compiler found!')

  elif Command == CMD_INSTALL: # --== INSTALL ==--
    print (Fore.MAGENTA + 'Installing...')
    if not Mode:
      print(Fore.YELLOW + 'Inform a compiler! (-m option)')
      exit(1)
    if Mode == MODE_EMCC:
      Platform = WASM
    if not Platform:
      print(Fore.YELLOW + 'Inform a platform! (-p option)')
      exit(1)
    if Platform == WASM:
      Mode = MODE_EMCC
    if not Configuration:
      print(Fore.YELLOW + 'Inform a configuration! (-c option)')
      exit(1)
    print (Fore.CYAN + '[' + Mode + ' ' + Platform + ' ' + Configuration + ']')
    Ok = False
    CData = MakeEnv(CheckConfig(False))
    if len(CData) > 0:
      if PrjJsonLoaded:
        if CData.get(INSTALL, {}):
          if CData[INSTALL].get(PREFIX, {}) and (CData[INSTALL][PREFIX] != ''):
            if CData[INSTALL].get(OUTPUT, {}) and CData[INSTALL][OUTPUT]:
              Ok = True
            else:
              print(Fore.RED + 'No output options available for install.' + Fore.RESET)
              exit(1)
          else:
            print(Fore.RED + 'No prefix options available for install.' + Fore.RESET)
            exit(1)
        else:
          print(Fore.RED + 'No install options available.' + Fore.RESET)
          exit(1)
      else:
        print(Fore.RED + 'Cannot proceed without a project configuration file.' + Fore.RESET)
        exit(1)
    else:
      print(Fore.RED + 'Cannot proceed with bad or empty configuration file.' + Fore.RESET)
      exit(1)
    if Ok:
      Prefix = os.path.abspath(MacroResolve(CData[INSTALL][PREFIX].strip()))
      Output = []
      for o in CData[INSTALL][OUTPUT]:
        if o.get('sub_dir', {}) and (o['sub_dir'] != ''):
          ToPath = os.path.join(Prefix, MacroResolve(o['sub_dir'].strip()))
          if o.get('files', {}) and o['files']:
            for f in o['files']:
              FromFile = f.strip()
              if FromFile != '':
                FromFile = MacroResolve(FromFile)
                ToFile = os.path.basename(FromFile)
                ToFile = os.path.join(ToPath, ToFile)
                Otp = {}
                Otp['FFrom'] = FromFile
                Otp['FTo'] = ToFile
                Output.append(Otp)
          else:
            print(Fore.RED + 'No files option available.' + Fore.RESET)
            exit(1)
        else:
          print(Fore.RED + 'No subdir option available.' + Fore.RESET)
          exit(1)
      if not os.path.exists(Prefix):
        os.makedirs(Prefix)
      if os.path.exists(Prefix):
        print('Installing on ' + Fore.YELLOW + Prefix)
        Count = 0
        for o in Output:
          if os.path.exists(o['FFrom']):
            OPath = os.path.dirname(o['FTo'])
            if not os.path.exists(OPath):
              os.makedirs(OPath)
            shutil.copyfile(o['FFrom'], o['FTo'])
            print('  ' + o['FFrom'] + ' -> ' + Fore.YELLOW + o['FTo'])
            Count += 1
          else:
            print('  ' + o['FFrom'] + Fore.RED + ' ( NOT FOUND )')
        print (Fore.YELLOW + '{0} files copied.'.format(Count))
        Ret = 0
      else:
        print(Fore.RED + 'Cannot create destination install path (prefix).' + Fore.RESET + '[' + ToPath + ']')
        exit(1)

  elif Command == CMD_HOST:
    HDir = args.hostdir
    if not HDir:
      HDir = os.getcwd()
    HPort = int(args.hostport)
    if not HPort:
      HPort = 8080
    SPage = args.startpage
    if not SPage:
      SPage = 'index.html'
    Url = 'http://127.0.0.1:' + str(HPort) + '/' + SPage
    class Handler(http.server.SimpleHTTPRequestHandler):
      def __init__(self, *args, **kwargs):
        self.path = SPage
        super().__init__(*args, directory=HDir, **kwargs)
    with socketserver.TCPServer(("", HPort), Handler) as httpd:
      print('Starting http server...')
      print('Accessing ' + Url + '...')
      webbrowser.open(Url)
      httpd.serve_forever()

  else:
    print ('Invalid command ' + Fore.YELLOW + Command)
  print ('Total Time {:.1f}s'.format(timer() - tmrProcess))
  if (Ret == 0):
    if PubDir:
      if os.path.exists(OutFile):
        PubFile = os.path.join(PubDir, os.path.basename(OutFile))
        shutil.copy2(OutFile, PubFile)
  exit(Ret)
