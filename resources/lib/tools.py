#!/usr/bin/python
# -*- coding: utf-8 -*-

# -- This is a set of utility functions for use when developing XBMC-Kodi addons -- #

import urllib2
import sys
import time
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

#pluginhandle = int(sys.argv[1])
addon_name = xbmcaddon.Addon().getAddonInfo('name')
#extendedLog = xbmcaddon.Addon().getSetting("extendedLog") == "true"

# Suggested view codes for each type from different skins (initial list thanks to xbmcswift2 library)
ALL_VIEW_CODES = {
	'list': {
		'skin.confluence': 50, # List
		'skin.aeon.nox': 50, # List
		'skin.droid': 50, # List
		'skin.quartz': 50, # List
		'skin.re-touched': 50, # List
	},
	'thumbnail': {
		'skin.confluence': 500, # Thumbnail
		'skin.aeon.nox': 500, # Wall
		'skin.droid': 51, # Big icons
		'skin.quartz': 51, # Big icons
		'skin.re-touched': 500, #Thumbnail
		'skin.confluence-vertical': 500,
		'skin.jx720': 52,
		'skin.pm3-hd': 53,
		'skin.rapier': 50,
		'skin.simplicity': 500,
		'skin.slik': 53,
		'skin.touched': 500,
		'skin.transparency': 53,
		'skin.xeebo': 55,
	},
}


# Sets the view mode if specified in addon properties
def set_view(view_mode, view_code=0):
	log("set_view view_mode='"+view_mode+"', view_code="+str(view_code))

	# Reads skin name
	skin_name = xbmc.getSkinDir()
	log("set_view skin_name='"+skin_name+"'")

	try:
		if view_code==0:
			log("set_view view mode is "+view_mode)
			view_codes = ALL_VIEW_CODES.get(view_mode)
			view_code = view_codes.get(skin_name)
			log("set_view view code for "+view_mode+" in "+skin_name+" is "+str(view_code))
			xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
		else:
			log("set_view view code forced to "+str(view_code))
			xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
	except:
		xbmc.log(addon_name + " | Unable to find view code for view mode "+str(view_mode)+" and skin "+skin_name)


# XBMC log with added addon identifier
def log(message):
	import default
	if default.extendedLog == True:
		xbmc.log("[" + addon_name + "] " + message)


# Retrieves full content of a given url
def getUrl(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	return content


# Convert parameters encoded in a URL to a dict.
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict


# Replaces HTML character entities with equivalent characters
def cleanText(text):
	text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
	text = text.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
	text = text.replace("\r", "").replace("\n", "")
	text = text.strip()
	return text


# Adds a link item in XBMC-Kodi
def addLink(name, url, mode, iconimage):
	#u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	u = sys.argv[0]+"?url="+urllib2.quote(url)+"&mode="+str(mode)
	item = True
	list_item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	list_item.setInfo(type="Video", infoLabels={"Title": name})
	list_item.setProperty('IsPlayable', 'true')
	item = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=list_item)
	return item


# Adds a directory item in XBMC-Kodi
def addDir(name, url, mode, iconimage):
	u = sys.argv[0]+"?url="+urllib2.quote(url)+"&mode="+str(mode)
	item = True
	list_item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	list_item.setInfo(type="Video", infoLabels={"Title": name})
	item = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=list_item, isFolder=True)
	return item


# Creates a playable XBMC-Kodi item and plays it
def play(url):
	import default
	# Create a playable item with a path to play.
	play_item = xbmcgui.ListItem(path=url)
	# Pass the item to the Kodi player.
	xbmcplugin.setResolvedUrl(default.pluginhandle, True, listitem=play_item)


# Convert from epoch to human readable date
def unix2humanTime(epoch):
	return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(epoch))


