#!/usr/bin/python
# -*- coding:utf8 -*-
"""
Copyright (C) 2011 by lwp
levin108@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the
Free Software Foundation, Inc.,
51 Franklin Street, Suite 500, Boston, MA 02110-1335, USA.
"""

import oauth
import Image
import types
import os, time, urllib2, urllib
from xml.dom import minidom

CONSUMER_KEY = 'V3r08E6kXGWFKDM72yl66g'
CONSUMER_SECRET = 's3R6uQuadL91TulXwvUW2773hgePfQ2zHOmCNKuOjU'

RESOURCE_URL = 'http://api.twitter.com/1/%s.json'

class tpOAuth(oauth.OAuthClient):
    
    def __init__(self, http_proxy = None):
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.http_proxy = http_proxy
        self.access_token = None

    def _set_http_proxy(self, proxy_type = 'http'):
        try:
            if self.http_proxy is None:
                null_handler = urllib2.ProxyHandler({})
                opener = urllib2.build_opener(null_handler, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                return
            proxy = 'http://' + self.http_proxy['host'] + ':' + self.http_proxy['port']
            proxy_support = urllib2.ProxyHandler({proxy_type: proxy})
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        except:
            null_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(null_handler, urllib2.HTTPHandler)
        finally:
            urllib2.install_opener(opener)

    def make_oauth_request(self, http_method = 'GET', http_url = {}, has_param = False, parameters = None, token = None):

        param = {
        'oauth_version': '1.0',
        'oauth_timestamp': int(time.time()),
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_consumer_key': self.consumer.key
        }
        
        if(parameters):
            param.update(parameters)

        if(token):
            param.update({ 'oauth_token': token.key })

        oauth_request = oauth.OAuthRequest(http_method = http_method, http_url = http_url, parameters = param)
        oauth_request.sign_request(self.signature_method, self.consumer, token)

        oauth_header = oauth_request.to_header()

        if http_method == 'POST':
            postdata = oauth_request.to_postdata()
            req = urllib2.Request(http_url, postdata, oauth_header)
        else:
            if has_param:
                url = oauth_request.to_url()
                req = urllib2.Request(url)
            else:
                url = http_url
                req = urllib2.Request(url, None, oauth_header)
        
        try:
            req = urllib2.urlopen(req)
            return req.read()
        except urllib2.URLError as e:
            return e
        except urllib2.HTTPError as e:
            return e

    def fetch_url_result(self, http_method = 'GET', http_path = {}, options = None):

        self._set_http_proxy('http')
        http_url = RESOURCE_URL % http_path
        try:
            return self.make_oauth_request(http_method = http_method, \
                    http_url = http_url, \
                    has_param = True, \
                    parameters = options, \
                    token = self.access_token)
        except:
            return None

    def fetch_user_timeline(self, screen_name = {}, tweets_max_id = {}, tweets_min_id = {}, page = None, include_rts = {}):
        
        options = {
        'screen_name': screen_name,        
        'count': 10,
        'trim_user': 'true',
        'include_entities': 'true',
        'include_rts': 'false'
        }

        options['include_rts'] = 'true' if include_rts else 'false'

        if tweets_max_id != 0:
            options['max_id'] = tweets_max_id

        if tweets_min_id != 0:
            options['since_id'] = tweets_min_id

        if page:
            options['page'] = page

        return self.fetch_url_result(http_path = 'statuses/user_timeline', options = options)
