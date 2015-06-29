#
# Copyright 2015 Rackspace, Inc
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import appdirs
import dogpile.cache


AUTHOR = 'openstack'
PROGNAME = 'python-ironicclient'

CACHE_DIR = appdirs.user_cache_dir(PROGNAME, AUTHOR)
CACHE_FILENAME = os.path.join(CACHE_DIR, 'ironic-api-version.dbm')
CACHE = None
DEFAULT_EXPIRY = 300  # seconds


def _get_cache():
    """Configure file caching."""
    global CACHE
    if CACHE is None:

        # Ensure cache directory present
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        CACHE = dogpile.cache.make_region().configure(
            'dogpile.cache.dbm',
            expiration_time=DEFAULT_EXPIRY,
            arguments={
                "filename": CACHE_FILENAME,
            }
        )
    return CACHE


def _build_key(host, port):
    """Build a key based upon the hostname or address supplied."""
    return "%s:%s" % (host, port)


def save_data(host, port, data):
    """Save 'data' for a particular 'host' in the appropriate cache dir.

    param host: The host that we need to save data for
    param port: The port on the host that we need to save data for
    param data: The data we want saved
    """
    key = _build_key(host, port)
    _get_cache().set(key, data)


def retrieve_data(host, port, expiry=None):
    """Retrieve the version stored for an ironic 'host', if it's not stale.

    Check to see if there is valid cached data for the host/port
    combination and return that if it isn't stale.

    param host: The host that we need to retrieve data for
    param port: The port on the host that we need to retrieve data for
    param expiry: The age in seconds before cached data is deemed invalid
    """
    # Ensure that a cache file exists first
    if not os.path.isfile(CACHE_FILENAME):
        return None

    key = _build_key(host, port)
    data = _get_cache().get(key, expiration_time=expiry)

    if data == dogpile.cache.api.NO_VALUE:
        return None
    return data
