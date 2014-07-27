__author__ = 'Rudy'

import time
import os
import tempfile
import zlib
import pickle as cPickle
import hashlib

from os.path import join, exists

class MyCacheHandler(object):
    # Note: this is an example handler to demonstrate how to use them.
    # a -real- handler should probably be thread-safe and handle errors
    # properly (and perhaps use a better hashing scheme).

    def __init__(self, debug=False):
        self.debug = debug
        self.count = 0
        self.cache = {}
        self.tempdir = join(tempfile.gettempdir(), "eveapi")
        if not exists(self.tempdir):
            os.makedirs(self.tempdir)

    def log(self, what):
        if self.debug:
            print("[%d] %s" % (self.count, what))

    def getCacheKey(self, host, path, params):
        return ('-'.join([host, path, ':'.join(['%s.%s' for k, v in params.items()])])).encode()

    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        cacheKeyStr = self.getCacheKey(host, path, params)
        key = cacheKeyStr

        self.count += 1  # for logging

        # see if we have the requested page cached...
        cached = self.cache.get(key, None)
        if cached:
            cacheFile = None
            #print "'%s': retrieving from memory" % path
        else:
            # it wasn't cached in memory, but it might be on disk.
            cacheFile = join(self.tempdir, hashlib.sha1(key).hexdigest() + ".cache")
            if exists(cacheFile):
                self.log("%s: retrieving from disk" % path)
                f = open(cacheFile, "rb")
                cached = self.cache[key] = cPickle.loads(zlib.decompress(f.read()))
                f.close()

        if cached:
            # check if the cached doc is fresh enough
            if time.time() < cached[0]:
                self.log("%s: returning cached document" % path)
                return cached[1]  # return the cached XML doc

            # it's stale. purge it.
            self.log("%s: cache expired, purging!" % path)
            del self.cache[key]
            # if cacheFile:
            #     os.remove(cacheFile)

        self.log("%s: not cached, fetching from server..." % path)
        # we didn't get a cache hit so return None to indicate that the data
        # should be requested from the server.
        return None

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item

        cacheKeyStr = self.getCacheKey(host, path, params)

        key = cacheKeyStr

        cachedFor = obj.cachedUntil - obj.currentTime
        if cachedFor:


            cachedUntil = time.time() + cachedFor

            # store in memory
            cached = self.cache[key] = (cachedUntil, doc)

            # store in cache folder
            cacheFile = join(self.tempdir, hashlib.sha1(key).hexdigest() + ".cache")
            f = open(cacheFile, "wb")
            f.write(zlib.compress(cPickle.dumps(cached, -1)))
            f.close()

            self.log("URL %s cached for %d seconds under %s" % (path, cachedFor, cacheFile))
