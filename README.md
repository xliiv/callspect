# callspect


Inspect execution of python script

This is:  **proof of concept**, so expect buggy behaviour


## Usage:

```bash
# add command `callspectpy` which collects execution data
pip install callspectpy
# generate execution data from python script path-to-some-scirpt.py
callspectpy -i path-to-some-scirpt.py
# add command `callspect` which is a viewer for data generated by `callspectpy`
pip install callspect
# shows generated data in browser
callspect callspect.txt
# open browser at http://127.0.0.1:5000/
```

## Viewer preview

![alt text](https://raw.githubusercontent.com/xliiv/callspect/master/callspect-demo.gif "Callspect viewer in action")



## TODO:
    * clearify root aka mainthread
        * should it be displayed?
        * what should be named?
        * viewer adds it or collector adds it
    * threads
        * extractor should spit out mainthread or __main__?
            * viewer should consume already spit value (now viewer adds it)
    * exceptions in settrace: https://pymotw.com/2/sys/tracing.html
    * global variables are shown as arrow to main thread
    * create callspectrs?
        * research if possible
            * https://users.rust-lang.org/t/the-big-picture-of-compilation-in-rust/6380/3
            * https://blog.rust-lang.org/2016/04/19/MIR.html
