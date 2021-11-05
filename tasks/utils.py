import os
import logging
from cgl.plugins.Qt import QtWidgets
import time
import nuke
from cgl.core.utils.general import cgl_execute, write_to_cgl_data
from cgl.core.path import PathObject, Sequence, CreateProductionData, lj_list_dir
from cgl.core.config.config import user_config


PROCESSING_METHOD = user_config()['methodology']
X_SPACE = 120
Y_SPACE = 120


''''___________________NODES ______________________'''


def set_default_settings():
    from cgl.plugins.nuke.tasks import plate as plate_task
    from cgl.plugins.nuke.alchemy import scene_object
    plate = plate_task.Task()
    proxy_res = scene_object().project_info['proxy_resolution']
    readNode = nuke.toNode('plate_Read')
    resolution = scene_object().project_info['high_resolution']
    root = nuke.root()
    startFrame = float(plate.start_frame)
    lastFrame = float(plate.end_frame)

    proxy_width, proxy_height = proxy_res.split('x')


    for f in nuke.formats():

        if f.name() == 'DEFAULT_PROXY':
            f.setWidth(int(proxy_width))
            f.setHeight(int(proxy_width))

    DEFAULT_PROXY = '%s PROXY' % proxy_res.replace('x', ' ')
    FULL = '%s FULL' % scene_object().project_info['high_resolution'].replace('x', ' ')

    nuke.addFormat(DEFAULT_PROXY)
    nuke.addFormat(FULL)

    root['proxy_type'].setValue('format')
    root['proxy_format'].setValue('PROXY')
    root['proxySetting'].setValue('if nearest')

    nuke.root()['format'].setValue('FULL')
    nuke.frame(startFrame)
    nuke.alert("Comp Size, duration and proxy set")

    working_colorspace = scene_object().project_info['working_colorspace']
    nuke.activeViewer().node().knob('viewerProcess').setValue(str(working_colorspace))


def switch_proxy(value = True):
    import nuke

    root = nuke.root()
    root.setProxy(value)




def set_write_version(object = None, version= None):
    import os
    import nuke
    from .alchemy import scene_object
    if object == None:
        object = get_selection()

    if not version:
        version = scene_object().version

    path_object = get_path_object_from_node(get_selection())
    print(path_object.path)

    filePath = path_object.copy(version=version)
    proxy = path_object.copy(version=version,resolution = path_object.project_info['proxy_resolution'])
    object['file'].setValue(filePath.path_root)
    object['proxy'].setValue(proxy.path_root)


def set_proxy_path(object= None, make_dirs= True):
    import os
    import nuke

    if object == None:
        object = get_selection()
    path_object = get_path_object_from_node(get_selection())
    print(path_object.path)

    proxyPath = path_object.copy(resolution=path_object.project_info['proxy_resolution'])

    object['proxy'].setValue(proxyPath.path_root)
    if make_dirs:

        dirname = proxyPath.copy(filename ='').path_root
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            os.makedirs(dirname.replace('render', 'source'))

def keep_tagged_nodes(tag='task', value='key'):
    key_nodes = get_tagged_nodes(tag, value)
    from .alchemy import scene_object
    if key_nodes:

        for i in key_nodes:
            i.selectNodes()
            i.setSelected(True)
            nuke.invertSelection()


        for i in nuke.selectedNodes():
            nuke.delete(i)
        return True

    else:
        nuke.alert('ERROR, please move nodes into {} backdrop'.format(value))
        name = scene_object().task
        if not scene_object().variant == 'default':
            name = scene_object().variant

        backdrop_node = backdrop(name, bg_color=get_default_color())
        tag_object(tag, scene_object().task, object=backdrop_node)
        return False


def get_default_color(task= None):
    from .alchemy import get_task_class,scene_object
    if not task:
        path_object = scene_object()
        task = path_object.task

    task_class = get_task_class(task)
    color = task_class().defaut_color


    return color



def rgb_to_nuke_color(color=(.267, .267, .267)):

    bg_r, bg_g, bg_b = color
    bg_color_int = int('%02x%02x%02x%02x' % (bg_r * 255, bg_g * 255, bg_b * 255, 255), 16)
    return bg_color_int


def change_node_color(node,color= (0.255,0.255,0.255)):
    nuke_color = rgb_to_nuke_color(color)
    node.knob('tile_color').setValue(nuke_color)


def tag_object(tag, value, object=None ):
    if object == None:
        object = nuke.selectedNode()

    object.addKnob(nuke.Text_Knob(tag, tag, value))
    print(object.name(),'tagged')

