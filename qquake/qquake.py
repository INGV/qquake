# -*- coding: utf-8 -*-
"""
QQuake plugin
"""

# .. note:: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

__author__ = 'Original authors: Mario Locati, Roberto Vallone, Matteo Ghetta, Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Istituto Nazionale di Geofisica e Vulcanologia (INGV)'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os.path

from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    QCoreApplication
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QMenu
)

from qgis.gui import (
    QgsOptionsWidgetFactory
)

from qquake.gui.gui_utils import GuiUtils
# Import the code for the dialog
from qquake.gui.qquake_dialog import QQuakeDialog
from qquake.gui.qquake_options_widget import QQuakeOptionsWidget


class QQuakeOptionsFactory(QgsOptionsWidgetFactory):
    """
    Factory class for SLYR options widget
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def icon(self):  # pylint: disable=missing-function-docstring
        return GuiUtils.get_icon('icon.svg')

    def createWidget(self, parent):  # pylint: disable=missing-function-docstring
        res = QQuakeOptionsWidget(parent)
        res.setObjectName('qquake_options')
        return res


class QQuake:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.dlg = None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QQuake_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = None

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.options_factory = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QQuake', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.menu = QMenu(self.tr('&QQuake'))
        self.iface.pluginMenu().addMenu(self.menu)

        show_dialog_action = QAction(self.tr('QQuake'))
        show_dialog_action.setIcon(GuiUtils.get_icon('icon.svg'))
        show_dialog_action.triggered.connect(self.show_dialog)
        self.iface.addToolBarIcon(show_dialog_action)
        self.menu.addAction(show_dialog_action)
        self.actions.append(show_dialog_action)

        show_options_action = QAction(self.tr('Options…'))
        show_options_action.setIcon(GuiUtils.get_icon('options.svg'))
        show_options_action.triggered.connect(self.show_options)
        self.menu.addAction(show_options_action)
        self.actions.append(show_options_action)

        # will be set False in run()
        self.first_start = True

        self.options_factory = QQuakeOptionsFactory()
        self.options_factory.setTitle(self.tr('QQuake'))
        self.iface.registerOptionsWidgetFactory(self.options_factory)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            action.deleteLater()
        self.actions = []

        if self.menu is not None:
            self.menu.deleteLater()
            self.menu = None

        if self.options_factory:
            self.iface.unregisterOptionsWidgetFactory(self.options_factory)

    def show_dialog(self):
        """
        Shows the QQuake dialog
        """
        self.dlg = QQuakeDialog(self.iface)
        # dlg.setAttribute(Qt.WA_DeleteOnClose)

        # show the dialog
        self.dlg.show()

    def show_options(self):
        """
        Shows the plugin options
        """
        self.iface.showOptionsDialog(self.iface.mainWindow(), currentPage='qquake_options')
