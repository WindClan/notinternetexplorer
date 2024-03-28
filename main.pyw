# Included Python libraries
import sys
import os
import uuid
import tkinter.messagebox
import _thread
from pathlib import Path

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
# Install PySide 6 main
try:
    import PySide6
except Exception as e:
    print(e)
    install("PySide6-Essentials")
    import PySide6
    
# Install Requests
try:
    import requests
except Exception as e:
    print(e)
    install("requests")
    import requests

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

# Install PySide 6 Web Engine
try:
    from PySide6.QtWebEngineWidgets import *
    from PySide6.QtWebEngineCore import *
except  Exception as e:
    print(e)
    install("PySide6-Addons")
    from PySide6.QtWebEngineWidgets import *
    from PySide6.QtWebEngineCore import *


# Make sure all the assets exist
base = "https://raw.githubusercontent.com/notbronwyn/notinternetexplorer/main/"
def verify(url):
    if not os.path.exists(url):
        print("Downloading: "+url)
        _thread.start_new_thread(tkinter.messagebox.showinfo,("Info", "Downloading file "+url))
        file = requests.get(base+url)
        a = open(url,"wb")
        a.write(file.content)
        a.close
    else:
        print("The file "+url+" exists!")

#dealing with the directories at launch
userfolder = str(Path.home())
cachepath = '%s/.shittywebbrowser/' %  userfolder
downloadpath = '%s/Downloads/' %  userfolder
if not os.path.exists(cachepath):
    os.makedirs(cachepath)
if not os.path.exists(downloadpath):
    os.makedirs(downloadpath)
tabs = {}
class Browser(QWebEngineView):
    tabUuid = ""
    def __init__(self):
        super(Browser,self).__init__()
        page = self.page()
        profile = page.profile()
        profile.setCachePath(cachepath)
        profile.setDownloadPath(downloadpath)
        profile.setPersistentStoragePath(cachepath)
        
        settings = profile.settings()
        settings.HyperlinkAuditingEnabled = True
        settings.ScrollAnimatorEnabled = True
        settings.PluginsEnabled = True
        settings.FullScreenSupportEnabled = True
        settings.ScreenCaptureEnabled = True
        settings.Accelerated2dCanvasEnabled = True
        settings.AllowWindowActivationFromJavaScript = True
        settings.PdfViewerEnabled = True
        
        settings.PlaybackRequiresUserGesture = False 
        settings.AllowGeolocationOnInsecureOrigins = False
        settings.AllowRunningInsecureContent = True