def get_tagged_nodes(tag,value):

    valid_nodes = []

    for node in nuke.allNodes():
        if node.knob(tag):
            if node.knob(tag).value() == value:
                valid_nodes.append(node)


    return valid_nodes



def get_path_object_from_node(object = None):
    import nuke
    from .alchemy import scene_object
    """
    returns a list of pathObject items for the selected write nodes.
    :return:
    """

    if object == None:
        objects = nuke.selectedNode()

    if check_type(object,'Write') or check_type(object,'Read'):
        path = object['file'].value()
        padding = scene_object().project_info['padding']
        reformatted_path = path.replace('%0{}d'.format(padding),int(padding) * '#')
        path_object = PathObject(reformatted_path)


    return path_object

def export_to_file(node,file):
    nuke.nodeCopy(to_file)

def duplicate_node(node, to_file = None):
    """
    duplicates current selectd nodes
    :param node: 
    :param to_file: file to duplicate to useful to export 
    :return: 
    """
    
    
    if not node: 
        node = get_selection(all=True)       

    if not to_file:
        to_file = "%clipboard%"
    
    nuke.nodeCopy(to_file)
    new_node = nuke.nodePaste(to_file)



    return new_node


def check_type(node, type ):
    return node.Class() == type


def get_node(name):
    nodes = nuke.allNodes()
    for n in nodes:
        if name in n['name'].value():
            return n
    return None

def find_node(name):
    nodes = nuke.allNodes()
    for n in nodes:
        if name in n['name'].value():
            return n
    return None


def normpath(filepath):
    return filepath.replace('\\', '/')



def find_nodes(node_class, top_node=nuke.root()):
    if top_node.Class() == node_class:
        yield top_node
    elif isinstance(top_node, nuke.Group):
        for child in top_node.nodes():
            for found_node in find_nodes(node_class, child):
                yield found_node



def version_up_selected_write_node():
    """
    Versions Up the Output path in the selected Write Node
    :return:
    """
    if nuke.selectedNodes():
        s = nuke.selectedNodes()[0]
        if s.Class() == 'Write':
            path = s['file'].value()
            path_object = NukePathObject(path)
            next_minor = path_object.new_minor_version_object()
            print('Setting File to %s' % next_minor.path_root)
            s.knob('file').fromUserText(next_minor.path_root)

def create_merge(nodes=None, operation='over'):
    a = nuke.createNode('Merge2')
    if not nodes:
        nodes = nuke.selectedNodes()
    if nodes:
        x = 0
        for n in nodes:
            a.setInput(x, n)
            x += 1
        a['operation'].setValue(operation)
    nuke.autoplace(a)
    return a

def set_selection(name, cl= True ):
    if cl:
        nuke.selectAll()
        nuke.invertSelection()
    for node in nuke.allNodes():
        if node.knob('name').value() == name:
            node['selected'].setValue(True)
            return(node)
        
def get_selection(all=False):
    """
    Returns the currently selected node , 
    :param all: returns array of selected ndoes
    :return: 
    :return: 
    """
    selection = None
    import nuke
    if all: 
        return nuke.selectedNodes()

    try:
        selection = nuke.selectedNode()
    except ValueError:
        return None

    return  selection


def select_node(name, cl= True ):
    """
    To be replaced by set_selection
    :param name: 
    :param cl: 
    :return: 
    """
    if cl:
        nuke.selectAll()
        nuke.invertSelection()
    for node in nuke.allNodes():
        if node.knob('name').value() == name:
            node['selected'].setValue(True)
            return(node)

def select(nodes=None, d=True):
    """
    to be replaced by get_selection
    :param nodes: 
    :param d: 
    :return: 
    """
    if d:
        nuke.selectAll()
        nuke.invertSelection()
    if nodes:
        nuke.selectAll()
        nuke.invertSelection()
        [x['selected'].setValue(True) for x in nodes]


def check_write_node_version(selected=True):
    from .alchemy import scene_object

    scene_object = scene_object()
    if selected:
        for s in nuke.selectedNodes():
            if s.Class() == 'Write':
                if 'elem' not in s.name():
                    path = s['file'].value()
                    path_object = NukePathObject(path)
                    if scene_object.version != path_object.version:
                        print('scene %s, render %s, versions do not match' % (scene_object.version,
                                                                              path_object.version))
                        return False
                    else:
                        return True


def write_node_selected():
    """
    if write node is selected returns it.
    :return:
    """
    write_nodes = []
    for s in nuke.selectedNodes():
        if s.Class() == 'Write':
            write_nodes.append(s)
        else:
            return False
    return write_nodes


