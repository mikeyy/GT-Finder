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

import requests
from requests import Session
from requests import Request
from requests import exceptions
from requests import codes

__author__ = 'Michael Mooney'
__license__ = 'GNU General Public License Version 2' # 'Prohibited/Intellectual Property'


class HttpClient(object):

    def __init__(self, proxy=None, headers={}, connect_timeout=5.0):
        self.connect_timeout = connect_timeout
        self.session = Session()

        self.proxy = proxy
        if proxy is not None:
            self.proxies = {'http': 'http://%s'% proxy,
                            'https': 'https://%s'% proxy}
        else:
            self.proxies = None
            
        self.headers = {'Accept-Encoding': 'gzip, deflate'}
        self.headers.update(headers)

    def get(self, url, fields={}, headers={}, timeout=None, stream=False):
        return self.send(url, 
        method='GET',
        params=fields,
        headers=headers,
        timeout=timeout
        )
    
    def post(self, url, fields={}, files={}, headers={}, timeout=None):
        return self.send(url, 
        method='POST',
        data=fields,
        files=files,
        headers=headers,
        timeout=timeout
        )

    def send(self, url, method='GET', params={}, data={}, files={}, headers={}, timeout=None):
        headers.update(self.headers)
        prepped = Request(method,
            url,
            params=params,
            data=data,
            files=files,
            headers=headers).prepare()

        try:
            resp = self.session.send(prepped,
                proxies=self.proxies,
                timeout=(self.connect_timeout, timeout),
                )
        except exceptions.Timeout, e:
            raise exceptions.Timeout(e)
        except exceptions.TooManyRedirects:
            raise exceptions.TooManyRedirects(e)
        except exceptions.ConnectionError, e:
            raise exceptions.ConnectionError(e)
        except exceptions.HTTPError, e:
            raise exceptions.HTTPError(e)
        except exceptions.RequestException, e:
            raise exceptions.RequestException(e)
        except Exception, e:
            raise Exception(e)
        else:
            resp.raw.decode_content = True
            if resp.status_code == codes.ok:
                return resp.content
            else:
                raise Exception('bad status code: %s'% resp.status_code)
                
    def close(self):
        self.session.close()
