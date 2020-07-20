# -*- coding: UTF-8 -*-

u'''
@author: guoliang@nfschina.com
'''

from __future__ import absolute_import
import sys
import os
import fc
import glsu
import time
import pandas

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QApplication, QSplitter, QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, 
    QSpinBox, QScrollArea, QFileDialog, QMessageBox, QAction, QComboBox, QDialog, QLabel, QListView, QCheckBox)
from PyQt5.QtCore import Qt, QTranslator, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QPalette, QPen, QBrush, QFontMetrics, QIcon

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

#added by guoliang 20191127
class DlgWaiting(QThread):
    def __init__(self, parent=None):
        super(DlgWaiting, self).__init__(parent)

    def __del__(self):
        self.wait()

    def set_params(self, fm, files):
        self.fm = fm
        self.files = files

    def run(self):
        self.fm.res, self.fm.cmd = fc.installFonts(self.files)
        fm.dlg_wait.close()

#added by hanxf 20191128
class DlgWaiting_c(QThread):
    def __init__(self, parent=None):
        super(DlgWaiting_c, self).__init__(parent)

    def __del__(self):
        self.wait()

    def set_params(self, fm, files):
        self.fm = fm
        self.files = files

    def run(self):
        self.fm.res, self.fm.cmd = fc.installFontFiles(self.files)
        fm.dlg_wait.close()

class DlgWaiting_u(QThread):
    def __init__(self, parent=None):
        super(DlgWaiting_u, self).__init__(parent)

    def __del__(self):
        self.wait()

    def set_params(self, fm, files):
        self.fm = fm
        self.files = files

    def run(self):
        self.fm.res, self.fm.cmd = fc.uninstallFonts(self.files)
        fm.dlg_wait.close()

class LoadFclist(QThread):
    trigger = pyqtSignal(pandas.DataFrame)
    def __init__(self, parent=None):
        super(LoadFclist, self).__init__(parent)

    def run(self):
        self.fclist = fc.listFc()
        self.trigger.emit(self.fclist)

class FontDisplayer(QWidget):
    def __init__(self, parent=None):
        super(FontDisplayer, self).__init__(parent)
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.pen = QPen(Qt.black)
        self.brush = QBrush(Qt.white)
        self.fontSize = 14
        self.fontVerticalSpace = 5
        self.fonts = []
        self.text = u""
       # self.setMinimumSize(3000, 3000)
        self.widths = 0
        self.heights = 0
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(qp)
        qp.end()
    
    def drawText(self, qp):      
        heights = 0
        widths = 0
        
        for index in xrange(len(self.fonts)):
            infoFont = self.fonts[index]
            font = QFont()
            font.setFamily(infoFont[0])
            if infoFont[1] != u'font without family':
                font.setStyleName(infoFont[1])
            font.setPointSize(self.fontSize)
            if qp is not None: qp.setFont(font)
            
            fullname = infoFont[2] if infoFont[2] != u'font without fullname' else infoFont[0]
            unicode = fullname + u': ' + self.text
                                     
            fm = QFontMetrics(font)            
            height = fm.height()
            width = fm.width(unicode)
            heights += (height + self.fontVerticalSpace)
            widths = width if width > widths else width            
            
            if qp is not None: qp.drawText(10, heights + 0, unicode)
        
        self.widths = widths
        self.heights = heights
        
    
        
    def updateFonts(self, text, fonts):
        self.fonts = fonts
        self.text = text
        self.update()
        
        self.recalc_region()
        
    def updateFontSize(self, fontSize):
        self.fontSize = fontSize
        self.update()
        self.recalc_region()
        
    def recalc_region(self):
        self.drawText(None) #only calc 
        if self.widths + 10 > self.parent().width():
            self.widths = 3000 if self.widths<3000 else self.widths + 10
        if self.heights + 10 > self.parent().height():
            self.heights = 3000 if self.heights < 3000 else self.heights + 10
        self.setMinimumSize(self.widths, self.heights)
        