def replace_in_path(input_script=None, find_pattern=None, replace_pattern=None, output_script=None, type_='Write'):
    """

    :param input_script:
    :param output_script:
    :param type_: This can be "Write" or "Read" for this current implementation as designed
    :param find_pattern:
    :return:
    """
    if input_script:
        nuke.scriptOpen(input_script)
    nodes_ = [w for w in find_nodes(type_)]
    for n in nodes_:
        path = n['file'].value()
        print(n.name(), path)
        path = path.replace(find_pattern, replace_pattern)
        n['file'].setValue(path)
    nuke.scriptSave(output_script)


def get_write_paths_as_path_objects():
    """
    returns a list of pathObject items for the selected write nodes.
    :return:
    """
    write_objects = []
    if nuke.selectedNodes():
        for s in nuke.selectedNodes():
            if s.Class() == 'Write':
                if 'elem' not in s.name():
                    path = s['file'].value()
                    path_object = NukePathObject(path)
                    write_objects.append(path_object)
    return write_objects


def match_scene_version():
    """
    ajdusts version number on the main write node, or all write nodes to version
    :param main: if true this only effects the version number of the main write node
    :param version: the version to set write node(s) at.
    :return:
    """
    from .alchemy import scene_object
    padding = '#'*int(scene_object().project_info['padding'])
    path_object = scene_object()
    for n in nuke.allNodes('Write'):
        write_output = PathObject(n['file'].value())
        if write_output.version == path_object.version:
            print('Write Node version %s matches scene version' % write_output.version)
        else:
            print(n.name())
            if not 'elem' in n.name():
                print('Changing Write Version %s to %s' % (write_output.version, path_object.version))
                write_output.set_attr(version=path_object.version)
                n.knob('file').fromUserText(write_output.path_root)
    nuke.scriptSave()


def get_children(node):
    children = []
    for i in nuke.allNodes():
        for dep in i.dependencies():
            if dep.name() == node.name():
                children.append(i)
    return children







''''_______________ARRANGEMENT___________'''




def arrange_children(node, offset=100):
    children = get_children(node)
    distance = 50
    initial_offset = 50
    node_x = node.xpos()
    node_y = node.ypos()

    children[0].setXpos(node_x)
    children[0].setYpos(node_y + distance)
    for i in children[1:]:
        i.setXpos(node_x + offset)
        i.setYpos(node_y + distance)
        offset += offset


def parent(object,parent, input= 0,offset=200):
    posX = parent.xpos()
    posY = parent.ypos()
    object.setInput(input,parent)
    object.setXpos(posX)
    object.setYpos(posY+offset)
    print(posX,posY)

def auto_backdrop(label=None):
    import nukescripts
    n = nukescripts.autoBackdrop()
    if label:
        n['label'].setValue(label)


def auto_place(nodes=False):
    if not nodes:
        nodes = nuke.selectedNodes()
    for n in nodes:
        nuke.autoplace(n)


def backdrop(name, bg_color=(.267, .267, .267), text_color=(.498, .498, .498), nodes=None, move=(0, 0),
             move_offset=(0, 0),label = None):

    z_index = get_highest_z_index()+1
    bg_r, bg_g, bg_b = bg_color
    t_r, t_g, t_b = text_color

    # Define Colors. The numbers have to be integers, so there's some math to convert them.
    bg_color_int = rgb_to_nuke_color(bg_color)
    text_color_int = rgb_to_nuke_color(text_color)

    if nodes is None:
        nodes = nuke.selectedNodes()
        # move_nodes(plus_x=move[0], plus_y=move[1], start_x=move_offset[0], start_y=move_offset[1])

    if len(nodes) == 0:
        nodes =[nuke.createNode("Dot")]



    # Calculate bounds for the backdrop node.
    bd_x = min([node.xpos() for node in nodes])
    bd_y = min([node.ypos() for node in nodes])
    bd_w = max([node.xpos() + node.screenWidth() for node in nodes]) - bd_x
    bd_h = max([node.ypos() + node.screenHeight() for node in nodes]) - bd_y

    # Expand the bounds to leave a little border.
    # Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-70, -140, 70, 70)
    bd_x += left
    bd_y += top
    bd_w += (right - left)
    bd_h += (bottom - top)

    # Set backdrop parameters
    if label ==None:
        label = name
    n = nuke.nodes.BackdropNode(xpos=bd_x,
                                bdwidth=bd_w,
                                ypos=bd_y,
                                bdheight=bd_h,
                                z_order=int(z_index),
                                tile_color=bg_color_int,
                                note_font_color=text_color_int,
                                note_font_size=100,
                                label=label,
                                name=name,
                                note_font='Courrier New')

    # Revert to previous selection
    for node in nodes:
        node['selected'].setValue(True)

    # Ensure backdrop is selected, to make moving easier
    select(d=True)
    n['selected'].setValue(True)
    all_ = nodes+[n]
    select(all_)
    if move_offset != (0, 0):
        move_nodes(plus_x=move[0], plus_y=move[1], start_x=move_offset[0], start_y=move_offset[1])
        select(d=True)
        move_nodes(plus_x=X_SPACE, nodes=[n])
    else:
        move_nodes(plus_x=move[0], plus_y=move[1], start_x=move_offset[0], start_y=move_offset[1])
        select(d=True)
    nuke.show(n)

    return n

