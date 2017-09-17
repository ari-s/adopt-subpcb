#!/usr/bin/python3

# this script is used to emulate instanciating the pcb_layout of a
#   function group - p.ex. when a power supply is to be reused.
# it appends to a "master" kicad_pcb another "child" kicad_pcb
# and modifies paths (list of timestamps identifying objects) and references
# according to a netlist


# reversal of the file_formats:
# unix timestamps... what would possibly go wrong if one were to add faster 1/s?
# .kicad_pcb:
# ($class $content)-hierarchy, opens with (kicad_pcb content)
# ignore classes: general, page, layers, setup
# merge classes appropriately: net, net_class
# append: module_s, segment, via,
#          ToDo: and probably others

import re
from s_parse import s_file_parse, s_file_write, namedlist
import os.path
import copy

def adopt_subdesign(product, subdesign, netlist, Dx, Dy, instance=0):
    '''adopts the pcb artwork for subdesign into product.
    to do this for another instance of subdesign instead of the first, specify the instance:
    most conveniently by either by its position in the netlist,
    this facilate reuse of an existing design for some subcomponent of a pcb (power supply for instance) for the product.
    Effectively:
    - modules in the product are moved to their position in subdesign+(Dx,Dy)
        - module nets are taken from the product
    - segments
    - vias
    there are probably thigs missing, like drawn lines, texts, zones, keepouts...
    '''

    ordering = ['version', 'host', 'general', 'page', 'layers', 'setup', 'net', 'net_class', 'module', 'segment', 'via']

    # TODO: a proper refactoring master->product; child-> subdesign
    master = product
    child = subdesign

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

    # TODO: should be doable without deepcopy
    merged = master
    child = copy.deepcopy(child)

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
        instance_index = [ i for i,(s,c) in enumerate(candidates) if s.get_unique('name')[0][1:-1] == instance ]

        # get intent by tstamp
        instance_index.extend( i for i,(s,c) in enumerate(candidates) if s.get_unique('tstamps')[0][1:-1] == instance )

        if len(instance_index) !=  1:
            raise ValueError('Did not find exactly one candidate sheet')
        instance = instance_index[0]

    child_sheet, child_components = candidates[instance]
    child_netpath_prefix = child_sheet.get_unique('name')[0]
    child_modpath_prefix = child_sheet.get_unique('tstamps')[0]

    # merge nets
    master_nets = [ name for i, name in master('net') ]
    child_nets = ( name for i, name in child('net') )

    for net in child_nets:
        if join_path(child_netpath_prefix, net) not in master_nets and net not in master_nets:
            raise ValueError('Child net not in master net')
    # done merging nets


    def get_insertpos(tree,name):
        indices = tree.indices(name)
        try:
            return max(indices)
        except ValueError:
            return 1

    # move modules
    # identifying a childs module corresponding master module:
    #   the master's module has the child's path prepended by
    def obtain_from_child(master,child,name,onlythese=None):
        mis = master(name)
        cis = list(map(copy.deepcopy,child(name)))
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

    # a module consists of the following:
    # [ !str(footprint), layer, tedit, tstamp, at, descr, tags, path, attr, fp_text..., fp_line..., pad..., model ]
    # of which should be taken from the child: layer, at, fp_line
    #   for fp_text layer and at from child
    # identifiable by path: /$sheetTstamp/$childModulePath
    for i, cmod in enumerate(child('module')):
        cmodpath = cmod.get_unique('path')
        mmodpath = join_path(child_modpath_prefix, cmodpath[0])
        cmod[cmodpath.parentpos] = namedlist('path',(mmodpath,))
        mmod = [ i for i in master('module') if i.get_unique('path')[0] == mmodpath ]
        if len(mmod) != 1:
            raise ValueError('Child module not uniqe in master')
        else:
            mmod=mmod[0]

        obtain_from_child(mmod, cmod, 'at')
        obtain_from_child(mmod, cmod, 'layer')
        obtain_from_child(mmod, cmod, 'fp_line')
        obtain_from_child(mmod, cmod, 'fp_text',('layer','at'))
        move(mmod, 'at')
        merged[mmod.parentpos] = mmod
    # done adding modules


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
    return orderedmerged

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('product', type=argparse.FileType('r+'),help='Product to adopt subdesign into (kicad_pcb)')
    arg('subdesign', type=argparse.FileType('r'),help='Subdesign (kicad_pcb)')
    arg('netlist', type=argparse.FileType('r'),help='netlist for the product')
    arg('DxDy', type=float, help='move (first) Subdesign instance by (Dx,Dy)', nargs=2)
    arg('dx', type=float, default=None, help='x-spacing of subdesign instances (default Dx)',nargs='?')
    arg('dy', type=float, default=0, help='y-spacing of subdesign instances (default 0)',nargs='?')
    arg('--instance', type=str, default=None, help='specify the subdesign instance you want to adopt (sheetname, integer or list thereof)')
    arg('--out','-o', type=argparse.FileType('x'),help='write to this file instead of overwriting product', default=None)

    args = parser.parse_args()
    if args.dx is None:
        args.dx = args.DxDy[0]
    product = s_file_parse(args.product)
    subdesign = s_file_parse(args.subdesign)
    netlist = s_file_parse(args.netlist)
    if args.instance is not None:
        product = adopt_subdesign(product,subdesign,netlist,*args.DxDy,instance=args.instance)
    else:
        i=0
        while True:
            Dx = args.DxDy[0] + i*args.dx
            Dy = args.DxDy[1] + i*args.dy
            try:
                product = adopt_subdesign(product,subdesign,netlist,Dx,Dy,i)
            except IndexError:
                break
            else:
                i+=1

    if args.out is not None:
        args.product.close()
        args.product = args.out
    else:
        args.product.seek(0)

    s_file_write(product,args.product)



