#!/usr/bin/python
#
# This file is part of GT Finder.
#
# Copyright(c) 2016 Michael Mooney(mikeyy@mikeyy.com).
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import gevent
import gevent.queue
from gevent.pool import Pool

import random
import time
import sys
import re
import os
import lib.httpclient as http

from contextlib import closing
from re import findall

__author__ = 'Michael Mooney'
__license__ = 'GNU General Public License Version 2' #'Prohibited/Intellectual Property'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ClientManager(object):

    proxy_pattern = r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[:][0-9]{1,6})'
    url_pattern = r'^((https?):((//)|(\\\\))+([\w\d:#@%/;$( )~_?\+-=\\\.&](#!)?)*)'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.debug = kwargs.get('debug')
        self.threads = kwargs.get('threads')
        self.http_timeout = kwargs.get('http_timeout')
        self.used_timeout = kwargs.get('used_timeout')
        self.proxies_enabled = kwargs.get('proxies_enabled')
        self.proxies_src = kwargs.get('proxies_src')
        self.reload_time = kwargs.get('reload_time')
        self.timeout = kwargs.get('timeout')
        self.wordlist_file = kwargs.get('wordlist_file')
        self.output_file = kwargs.get('output_file')
        self.proxies_temp = []
        self.proxies_used = []
        with open(resource_path('assets\\http\\useragents.txt'), 'r') as f:
            self.useragents = f.read().split("\n")
        with open(resource_path('assets\\http\\languages.txt'), 'r') as f:
            self.languages = f.read().split("\n")
        print 'Loading gamertags'
        self.gamertags = gevent.queue.Queue()
        with open(resource_path('assets\\cache.txt'), 'r') as f:
            cache = f.read().split("\n")
        with open(self._clean(self.wordlist_file), 'r') as f:
            wordlist = f.read().split("\n")
        map(self.gamertags.put, [g for g in wordlist if g not in cache and len(g) <= 15])
        self._id = self.gamertags.qsize()
        print 'Loaded %d gamertags'% self._id

    def spawn_connect(self):
        gamertag = self.gamertags.get()
        proxy, headers = self._new_session()
        
        while 1:
            status = self.check(gamertag, proxy, headers)

            if status:
                self._save_gamertag(gamertag, status)
                self._used(proxy, self.used_timeout)
                gamertag = self.gamertags.get()

            proxy, headers = self._new_session()
            
    def check(self, gamertag, proxy, headers):
        connector = http.HttpClient(proxy, headers)
        # Not affiliated with Checkgamertag.com
        remote_url = 'http://checkgamertag.com/CheckGamertag.php'
        fields = {'tag': gamertag, 't': random.random()}
        try:
            resp = connector.post(remote_url, fields=fields, timeout=self.http_timeout)
        except:
            return
        else:
            if resp:
                if resp == "taken" or resp == "available":
                    if resp == "taken":
                        return 200
                    else:
                        return 404
        return

    def _new_session(self):
        return [self._get_proxy(), self._new_headers()]
                     
    def _new_headers(self):
        return {'User-Agent': random.choice(self.useragents), 'Accept-Language': random.choice(self.languages)}
        
    def _clean(self, string_):
        return os.path.abspath(string_)
            
    def _save_gamertag(self, gamertag, status):
        self._id = self._id - 1
        if status == 404:
            print '%s %s %s'% (self._id, gamertag, '(*available)')
            with open(self._clean(self.output_file), 'a') as f:
                s = "%s\n"% gamertag
                f.write(s)
        
        if status == 200:
            print '%s %s %s'% (self._id, gamertag, '(taken)')
        with open(resource_path('assets\\cache.txt'), 'a') as f:
            s = "%s\n"% gamertag
            f.write(s)

    def _get_proxy(self):
        if not self.proxies_enabled:
            return None
        used = [lst[0] for lst in self.proxies_used]
        while not list(set(self.proxies_temp)-set(used)):
            gevent.sleep(0.1)
        fresh = list(set(self.proxies_temp)-set(used))
        proxy = random.choice(fresh)
        self._used(proxy, 0)
        return proxy

    def _used(self, proxy, length = 90):
        if length == 0:
            if [proxy, 0] in self.proxies_used:
                return
            t = 0
        else:
            t = time.time() + length + random.random()
            if [proxy, 0] in self.proxies_used:
                self.proxies_used.remove([proxy, 0])
        self.proxies_used.append([proxy, t])

    def _fresh_proxies_core(self):
        while 1:
            if self.proxies_used:
                [self.proxies_used.remove([p, t]) for p, t in list(self.proxies_used) if t != 0 and t <= time.time()]
            gevent.sleep(1)

    def _load_proxies_core(self, length):
        gevent.sleep(length)
        self._load_proxies(length)

    def _load_proxies(self, length):
        print 'Loading proxies...'

        proxies = []
        if 'http://' in proxies_src:
            resp = False
            connector = http.HttpClient()
            while not resp:
                try:
                    resp = connector.get(proxies_src, timeout=self.http_timeout)
                    proxies += re.compile(self.proxy_pattern).findall(resp)
                except:
                    pass

                gevent.sleep(3)
        else:
            with open(proxies_src) as f:
                proxies = re.compile(self.proxy_pattern).findall(f.read())
        
        if proxies:
            self.proxies_used[:] = [[p,t] for p, t in self.proxies_used if p in proxies and (t >= time.time() or t == 0)]
            used = [p for p, t in self.proxies_used]
            self.proxies_temp[:] = set(proxies) - set(used)
        print 'Proxies Loaded'

        gevent.spawn(self._load_proxies_core, length)