def move_nodes(plus_x=0, plus_y=0, start_x=0, start_y=0, nodes=None, padding=True):


    if start_x:
        x_multiplier = X_SPACE
        if padding:
            x_padding = x_multiplier*3
    else:
        x_multiplier = 0
        x_padding = 0
    if start_y:
        y_multiplier = Y_SPACE
        if padding:
            y_padding = y_multiplier*2.25
    else:
        y_multiplier = 0
        y_padding = 0
    if not nodes:
        nodes = nuke.selectedNodes()
    for i, n in enumerate(nodes):
        print(n['name'].value())
        if not start_x:
            start_x2 = n['xpos'].value()
        else:
            start_x2 = start_x
        if not start_y:
            start_y2 = n['ypos'].value()
        else:
            start_y2 = start_y
        new_x = (int(start_x2 + (x_multiplier*(i+1)) + x_padding + plus_x))
        new_y = (int(start_y2 - (y_multiplier*(i+1)) - y_padding - plus_y))
        print('moving x:%s to %s' % (n['xpos'].value(), new_x))
        print('moving y:%s to %s' % (n['ypos'].value(), new_y))
        n.setXpos(new_x)
        if start_y or plus_y:
            n.setYpos(new_y)


def biggest_x(nodes=None):
    if not nodes:
        nodes = nuke.allNodes()
    x_val = 0
    for n in nodes:
        if x_val == 0:
            x_val = n['xpos'].value()
        elif x_val < n['xpos'].value():
            x_val = n['xpos'].value()
    return x_val


def biggest_y(nodes=None):

    if not nodes:
        nodes = nuke.allNodes()
    y_val = 0
    for n in nodes:
        if y_val == 0:
            y_val = n['ypos'].value()
        elif y_val > n['ypos'].value():
            y_val = n['ypos'].value()
    return y_val

def get_frame_range():

    return str(nuke.root().frameRange()).split('-')

def get_min_max(node=None):
    if not node:
        node = nuke.selectedNodes()[0]
    min_color = nuke.nodes.MinColor(target=0, inputs=[node])
    inv = nuke.nodes.Invert(inputs=[node])
    max_color = nuke.nodes.MinColor(target=0, inputs=[inv])

    cur_frame = nuke.frame()
    nuke.execute(min_color, cur_frame, cur_frame)
    min_ = -min_color['pixeldelta'].value()

    nuke.execute(max_color, cur_frame, cur_frame)
    max_ = max_color['pixeldelta'].value() + 1

    for n in (min_color, max_color, inv):
        nuke.delete(n)
    return min_, max_


def setup_z_node(z_node):
    """
    This assumes we're using arnold AOVs when setting up this z network
    :param node:
    :return:
    """
    nodes = []
    z_object = PathObject(z_node['file'].value())
    beauty = find_node('beauty')
    min, max = get_min_max(z_node)
    mult_node = nuke.createNode('Multiply')
    mult_node['value'].setValue(1 / max)
    mult_node['name'].setValue('%s Z Preview' % z_object.render_pass[0:3])
    nodes.append(mult_node)

    select([z_node])
    sc = nuke.createNode('ShuffleCopy')
    sc['in2'].setValue('depth')
    sc['out'].setValue('depth')
    sc['red'].setValue('red')
    if beauty:
        sc.setInput(0, beauty)
    sc.setInput(1, z_node)
    nodes.append(sc)
    layer_name = z_object.render_pass.replace('_LAYER', '')
    z_defocus = nuke.createNode('ZDefocus2')
    z_defocus['name'].setValue('%s ZDefocus' % layer_name)
    z_defocus['z_channel'].setValue('depth.Z')
    z_defocus['math'].setValue('depth')
    z_defocus['output'].setValue('focal_plane_setup')
    z_defocus['size'].setValue(20)
    z_defocus['max_size'].setExpression('size')
    nodes.append(z_defocus)
    select()
    mult_node.setInput(0, z_node)

    return nodes



