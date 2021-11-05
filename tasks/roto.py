import nuke
import re


def track_to_roto():
    from ..ui.trackerToRoto import run_gui
    run_gui()



def set_transform_curve_expression(curves, expression, layer):
    import _curvelib as cl
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


def get_layer_names(roto_node):
    """
    returns the names of the layers from a RotoPaint node
    """

    curves = roto_node['curves']
    root = curves.rootLayer
    layers_name = []
    for shape in root:
        baseLayer = shape
        layers_name.append(shape.name)

    return layers_name


def link_track_to_roto(trackingPoints, rotoNode):
    """

    :param trackingPoints:
    :type trackingPoints:list formated ['[TrackName] track 1','[TrackName] track 2']]
    :param rotoNode:
    :type rotoNode:
    """

    roto_layers = get_layer_names(rotoNode)
    trackerSelection = re.findall('\[(.*?)\]', trackingPoints[0])  # Expression to get name of the the node

    tracker = nuke.toNode(trackerSelection[0])  # selects first tracker in list

    for point in trackingPoints:
        index = point.split(' ')[1]
        expression = '{}.tracks.{}.track_x'.format(tracker.name(), str(int(index)))

        layerName = point

        if not layerName in roto_layers:
            print(layerName + '   missing')
            print(type(layerName))
            add_layer(rotoNode, str(layerName))
        set_transform_curve_expression(rotoNode['curves'], expression, layerName)