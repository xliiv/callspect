# callspect


Inspect execution of python script

This is:  **proof of concept**, so expect buggy behaviour


## Example:

```bash
# installation

git clone https://github.com/xliiv/callspect
cd callspect/

python3 -m venv venv
. venv/bin/activate
# install `callspectpy` which generates data from python script
pip install -e collector/
# install `callspect` which shows data in browser
pip install -e viewer/
# if don't have `7z` then run:
# sudo apt install p7zip-full
7z x -oviewer/callspect/static/ viewer/callspect/static/deps.7z


# usage

# generate data
callspectpy -i collector/examples/async.py
# start `callspect` with data from `callspect.txt`
callspect callspect.txt
# open browser at http://127.0.0.1:5000/
```

## Viewer preview

![alt text](https://raw.githubusercontent.com/xliiv/callspect/master/callspect-demo.gif "Callspect viewer in action")



## TODO:
    * push packages to pypi & update installation in readme
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
