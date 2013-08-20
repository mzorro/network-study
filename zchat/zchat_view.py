# -*- coding:utf-8 -*-
from zchat import *
from zchat_client import Client, BroadcastReceiver
import wx
import wx.richtext
import threading
logger = Logger('view')
class LoginDialog (wx.Dialog):

    def __init__(self):
        self.app = wx.GetApp()
        wx.Dialog.__init__ (self, parent=None, title = u"登陆",
                            style = wx.CAPTION)
        
        self.font20 = wx.Font(20, 70, 90, 90, False, u"微软雅黑")
        self.font16 = wx.Font(16, 70, 90, 90, False, u"微软雅黑")
        self.name, self.pswd, self.pswd2 = (u'',) * 3
        self.CreateSizer()
        self.cbSignin.SetValue(False)
        
    def dataEntries(self):
        return ((u'用户', 0, self.OnName),
                (u'密码', wx.TE_PASSWORD, self.OnPswd),
                (u'确认', wx.TE_PASSWORD, self.OnPswd2))

    def dataButtons(self):
        return ((wx.CheckBox, u'注册', wx.ID_ANY, wx.EVT_CHECKBOX,  self.OnCheckBox),
                (wx.Button, u'登陆', wx.ID_OK, wx.EVT_BUTTON, self.OnOK),
                (wx.Button, u'退出', wx.ID_CANCEL, wx.EVT_BUTTON, lambda _:wx.Exit()))

    def CreateSizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label = u'请输入用户名和密码'),
                  0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.CreateEntries(sizer)
        self.stl = wx.StaticLine(self, size=(20, -1), style=wx.LI_HORIZONTAL) 
        sizer.Add(self.stl, 0, wx.GROW |wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)
        self.cbSignin, self.btnOk = self.CreateButtons(sizer)[:2]
        sizer.Hide(3)
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.Center(wx.BOTH)

    def CreateEntries(self, sizer):
        for entry in self.dataEntries():
            sizer.Add(self.CreateEntry(*entry), 1, wx.EXPAND, 5)

    def CreateButtons(self, sizer):
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons = []
        for btndata in self.dataButtons():
            buttons.append(self.CreateButton(btnsizer, *btndata))
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        return buttons
        
    def CreateEntry(self, label, style, handler):
        box = wx.BoxSizer(wx.HORIZONTAL)
        static = wx.StaticText(self, label = label)
        static.SetFont(self.font20)
        box.Add(static, 0, wx.ALL, 5)
        text = wx.TextCtrl(self, style = style)
        text.SetFont(self.font20)
        text.Bind(wx.EVT_TEXT, handler)
        box.Add(text, 1, wx.ALL, 5)
        return box
        
    def CreateButton(self, btnsizer, kind, label, id, evt, handler):
        button = kind(self, id, label)
        button.Bind(evt, handler)
        button.SetFont(self.font16)
        if id == wx.ID_OK:
            button.SetDefault()
        btnsizer.Add(button)
        return button

    def OnName(self, event):
        self.name = event.GetString()

    def OnPswd(self, event):
        self.pswd = event.GetString()

    def OnPswd2(self, event):
        self.pswd2 = event.GetString()

    def ChangeMode(self):
        if not self.cbSignin.IsChecked():
            self.GetSizer().Hide(3)
            self.btnOk.SetLabel(u'登陆')
            self.Fit()
        else:
            self.GetSizer().Show(3)
            self.btnOk.SetLabel(u'注册')
            self.Fit()
        
    def ConfirmValue(self):
        name_len = len(self.name)
        if name_len == 0:
            wx.MessageBox(u'请输入用户名！')
            return False
        elif name_len > 16:
            wx.MessageBox(u'用户名太长！')
            return False
        if self.cbSignin.IsChecked():
            if self.pswd != self.pswd2:
                wx.MessageBox(u'密码不一致！')
                return False
        return True
        
    def GetValue(self):
        return self.name, MD5_CONVERT(self.pswd)

    def OnOK(self, event):
        if not self.app.Connected(): return
        if not self.ConfirmValue(): return
        if not self.cbSignin.IsChecked():
            reply = self.app.client.makeRequest(LOGIN, *self.GetValue())
            if not reply[0]:
                wx.MessageBox(reply[1])
            else:
                self.Close()
                self.app.user_name = self.name
                self.app.frame.Show()
                self.app.frame.panel.FreshInfoList()
        else:
            reply = self.app.client.makeRequest(SIGNIN, *self.GetValue())
            if not reply[0]:
                wx.MessageBox(reply[1])
            else:
                wx.MessageBox(u'注册成功！')
                self.cbSignin.SetValue(False)          
                self.ChangeMode()

    def OnCheckBox(self, event):
        self.ChangeMode()

