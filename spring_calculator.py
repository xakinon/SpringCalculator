import sys
import configparser
import pathlib
from PyQt5 import QtWidgets, QtCore
from mainwindow import Ui_MainWindow
from springCalculate import SpringCalculate
from model import Model, Delegate

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_start.clicked.connect(self.calicurate)
        self.ui.pushButton_count.clicked.connect(self.calicurateCount)
        self.springCalculate = SpringCalculate(self.app, self.ui)

        # iniファイル読み込み
        self.inifile = configparser.ConfigParser()
        self.inifile.read('setting.ini', encoding='utf8')

        # テーブルビュー設定
        self.model = {}
        keys = ['d', 'stepedConditions', 'g', 'force', 'result']
        tableViews = [self.ui.tableView_d, self.ui.tableView_conditions_steped, self.ui.tableView_g, self.ui.tableView_force, self.ui.tableView_result]
        for key, tableView in zip(keys, tableViews):
            self.model[key] = Model()
            self.model[key].addColumns( self.inifile.get(key, 'columns').split(',') )
            self.model[key].addItems( [ [ j for j in i.split(',') ] for i in self.inifile.get(key, 'datas').splitlines() ] )
            self.model[key].rows = self.inifile.get(key, 'rows').split(',')
            tableView.setModel( self.model[key] )
            tableView.setItemDelegate( Delegate() )
        
        # 結果テーブルビューはソートを有効
        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model['result'])
        self.proxyModel.sort(-1, QtCore.Qt.AscendingOrder)
        self.proxyModel.setFilterKeyColumn(1)
        self.ui.tableView_result.setModel(self.proxyModel)
        self.ui.tableView_result.setSortingEnabled(True)
        
    def conditions(self):
        def drange(begin, end, step):
            n = begin
            while round(n, 6) <= end:
                yield round(n, 6)
                n += step
        
        c = []
        c.append( [ float(cell) for item in self.model['d'].items for cell in item if not cell == '' ] )

        for item in self.model['stepedConditions'].items:
            if item[0] == item[1]:
                c.append( [float(item[0])] )
                continue
            c.append( drange(float(item[0]), float(item[1]), float(item[2])) )
        
        c.append( [ float(cell) for item in self.model['g'].items for cell in item if not cell == '' ] ) # 横弾性係数
        
        kensaku = []
        if self.ui.checkBox_no.isChecked():
            kensaku.append(0)
        if self.ui.checkBox_yes.isChecked():
            kensaku.append(1)
        c.append( kensaku )

        return c

    def calicurate(self):
        # 結果ファイルがあれば削除
        filename = 'SpringList.csv'
        if pathlib.Path(filename).exists():
            pathlib.Path(filename).unlink()
        self.springCalculate.conditions = self.conditions
        self.springCalculate.Flist  = [ float(cell) for item in self.model['force'].items for cell in item if not cell == '' ]
        self.ui.progressBar.setMaximum( self.springCalculate.calicurateCount() )
        self.springCalculate.calicurate(filename) # 実行
        self.ui.label.setText('finish')
        self.ui.progressBar.setValue(0)

        # 結果をテーブルに追加
        with open(filename, 'r') as f:
            txt = f.read().splitlines()
        self.model['result'].removeAllItems()
        self.model['result'].addItems( [ [ float(s.strip()) for s in line.split(',') ] for line in txt[1:] ] )

        self.ui.tabWidget.setCurrentIndex(1)

    def calicurateCount(self):
        self.springCalculate.conditions = self.conditions
        self.ui.label.setText( str(0) + '/' + str(self.springCalculate.calicurateCount()))
        
    def copyTableData(self, tableView):
        _str = ''
        # 最初の行を取得
        r = tableView.selectedIndexes()[0].row()
        # モデル取得
        model = tableView.selectedIndexes()[0].model()
        if type(model) is QtCore.QSortFilterProxyModel:
            model = model.sourceModel()
        # セルを文字列で結合
        for index in tableView.selectedIndexes():
            if not r == index.row():
                # 行が変わったら改行を追加
                _str = _str[:-1] + '\n'
                r = index.row()
            # タブつきでセルの値を文字列に追加
            _str = _str + str(model.data(index)) + '\t'
        # クリップボードに文字列をセット
        QtWidgets.QApplication.clipboard().setText(_str)

    def ctrlC(self):
        # ctrlCが押されたとき
        focusWidget = self.ui.centralwidget.focusWidget()
        if type(focusWidget) is QtWidgets.QTableView:
            # QTableViewにフォーカスしていればデータをコピー
            self.copyTableData(focusWidget)

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            # Ctrlキーが押されたら
            if e.key() == QtCore.Qt.Key_C:
                # cが押されたら
                self.ctrlC()
            if e.key() == QtCore.Qt.Key_V:
                # vが押されたら
                pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()