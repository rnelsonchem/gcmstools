import shutil
import subprocess as sub

pdf = '_build/latex/gcmstools.pdf'

try:
    sub.call(['make', 'latexpdf'])
except:
    print("There was an error in latexpdf generation.")
else:
    shutil.copy(pdf, '..')

    sub.call(['make', 'clean'])