class RoomPanel(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent = parent)
        self.app = wx.GetApp()
        self.parent = parent
        self.SetBackgroundColour(wx.Colour(43,43,43))
        self.textInput = ''
        self.CreateSizer()
        self.Bind(wx.EVT_IDLE, self.OnIDLE)
        
    def CreateSizer(self):
        font14 = wx.Font(14, 70, 90, 90, False, u"微软雅黑")
        ctrlBKGR = wx.Colour(83,83,83)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        msgSizer = wx.BoxSizer(wx.VERTICAL)
        self.msgBox = wx.TextCtrl(self, size = (500,400),
                                  style = wx.TE_READONLY | wx.TE_MULTILINE
                                  | wx.TE_WORDWRAP) 
        self.msgBox.SetFont(font14)
        self.msgBox.SetBackgroundColour(ctrlBKGR)
        msgSizer.Add(self.msgBox, 1, wx.ALL, 5)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inputBox = wx.TextCtrl(self, size = (-1,40),
                                    style = wx.TE_PROCESS_ENTER)
        self.inputBox.SetFont(font14)
        self.inputBox.Bind(wx.EVT_TEXT, self.OnTextInput)
        self.inputBox.Bind(wx.EVT_TEXT_ENTER, self.OnSendMsg)
        self.inputBox.SetBackgroundColour(ctrlBKGR)
        btnsizer.Add(self.inputBox, 1, wx.ALL, 5)
        self.staticSend = wx.StaticText(self, label = u"Enter\n发送",
                                        size = (80,40),
                                        style = wx.BOTTOM | wx.ALIGN_CENTER)
        self.staticSend.SetFont(font14)
        btnsizer.Add(self.staticSend, 0, wx.EXPAND, 5)
        msgSizer.Add(btnsizer, 0, wx.EXPAND, 0)
         
        sizer.Add(msgSizer, 0, wx.EXPAND, 0)
        
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.infoList = wx.ListCtrl(self, size = (200,350),
                                    style = wx.LC_REPORT)
        self.infoList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.infoList.SetBackgroundColour(ctrlBKGR)
        sizer2.Add(self.infoList, 0, wx.GROW | wx.ALL, 5)
        self.detailList = wx.ListCtrl(self, size = (200,240),
                                      style = wx.LC_REPORT)
        self.detailList.SetBackgroundColour(ctrlBKGR)
        sizer2.Add(self.detailList, 1, wx.GROW | wx.ALL, 5)
        sizer.Add(sizer2, 1, wx.GROW | wx.ALL, 0)
        self.SetSizer(sizer)
        self.Fit()

    def OnTextInput(self, event):
        self.textInput = event.GetString()

    def OnSendMsg(self, event):
        if not self.textInput: return
        logger.info('sending msg: ' + self.textInput)
        self.app.client.makeRequest(TALK, self.app.user_name, self.textInput)
        self.inputBox.Clear()
        self.msgBox.UpdateWindowUI()

    def FreshInfoList(self):
        self.infoList.ClearAll()
        self.infoList.InsertColumn(0, u'当前在线用户', width = 300)
        info = self.app.client.makeRequest(USER_INFO, self.app.user_name)
        for i in info:
            name = i[0]
            if not i[1]:
                name += u'(管理员)'
            if i[2]:
                name += u'(禁言)'
            self.infoList.Append((name,))

    def ShowDetail(self, detail):
        self.detailList.ClearAll()
        self.detailList.InsertColumn(0, u'用户属性', width = 100)
        self.detailList.InsertColumn(1, u'', width = 200);
        self.detailList.Append((u'用户名', detail[0]))
        
        self.detailList.Append((u'用户类型',
                               u'普通用户' if detail[1]
                               else u'管理员'))
        status = u'离线'
        if detail[2]:
            status = u'在线'
        if detail[3]:
            status = u'禁言'
            self.detailList.Append((u'禁言剩余', u'%d分钟' % detail[4]))
        self.detailList.Append((u'上次登陆', detail[5]))
        self.detailList.Append((u'累计在线', u'%d分钟' % (detail[6] / 60)))
            
    def OnItemSelected(self, event):
        name = self.infoList.GetItem(event.GetIndex(), 0).GetText()
        detail = self.app.client.makeRequest(USER_DETAIL, name)
        self.ShowDetail(detail)

    def OnIDLE(self, event):
        if self.parent.IsShown() and self.FindFocus() != self.inputBox:
            self.inputBox.SetFocus()

