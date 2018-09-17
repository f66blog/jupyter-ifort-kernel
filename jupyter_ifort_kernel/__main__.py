from ipykernel.kernelapp import IPKernelApp
from .kernel import ifortKernel
IPKernelApp.launch_instance(kernel_class=ifortKernel)
