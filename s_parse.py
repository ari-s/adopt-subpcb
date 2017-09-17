#!/usr/bin/python3

from collections import defaultdict, namedtuple, OrderedDict

class namedlist(list):
    '''list with a name'''
    def __init__(self, name, *content, parentpos=None):
        self.name = str(name)
        list.__init__(self, content)

    def __str__(self):
        a = self.name + ': [ '
        for i in self:
            if isinstance(i, namedlist):
                a += '\n%s'%i.__str__().replace('\n','\n ')
            else:
                a += '%s, '%i.__str__()
        return a+']'

    def __call__(self, childtype):
        a = []
        for i,v in enumerate(self):
            if isinstance(v,namedlist) and childtype == v.name:
                a.append(v)
                v.parentpos = i

        return a

    def indices(self, name):
        ans = []
        for i,v in enumerate(self):
            if isinstance(v,namedlist) and v.name == name:
                ans.append(i)
        return ans

    def get_unique(self, name):
        items = self(name)
        if len(items) != 1:
            raise ValueError('name not unique')
        return items[0]


def get_scalar(cfactory,c):
    '''get the next scalar value - call only when at the start of a scalar!'''
    scalar = c
    for c in cfactory:
        if c in ' )\n':
            break
        scalar+=c
    try: scalar = int(scalar)
    except ValueError:
        try: scalar = float(scalar)
        except ValueError: pass
    return scalar, c

def get_str(cfactory):
    '''get the string (chars up to next ") - call only when at start of such a string'''
    result = ''
    for c in cfactory:
        if c != '"':
            result += c
        else:
            break
    else:
        raise ValueError('no closing " found')
    return result

def s_parser(cfactory):
    '''parse an s_expression out of iterable that outputs single characters and advances open(fn).read(1)'''

    name, c = get_scalar(cfactory, '')
    tree = namedlist(name)
    if c == ')':
        return tree

    for c in cfactory:
        if c == ')':
            return tree
        elif c == '(':
            tree.append( s_parser(cfactory) )
        elif c == '"':
            tree.append( '"%s"'%get_str(cfactory) )
        elif c in ' \n':
            continue
        else:
            item, c = get_scalar(cfactory, c)
            tree.append(item)
            if c == ')':
                return tree

    return tree

def s_file_parse(fn, fn_tag='filename'):
    '''parse an s_expression file. You want to use this one

    this is minimally more than a parser: it also inserts the filename into the tree
    at the filename tag (modifable). In order not to modify data loaded from the
    file, this raises a valueError if fn_tag is already in the data'''

    if isinstance(fn,str):
        fn = open(fn)
    if 'b' in fn.mode:
        fn = open(fn.name)

    cfactory = iter(lambda: fn.read(1),'')
    if next(cfactory) != '(':
        raise ValueError('not an s_expression')

    s_file = s_parser(cfactory)
    try:
        s_file.filename
    except AttributeError:
        s_file.filename = fn.name
    else:
        raise ValueError('attempting to overwrite tag %s when inserting filename' % fn_tag)

    return(s_file)

def s_file_write(tree, fd, line_len=70):
    '''write an s_expression file. Note that
    outfd = open('/tmp/foobar','w')
    s_file_write(s_file_parse(fn),fd)
    at least destroys formatting of fn. Also, Dragons.'''

    # TODO: fix top-level vertex order
    current_linepos=0
    def write_item(item, current_linepos):
        fd.write('(%s '%item.name)
        current_linepos += len(item.name)
        for i in item:
            if isinstance(i, namedlist):
                current_linepos = write_item(i, current_linepos)
            else:
                fd.write('%s '%i)
                current_linepos += len(str(i))
        fd.write(')')
        if current_linepos > line_len:
            fd.write('\n')
            current_linepos = 0
        return current_linepos

    if isinstance(fd,str):
        import os.path
        if os.path.exists(fd):
            raise ValueError('fd is a path that exists, not overwriting')
        fd = open(fd,'w')

    write_item(tree, 0)
    fd.flush()
