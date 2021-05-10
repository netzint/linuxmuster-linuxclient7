import ldap, ldap.sasl, sys, getpass, subprocess, pwd, os, os.path
from linuxmusterLinuxclient7 import logging, constants, config, user, ldapHelper, shares, fileHelper, computer, localUserHelper

def readAttributes():
    if not user.isInAD():
        return False, None

    return ldapHelper.searchOne("(sAMAccountName={})".format(user.username()))

def school():
    rc, userdata = readAttributes()
    
    if not rc:
        return False, None

    return True, userdata["sophomorixSchoolname"]

def username():
    return getpass.getuser()

def isUserInAD(user):
    if not computer.isInAD():
        return False
    
    rc, groups = localUserHelper.getGroupsOfLocalUser(user)
    if not rc:
        return False

    return "domain users" in groups

def isInAD():
    return isUserInAD(username())

def isRoot():
    return os.geteuid() == 0

def isInGroup(groupName):
    rc, groups = localUserHelper.getGroupsOfLocalUser(username())
    if not rc:
        return False

    return groupName in groups

def cleanTemplateUserGtkBookmarks():
    logging.info("Cleaning {} gtk bookmarks".format(constants.templateUser))
    gtkBookmarksFile = "/home/{0}/.config/gtk-3.0/bookmarks".format(user.username())

    if not os.path.isfile(gtkBookmarksFile):
        logging.warning("Gtk bookmarks file not found, skipping!")
        return

    fileHelper.removeLinesInFileContainingString(gtkBookmarksFile, constants.templateUser)

def mountHomeShare():
    rc, userAttributes = readAttributes()
    if rc:
        # Try to mount home share!
        try:
            homeShareServerPath = userAttributes["homeDirectory"]
            username = userAttributes["sAMAccountName"]
            shareName = "{0} ({1})".format(username, userAttributes["homeDrive"])
            shares.mountShare(homeShareServerPath, shareName=shareName, hiddenShare=False, username=username)
        except Exception as e:
            logging.error("Could not mount home dir of user")
            logging.exception(e)