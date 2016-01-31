#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import re
import sys
import xbmc
import xbmcplugin
import xbmcaddon
import socket

from resources.lib import tools, dailymotion


socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.video.formulae')
translation = settings.getLocalizedString
forceViewMode = settings.getSetting("forceViewMode") == "true"
viewMode = settings.getSetting("viewMode")
view = ["list", "thumbnail"]
viewMode = view[int(viewMode)]
extendedLog = settings.getSetting("extendedLog") == "true"


def index():
	live_streaming = getNextRace()

	tools.addLink(live_streaming, 'http://aos001feh-live.hls.adaptive.level3.net/formulae/live/wif/wif.m3u8', 'play', 'http://osp001feh-vod.hls.adaptive.level3.net/web/liveplayer/image.png')
	tools.addDir('[COLOR orange]'+translation(30001)+'[/COLOR]', 'http://www.fiaformulae.com/en/video.aspx', 'videos', '')
	tools.addDir('[COLOR orange]'+translation(30002)+'[/COLOR]', 'http://www.fiaformulae.com/en/video/archive/highlights.aspx', 'videos', '')
	tools.addDir('[COLOR blue]'+translation(30003)+'[/COLOR]', 'http://www.fiaformulae.com/en/live-streaming.aspx', 'extendedhighlights', '')
	tools.addDir(translation(30004), 'http://www.fiaformulae.com/en/video/archive/formula-e-onboard-videos.aspx', 'videos', '')
	tools.addDir(translation(30005), 'http://www.fiaformulae.com/en/video/archive/pre-season-testing.aspx', 'videos', '')
	tools.addDir(translation(30006), 'http://www.fiaformulae.com/en/video/archive/street-demos.aspx', 'videos', '')
	tools.addDir(translation(30007), 'http://www.fiaformulae.com/en/video/archive/insight.aspx', 'videos', '')
	xbmcplugin.endOfDirectory(pluginhandle)


def getNextRace():
	data = tools.getUrl('http://www.fiaformulae.com')
	matches = re.compile('<div id="startTime">(.*?)</div>.*?<div id="countdown">[^<]+<p>([^<]+)', re.DOTALL).findall(data)

	for date, location in matches:
		date = tools.cleanText(date)

	color = 'green' if date<3600 else 'red'
	
	days = int(date)/86400
	hours = (int(date)/3600) - (int(days)*24)
	
	return '[COLOR '+color+']'+translation(30000)+' ['+location+'] ('+str(days)+' '+translation(30008)+' & '+str(hours)+' '+translation(30009)+' '+translation(30010)+')[/COLOR]'


def listVideos(url, pattern):
	data = tools.getUrl(url)

	matches = re.compile(pattern, re.DOTALL).findall(data)

	for match in matches:
		tools.log("listVideos->match: "+str(match))
		
	for scrapedurl, scrapedthumbnail, scrapedtitle, scrapeddate in matches:
		scrapedtitle = tools.cleanText(scrapedtitle)
		scrapeddate = scrapeddate.replace('<span class="dateseparator">|</span>\r\n                            ', ' | ').strip()
		tools.addLink(scrapedtitle+" ["+scrapeddate+"]", scrapedurl, 'playVideo', scrapedthumbnail)

	xbmcplugin.endOfDirectory(pluginhandle)
	
	if forceViewMode:
		tools.set_view(viewMode)


def playVideo(url):
	xbmc.log("[Formula-e] url='%s')" % url)
	
	content = tools.getUrl(url)
	(video_id, video_source) = findVideo(content)
	
	if video_source == 'dailymotion':
		dailymotion.playDailyMotionVideo(video_id)
	elif video_source == 'youtube':
		tools.play('plugin://plugin.video.youtube/play/?video_id='+video_id)
	elif video_source == 'vod':
		tools.play(video_id)
	else:
		print '[Formula-e] No playable video found'
		xbmc.executebuiltin('XBMC.Notification(Info:, "No playable video found", 5000)')


def findVideo(content):
	pattern = 'dailymotion.com/embed/video/([^"]+)'
	matches = re.compile(pattern,re.DOTALL).findall(content)
	
	for match in matches:
		xbmc.log("[Formula-e] DailyMotion video id="+match)
		video_source = 'dailymotion'

	pattern	 = 'youtube.com/embed/([0-9A-Za-z_-]{11})'
	matches = re.compile(pattern,re.DOTALL).findall(content)

	for match in matches:
		xbmc.log("[Formula-e] Youtube video id="+match)
		video_source = 'youtube'

	pattern = "file: '([^']+)"
	matches = re.compile(pattern,re.DOTALL).findall(content)
	
	for match  in matches:
		xbmc.log("[Formula-e] VOD video url="+match)
		video_source = 'vod'

	return (match, video_source)


params = tools.parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if isinstance(url, type(str())):
	url = urllib.unquote_plus(url)

if mode == 'listVideos':
	listVideos(url,'')
elif mode == 'playVideo':
	playVideo(url)
elif mode == 'play':
	tools.play(url)
elif mode == 'videos':
	listVideos(url, '<div class="item1 video[^"]*">[^<]+<div class="container">[^<]+<a href="([^"]+)"[^<]+<img src="([^"]+)" alt="([^"]+)".*?<p class="dtc">(.*?)</p>')
	#listVideos(url, '<div class="item1 video[^"]*">[^<]+<div class="container">[^<]+<a href="([^"]+)"[^<]+<img src="([^"]+)" alt="([^"]+)".*?<p class="dtc">\s*([^<]*)[<span class="dateseparator">|</span>\s]*(\d{2}\s[a-zA-Z]{3}\s\d{2})*')
elif mode == 'extendedhighlights':
	listVideos(url, '<div class="item1 vod[^"]*">[^<]+<div class="container">[^<]+<a href="([^"]+)"[^<]+<img src="([^"]+)" alt="([^"]+)".*?<div class="play">(.*?)</div>')
else:
	index()
