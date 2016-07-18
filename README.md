# Sublime TTCN-3 plugin

Sublime Text 3 plugin that offers auto-completion, Goto Definition and syntax highlight for TTCN-3 and ASN.1

![Example](demo_external.gif)

This plugin aims to provide easy-to-use, minimal-setup autocompletions for TTCN-3 for Sublime Text 3.

## Install this plugin ##
- Install from source code.
  + download one of the releases from
    [here](https://github.com/HuiMi24/TtcnComplete).
  + `Preferences->Browse Packages...`, copy "TtcnComplete" to open folder
- Package Control
  + Package Control doesn't include this plugin yet.

## Settings auto completion trigger ##

Copy this to Setting User

`Preferences->Setting-User`

  ```json
	"auto_complete_triggers":
	[
		{
			"characters": ".",
			"selector": "source.ttcn3"
		}
	]
  ```

#Notes:
1. It only support file end with ".ttcn"
2. The module name must be same as the file name
