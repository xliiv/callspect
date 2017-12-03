# callspectpy

Collects execution data from python script

## CLI

```bash
$ callspectpy -i my-script.py
```


## API

To collect data for specific code, just wrap the code like this:

```python
import callspectpy, os
callspectpy.trace2file_start(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'callspect.txt')
)

#
# YOUR CODE HERE
#

callspectpy.trace2file_stop()
```

Or better, use context manager:

```python
from callspect.py import trace2file
with trace2file('output.txt'):
    # YOUR CODE HERE

```



### TODO:
    * exec(code_obj) generates odd "<module>", replace it with name user passes
    * when runnnig "from my_package.lib import my_fn", module is equal "lib" :(