def connect_z_nodes(connect_from_node='ANIM ZDefocus', connect_to_node='ENV ZDefocus'):
    """
    this is a convenience method for connecting z depth nodes from different render layers to each other on an
    animation import for depth of field purposes.
    :param connect_from_node:
    :param connect_to_node:
    :return:
    """
    to_node = find_node(connect_to_node)
    from_node = find_node(connect_from_node)
    if to_node and from_node:
        # Need to step up my game on this - and connect it as a link.
        to_node['center'].setExpression(str(from_node['center'].value()))
        to_node['output'].setValue('result')


def get_biggest_read_padding():
    biggest_padding = 0
    for n in nuke.allNodes('Read'):
        temp = os.path.splitext(n['file'].value())[0]
        if '%' in temp:
            padding = int(temp.split('%')[1].replace('d', ''))
        else:
            padding = 0
        if padding > biggest_padding:
            biggest_padding = padding
    return biggest_padding


def check_write_padding():
    """
    Checks all read nodes in the scene to find the largest num padding.  then checks all write nodes to ensure they
    comply.
    :return:
    """
    edited_nodes = []
    scene_padding = get_biggest_read_padding()
    for n in nuke.allNodes('Write'):
        temp, ext = os.path.splitext(n['file'].value())
        base_file = temp.split('%')[0]
        padding = int(temp.split('%')[1].replace('d', ''))
        if padding < scene_padding:
            if scene_padding < 10:
                numformat = '%0'+str(scene_padding)+'d'
            elif scene_padding < 100 and scene_padding > 9:
                numformat = '%'+str(scene_padding)+'d'
            new_file_name = '%s%s%s' % (base_file, numformat, ext)
            edited_nodes.append(new_file_name)
            n.knob('file').fromUserText(new_file_name)
    return edited_nodes


def select(nodes=None, d=True):
    if d:
        nuke.selectAll()
        nuke.invertSelection()
    if nodes:
        nuke.selectAll()
        nuke.invertSelection()
        [x['selected'].setValue(True) for x in nodes]


def get_highest_z_index():
    z_index = -10
    bd_nodes = nuke.allNodes('BackdropNode')
    for node in bd_nodes:
        print(node['label'].value())
        if node['z_order'].value() > z_index:
            z_index = node['z_order'].value()
    return int(z_index)


def auto_place(nodes=False):
    if not nodes:
        nodes = nuke.selectedNodes()
    for n in nodes:
        nuke.autoplace(n)


def move_nodes(plus_x=0, plus_y=0, start_x=0, start_y=0, nodes=None, padding=True):
    if start_x:
        x_multiplier = X_SPACE
        if padding:
            x_padding = x_multiplier*3
    else:
        x_multiplier = 0
        x_padding = 0
    if start_y:
        y_multiplier = Y_SPACE
        if padding:
            y_padding = y_multiplier*2.25
    else:
        y_multiplier = 0
        y_padding = 0
    if not nodes:
        nodes = nuke.selectedNodes()
    for i, n in enumerate(nodes):
        print(n['name'].value())
        if not start_x:
            start_x2 = n['xpos'].value()
        else:
            start_x2 = start_x
        if not start_y:
            start_y2 = n['ypos'].value()
        else:
            start_y2 = start_y
        new_x = (int(start_x2 + (x_multiplier*(i+1)) + x_padding + plus_x))
        new_y = (int(start_y2 - (y_multiplier*(i+1)) - y_padding - plus_y))
        print('moving x:%s to %s' % (n['xpos'].value(), new_x))
        print('moving y:%s to %s' % (n['ypos'].value(), new_y))
        n.setXpos(new_x)
        if start_y or plus_y:
            n.setYpos(new_y)


def biggest_x(nodes=None):
    if not nodes:
        nodes = nuke.allNodes()
    x_val = 0
    for n in nodes:
        if x_val == 0:
            x_val = n['xpos'].value()
        elif x_val < n['xpos'].value():
            x_val = n['xpos'].value()
    return x_val


def biggest_y(nodes=None):

    if not nodes:
        nodes = nuke.allNodes()
    y_val = 0
    for n in nodes:
        if y_val == 0:
            y_val = n['ypos'].value()
        elif y_val > n['ypos'].value():
            y_val = n['ypos'].value()
    return y_val