class FontManager(QWidget):
    def __init__(self, parent=None):
        super(FontManager, self).__init__(parent, flags=Qt.Window)

        #item being selected
        self.app = QApplication.instance()
        self.translator = None
        self.qt_translator = None
        self.checked = []
        self.itemFonts = []
        self.wheres = [self.tr(u'All Fonts'), self.tr(u'System Fonts'), self.tr(u'User Fonts')]
        self.where = 0
        self.languages = [self.tr(u'zh_CN'), self.tr(u'English')]
        self.lang = 0
        self.in_retranslating = False
        self.setupUI()
        self.translate(self.lang)
        self.searchText = []
        self.loop = 0
        self.items =0
        self.checkbox_val = 0
        
    def setupUI(self):
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(22,12,22,12)
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle{border-image: url(icons/split_line.png)}")
        splitter.setHandleWidth(17)

        hbox.addWidget(splitter)
        
        left=QWidget(splitter)
        vbox = QVBoxLayout(left) 
        vbox.setSpacing(0)
        vbox.setContentsMargins(0,0,0,4)        

        buttonsContainer1 = QWidget()
        vbox.addWidget(buttonsContainer1)        
        hbox2 = QHBoxLayout(buttonsContainer1)
        hbox2.setContentsMargins(2,3,2,10)
        
        comboWhere = QComboBox()
        comboWhere.setStyleSheet("QComboBox {width:160px;min-width:20px;height:28px;border:1px solid #c7c7c7;font-size:14px;selection-background-color:#f4f4f4;}"
                                 "QComboBox QAbstractItemView {background:#ffffff;color:#333333;}"
                                 "QComboBox::drop-down{width: 21px;border-left: 0px solid #333333;}"
                                 "QComboBox::down-arrow:hover {image: url(icons/ComboBox_hover.png);}"
                                 "QComboBox::down-arrow {image: url(icons/ComboBox_default.png);}")
        comboWhere.currentIndexChanged.connect(self.handleComboWhereIndexChanged)
        hbox2.addWidget(comboWhere)
        self.comboWhere = comboWhere
        
        comboLang = QComboBox()
        comboLang.setStyleSheet("QComboBox {width:160px;min-width:20px;height:28px;border:1px solid #c7c7c7;font-size:14px;selection-background-color:#f4f4f4;}"
                                "QComboBox QAbstractItemView {background:#ffffff;color:#333333;}"
                                "QComboBox::drop-down{width: 21px;border-left: 0px solid #333333;}"
                                "QComboBox::down-arrow:hover {image: url(icons/ComboBox_hover.png);}"
                                "QComboBox::down-arrow {image: url(icons/ComboBox_default.png);}")
        comboLang.currentIndexChanged.connect(self.handleComboLanguageIndexChanged)
        hbox2.addWidget(comboLang)
        self.comboLang = comboLang
        
        #addStretch
        hbox2.addStretch()

        btnInstallFont = QPushButton()
        btnInstallFont.setEnabled(True)
        btnInstallFont.clicked.connect(self.installFonts)
        btnInstallFont.setStyleSheet("QPushButton{border-image: url(icons/install_default.png) 0 0 0 0;border:none;color:rgb(255, 255, 255);font-size:14px;}"
                                     "QPushButton:hover{border-image: url(icons/install_hover.png) 0 0 0 0;border:none;color:rgb(255, 255, 255);}"
                                     "QPushButton:checked{border-image: url(icons/install_click.png) 0 0 0 0;border:none;color:rgb(255, 255, 255);}")
        btnInstallFont.setFixedSize(100,30)
        hbox2.addWidget(btnInstallFont)
        self.btnInstallFont =  btnInstallFont
        
        btnUninstallFont = QPushButton()
        btnUninstallFont.setEnabled(False)
        btnUninstallFont.clicked.connect(self.uninstallFonts)
        btnUninstallFont.setStyleSheet("QPushButton{border-image: url(icons/uninstall_default.png);font-size:14px;}"
                                       "QPushButton:disabled{border-image: url(icons/uninstall_forbid.png) 0 0 0 0;border:none;color:#c1c1c1;font-size:14px;}"
                                       "QPushButton:hover{border-image: url(icons/uninstall_hover.png) 0 0 0 0;border:none;color:rgb(51, 51, 51);}"
                                       "QPushButton:checked{border-image: url(icons/uninstall_click.png) 0 0 0 0;border:none;color:rgb(51, 51, 51);}")
        btnUninstallFont.setFixedSize(100,30)
        hbox2.addWidget(btnUninstallFont)        
        self.btnUninstallFont = btnUninstallFont

        buttonsContainer4 = QWidget()
        vbox.addWidget(buttonsContainer4)        
        hbox4 = QHBoxLayout(buttonsContainer4)
        hbox4.setContentsMargins(0,0,0,6)
        hbox4.setSpacing(3)

        #add checkBox
        checkCheckALL = QCheckBox()
        checkCheckALL.setChecked(False)
        checkCheckALL.setStyleSheet(
         "QCheckBox::indicator {width: 20px; height: 20px;}"
         "QCheckBox::indicator:unchecked {image:url(icons/CheckBox_uncheck_default.png);}"
         "QCheckBox::indicator:unchecked:hover {image:url(icons/CheckBox_uncheck_hover.png);}"
         "QCheckBox::indicator:checked:hover {image:url(icons/CheckBox_checked_hover.png);}"
         "QCheckBox::indicator:checked {image:url(icons/CheckBox_checked_default.png);}")
        checkCheckALL.stateChanged.connect(self.CheckboxChange)
        checkCheckALL.stateChanged.connect(self.apply)
        hbox4.addWidget(checkCheckALL)
        self.checkCheckALL = checkCheckALL       
	
	#add Label
        textLabel = QLabel()
        hbox4.addWidget(textLabel)
        self.textLabel = textLabel

        textLabel3 = QLabel()
        hbox4.addWidget(textLabel3)
        self.textLabel3 = textLabel3

        textLabel4 = QLabel()
        hbox4.addWidget(textLabel4)
        self.textLabel4 = textLabel4
        
        btnExpandAll = QPushButton()
        btnExpandAll.setStyleSheet("QPushButton{border-image: url(icons/ExpandAll_default.png) 0 0 0 0;border:none;color:rgb(51, 51, 51);}"
                                   "QPushButton:hover{border-image: url(icons/ExpandAll_hover.png) 0 0 0 0;border:none;color:rgb(51, 51, 51);}"
                                   "QPushButton:checked{border-image: url(icons/ExpandAll_click.png) 0 0 0 0;border:none;color:rgb(51, 51, 51);}")
        btnExpandAll.setFixedSize(87,26)
        btnExpandAll.clicked.connect(self.expandORcollapse)

        self.btnExpandAll = btnExpandAll
        hbox4.addWidget(btnExpandAll)

        #addStretch
        hbox4.addStretch()
        
        tree = QTreeWidget()
        tree.setColumnCount(3)
        tree.setColumnWidth(0, 250)
        tree.setColumnWidth(1, 250)
        tree.setColumnWidth(2, 300)
        tree.setStyleSheet("QTreeWidget {border:1px solid #c7c7c7;}"
                           "QTreeWidget QHeaderView::section{padding-left:6px;height:24px;background-color:#f8f8f8;border:1px solid #dddddd;border-bottom: 0px;border-top: 0px;}" 
                           "QTreeView::branch:has-children:!has-siblings:closed,\
                            QTreeView::branch:closed:has-children:has-siblings{border-image: none; image: url(icons/treeArrow_right.png);}\
                            QTreeView::branch:open:has-children:!has-siblings,\
                            QTreeView::branch:open:has-children:has-siblings{border-image: none; image: url(icons/treeArrow_bottom.png);}\
                            QTreeWidget::indicator:checked {image: url(icons/CheckBox_checked_default.png);}\
                            QTreeWidget::indicator:checked:hover {image: url(icons/CheckBox_checked_hover.png);}\
                            QTreeWidget::indicator:unchecked {image: url(icons/CheckBox_uncheck_default.png);}\
                            QTreeWidget::indicator:unchecked:hover {image: url(icons/CheckBox_uncheck_hover.png);}"
                            "QTreeView QScrollBar:vertical {border:1px solid #c7c7c7;border-left: 0px;background-color:#f1f1f1;padding-top:15px;padding-bottom:15px;}"
                            "QTreeView QScrollBar::handle:vertical {background-color:#c7c7c7;min-height:30px;}"
                            "QTreeView QScrollBar::handle:vertical:hover {background-color:#a6a6a6;}"
                            "QTreeView QScrollBar::add-line:vertical {border-image: url(icons/scorllAdd_default.png);}"
                            "QTreeView QScrollBar::add-line:vertical:hover {border-image: url(icons/scorllAdd_hover.png);}"
                            "QTreeView QScrollBar::sub-line:vertical:hover {border-image: url(icons/scorllSub_hover.png);}"
                            "QTreeView QScrollBar::sub-line:vertical {border-image: url(icons/scorllSub_default.png);}")
        tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tree.itemChanged.connect(self.handleTreeItemChanged)
        vbox.addWidget(tree)
        self.tree = tree      

        editSearch = QLineEdit("")
        editSearch.setFixedSize(210,30)
        editAction = QAction(editSearch)
        editSearch.addAction(editAction,QLineEdit.TrailingPosition)
        editAction.setIcon(QIcon("icons/search.png"))
        editSearch.textChanged.connect(self.handleEditSearchTextChanged)
        editAction.triggered.connect(self.loopSearch) 
        editSearch.setStyleSheet("QLineEdit {border:1px solid #c7c7c7;}")
        self.editSearch = editSearch   
        hbox4.addWidget(editSearch)
        
        right = QWidget()
        splitter.addWidget(right)
