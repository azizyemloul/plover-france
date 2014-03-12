# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

import sys

if sys.platform.startswith('win32'):
    import win32gui
    GetForegroundWindow = win32gui.GetForegroundWindow
    SetForegroundWindow = win32gui.SetForegroundWindow

    def SetTopApp():
        # Nothing else is necessary for windows.
        pass

elif sys.platform.startswith('darwin'):
    from Foundation import NSAppleScript
    from AppKit import NSApp, NSApplication

    def GetForegroundWindow():
        return NSAppleScript.alloc().initWithSource_("""
tell application "System Events"
    return unix id of first process whose frontmost = true
end tell""").executeAndReturnError_(None)[0].int32Value()

    def SetForegroundWindow(pid):
        NSAppleScript.alloc().initWithSource_("""
tell application "System Events"
    set the frontmost of first process whose unix id is %d to true
end tell""" % pid).executeAndReturnError_(None)

    def SetTopApp():
        NSApplication.sharedApplication()
        NSApp().activateIgnoringOtherApps_(True)

elif sys.platform.startswith('linux'):
    from subprocess import call, check_output, CalledProcessError

    def GetForegroundWindow():
        try:
            output = check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW'])
            return output.split()[-1]
        except CalledProcessError:
            return None

    def SetForegroundWindow(w):
        try:
            call(['wmctrl', '-i', '-a', w])
        except CalledProcessError:
            pass

    def SetTopApp():
        try:
            call(['wmctrl', '-a', TITLE])
        except CalledProcessError:
            pass

else:
    # These functions are optional so provide a non-functional default 
    # implementation.
    def GetForegroundWindow():
        return None

    def SetForegroundWindow(w):
        pass

    def SetTopApp():
        pass
