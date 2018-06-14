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

import gevent.monkey
gevent.monkey.patch_all()

import gevent
import argparse
import sys
from gevent.pool import Pool

import lib.manager as m

__author__ = 'Michael Mooney'
__license__ = 'GNU General Public License Version 2' #'Prohibited/Intellectual Property'


parser = argparse.ArgumentParser(description="Example: main.exe -w freebies.txt -o freebies.good.txt -p 1 -s proxies.txt")

parser.add_argument('-w', action='store', dest='wordlist_file',
                    help='Set wordlist to scan (example.txt)')

parser.add_argument('-o', action='store', dest='output_file',
                    help='Set location to output gamertags (example.txt)')

parser.add_argument('-t', action='store', default=10,
                    dest='threads',
                    help='Set amount of threads to use')

parser.add_argument('-T', action='store', default=10.0,
                    dest='http_timeout',
                    help='Set http read timeout in seconds')

parser.add_argument('-u', action='store', default=30.0,
                    dest='used_timeout',
                    help='Set in seconds when proxies rejoin active pool')

parser.add_argument('-s', action='store', dest='proxies_src',
                    help='Set location of your proxies list (from URL or file)')

parser.add_argument('-r', action='store', default=10.0,
                    dest='reload_time',
                    help='Set time in minutes when to reload proxies list')

parser.add_argument('-p', action='store', default=0,
                    dest='proxies_enabled',
                    help='Set 1 if proxies are enabled, 0 if not')

parser.add_argument('--version', action='version', version='GT Finder - 1.2 (exe)')

results = parser.parse_args()

if not results.wordlist_file:
    print 'Please supply a value to -w. Type -h for help.'
    sys.exit(0)
if not results.output_file:
    print 'Please supply a value to -o. Type -h for help.'
    sys.exit(0)
if results.proxies_enabled:
    if not results.proxies_src:
        print 'Please supply a value to -s. Type -h for help.'
        sys.exit(0)

manager = m.ClientManager(wordlist_file=results.wordlist_file,
    output_file=results.output_file,
    connect_threads=results.threads,
    http_timeout=results.http_timeout,
    used_timeout = results.used_timeout,
    proxies_enabled = results.proxies_enabled,
    reload_time = results.reload_time,
    proxies_src = results.proxies_src
)

def _init_manager():
    if results.proxies_enabled:
        manager._load_proxies(manager.reload_time*60)
        gevent.spawn(manager._fresh_proxies_core)

def main():
    pool = Pool(results.threads)
    while 1:
        try:
            if manager.gamertags.empty():
                print 'Finished'
                break
            for i in xrange(min(pool.free_count(), 50)):
                pool.spawn(manager.spawn_connect)
            gevent.sleep(1)
        except KeyboardInterrupt:
            print '[KYBRD_NTRPT] Finishing active threads'
            pool.join()
            break

if __name__ == '__main__':
    _init_manager()
    while manager.gamertags.empty():
        gevent.sleep(1)
    main()