#        splitter.setSizes([200, 200])
        splitter.setStretchFactor(0,45)
        splitter.setStretchFactor(1,55)   

        vbox2 = QVBoxLayout(right)
        vbox2.setSpacing(0)
        vbox2.setContentsMargins(0,4,0,10)

        buttonsContainer2 = QWidget()
        vbox2.addWidget(buttonsContainer2)        
        hbox3 = QHBoxLayout(buttonsContainer2)
        hbox3.setContentsMargins(0,0,0,5)
        hbox3.setSpacing(7)
        
	#add Label
        textLabel2 = QLabel()
        hbox3.addWidget(textLabel2)
        self.textLabel2 = textLabel2

        spinBox = QSpinBox()
        spinBox.setRange(5, 60)
        spinBox.setValue(14)
        spinBox.setSingleStep(1)
        spinBox.setFixedSize(150,26)
        spinBox.setStyleSheet("QSpinBox {padding-right:23px;border: 1px solid #c7c7c7;}"
                              "QSpinBox::down-button{subcontrol-origin: padding;subcontrol-origin:border;subcontrol-position:right;image: url(icons/reduce_default.png);position:relative;right:23px;}"
                              "QSpinBox::down-button:hover{image: url(icons/reduce_click.png);}"
                              "QSpinBox::up-button{subcontrol-origin:border;subcontrol-position:right;image: url(icons/add_default.png);position:relative;right:2px;}"
                              "QSpinBox::up-button:hover{image: url(icons/add_click.png);}")

        spinBox.valueChanged.connect(self.handleFontSizeChanged)
        hbox3.addWidget(spinBox)
        self.spinBox = spinBox
        
        lineEdit = QLineEdit()
        lineEdit.setStyleSheet("QLineEdit {border:1px solid #c7c7c7;height:24px;}")   
        hbox3.addWidget(lineEdit)
        self.lineEdit = lineEdit
        
        scroll = QScrollArea()
        #scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea {border:1px solid #c7c7c7;}"
                             "QScrollArea QScrollBar {border:1px solid #c7c7c7;border-left: 0px;}"
                             "QScrollArea QScrollBar:vertical {background-color:#f1f1f1;padding-top:15px;padding-bottom:15px;}"
                             "QScrollArea QScrollBar::handle:vertical {background-color:#c7c7c7;min-height:30px;}"
                             "QScrollArea QScrollBar::handle:vertical:hover {background-color:#a6a6a6;}"
                             "QScrollArea QScrollBar::add-line:vertical {border-image: url(icons/scorllAdd_default.png);}"
                             "QScrollArea QScrollBar::add-line:vertical:hover {border-image: url(icons/scorllAdd_hover.png);}"
                             "QScrollArea QScrollBar::sub-line:vertical:hover {border-image: url(icons/scorllSub_hover.png);}"
                             "QScrollArea QScrollBar::sub-line:vertical {border-image: url(icons/scorllSub_default.png);}")
        vbox2.addWidget(scroll)
        
        displayer = FontDisplayer()
        scroll.setWidget(displayer)
        self.displayer = displayer
        #right.addWidget(displayer)

    def retranslateUI(self):
        self.in_retranslating = True
        
        self.wheres = [self.tr(u'All Fonts'), self.tr(u'System Fonts'), self.tr(u'User Fonts')]
        self.comboWhere.clear()
        self.comboWhere.addItems(self.wheres)
        self.comboWhere.setCurrentIndex(self.where)
        
        self.languages = [self.tr(u'zh_CN'), self.tr(u'English')]
        self.comboLang.clear()
        self.comboLang.addItems(self.languages)
        self.comboLang.setCurrentIndex(self.lang)
        
        self.checkCheckALL.setText(self.tr(u"Check All"))
        self.textLabel.setText(self.tr(u"(select"))
        self.textLabel3.setText(self.tr(u"0"))
        self.textLabel4.setText(self.tr(u"items)"))
        self.textLabel2.setText(self.tr(u"font preview:"))
        if self.btnExpandAll.text() == self.tr(u"全部展开") or self.btnExpandAll.text() == "Expand All":
            self.btnExpandAll.setText(self.tr(u"Expand All"))
        else:
            self.btnExpandAll.setText(self.tr(u"Collapse All"))
        
        self.tree.setHeaderLabels([self.tr(u'Font (Style)'), self.tr(u'Font Fullname'), self.tr(u'File')]) 
        self.editSearch.setPlaceholderText(self.tr(u'search'))       
        self.spinBox.setPrefix(self.tr(u'FontSize:'))
        self.spinBox.setSuffix(self.tr(u'pt'))
        self.btnInstallFont.setText(self.tr(u"Install Font"))
        self.btnUninstallFont.setText(self.tr(u"Uninstall Font"))
        self.lineEdit.setText(self.tr(u"How do you do, i am fine, and you ? This is a sentence just used for testing! "))
    
        self.setWindowTitle(self.tr(u'Fangde FontManager'))
        self.setWindowIcon(QIcon(u'/usr/share/nfs-fontmanager/icons/fmLogo.png'));
        
        self.in_retranslating = False
        
    def loadFonts(self):
        df = fc.listFc()
        families = list(set(df[u'family_'].tolist()))
        families.sort()
        for family in families:
            dfFamily = df[(df[u'family_'] == family) & ~df[u'is_symlink_'] &df[u'file'].apply(lambda file:self.fontsInWhere(file))]

            if len(dfFamily) == 0:
                continue
            
            itemFamily = QTreeWidgetItem(self.tree)
            itemFamily.setText(0, family)
            
            for index in dfFamily.index:
                item = dfFamily.loc[index]
                itemFont = QTreeWidgetItem(itemFamily)
                itemFont.setText(0, item[u'style_'])
                itemFont.setText(1, item[u'fullname_'])
                itemFont.setText(2, item[u'file'])
                itemFont.setCheckState(0, Qt.Unchecked)
                self.itemFonts.append(itemFont)
        self.tree.expandAll()

    def First_loadFonts(self,fclist):
        df = fclist
        families = list(set(df[u'family_'].tolist()))
        families.sort()
        for family in families:
            dfFamily = df[(df[u'family_'] == family) & ~df[u'is_symlink_'] &df[u'file'].apply(lambda file:self.fontsInWhere(file))]

            if len(dfFamily) == 0:
                continue
            
            itemFamily = QTreeWidgetItem(self.tree)
            itemFamily.setText(0, family)
            
            for index in dfFamily.index:
                item = dfFamily.loc[index]
                itemFont = QTreeWidgetItem(itemFamily)
                itemFont.setText(0, item[u'style_'])
                itemFont.setText(1, item[u'fullname_'])
                itemFont.setText(2, item[u'file'])
                itemFont.setCheckState(0, Qt.Unchecked)
                self.itemFonts.append(itemFont)
        self.tree.expandAll()
    
    def installFonts(self):
        files, filetype = QFileDialog.getOpenFileNames(self, self.tr(u"Select Font files to install"), os.getcwdu(), u"TTF Files (*.ttf *.TTF);; ODF Files (*.odf *.ODF);; TTC Files (*.ttc *.TTC);; All Font FIles (*.ttf *.TTF *.ttc *.TTC *.odf *.ODF);;")
        if len(files) == 0: return

        #added by guoliang 2019-11-26
        self.dlg_wait = QDialog()
        self.dlg_wait.setFixedSize(200,60)
        self.label_wait = QLabel(self.tr(u"Waiting for install fonts!"), self.dlg_wait)
        self.label_wait.move(30,20)
        self.dlg_wait.setWindowFlags(Qt.FramelessWindowHint)
        self.dlg_wait.setWindowModality(Qt.ApplicationModal);

        thread = DlgWaiting() 
        thread.set_params(fm, files)
        thread.start()
        self.dlg_wait.exec_()
    
        #res, cmd = fc.installFonts(files)
        res = self.res
        cmd = self.cmd

        if res==0:
            QMessageBox.information(self, self.tr(u"Prompt!"), self.tr(u"Fonts install Ok!"), QMessageBox.Yes)
            self.clearFonts()
            self.loadFonts()
            self.btnExpandAll.setText(self.tr(u"Collapse All"))         
        elif res==-1:
            pass #cancel 
        elif isinstance(res, int):
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Fonts install with unzero result: {} while executing command: {}").format(res, cmd), QMessageBox.Cancel)
        else:
            assert isinstance(res, Exception)
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Fonts install with exception: {} while executing command: {}").format(res, cmd), QMessageBox.Cancel)

    #double click to install font-file
    def installFonts_click(self,fontfile):
        files=fontfile
        if len(files) == 0: return

        reply = QMessageBox.question(self, self.tr(u"Question!"), self.tr(u"Are you sure to install this fonts?"), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return

        self.dlg_wait = QDialog()
        self.dlg_wait.setFixedSize(200,60)
        self.label_wait = QLabel(self.tr(u"Waiting for install fonts!"), self.dlg_wait)
        self.label_wait.move(30,20)
        self.dlg_wait.setWindowFlags(Qt.FramelessWindowHint)
        self.dlg_wait.setWindowModality(Qt.ApplicationModal);

        thread = DlgWaiting_c() 
        thread.set_params(fm, files)
        thread.start()
        self.dlg_wait.exec_()
    
        #res, cmd = fc.installFonts(files)
        res = self.res
        cmd = self.cmd

        if res==0:
            QMessageBox.information(self, self.tr(u"Prompt!"), self.tr(u"Fonts install Ok!"), QMessageBox.Yes)
            self.clearFonts()
            self.loadFonts()
            self.btnExpandAll.setText(self.tr(u"Collapse All"))         
        elif res==-1:
            pass #cancel 
        elif isinstance(res, int):
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Fonts install with unzero result: {} while executing command: {}").format(res, cmd), QMessageBox.Cancel)
        else:
            assert isinstance(res, Exception)
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Fonts install with exception: {} while executing command: {}").format(res, cmd), QMessageBox.Cancel)
        
    def uninstallFonts(self):
        files =[]
        for item in self.checked:
            file = item.text(2)
            if not file.startswith(u'/'): file = u'/usr/share/fonts/truetype/' + file
            files.append(file)
        reply = QMessageBox.question(self, self.tr(u"Question!"), self.tr(u"Are you sure to uninstall fonts?\nMaybe you can backup the font files before uninstall since it will be removed from the disk!"), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return            

        #added by hanxf 2019-11-28
        self.dlg_wait = QDialog()
        self.dlg_wait.setFixedSize(200,60)
        self.label_wait = QLabel(self.tr(u"Waiting for uninstall fonts!"), self.dlg_wait)
        self.label_wait.move(30,20)
        self.dlg_wait.setWindowFlags(Qt.FramelessWindowHint)
        self.dlg_wait.setWindowModality(Qt.ApplicationModal);

        thread = DlgWaiting_u() 
        thread.set_params(fm, files)
        thread.start()
        self.dlg_wait.exec_()
   
        #res, cmd = fc.uninstallFonts(files)
        res = self.res
        cmd = self.cmd

        if res==0:
            QMessageBox.information(self, self.tr(u"Prompt!"), self.tr(u"Fonts uninstall Ok!"), QMessageBox.Yes)
            self.clearFonts()
            self.loadFonts()
            self.btnExpandAll.setText(self.tr(u"Collapse All"))         
        elif res==-1:
            pass #cancel 
        elif isinstance(res, int):
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Font uninstall failed! Administrator privileges are required to uninstall system fonts."), QMessageBox.Cancel)
        else:
            assert isinstance(res, Exception)
            QMessageBox.warning(self, self.tr(u"Warning!"), self.tr(u"Fonts uninstall with exception: {} while executing command: {}").format(res, cmd), QMessageBox.Cancel)
    
    def fontsInWhere(self, file):
        #All fonts
	user_home = os.path.expanduser('~')
        res = glsu.checkSudo()
        if res:
            dest = '/usr/local/share/fonts/'
        else: 
            dest = user_home+'/.local/share/fonts/'

        if self.where == 0:
            result = True
        #user fonts
        elif self.where == 2:
            result = file.startswith(dest)
        else: 
        #system fonts
            result = not file.startswith(dest)

        return result
    
        
    def clearFonts(self):
        self.tree.clear()
        self.checked = []
        self.itemFonts = []
    
    def checkAll(self):
        for itemFont in self.itemFonts:
            itemFont.setCheckState(0, Qt.Checked)
            
    def unCheckAll(self):
        for itemFont in self.itemFonts:
            itemFont.setCheckState(0, Qt.Unchecked)
    
    def CheckboxChange(self, state):
        self.checkbox_val = 1
        if state == Qt.Checked:
            self.checkAll()
        else: 
            self.unCheckAll()
#        self.apply()
        self.checkbox_val = 0

    def expandORcollapse(self): 
        if self.btnExpandAll.text() == self.tr(u"Expand All"):
            self.expandAll()
        else:
            self.collapseAll()

    def expandAll(self):
        self.tree.expandAll()
        self.btnExpandAll.setText(self.tr(u"Collapse All"))
    
    def collapseAll(self):
        self.tree.collapseAll()
        self.btnExpandAll.setText(self.tr(u"Expand All"))
        
    def handleTreeItemChanged(self, item, column):
        if item.checkState(column) == Qt.Checked:
            self.checked.append(item)
            if self.checkbox_val == 0:self.apply()
            self.items = self.items + 1
            self.textLabel3.setText(str(self.items))
        elif item.checkState(column) == Qt.Unchecked:
            if item in self.checked: self.checked.remove(item)
            if self.checkbox_val == 0:self.apply()
            if self.items > 0 :
                self.items = self.items - 1
            self.textLabel3.setText(str(self.items))
        self.btnUninstallFont.setEnabled(len(self.checked)>0)
        if self.items == 0 : self.checkCheckALL.setChecked(False)
    
    def handleFontSizeChanged(self):
        self.displayer.updateFontSize(self.spinBox.value())

    def loopSearch(self,):
        if len(self.searchText) == 0:
            return
        self.tree.setCurrentItem(self.searchText[self.loop])
        self.loop = self.loop + 1
        if self.loop >= len(self.searchText):
            self.loop = 0

    def handleEditSearchTextChanged(self, keyword):
        all_items = self.tree.findItems("", Qt.MatchStartsWith)
        for item in all_items:
            item.setHidden(True)
        count = self.tree.topLevelItemCount()
        self.searchText = []
        for i in xrange(count): 
            item = self.tree.topLevelItem(i)
            if keyword.lower() in item.text(0).lower(): #case insensitive
                item.setHidden(False)
                self.searchText.append(item)
        self.loop = 0     

    def handleComboWhereIndexChanged(self, index):
        if index==-1 or self.where == index or self.in_retranslating:
            return
        self.where = index
        self.clearFonts()
        self.loadFonts()
        self.checkCheckALL.setChecked(False)
        self.items =0
        self.textLabel3.setText(str(self.items))
        self.btnExpandAll.setText(self.tr(u"Collapse All"))
            
    def handleComboLanguageIndexChanged(self, index):           
        if not self.in_retranslating:
            self.lang = index
            self.translate(index)
            self.textLabel3.setText(str(self.items))
                   
    def translate(self, index):
        self.translator = QTranslator()
        self.qt_translator = QTranslator()           
        if index == 0:
            #zh_CN
            self.translator.load(u"translation/fm.qm")
            self.qt_translator.load("translation/qt_zh_CN.qm")            
        self.app.installTranslator(self.translator)
        self.app.installTranslator(self.qt_translator)
        self.retranslateUI()
        
    def apply(self):
        self.displayer.updateFonts(self.lineEdit.text(), [(item.parent().text(0), item.text(0), item.text(1)) for item in self.checked])   

if __name__ == u'__main__':
    app = QApplication(sys.argv)
    
    Newthread = LoadFclist() 
    Newthread.start()

    fm = FontManager()
    #fm.loadFonts()
    fm.resize(900,600)
    fm.setStyleSheet("QWidget{background-color:white;color:#333333}")
    fm.show()
    Newthread.trigger.connect(fm.First_loadFonts) 

    if (len(sys.argv) ==2) and sys.argv[1]:
        fm.installFonts_click(sys.argv[1])
    sys.exit(app.exec_())



