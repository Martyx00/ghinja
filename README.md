# Ghinja (0.1)
Author: **Martin Petran**
_Plugin to embed Ghidra Decompiler into Binary Ninja_
## Description:
This plugin allows you to enable a dock in the UI that will show a result of the Ghidra decompiler for the given function. There is basic syntax highlighting and renaming functions and variables in the Binary Ninja view is refleced in the Ghinja view as well. The plugin will prompt you for pointing it to the path of the `analyzeHeadless` file which is relevant for your operating system. When chosen it will automatically start ghidra decompilation whenever a new file is opened. The decompile results are stored in the `user_plugin_path() + "/ghinja_projects"` folder.

![Sample](https://github.com/Martyx00/ghinja/blob/master/img/demo.gif?raw=true "Sample")


## Minimum Version

This plugin requires the following minimum version of Binary Ninja:

 * 2263

## Required Dependencies

The following dependencies are required for this plugin:

 * other - https://ghidra-sre.org/

## Disclaimer

I have nothing in common with development of Ghidra decompiler.
Also note that as the version of the plugin stays below 1.0 there are likely many bugs to address.

## License

This plugin is released under a Apache license.
## Metadata Version

2
