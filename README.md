# Ghinja (1.7)
Author: **Martin Petran**

_Plugin to embed Ghidra Decompiler into Binary Ninja_

## Description:
This plugin allows you to enable a dock in the UI that will show a result of the Ghidra decompiler for the given function. There is basic syntax highlighting and selected text highlighting (something missing in Ghidra). Renaming functions and variables in the Binary Ninja view is refleced in the Ghinja view as well. The plugin will prompt you for pointing it to the path of the `analyzeHeadless` file which is relevant for your operating system. When chosen it will automatically start ghidra decompilation whenever a new file is opened. The decompile results are stored in the `user_plugin_path() + "/ghinja_projects"` folder.

![Sample](https://github.com/Martyx00/ghinja/blob/master/img/demo.gif?raw=true "Sample")

**Available Hotkeys:**
* ***N*** - When Ghinja window has focus you can use this hotkey to rename the variable that does not have equivalent in the Binary Ninja view. This function allows you to rename anything, however all labels (functions, variables, etc.) that are are avialable in Binary Ninja view should be renamed there rather than in Ghinja as that is string replace only.
* ***F*** - When Ghinja window has focus you can use this hotkey to perform a simple text seatch in the decompiler result.


## Minimum Version

This plugin requires the following minimum version of Binary Ninja:

 * 2263

## Required Dependencies

The following dependencies are required for this plugin:

 * other - https://ghidra-sre.org/

## Disclaimer

I have nothing in common with development of Ghidra decompiler.

**If you have used versions prior to 1.0, it will be better if you remove all old ghinja projects and start from scratch. Sorry ... :(**

## License

This plugin is released under a Apache license.
## Metadata Version

2
