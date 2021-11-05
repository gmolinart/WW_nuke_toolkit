import nuke
import nuke.rotopaint as rp
import _curvelib as cl



############ TRACKING UTILITIES FOR NUKE #############


def get_knobs(node):
    """"
    :param node:the
    :type node:
    """
    for i in range(node.getNumKnobs()):
        print(node.knob(i).name())


def set_transform_curve_expression(curves, expression, layer):
    ##get aniamtion curves

    folder = curves.toElement(layer)

    transform = folder.getTransform()
    translation_curve_x = cl.AnimCurve()
    translation_curve_y = cl.AnimCurve()
    rotation_curve = cl.AnimCurve()
    scale_curve = cl.AnimCurve()

    translation_curve_x.expressionString = expression
    translation_curve_y.expressionString = expression.replace('track_x', 'track_y')

    for curve in [translation_curve_x, translation_curve_y, rotation_curve, scale_curve]:
        curve.useExpression = True

    transform.setTranslationAnimCurve(0, translation_curve_x)
    transform.setTranslationAnimCurve(1, translation_curve_y)
    transform.setPivotPointAnimCurve(1, cl.AnimCurve())
    transform.setPivotPointAnimCurve(0, cl.AnimCurve())


def add_layer(roto_node, name):
    """
    to use exclusily with roto selectedNodes
    :param roto_node:
    :type roto_node:
    :param name:
    :type name:
    """


    if roto_node.Class() == "RotoPaint":

        root = roto_node['curves'].rootLayer
        new_layer = root.clone()
        new_layer.name = name
        root.append(new_layer)


def remove_layer(roto_node, name):
    """
    Given a roto node it removes the given layer
    :param roto_node:
    :type roto_node:
    :param name:
    :type name:
    """
    if roto_node.Class() == "RotoPaint":

        root = roto_node['curves'].rootLayer
        for idx, shape in enumerate(root):
            print(idx, shape)

            if shape.name == name:
                root.remove(idx)
    else:
        nuke.message("please select a rotoPaint node")

def get_layer_names(root):
    layers_name = []
    for shape in root:
        baseLayer = shape

        layers_name.append(shape.name)

    return layers_name


############ get selection
selection = nuke.selectedNodes()
for i in selection:
    if i.Class() == 'Tracker4':
        tracker = i

    else:
        print(i.Class())
        # == 'RotoPaint' or i.Class == 'Roto':
        roto_node = i

    ###################mainVariables

tracks = tracker.knobs()['selected_tracks'].getValue().split(',')

curves = roto_node['curves']
root = curves.rootLayer

xtrans = root.getTransform()

layers_name = get_layer_names(root)

### Go trough tracks and add missing layers

for trackp in tracks:
    expression = '{}.tracks.{}.track_x'.format(tracker.name(), str(int(trackp) + 1))
    layer_name = 'track_' + str(int(trackp) + 1)

    if not layer_name in layers_name:
        print(trackp + '   missing')
        add_layer(roto_node, layer_name)

    set_transform_expression(curves, expression, layer_name)

# add_layer(roto,'guillermo_2')

# for shape in root:
#    print(shape.name)






