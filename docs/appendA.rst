.. _cli:

Appendix A: Running Code Samples
################################

Running the code samples in this documentation requires a rudimentary
knowledge of using command-line terminal (command prompt on Windows). The
terminal can seem very "texty" and confusing at first; however, with a little
practice it gets to be fairly intuitive and *efficient*. There are many
tutorials online. See `The Command Line Crash Course`_, for example.

A few basics are covered there, though, for reference. When you start a
terminal, you will be presented with a little window where you can type
commands. In this documentation, the terminal command prompt will be denoted
as ``home>$`` in this document. Where *home* is simply the current folder
where the commands will be executed, and *>$* is just a separator. These
things do not need to be typed when entering commands. 

A couple of useful command line options are "change directory" (``cd``) and
"present working directory" (``pwd``). The most important thing you'll want to
be able to do is move directories (i.e. folders). When you open the terminal,
you will usually start in your *home* directory. This will probably be
"/Users/username" on Mac, "/home/username" on Linux, or "C:\Users\username" on
windows. To move to a different directory, use the ``cd`` command: to find out
the location of the current folder use ``pwd``. Here's an example. 

.. code::

    home$> pwd
    /home/username/
    home$> cd folder1
    folder1$> pwd
    /home/username/folder1

The second command here moved active directory to the folder "folder1". There
are a few special directory shortcuts:

* ``~`` : This refers to the home directory.
* ``..`` :  (Double period) This refers to the base directory of the current
  directory.
* ``.`` : (Single period) This refers to the current directory.
* ``\`` or ``/`` : Separators to combine directory names. The first works on
  Linux/Mac, the second is required on Windows.

Here's these shortcuts in action.

.. code::

    home>$ cd folder1/folder2
    folder2>$ pwd
    /home/username/folder1/folder2
    folder2>$ cd .
    folder2>$ pwd
    /home/username/folder1/folder2
    folder2>$ cd ../..
    home>$ pwd
    /home/username
    home>$ cd folder1/folder2
    folder2>$ cd ~
    home>$ pwd
    /home/username
    home>$ cd folder1/folder2
    folder2>$ cd ~/folder3
    folder3>$ pwd
    /home/username/folder3

The other important command is going to be "list" (``ls`` or ``dir`` on
Windows). This lists the contents of the current directory.

.. code::

    folder3>$ ls
    file1 file2 folder4

.. _The Command Line Crash Course: http://cli.learncodethehardway.org/book/

