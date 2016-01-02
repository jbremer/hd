# Source: https://gist.github.com/jtriley/1108174
import os
import struct
import platform
import subprocess


def get_terminal_size():
    """Get width and height of the console.

    Works on Linux, OS X, Windows, Cygwin (windows)

    Source: http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    if current_os == 'Windows':
        size = _get_terminal_size_windows()
        if not size:
            # Needed for Window's Python in Cygwin's xterm!
            size = _get_terminal_size_tput()

        return size or (80, 25)

    if current_os in ('Linux', 'Darwin') or current_os.startswith('CYGWIN'):
        return _get_terminal_size_linux()

    # Default value.
    return 80, 25


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer

        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            left, top, right, bottom = struct.unpack("4h", csbi.raw[10:18])

            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    # Source: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_output(['tput', 'cols']))
        rows = int(subprocess.check_output(['tput', 'lines']))
        return cols, rows
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios

            value = fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
            return struct.unpack('hh', value)
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass

    if not cr and 'LINES' in os.environ and 'COLUMNS' in os.environ:
        cr = os.environ['LINES'], os.environ['COLUMNS']

    return int(cr[1]), int(cr[0])
