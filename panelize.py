#!/usr/bin/python3

# this script is used to emulate instanciating the pcb_layout of a
#   function group - p.ex. when a power supply is to be reused.
# it appends to a "master" kicad_pcb another "child" kicad_pcb
# and modifies paths (list of timestamps identifying objects) and references
# according to a netlist


# reversal of the file_formats:
# unix timestamps... what would possibly go wrong if one were to add faster 1/s?
# .sch:
#  AR PATH= contains subsch_timestamp/part_timestamp + Ref
# .kicad_pcb:
# ($class $content)-hierarchy, opens with (kicad_pcb content)
# ignore classes: general, page, layers, setup
# merge classes appropriately: net, net_class
# append: module_s, segment, via,
#          ToDo: and probably others
# place at appropriate offset
#
# unclear: general...

import re
from s_parse import s_file_parse, namedlist
import os.path

def append(master,child, netlist, Dx, Dy, instance=0):

    ordering = ['version', 'host', 'general', 'page', 'layers', 'setup', 'net', 'net_class', 'module', 'segment', 'via']


    def move(item, subitem=None, newpos=None):
        '''moves item or the first subitem of item by Dx, Dy'''
        if subitem is not None:
            item = item(subitem)[0]
        try:
            x,y,z = item('xyz')[0]
        except IndexError:
            if newpos is None:
                item[0] += Dx
                item[1] += Dy
            else:
                item[0] = newpos[0] + Dx
                item[1] = newpos[1] + Dy
        else:
            item[item.indices('xyz')[0]] = namedlist('xyz', x+Dx, y+Dy, z)

    def get_ts(tree,name,identifier='tstamp'):
        '''for each vertex of name in tree, obtain identifier like tstamp
        this unpacks the 1-tuple that make up timestamps, which may be undesirable'''

        ts = [ i.get_unique(identifier)[0] for i in tree(name) ]
        ts.sort()
        return ts

    def get_comp_sheet_ts():
        pass

    def get_sheet_ts(sheet):
        pass

    def join_path(*p):
        ans = '{}'
        p = list(p)
        for i,v in enumerate(p):
            fl = v[0]+v[-1]
            if fl == '""':
                ans = '"{}"'
                p[i] = v[1:-1]
            elif '"' in fl:
                raise ValueError('%s with " at one end'%v)

        return ans.format(os.path.normpath('/'.join(p)))

    merged = master

    # check whether the child we got is in the netlist
    # kicad_pcb is considered corresponding to a netlist
    child_module_ts = [ i[1:] for i in get_ts(child,'module','path')]
    netlist_components = netlist.get_unique('components')
    candidates = []

    for sheet in netlist.get_unique('design')('sheet'):
        sheetpath = sheet.get_unique('name')
        components = namedlist('components',
            *[ i for i in netlist_components('comp') if
                i.get_unique('sheetpath').get_unique('names') == sheetpath ]
            )
        if get_ts(components,'comp') == child_module_ts:
            candidates.append((sheet,components))

    if not isinstance(instance,int):
        # get intent by path / name
        instance_index = [ i for i,(s,c) in enumerate(candidates) if s.get_unique('name') == instance ]

        # get intent by tstamp
        instance_index.extend( i for i,(s,c) in enumerate(candidates) if s.get_unique('tstamps')[1:-2] == instance )

        if len(instance_index !=  1):
            raise ValueError('Did not find exactly one candidate sheet')
        instance = instance_index[0]

    child_sheet, child_components = candidates[instance]
    child_netpath_prefix = child_sheet.get_unique('name')[0]
    child_modpath_prefix = child_sheet.get_unique('tstamps')[0]

    # merge nets
    # TODO: check wether this is necessary (adds nets)
    # This attempt is wrong - we need to prefix the child nets
    master_nets = [ name for i, name in master('net') ]
    child_nets = ( name for i, name in child('net') )

    for net in child_nets:
        if join_path(child_netpath_prefix, net) not in master_nets and net not in master_nets:
            # merged_nets.append(net)
            raise ValueError('Child net not in master net')

    # merged_nets = ( namedlist('net', i, net) for i, net in enumerate(merged_nets))
    # done merging nets


    def get_insertpos(tree,name):
        indices = tree.indices(name)
        try:
            return max(indices)
        except ValueError:
            return 1

    # move and add modules
    # TODO: rather move existing modules - they have correct net
    # identifying a childs module corresponding master module:
    #   the master's module has the child's path prepended by
    def obtain_from_child(master,child,name,onlythese=None):
        mis = master(name)
        cis = child(name)
        if len(mis) != len(cis):
            raise ValueError('master and child have unequal many vertices of name %s'%name)
        for mi,ci in zip(mis,cis):
            if onlythese is None:
                master[mi.parentpos] = ci
            else:
                for rescursion_name in onlythese:
                    if isinstance(rescursion_name,(str,int,float)):
                        obtain_from_child(mi, ci, rescursion_name)
                    else:
                        obtain_from_child(mi, ci, name, rescursion_name)

    insertpos = get_insertpos(master,'module')
    for i, module in enumerate(child('module')):

        # a module consists of the following:
        # [ !str(footprint), layer, tedit, tstamp, at, descr, tags, path, attr, fp_text..., fp_line..., pad..., model ]
        # of which should be taken from the child: layer, at, fp_line
        #   for fp_text layer and at from child
        cmodpath = module.get_unique('path')
        mmodpath = join_path(child_modpath_prefix, cmodpath[0])
        module[cmodpath.parentpos] = namedlist('path',(mmodpath,))
        mmod = [ i for i in master('module') if i.get_unique('path')[0] == mmodpath ]
        if len(mmod) != 1:
            raise ValueError('Child module not uniqe in master')
        else:
            mmod=mmod[0]

        obtain_from_child(mmod, module, 'at')
        obtain_from_child(mmod, module, 'layer')
        obtain_from_child(mmod, module, 'fp_line')
        obtain_from_child(mmod, module, 'fp_text',('layer','at'))

        move(mmod, 'at')
        # for p,point in enumerate(mmod('fp_text') + mmod('pad') + mmod('model')):
        #     move(point,'at')
        # for l,line in enumerate(mmod('fp_line')):
        #     move(line, 'start')
        #     move(line, 'end')

        merged[mmod.parentpos] = mmod
        #print('moved %i points and %i lines'%(p,l))
    print('moved %i modules'%i)
    # done adding modules
    # TODO: move modules already there
    # identifiable by path: /$sheetTstamp/$childModulePath


    # move and add segments
    insertpos = get_insertpos(master, 'segment')
    for i, segment in enumerate(child('segment')):
        move(segment, 'start')
        move(segment, 'end')
        merged.insert(insertpos+i,segment)
    # done adding segments


    # adding vias
    insertpos = get_insertpos(master,'via')
    for i,via in enumerate(child('via')):
        move(via,'at')
        merged.insert(insertpos+i, via)
    # done adding vias

    orderedmerged = namedlist(merged.name)
    for name in ordering:
        orderedmerged.extend(merged(name))

    #open('foobarfjauafpouvi')

    return orderedmerged


def s_writer(tree, fd, line_len=70):
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

if __name__ == '__main__':
    child = s_file_parse('test-rc/rc.kicad_pcb')
    master = s_file_parse('test-rc/2x rc.kicad_pcb')
    netlist = s_file_parse('test-rc/2x rc.net')
    merged = append(master, child, netlist, 10, 20)
    child = s_file_parse('test-rc/rc.kicad_pcb')
    merged = append(master, child, netlist, 30, 20,instance=1)
    s_writer(merged,'/tmp/merged.kicad_pcb')