class Window(QMainWindow):
    #3d color balance: -76 16 0
    currentBrowser = None
    bypass = False
    def __init__(self):
        super(Window,self).__init__()
        verify('icon.png')
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("Not Internet Explorer")
        self.setMinimumSize(640, 480);
        navbar = QToolBar()
        navbar.setStyleSheet('opacity:0;')
        navbar.setMovable(False)
        searchbar = QToolBar()
        searchbar.setStyleSheet('opacity:0; height:32px; padding:0; margin:0;')
        searchbar.setMovable(False)
        self.addToolBar(searchbar)
        self.addToolBarBreak()
        self.addToolBar(navbar)

        back = QLabel(self)
        verify('buttonFrame.png')
        backIcon = QIcon("buttonFrame.png").pixmap(70,29)
        back.setPixmap(backIcon)
        back.setMask(backIcon.mask());
        back.setFixedSize(QSize(70,29))
        searchbar.addWidget(back)
        
        self.prevBtn = QPushButton(back)
        verify('back.png')
        self.prevBtn.setIcon(QIcon('back.png'))
        self.prevBtn.setIconSize(QSize(27,27))
        self.prevBtn.setStyleSheet("background-color: rgba(255, 255, 255, 0);");
        self.prevBtn.setFixedSize(QSize(27,27))
        self.prevBtn.move(1,1)
        
        self.nextBtn = QPushButton(back)
        verify('forward.png')
        self.nextBtn.setIcon(QIcon('forward.png'))
        self.nextBtn.setStyleSheet("background-color: rgba(255, 255, 255, 0);");
        self.nextBtn.setIconSize(QSize(27,27))
        self.nextBtn.setFixedSize(QSize(27,27))
        self.nextBtn.move(29,1)

        self.searchBar = QLineEdit()
        self.currentIcon = QIcon()
        self.searchBar.returnPressed.connect(self.loadUrl)
        self.searchBar.setFixedHeight(20)
        self.searchBar.setPlaceholderText("Enter web address")
        self.searchBar.addAction(self.currentIcon, QLineEdit.LeadingPosition)
        
        searchbar.addWidget(self.searchBar)

        self.refreshBtn = QToolButton(self)
        
        verify('refresh.png')
        self.refreshBtn.setIcon(QIcon('refresh.png'))
        self.refreshBtn.setIconSize(QSize(22,22))
        searchbar.addWidget(self.refreshBtn)

        self.searchBar1 = QLineEdit()
        self.searchBar1.setStyleSheet("width:253px;")
        self.searchBar1.setMaximumWidth(253)
        self.searchBar1.setFixedHeight(20)
        self.searchBar1.returnPressed.connect(self.search)
        self.searchBar1.setPlaceholderText("Google")
        verify('search.png')
        self.searchBar1.addAction(QIcon("search.png"), QLineEdit.LeadingPosition)
        searchbar.addWidget(self.searchBar1)

        searchBtn = QToolButton(self)
        verify('search1.png')
        searchBtn.setIcon(QIcon('search1.png'))
        searchBtn.setIconSize(QSize(22,22))
        searchBtn.pressed.connect(self.search)
        searchbar.addWidget(searchBtn)
        
        self.tabBar = QTabBar(self)
        self.tabBar.setShape(QTabBar.RoundedNorth)
        self.tabBar.setTabsClosable(True)
        self.tabBar.currentChanged.connect(self.changeTab)
        self.tabBar.tabCloseRequested.connect(self.closeTab)
        navbar.addWidget(self.tabBar)

        addTab = QToolButton(self)
        addTab.setStyleSheet("""background-color:#E3EEFB;
                                height: 23px;
                                width:  28px;
                                border-radius: 2px 2px 0px 0px;
                                border: 1px solid #A2A6AB;
                                border-bottom: none;
                                bottom:0;""")
        addTab.font().setBold(True)
        navbar.addWidget(addTab)
        addTab.clicked.connect(self.newTab)
        self.newTab()
        self.bypass = True
        self.changeTab(0)
        self.showMaximized()
    def closeTab(self,index):
        tabUuid = self.tabBar.tabWhatsThis(index)
        old = tabs[tabUuid]
        try:
            old.titleChanged.disconnect()
            old.iconChanged.disconnect()
        except Exception as e:
            print(e)
        old.deleteLater()
        self.tabBar.removeTab(index)
    def newTab(self):
        browser = Browser()
        tabUuid = str(uuid.uuid4())
        browser.tabUuid = tabUuid
        tabs[tabUuid] = browser
        tab = self.tabBar.addTab("New Tab")
        self.tabBar.setTabWhatsThis(tab,tabUuid)
        def changeTabName(newName):
            if len(newName) == 0:
                newName = "(blank name)"
            self.tabBar.setTabText(tab,newName)
            if browser == self.currentBrowser:
                self.setWindowTitle(newName+" - Not Internet Explorer")
                    
        def changeTabIcon(newName):
            self.tabBar.setTabIcon(tab,newName)
            if browser == self.currentBrowser and False:
                try:
                    self.currentIcon = None
                    self.currentIcon = newName
                    self.searchBar.addAction(self.currentIcon, QLineEdit.LeadingPosition)
                except Exception as e:
                    print(e)
        tabs[tabUuid].titleChanged.connect(changeTabName)
        tabs[tabUuid].iconChanged.connect(changeTabIcon)
        self.tabBar.setCurrentIndex(tab)
        return tabUuid
    def changeTab(self,index):
        if index != 0 or self.bypass == True:
            if self.currentBrowser != None:
                self.currentBrowser.urlChanged.disconnect()
                #self.currentBrowser.iconChanged.disconnect()     
                self.currentBrowser.setParent(None)
            self.currentBrowser = None
            self.currentBrowser = tabs[self.tabBar.tabWhatsThis(index)]
            self.searchBar.setText(self.currentBrowser.url().toString())
            newName = self.currentBrowser.title()
            if len(newName) == 0:
                self.setWindowTitle("Not Internet Explorer")
            else:
                self.setWindowTitle(newName+" - Not Internet Explorer")
            self.setCentralWidget(self.currentBrowser)
            self.HookUpEvents()
        else:
            print(index)
            print(self.bypass)

    def loadUrl(self):
        url = self.searchBar.text()
        if (url.startswith("https://") or url.startswith("http://") or url.startswith("view-source:")):
            self.currentBrowser.setUrl(QUrl(url))
        else:
            self.currentBrowser.setUrl(QUrl("https://www.google.com/search?q="+url))
    def search(self):
        url = self.searchBar1.text()
        self.currentBrowser.setUrl(QUrl("https://www.google.com/search?q="+url))
    def updateUrl(self, url):
        self.searchBar.setText(url.toString())        
    def HookUpEvents(self):
        try:
            self.prevBtn.clicked.disconnect()
            self.nextBtn.clicked.disconnect()
            self.refreshBtn.clicked.disconnect()
        except Exception as e:
            print(e)
            
        self.currentBrowser.urlChanged.connect(self.updateUrl)
        #self.currentBrowser.iconChanged.connect(self.updateIcon)     
        self.prevBtn.clicked.connect(self.currentBrowser.back)
        self.nextBtn.clicked.connect(self.currentBrowser.forward)
        self.refreshBtn.clicked.connect(self.currentBrowser.reload)
    def resizeEvent(self, event):
        #self.searchBar.setMaximumWidth(event.size().width()/3.1)
        QMainWindow.resizeEvent(self, event)
main = QApplication(sys.argv)
main.setStyleSheet("""
QTabBar::tab {
    /* background: linear-gradient(0deg, rgba(242,246,251,1) 0%, rgba(195,221,251,1) 100%); */
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 rgba(195,221,251,1), stop: 1 rgba(242,246,251,1));
    border: 1px solid #A2A6AB;
    height: 27px;
    border-radius: 2px 2px 0px 0px;
    border-bottom: none;
}
QTabBar:: {
    height:30px;
    margin-bottom:0;
    opacity:0;
}
QMainWindow {
    background-color: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0,stop: 0 rgba(243,244,247,1), stop: 1 rgba(234,229,203,1));
}
QLineEdit {
    height: 20px;
    border 1px solid #A2A6AB;
}
""")
main.setApplicationName('shittywebbrowser')
#main.setStyle('Fusion')
window = Window()
main.exec()
