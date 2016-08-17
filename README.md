## Next Plan ##
I will add TTCN-3 code formatter/lint in next release. If you find any bug or you have any new idea, please feel free to contact me. You can also commit your code with pull request.

# Sublime Text 3 TTCN-3 plugin: TtcnComplete

Sublime Text 3 plugin that offers auto-completion, Goto Definition and syntax highlight for TTCN-3 and ASN.1

![Example](demo_external.gif)

This plugin aims to provide easy-to-use, minimal-setup autocompletions for TTCN-3 for Sublime Text 3.

## Install this plugin ##
- Package Control
  + `Preferences->Package Control->Install Package`, search TtcnComplete.
  + Restart Sublime
- Install from source code.
  + download one of the releases from
    [here](https://github.com/HuiMi24/TtcnComplete).
  + `Preferences->Browse Packages...`, copy "TtcnComplete" to open folder

## Usage ##
- Open you code with Sublime.
  + `Project->Add Folder to Project...`

#Notes:
1. Support TTCN-3 file extension ".ttcn", ".ttcn3", ASN.1 file extension ".asn", module parameter file extension ".par". If the extension does not included, please post an issue or commit a pull request.
2. The module name must be same as the file name
3. Currently, it only tested on Windows and Linux. Mac OS not tested, however, it should work.
