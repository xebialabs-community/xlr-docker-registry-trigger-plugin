#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys, string, time, traceback
import com.xhaus.jyson.JysonCodec as json
from docker.DockerRegistryClient import DockerRegistryClient
import __builtin__

logger = getattr(__builtin__, 'logger', None)

if server is None:
    logger.error("No server provided.")
    sys.exit(1)

if imageName is None:
    logger.error("No imageName provided.")
    sys.exit(1)

client = DockerRegistryClient.create_client(server, username, password)

try:
    latest_version = client.get_latest_version( imageName )

    triggerState = latest_version
    imageVersion = triggerState

    logger.info("Setting triggerState/imageVersion %s" % triggerState)

except Exception, e:
    exc_info = sys.exc_info()
    traceback.print_exception( *exc_info )
    logger.error(e)
    logger.error("Failed to find docker image in Registry")
    sys.exit(1)
