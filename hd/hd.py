# Copyright (C) 2015 Jurriaan Bremer.

import struct


# ASCII Charset.
ASCII_CHARSET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
ASCII_CHARSET += '0123456789/\\ $@!^%*()_[]-`,.#~+{}|'
GREEN_CHARSET = '\r\n\t'

# Colors.
COLORS = 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

green = lambda s: color('green', s)
red = lambda s: color('red', s)
blue = lambda s: color('blue', s)


def color(clr, s):
    return '\x1b[%dm%s\x1b[0m' % (30 + COLORS.index(clr), s)


class PartialContent(Exception):
    def __init__(self, content):
        self.content = content


def _iter_file(f, offset, count):
    f.seek(offset)
    buf = f.read(count)
    if len(buf) != count:
        raise PartialContent(buf)
    return buf


def _iter_buf(f, offset, count):
    buf = f[offset:offset+count]
    if len(buf) != count:
        raise PartialContent(buf)
    return buf


def _determine_iter(obj):
    if isinstance(obj, file):
        return _iter_file

    if isinstance(obj, str):
        return _iter_buf


def hexdump(data, **kwargs):
    offset = int(kwargs.pop('offset', kwargs.pop('o', 0)))
    length = int(kwargs.pop('length', kwargs.pop('l', 0)))
    blocksize = int(kwargs.pop('blocksize', kwargs.pop('bs', 1)))
    count = int(kwargs.pop('count', kwargs.pop('c', 16)))
    endian = kwargs.pop('endian', kwargs.pop('e', 'le'))
    mode = kwargs.pop('mode', kwargs.pop('m', 'fancy'))

    types = {1: 'B', 2: 'H', 4: 'I'}
    endians = {'le': '<', 'be': '>', 'na': '='}

    more, it, offset, instar = True, _determine_iter(data), 0, False
    while more and (not length or offset < length):
        try:
            buf = it(data, offset, blocksize * count)
        except PartialContent as e:
            buf = e.content
            more = False
        except EOFError:
            break

        if not buf:
            break

        actual_count = len(buf) / blocksize
        fmt = endians[endian] + types[blocksize] * actual_count
        values = struct.unpack(fmt, buf)

        # Check whether the entire row contains nulls.
        if not buf.translate(None, '\x00'):
            if not instar:
                print '*'
            instar = True
            offset += blocksize * count
            continue

        instar = False

        h = []
        for value in values:
            if not value and mode != 'normal':
                h.append(' '*(2 * blocksize))
            elif blocksize != 1:
                h.append(('%%0%dx' % (2 * blocksize)) % value)
            elif mode == 'normal':
                h.append(('%%0%dx' % (2 * blocksize)) % value)
            elif chr(value) in ASCII_CHARSET or chr(value) in GREEN_CHARSET:
                h.append(green('%%0%dx' % (2 * blocksize)) % value)
            elif value >= 0x80:
                h.append(red('%%0%dx' % (2 * blocksize)) % value)
            else:
                h.append(blue('%%0%dx' % (2 * blocksize)) % value)

        h = ' '.join('%s' % x for x in h)

        if blocksize == 1:
            a = ''
            for ch in values:
                if not ch:
                    a += '.' if mode == 'normal' else ' '
                elif chr(ch) in ASCII_CHARSET:
                    a += green(chr(ch)) if mode != 'normal' else chr(ch)
                elif chr(ch) in GREEN_CHARSET and mode != 'normal':
                    a += green('.')
                else:
                    a += '.'

            padding = '   '*(count - actual_count)
            print '%04x: %s%s   %s' % (offset, h, padding, a)
        else:
            print '%04x: %s' % (offset, h)

        offset += blocksize * count
