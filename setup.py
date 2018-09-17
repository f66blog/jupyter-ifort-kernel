from setuptools import setup

setup(name='jupyter_ifort_kernel',
      version='0.1.0',
      description='Minimalistic Fortran kernel for Jupyter with plotting features',
      author='f66blog',
      author_email='fortran667790@gmail.com',
      url='https://github.com/f66blog/jupyter-ifort-kernel/',
      download_url='https://github.com/ZedThree/jupyter-fortran-kernel/tarball/0.1.0',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Framework :: IPython',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Fortran',
      ],
      packages=['jupyter_ifort_kernel'],
      keywords=['jupyter', 'kernel', 'fortran']
)
