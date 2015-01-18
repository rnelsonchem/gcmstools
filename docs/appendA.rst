.. _cli:

Appendix A: Running Code Samples
################################

Using the Command Line
----------------------

Running the code samples in this documentation requires a rudimentary
knowledge of the command-line terminal (command prompt on Windows). The
terminal can seem very "texty" and confusing at first; however, with a little
practice it gets to be fairly intuitive and *efficient*. There are many
tutorials online, for example, `The Command Line Crash Course`_. However, A
few basic command line concepts are covered here, for reference.

When you start a terminal, you will be presented with a window to type
commands. In this documentation, the terminal command prompt will be denoted
as ``home>$``, where "home" indicates the current folder where the commands
will be executed and ">$" is just a separator. These things do not need to be
typed when entering commands. A similar format is common in a lot of online
documentation.  Some commands generate output. The output will occur after the
command prompt, but will not be preceded by a command prompt symbol.

The most important thing you'll want to be able to do is move to different
directories (i.e. folders). To do this there are a couple of useful terminal
commands: "change directory" (``cd``) and "present working directory"
(``pwd``).  When you open the terminal, you will usually start in your "home"
directory. This will probably be "/Users/username" on Mac, "/home/username" on
Linux, or "C:\\Users\\username" on Windows. To move to a different directory,
use the ``cd`` command; to find out the location of the current folder, use
``pwd``.  Here's an example. 

.. code::

    home$> pwd
    /home/username/

    home$> cd folder1

    folder1$> pwd
    /home/username/folder1

The second command here moved active directory to the folder *folder1*. There
are also a few special directory shortcuts:

* ``~`` This refers to the home directory.
* ``..`` (Double dot) This refers to the parent directory of the current
  directory.
* ``.`` (Single dot) This refers to the current directory.
* ``\`` or ``/`` Separators to combine directory names. The first works on
  Linux/Mac (and in IPython, see below), the second is required on Windows.

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

The other important command is ``ls``, which lists the contents of the current
directory. (In Windows, the equivalent command is ``dir``.)

.. code::

    folder3>$ ls
    file1 file2 folder4

.. _The Command Line Crash Course: http://cli.learncodethehardway.org/book/

.. _ipython:

IPython
-------

Start IPython
+++++++++++++

One of Python's strengths as a data analysis language is its interactive
interpreter. This mode is accessed from a terminal by typing ``python``. 

.. code::

    home>$ python
    Python 3.4.1 (default, Oct 10 2014, 15:29:52)
    [GCC 4.7.3] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Any command that is typed at the ``>>>`` prompt is treated as Python code, and
executed appropriately. That means you can interactively write and explore
code in this manner.

.. code::

    >>> 2 + 2
    4
    >>> print('Hello World')
    Hello World

The default Python interpreter is very limited, which is why IPython was
developed. IPython is an advanced Python interpreter, which has several
advanced features like autocompletion and introspection, just to name two.
Over the years, this project has grown substantially, and in addition to a
terminal based interpreter, there is now a GUI version and a very cool
web-based Notebook as well. To learn more about the other features, consult
the `IPython documentation`_.

IPython is started from the terminal using the ``ipython`` command::

    home>$ ipython
    Python 3.4.1 (default, Oct 10 2014, 15:29:52)
    Type "copyright", "credits" or "license" for more information.
    
    IPython 2.3.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.
    
    In [1]: 2 + 2
    Out[1]: 4

    In [2]: print('Hello World')
    Hello World

