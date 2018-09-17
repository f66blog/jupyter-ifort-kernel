# Simple Fortran kernel for Jupyter  

Shamelessly hacked together from ... 
 * [jupyter-fortran-kernel](https://github.com/ZedThree/jupyter-fortran-kernel)
 * [jupyter-CAF-kernel](https://github.com/sourceryinstitute/jupyter-CAF-kernel)
 * [jupyter-c-kernel](https://github.com/brendan-rius/jupyter-c-kernel)
 * [idl_kernel](https://github.com/lstagner/idl_kernel)
 * [IPython Cookbook](https://ipython-books.github.io/16-creating-a-simple-kernel-for-jupyter/)

## Manual installation

 * Make sure you have the following requirements installed:
  * ifort or gfortran (or gcc)
  * jupyter 
  * python 3 with matplotlib/numpy
  * pip

### Step-by-step:
 * `pip install -e --user jupyter-ifort-kernel`
 * `cd jupyter-ifort-kernel`
 * `jupyter-kernelspec install ifort_spec`
 * `jupyter notebook
 

## License

[MIT](LICENSE.txt)
