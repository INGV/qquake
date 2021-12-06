# -*- coding: utf-8 -*-
"""
Simple node based model
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

from typing import Optional

from qgis.PyQt.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    Qt
)
from qgis.PyQt.QtGui import QFont


class ModelNode:
    """
    Represents a node in the model
    """

    def __init__(self, data, checked=None, user_data=None):
        self._data = data
        self._column_count = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0
        self._checked = checked
        self._user_data = user_data

    def data(self, column: int):
        """
        Returns the data for a specific column
        """
        if 0 <= column < len(self._data):
            return self._data[column]
        return None

    def setData(self, column: int, value) -> bool:
        """
        Sets the data for a column
        """
        if 0 <= column < len(self._data):
            self._data[column] = value
            return True
        return False

    def user_data(self):
        """
        Returns the user data for the node
        """
        return self._user_data

    def columnCount(self) -> int:
        """
        Returns the node's column count
        """
        return self._column_count

    def childCount(self) -> int:
        """
        Returns the node's child count
        """
        return len(self._children)

    def checkable(self) -> bool:
        """
        Returns True if the node is checkable
        """
        return self._checked is not None

    def checked(self) -> bool:
        """
        Returns True if the node is checked
        """
        return self._checked

    def setChecked(self, checked: bool):
        """
        Sets whether the node is checked
        """
        self._checked = checked

    def child(self, row: int) -> Optional['ModelNode']:
        """
        Returns the child node at the specified row
        """
        if 0 <= row < self.childCount():
            return self._children[row]

        return None

    def parent(self) -> Optional['ModelNode']:
        """
        Returns the node's parent
        """
        return self._parent

    def row(self) -> int:
        """
        Returns the node's row number
        """
        return self._row

    def show_bold(self) -> bool:
        """
        Returns True if the node should appear bold
        """
        return bool(self._children)

    def addChild(self, child: 'ModelNode'):
        """
        Adds a child node to this node
        """
        child._parent = self  # pylint: disable=protected-access
        child._row = len(self._children)  # pylint: disable=protected-access
        self._children.append(child)
        self._column_count = max(child.columnCount(), self._column_count)


class SimpleNodeModel(QAbstractItemModel):
    """
    A qt model for showing simple hierarchy of nodes
    """

    def __init__(self, nodes, headers=None):
        super().__init__()
        self._root = ModelNode([None])
        for node in nodes:
            self._root.addChild(node)
        self.headers = headers or []

    def rowCount(self, index):  # pylint: disable=missing-function-docstring
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node: ModelNode, _parent: Optional[QModelIndex]):
        """
        Adds a child node to the model
        """
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):  # pylint: disable=missing-function-docstring
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not super().hasIndex(row, column, _parent):
            return QModelIndex()

        child = parent.child(row)
        if child:
            return super().createIndex(row, column, child)

        return QModelIndex()

    def parent(self, index):  # pylint: disable=missing-function-docstring
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return super().createIndex(p.row(), 0, p)
        return QModelIndex()

    def columnCount(self, index):  # pylint: disable=missing-function-docstring
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):  # pylint: disable=missing-function-docstring,too-many-return-statements
        if not index.isValid():
            return None
        node = index.internalPointer()

        if node.checkable() and index.column() == 0:
            if role == Qt.CheckStateRole:
                return Qt.Checked if node.checked() else Qt.Unchecked
            return None

        if role == Qt.DisplayRole:
            return node.data(index.column())
        if role == Qt.UserRole:
            return node.user_data()
        if role == Qt.FontRole and node.show_bold():
            f = QFont()
            f.setBold(True)
            return f
        return None

    def setData(self, index, value, role):  # pylint: disable=missing-function-docstring,unused-argument
        if not index.isValid():
            return None
        node = index.internalPointer()

        if node.checkable() and index.column() == 0:
            node.setChecked(value)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        if index.column() == 1:
            if node.setData(index.column(), value):
                self.dataChanged.emit(index, index, [Qt.DisplayRole])
                return True
            return False

        return False

    def flags(self, index):  # pylint: disable=missing-function-docstring
        f = super().flags(index)

        node = index.internalPointer()
        if node.checkable() and index.column() == 0:
            f = f | Qt.ItemIsUserCheckable
        return f

    def headerData(self, section, orientation, role):  # pylint: disable=missing-function-docstring
        if self.headers and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)