The ``In [#]:`` prompt now takes the place of ``>>>`` in the regular Python
interpreter. In addition, certain types of output are preceded by an
``Out[#]:`` prompt. The numbers in brackets help you to determine the order
that commands are processed. For this documentation, though, the numbers will
be stripped for clarity, e.g. ``In :`` and ``Out:``. If you see these prompts,
you should know that the commands are being run in an IPython session.

.. _ipytab:

Autocompletion and Introscpection
+++++++++++++++++++++++++++++++++

The take home message of this section is *use the Tab key a lot!* It will make
you much more productive.

Two very nice aspect of the IPython interpreter are autocompletion and object
introspection. Both of these will make use of the Tab key on your keyboard; in
code snippets, this key will be denoted as ``<tab>``, which means you should
press the Tab key rather than typing it out. To see these two operations in
action, we can first create a new string object.

.. code::

    In : my_string = 'Hello World'

    In : print(my_string)
    Hello World

To determine the methods available to a string object, we can use IPython's
object introspection.

.. code::

    In : my_string.<tab>
    my_string.capitalize    my_string.isidentifier  my_string.rindex
    my_string.casefold      my_string.islower       my_string.rjust
    my_string.center        my_string.isnumeric     my_string.rpartition
    my_string.count         my_string.isprintable   my_string.rsplit
    my_string.encode        my_string.isspace       my_string.rstrip
    my_string.endswith      my_string.istitle       my_string.split
    my_string.expandtabs    my_string.isupper       my_string.splitlines
    my_string.find          my_string.join          my_string.startswith
    my_string.format        my_string.ljust         my_string.strip
    my_string.format_map    my_string.lower         my_string.swapcase
    my_string.index         my_string.lstrip        my_string.title
    my_string.isalnum       my_string.maketrans     my_string.translate
    my_string.isalpha       my_string.partition     my_string.upper
    my_string.isdecimal     my_string.replace       my_string.zfill
    my_string.isdigit       my_string.rfind   

As you can see, there are many, many things that you can do with this string
object. IPython can also use the Tab key to autocomplete long names for
variables, path strings, etc. Here's an example::

    In : my_string.is<tab>
    my_string.isalnum       my_string.isidentifier  my_string.isspace
    my_string.isalpha       my_string.islower       my_string.istitle  
    my_string.isdecimal     my_string.isnumeric     my_string.isupper      
    my_string.isdigit       my_string.isprintable   

    In : my_string.isi<tab>

Notice that when you type tab here IPython automatically expands this to
``my_string.isidentifier``. This works for path strings as well.

.. note::
    
    It should be pointed out that tab completion also works on the regular
    command line terminal interface as well.

Magic Commands
++++++++++++++

IPython has a number of special commands that make its interpreter behave much
like a command-line terminal. These commands, called Magic Commands, are
preceded by ``%`` or ``%%``. The `magic command documentation`_ covers many of
them, but a few that are useful to the examples in this document are discussed
here.

The magics ``%cd``, ``%pwd``, and ``%ls`` serve the exact same purpose as in
the terminal. Another very useful magic is ``%run``. This command executes a
Python program file from inside the IPython session, and in addition to
executing the code, it also loads the data and variables into the current
IPython session. This is best explained by example. Create a new folder called
``folder1`` in your home directory. Create the file ``test.py`` in ``folder1``
and paste the following code into that file. (See :ref:`textfiles` for some
information on text files and Python programs.)

.. code:: python

    var1 = 7
    var2 = "Hello World"
    var3 = var1*var2

Now let's start up IPython and run this new program.

.. code::

    home>$ ipython
    Python 3.4.1 (default, Oct 10 2014, 15:29:52)
    Type "copyright", "credits" or "license" for more information.
    
    IPython 2.3.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.
    
    In : %pwd
    /home/username

    In : %cd folder1
    /home/username/folder1

    In : %ls
    test.py

    In : %run test.py

    In :

At this point, it seems like nothing has happened; however, the variable that
we defined in our file "test.py" are now contained in our IPython session.
Assuming that the following IPython code is the same session as above.

.. code::

    In : var1
    Out: 7
   
    In : var3
    Out: Hello WorldHello WorldHello WorldHello WorldHello WorldHello
    WorldHello WorldHello World

As you can see, this is a very powerful way to save your work for later or to
run code that is fairly repetitive. 

.. _IPython documentation: http://ipython.org/documentation.html
.. _magic command documentation: http://ipython.org/ipython-doc/
    dev/interactive/tutorial.html  

Notebook Interface
++++++++++++++++++

Todo.


.. _textfiles:

Working with Text Files
-----------------------

There are many instances where you will need to work with plain text files,
including when writing Python programs. Plain text files are *not* word
processing documents (e.g. MS Word), so you will want to use a dedicated text
editor. Another source of problems for beginners is that leading white space in
Python programs is important. For these reasons, a dedicated Python text
editor can be very useful for beginners. Anaconda is bundled with `Spyder`_,
which has a builtin text editor. The Anaconda FAQ has `information on running
Spyder`_ on your system. Spyder is actually a full development environment, so
it can be very intimidating for beginners. Don't worry! The far left panel is
the text editor, and you can use that without knowing what any of the other
panels are doing. Some internet searches will reveal other text editors if
you'd prefer something smaller. (Do *not* use MS Notepad.)

The ".py" suffix for Python programs can be important.  On Windows, however,
file extensions are not shown by default, which makes them difficult to
modify. In these cases, you may inadvertently create a file with the extension
".py.txt", which will not behave as you expect. Consult the internet for ways
to show file extensions on a Windows machine. 

.. _Spyder: https://code.google.com/p/spyderlib/
.. _information on running Spyder: http://
    docs.continuum.io/anaconda/faq.html#open-packages
