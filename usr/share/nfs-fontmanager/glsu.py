#-*- encoding:utf-8 -*-

u'''
@author:guoliang@nfschina.com
'''

from __future__ import absolute_import
import os
import sys
import getpass
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QWidget, QPushButton, QHBoxLayout, QMessageBox, QApplication

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def run(cmd):
#    if not inSudo():
#        while True:
#            b = getSudo()
#            if b is None:  return -1 #Cancel
#            if b == False:  #error sudo password
#                continue   
#            else:
#                assert b==True #get sudo priviledge
#                break
    if isinstance(cmd, unicode):
#        res = os.system(u'sudo ' + cmd)
        res = os.system(cmd)
    else:
#        cmds = [u'sudo %s'%c for c in cmd]
        cmds = [u'%s'%c for c in cmd]
        res = os.system(u' && '.join(cmds))
    return res

#sudo -v need sudo priviledge, but no outputs
#2>/dev/null used hide the information when sudo password error
def inSudo():
    res = os.system(u'echo "" | sudo -S -p "" -v  2>/dev/null')
    return res == 0

def testSudo(passwd):
    cmd = u'echo "%s" | sudo -S -p "" -v 2>/dev/null' % passwd
    res = os.system(cmd)
    return res == 0

#check user
def checkSudo():
    user_name = getpass.getuser()
    root_name = u"root"
    secadm_name = u"secadm"
    auditadm_name = u"auditadm"   
    desktop = QApplication.desktop()
    if (user_name == root_name or user_name == secadm_name or user_name == auditadm_name):  
        return 1  
    return 0

def getSudo():
    desktop = QApplication.desktop()
    passwd,ok = QInputDialog.getText(desktop, desktop.tr(u'Password Dialog'), desktop.tr(u"Please input sudo password:"),QLineEdit.Password, u" ")
    if not ok:
        return None
    b = testSudo(passwd)
    if not b:
        QMessageBox.warning(desktop, desktop.tr(u"Error!"), desktop.tr(u"Invalid sudo password!"), QMessageBox.Yes)    
    return b

#from PyQt5.QWidgets import QPushButton, QHBoxLayout, QWidget
class TestWindow(QWidget):    
    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)
        hbox = QHBoxLayout(self)
        okBtn = QPushButton(u"ok")
        okBtn.clicked.connect(self.test)
        hbox.addWidget(okBtn)
        
    def test(self):
        res = run(u"ls /root")
        print res
        
if __name__ == u'__main__':
    import sys
    app = QApplication(sys.argv)
    window = TestWindow()
    window.setWindowTitle(u"test")
    window.show()
    sys.exit(app.exec_())
    
