import nuke

from Qt import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Tracker to Roto")
        MainWindow.resize(446, 573)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Header = QtWidgets.QHBoxLayout()
        self.Header.setObjectName("Header")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.Header.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.Header.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.Header)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.trackerList = QtWidgets.QListWidget(self.centralwidget)

        ##Tracker list
        self.trackerList.setObjectName("trackerList")
        self.horizontalLayout_2.addWidget(self.trackerList)
        self.trackerList.itemSelectionChanged.connect(self.updateTrackPointList)
        self.addNodesOfClassToList('Tracker4', self.trackerList)

        ## Roto list
        self.rotoList = QtWidgets.QListWidget(self.centralwidget)
        self.rotoList.setObjectName("rotoList")
        self.addNodesOfClassToList('RotoPaint', self.rotoList)

        self.horizontalLayout_2.addWidget(self.rotoList)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)

        ##Tracking points list
        self.trackingPoints = QtWidgets.QListWidget(self.centralwidget)
        self.trackingPoints.setObjectName("trackingPoints")
        self.trackingPoints.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.horizontalLayout_3.addWidget(self.trackingPoints)
        spacerItem1 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        ## Connect pushButton
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.connectTrackers)

        self.verticalLayout_2.addWidget(self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 446, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.updateTrackPointList()

    def updateTrackPointList(self):
        self.trackingPoints.clear()
        trackerNodeName = self.trackerList.selectedItems()[0].text()
        trackerNode = nuke.toNode(trackerNodeName)
        trackingPointsNames = get_track_names(trackerNode)
        self.trackingPoints.addItems(trackingPointsNames)

    def addNodesOfClassToList(self, className, list):
        tracker = get_all_nodes_of_class(className)
        tracks_names = []
        for tracks in tracker:
            tracks_names.append(tracks.name())

        list.addItems(tracks_names)
        list.setCurrentItem(list.item(0))
        list.repaint()

    def connectTrackers(self):
        # print(self.trackerList.selectedItems[0].text())
        selectedTrackingPoints = self.trackingPoints.selectedItems()

        cleanTPList = []

        roto_list = self.rotoList.selectedItems()
        if roto_list:
            roto = nuke.toNode(roto_list[0].text())

        for track in selectedTrackingPoints:
            cleanTPList.append(track.text())

        for trackPoint in cleanTPList:
            print(trackPoint, roto)
            from ..tasks.roto import link_track_to_roto
        link_track_to_roto(cleanTPList,roto)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Tracker to Roto", "Tracker to Roto"))
        self.label_2.setText(_translate("MainWindow", "Trackers"))
        self.label.setText(_translate("MainWindow", "RotoNodes"))
        self.label_3.setText(_translate("MainWindow", "Select Tracking Points to Connect"))
        self.pushButton.setText(_translate("MainWindow", "Connect"))


def get_nuke_main_window():
    """Returns Nuke's main window"""

    app = QtWidgets.QApplication.instance()
    for obj in app.topLevelWidgets():
        if obj.inherits('QMainWindow') and obj.metaObject().className() == 'Foundry::UI::DockMainWindow':
            return obj
    else:
        raise RuntimeError('Could not find DockMainWindow instance')


def get_track_names(track):
    import re
    track_names = []
    track_script = track['tracks'].toScript()
    matchObj = re.findall(r'curve.*."', track_script, re.M | re.I)
    iter = 1

    for name in matchObj:
        cleanName = name.split('"')[1]
        track_names.append('[{}] {} {}'.format(track.name(),iter,  cleanName))
        iter +=1
    return track_names


def get_all_nodes_of_class(class_name):
    NodesOfClass = []

    for n in nuke.allNodes():
        print(n.Class())
        if n.Class() == class_name:
            print('match found')
            NodesOfClass.append(n)

    return NodesOfClass

def run_gui():
    app = get_nuke_main_window()
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

if __name__ == "__main__":
    import sys

    app = get_nuke_main_window()
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # sys.exit(app.exec_())

