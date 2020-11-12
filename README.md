# importmagic.nvim
A neovim plugin to automatically import unresolved symbols in python, using [importmagic](https://github.com/alecthomas/importmagic). Highly WIP, expect lots of issues and breaking changes

## Installation
For now, it's simple -
1. Install the importmagic package - `pip install importmagic`
2. Install the plugin however you install other plugins
3. Run `:UpdateRemotePlugins` to register the plugin  
_Note_: Some plugin managers do this for you. If you have trouble just run it once and it should work fine  
For example, if you are using [vim-plug](https://github.com/junegunn/vim-plug), you can add this to your plugin section -
```
Plug "anihm136/importmagic.nvim", {'do': ':UpdateRemotePlugins'}
```
4. Profit

## Usage
Currently the plugin exposes a single command - `:UpdateImports`, which searches the file for unresolved symbols and unused imports. It then replaces these with a new import block, containing the best matches for where these symbols are defined  
**tl;dr: Run `:UpdateImports` in your python file to fix imports**

## Issues
1. The version of importmagic on PyPi does not recognise type hints as references. To fix this, install from source - `pip install git+https://github.com/alecthomas/importmagic`
2. If the package containing the symbols is not installed, importmagic may find the symbol in a wrong package (rarely, most of the time it does nothing)
3. Running `:UpdateImports` for the first time may be slow. The package needs to create an index of all packages in the environment, which happens in the background. However, if the function is called before indexing is finished, it blocks until the indexing is done and then performs the imports. Will be fixed  
_Note_: This should be fixed, not rigorously tested yet


## TODO
- [x] Prevent blocking on running `:UpdateImports` when indexing is running
- [ ] Provide functionality to choose among available import targets when multiple are available
- [ ] Find a way to save generated indexes
	* May require dabbling in the importmagic package itself
	*	_Note_: The package currently does not support incremental indexing
- [ ]	Find a better way to get `sys.path` of the editor

