#!/usr/bin/env python2

# See: http://support.godaddy.com/groups/web-hosting/forum/topic/rsync-over-ssh-on-a-linux-host/

import os
import subprocess as sub
from zipfile import ZipFile, ZIP_DEFLATED

CWD = os.getcwd()

# Make a zip file of the sample data
if os.path.exists('../sampledata.zip'):
    os.remove('../sampledata.zip')
os.chdir('../sampledata')
print('Creating Zip Archive')
with ZipFile('../sampledata.zip', mode='a', compression=ZIP_DEFLATED) as zipf:
    for root, dirnames, fnames in os.walk('.'):
        for fname in fnames:
            if fname == 'data.h5' or fname.endswith('pdf'):
                continue
            dir_file = os.path.join(root, fname)
            print(dir_file)
            zipf.write(dir_file)
os.chdir(CWD)

# Create a remote directory for connecting to GoDaddy
local_dir = '_build/html/'
remote_dir = '_build/_remote/'
os.mkdir(remote_dir)

# Create HTML files
sub.call(['make', 'html'])

try:
    # Create an ssh filesystem
    sub.call(['sshfs', 'gcmstools:html/gcmstools', remote_dir])
except:
    print("Couldn't connect to GoDaddy.")
else:
    # Sync the files. Use size only because of time mismatch between my computer
    # and hosting server
    #sub.call(['rsync', '-rzv', '--size-only', local_dir, remote_dir])
    sub.call(['rsync', '-rzv', local_dir, remote_dir])
    
    # Force the index file to update.
    sub.call(['scp', local_dir+'index.html', remote_dir])

# Close the scp connection
sub.call(['fusermount', '-u', remote_dir])
# Clean up the html directory
sub.call(['make', 'clean'])

