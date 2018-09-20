from queue import Queue
from threading import Thread

from ipykernel.kernelbase import Kernel
import subprocess
import tempfile
import os
import os.path as path
from shlex import split as shsplit
from shutil import copyfile


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    def __init__(self, cmd, write_to_stdout, write_to_stderr):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr

        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            self._write_to_stdout(stdout_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents)


class ifortKernel(Kernel):
    implementation = 'jupyter_ifort_kernel'
    implementation_version = '0.1'
    language = 'Fortran'
    language_version = 'F2008'
    language_info = {'name': 'fortran',
                     'mimetype': 'text/plain',
                     'file_extension': 'f90'}
    banner = "ifort kernel.\n" \
             "Uses intel fortran, compiles in F2008, and creates source code files and executables in temporary folder.\n"

    def __init__(self, *args, **kwargs):
        super(ifortKernel, self).__init__(*args, **kwargs)
        self.files = []
  #      mastertemp = tempfile.mkstemp(suffix='.out')
  #      os.close(mastertemp[0])
  #      self.master_path = mastertemp[1]
        self.master_path = os.getcwd() + '/temp'
        if os.path.isdir(self.master_path):
            pass
        else:
            os.mkdir(self.master_path)


    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        for file in self.files:
            os.remove(file)
        if os.path.isdir(self.master_path):
            os.rmdir(self.master_path)


    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file


    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': contents})


    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': contents})


    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd,
                                  lambda contents: self._write_to_stdout(contents.decode()),
                                  lambda contents: self._write_to_stderr(contents.decode()))


    def compile_with_fortran(self, compiler, source_filename, binary_filename, fcflags=None, ldflags=None):
#        if '-c' in ldflags:                                                                   #windows ifort
#            text = [compiler, source_filename] + fcflags + ['-nologo'] + ldflags              #windows ifort
#        else:                                                                                 #windows ifort
#            src, _ = os.path.splitext(source_filename)                                        #windows ifort
#            text = [compiler, source_filename] + fcflags + ['-o', src, '-nologo'] + ldflags   #windows ifort
        
        text = [compiler, source_filename] + fcflags + ['-o', binary_filename] + ldflags      # Linux/WSL
        return self.create_jupyter_subprocess(text)                                        

    
    def _filter_magics(self, code):

        magics = {'fcflags': [],
                  'ldflags': [],
                  'module': [],
                  'args': [],
                  'compiler': ['gfortran-8', '.f90'],
                  'fig': False,
                  'fig_arg': [],
                  'image': [],
                 }
        
        for line in code.splitlines():
            if line.strip().startswith('%'):
                key, value = line.strip().strip('%').split(":", 1)
                key = key.lower()
             
                if key in ['ldflags', 'fcflags', 'args']:
                    magics[key] = shsplit(value)
                elif key in ['module']:  
                    magics[key] = shsplit(value)
                    magics['ldflags'].append('-c')
                elif key in ['compiler']:
                    for i, item in enumerate(shsplit(value)):
                        magics[key][i] = item
                elif key in ['fig']:  
                    magics[key] = True
                    magics['fig_arg'] = value
                elif key in ['image']:  
                    magics[key] = shsplit(value)
                else:
                    pass # need to add exception handling
        return magics
             
              
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
                     
        magics = self._filter_magics(code) 
             
        if magics['fig']:
            try: 
                from matplotlib import use
                use('Agg')
                import matplotlib.pyplot as plt
                import numpy as np
                from base64 import b64encode
                from io import BytesIO
            
                _fig = eval('plt.figure(' + magics['fig_arg'] + ')') 
                for line in code.splitlines():
                    if line.startswith(('%', '%%', '$', '?')):
                        continue
                    elif line.strip().startswith(('_fig')):
                        _, rhs = line.strip().strip('%').split("=", 1)
                        _fig = eval(rhs)
                    else:
                        exec(line)
                _imgdata = BytesIO()
                _fig.savefig(_imgdata, format='png')
                _imgdata.seek(0)
                _data = {'image/png': b64encode(_imgdata.getvalue()).decode('ascii')}
                self.send_response(self.iopub_socket, 'display_data', {'data':_data, 'metadata':{}})
            except Exception as e:
                self._write_to_stderr("[ifort kernel]{}".format(e))
            finally:
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                    'user_expressions': {}}

        elif magics['image'] != []:
            from base64 import b64encode
                          
            for file_name in magics['image']: 
                if path.exists(file_name):
                    _, ext = os.path.splitext(file_name)
                    ext = ext[1:]
                    if ext == 'jpg': # MIME type
                        ext = 'jpeg'
                    image_type = 'image/' + ext
                    image = open(file_name, 'rb').read() 
                    data = {image_type: b64encode(image).decode('ascii')}
                    self.send_response(self.iopub_socket, 'display_data',{'data':data,'metadata':{}})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                    'user_expressions': {}}
        else:
            tmpdir = self.master_path
            with self.new_temp_file(suffix=magics['compiler'][1], dir=tmpdir) as source_file:
                for line in code.splitlines():
                    if line.startswith(('%', '%%', '$', '?')):
                         continue
                    source_file.write(line + '\n')
                source_file.flush()
#                with self.new_temp_file(suffix='.obj', dir=tmpdir) as binary_file:          # windows ifort
#                    p = self.compile_with_fortran(magics['compiler'][0], source_file.name,  # windows ifort  
#                        binary_file.name, magics['fcflags'], magics['ldflags'])             # windows ifort
                
                with self.new_temp_file(suffix='.out', dir=tmpdir) as binary_file:           # Linux/WSL
                    p = self.compile_with_fortran(magics['compiler'][0], source_file.name,   # Linux/WSL 
                        binary_file.name, magics['fcflags'], magics['ldflags'])              # Linux/WSL

                    while p.poll() is None:
                        p.write_contents()
                    p.write_contents()
                    if p.returncode != 0:  # Compilation failed
                        self._write_to_stdout(
                            "[ifort kernel] fortran exited with code {}, the executable will not be executed".format(
                                    p.returncode))
                        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                             'user_expressions': {}}
            if magics['module'] != []:
                tmp = magics['module']
#                mod_name = tmp[0] + ".obj"                         # windows ifort
#                src, _ = os.path.splitext(source_file.name)        # windows ifort
#                copyfile(src[-11:] + '.obj', mod_name)      # windows ifort
#                os.remove(src[-11:] + '.obj')                      # windows ifort
                mod_name = tmp[0] + ".o"                           # Linux/WSL
                copyfile(binary_file.name, mod_name)               # Linux/WSL
                self._write_to_stderr("[ifort kernel] module objects created successfully: {}".format(mod_name))
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
                
#            src, _ = os.path.splitext(source_file.name)            # windows ifort
#            exe_file = src + '.exe'                                # windows ifort
#            p = self.create_jupyter_subprocess(exe_file)           # windows ifort
#            os.remove(src[-11:] + '.obj')                          # windows ifort
            p = self.create_jupyter_subprocess(binary_file.name)   # Linux/WSL
            while p.poll() is None:
                p.write_contents()
            p.write_contents()
            
#            os.remove(exe_file)                                    # windows ifort               
         
        if p.returncode != 0:
            self._write_to_stderr("[ifort kernel] Executable exited with code {}".format(p.returncode))
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
          
    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()
