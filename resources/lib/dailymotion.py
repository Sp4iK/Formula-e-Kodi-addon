#!/usr/bin/python
# -*- coding: utf-8 -*-

# -- Basic DailyMotion video manager -- #
# Code extracted from Dailymotion addon #
# ----- Thanks to AddonScriptorDE ----- #

import xbmcplugin
import xbmcgui
import urllib
import requests
import json
import tools

def playDailyMotionVideo(videoid):
	import default

	tools.log("playDailyMotionVideo->id="+videoid)

	dm_url = getStreamUrl(videoid)
	tools.log("playDailyMotionVideo->url: "+dm_url)

	if dm_url and not '.f4mTester' in dm_url:
		listitem = xbmcgui.ListItem(path=dm_url)
		xbmcplugin.setResolvedUrl(default.pluginhandle, True, listitem)
	elif dm_url:
		xbmc.executebuiltin('XBMC.RunPlugin('+dm_url+')')
	else:
		tools.log('playDailyMotionVideo->No playable url found')


def getStreamUrl(id,live=False):
	headers = {'User-Agent':'Android'}
	cookie = {'Cookie':"lang=en_EN; family_filter=off"}
	r = requests.get("http://www.dailymotion.com/player/metadata/video/"+id,headers=headers,cookies=cookie)
	content = r.json()
	
	if content.get('error') is not None:
		Error = 'DailyMotion Says:[COLOR yellow]%s[/COLOR]' %(content['error']['title'])
		xbmc.executebuiltin('XBMC.Notification(Info:,'+ Error +' ,5000)')
		return
	else:
		cc = content['qualities']  #['380'][0]['url']
		   
		m_url = ''
		other_playable_url = []
		
		for source, auto in cc.items():
			tools.log("getStreamUrl->source: "+source)
			tools.log("getStreamUrl->auto: "+str(auto))
			
			for m3u8 in auto:
				m_url = m3u8.get('url',None)
				
				if m_url:
					if not live:
						if	source == '1080':
							return m_url		
						elif source == '720': #720 found no more iteration need
							return m_url
						elif source == '480': #send cookie for mp4
							return m_url+'|Cookie='+r.headers['set-cookie']
						elif source == '380': #720 found no more iteration need
							return m_url+'|Cookie='+r.headers['set-cookie']
						elif source == '240': #720 found no more iteration need
							return m_url+'|Cookie='+r.headers['set-cookie']
						elif '.mnft' in m_url:
							continue
					else:
						if '.m3u8?auth' in m_url:
							m_url = m_url.split('?auth=')
							the_url = m_url[0]+'?redirect=0&auth='+urllib.quote(m_url[1])
							rr = requests.get(the_url,cookies=r.cookies.get_dict() ,headers=headers)
							if rr.headers.get('set-cookie'):
								tools.log('getStreamUrl->adding cookie to url')
								return rr.text.split('#cell')[0]+'|Cookie='+rr.headers['set-cookie']
							else:
								return rr.text.split('#cell')[0]
					other_playable_url.append(m_url)
					
		if len(other_playable_url)>0: # probable not needed only for last resort
			for m_url in other_playable_url:
				if '.m3u8?auth' in m_url:
					sep_url = m_url.split('?auth=')
					the_url = sep_url[0]+'?redirect=0&auth='+urllib.quote(sep_url[1])
					rr = requests.get(the_url,cookies=r.cookies.get_dict() ,headers=headers)
					if rr.headers.get('set-cookie'):
						tools.log('getStreamUrl->adding cookie to url')
						return rr.text.split('#cell')[0]+'|Cookie='+rr.headers['set-cookie']
					else:
						return rr.text.split('#cell')[0]


