# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.items = []
        self.columns = []
        self.rows = []
        
    def addColumns(self, texts):
        self.beginInsertColumns(QtCore.QModelIndex(), len(self.columns), len(self.columns) + len(texts) - 1)
        self.columns.extend(texts)
        self.endInsertColumns()
        
    def addItems(self, texts):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.items), len(self.items) + len(texts) - 1)
        self.items.extend(texts)
        self.endInsertRows()
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.EditRole:
            return self.items[index.row()][index.column()]
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()][index.column()]
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    def headerData(self, i, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if int (i) >= len(self.columns):
                return ''
            else:
                return self.columns[i]
        
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if len(self.rows) > 1:
                return self.rows[i]
            return i
        
    def index(self, row, column, parent):
        return self.createIndex(row, column, QtCore.QModelIndex())
        
    def parent(self, index):
        return QtCore.QModelIndex()
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)
        
    def removeAllItems(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self.items) - 1)
        self.items = []
        self.endRemoveRows()
        
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.items[index.row()][index.column()] = value
            return True
        return False
        
class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(Delegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())