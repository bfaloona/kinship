## install

### pygraphviz
To create charts, [pygraphviz](https://www.graphviz.org/) is required. This package is not installed by default.
#### MacOS
[This post](https://stackoverflow.com/questions/69970147/how-do-i-resolve-the-pygraphviz-error-on-mac-os) provided useful information for solving the install on MacOS.

1. `brew install graphviz`
2. Add this to your `.zshrc` or otherwise invoke it in the shell you are using. `brew --prefix graphviz` or `brew info graphviz` will provide the path to the graphviz install.
```bash
export GRAPHVIZ_DIR="/opt/homebrew/opt/graphviz"
export CFLAGS="-I $GRAPHVIZ_DIR/include"
export LDFLAGS="-L $GRAPHVIZ_DIR/lib"
```
3. `pip install pygraphviz`

## Sample gedcom files
https://github.com/findmypast/gedcom-samples/tree/main
