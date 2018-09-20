# Simple Fortran kernel for Jupyter 

**Matplotlib ready Fortran Kernel (intel/gnu)**  

Shamelessly hacked together from ... 
 * [jupyter-fortran-kernel](https://github.com/ZedThree/jupyter-fortran-kernel)
 * [jupyter-CAF-kernel](https://github.com/sourceryinstitute/jupyter-CAF-kernel)
 * [jupyter-c-kernel](https://github.com/brendan-rius/jupyter-c-kernel)
 * [idl_kernel](https://github.com/lstagner/idl_kernel)
 * [IPython Cookbook](https://ipython-books.github.io/16-creating-a-simple-kernel-for-jupyter/)

## Manual installation

 * Requirements: 
  * ifort or gfortran (or gcc)
  * jupyter 
  * python 3 with matplotlib/numpy
  * pip

### Step-by-step:
 * `pip install -e --user jupyter-ifort-kernel`
 * `cd jupyter-ifort-kernel`
 * `jupyter-kernelspec install ifort_spec`
 * `jupyter notebook` or `jupyter lab`

### Example notebook [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/f66blog/binder_test/master?filepath=examples%2Fexample.ipynb)
 * [example.ipynb](https://github.com/f66blog/jupyter-ifort-kernel/blob/master/example/example.ipynb)

It seems that GIF/BMP files aren't shown.??

## License

[MIT](LICENSE.txt)