class RoomFrame(wx.Frame):
    
    def __init__(self):
        self.app = wx.GetApp()
        wx.Frame.__init__ (self, None,
                           title = u"zchat聊天室",
                           size = (-1 ,-1 ))
        self.panel = RoomPanel(self)
        self.Fit()
        self.Center(wx.BOTH)
        self.statusbar = self.CreateStatusBar()
        self.PushStatusText(u'成功登陆！')
        self.Fit()
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnExit(self, event):
        if wx.OK==wx.MessageBox(u'确定退出zchat聊天室？',
                                style = wx.OK | wx.CENTER | wx.CANCEL):
            self.app.client.makeRequest(LOGOUT, self.app.user_name)
            wx.CallLater(1000, wx.Exit)

class BroadcastHandler():
    
    def __init__(self):
        self.msgBox = wx.GetApp().frame.panel.msgBox
        self.handlers = [
            self.handle_signin,
            self.handle_login,
            self.handle_logout,
            None,
            self.handle_talk,
            self.handle_kickout,
            self.handle_shutup,
            self.handle_unshutup,
            None
        ]

    def handle(self, cmd):
        return self.handlers[cmd[0]](cmd[1])

    __call__ = handle

    def AppendSystemMsg(self, msg):
        self.msgBox.WriteText(u'系统提示：')
        self.msgBox.WriteText(msg)

    def AppendTalk(self, name, msg):
        self.msgBox.AppendText(u'%s 说：' % name)
        self.msgBox.AppendText(msg + u'\n')


    def handle_signin(self, cmd):
        logger.info(repr(cmd))

    def handle_login(self, cmd):
        self.user_name = cmd[1]
        name = self.user_name + '' if cmd[0] else '(管理员)'
        self.AppendSystemMsg(u'%s 登陆啦!~~\n' % name)
        logger.info(repr(cmd))
                    
    def handle_logout(self, cmd):
        self.AppendSystemMsg(u'%s 退出啦!~~\n' % cmd)
        logger.info(repr(cmd))
       
    def handle_talk(self, cmd):
        self.AppendTalk(*cmd)
        logger.info(repr(cmd))
        
    def handle_kickout(self, cmd):
        self.AppendSystemMsg(u'%s 被管理员 %s 踢出!~~\n'
                             % (cmd[1], cmd[0]))
        logger.info(repr(cmd))

    def handle_shutup(self, cmd):
        self.AppendSystemMsg(u'%s 被管理员 %s 禁言 %d 分钟!~~\n'
                             % (cmd[1], cmd[0], cmd[2]))
        logger.info(repr(cmd))

    def handle_unshutup(self, cmd):
        self.AppendSystemMsg(u'%s 被管理员 %s 禁言 %d 分钟!~~\n'
                             % (cmd[1], cmd[0]))
        logger.info(repr(cmd))

class App(wx.App):
    def __init__(self, redirect = False, filename = None):
        print 'App Init...'
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):
        print 'OnInit...'
        self.frame = RoomFrame()
        self.SetTopWindow(self.frame)
        self.SetExitOnFrameDelete(True)
        self.client = Client(self)
        self.receiver = BroadcastReceiver(self)
        self.receiver.set_handler(BroadcastHandler())
        self.user_name = None
        LoginDialog().Show()
        return True

    def Connected(self):
        if not self.receiver.sock:
            res = self.receiver.connect()
            if res:
                wx.MessageBox(res)
                return False
            self.receiver.start()
        if not self.client.sock:
            res = self.client.connect()
            if res:
                wx.MessageBox(res)
                return False
        return True

    def OnExit(self):
        say_it = lambda : logger.info('stoping thread...'
                                      'current active_count : %d'
                                      % threading.active_count())
        say_it()
        self.receiver.stop_running()
        while threading.active_count() > 1:
            wx.CallLater(200, say_it)
        logger.info('exiting...')

    def ErrorExit(self, msg):
        wx.MessageBox(msg)
        logger.error('error exiting...')
        wx.Exit()

app = App(False)
app.MainLoop()
