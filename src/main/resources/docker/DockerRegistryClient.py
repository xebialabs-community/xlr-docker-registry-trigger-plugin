#
# Copyright 2020 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import math
import sys
import urllib
import com.xhaus.jyson.JysonCodec as json
from docker.HttpRequest import HttpRequest
from distutils.version import LooseVersion

SUCCESS_RESULT_STATUS   = 200
RECORD_CREATED_STATUS  = 201

class DockerRegistryClient(object):
    def __init__(self, httpConnection, verify=True, username=None, password=None):
        self.headers        = {}
        self.query_params   = ""
        self.httpConnection = httpConnection
        if username is not None:
           self.httpConnection['username'] = username
        if password is not None:
           self.httpConnection['password'] = password
        self.httpRequest = HttpRequest(self.httpConnection, username, password, verify)

    @staticmethod
    def create_client(httpConnection, verify=True, username=None, password=None):
        return DockerRegistryClient(httpConnection, verify, username, password)

    def get_repositories(self):
        api_url = '/_catalog/'
        response = self.httpRequest.get(api_url, contentType='application/json', headers = self.headers)
        if response.getStatus() == SUCCESS_RESULT_STATUS:
            return json.loads(response.getResponse())['repositories']
        else:
            print("get_repositories error %s" % (response))
            self.throw_error(response)

    def get_tags(self, repository):
        api_url = '/%s/tags/list' % (repository)
        response = self.httpRequest.get(api_url, contentType='application/json', headers = self.headers)
        if response.getStatus() == SUCCESS_RESULT_STATUS:
            return json.loads(response.getResponse())['tags']
        else:
            print("get_tags error %s" % (response))
            self.throw_error(response)

    def get_plot_data(self, repositories_scope):
        def increment_color(color_rgb_ind):
            return [40*math.sin(2*math.pi*color_rgb_ind/17)+40, 70*math.sin(2*math.pi*color_rgb_ind/43)+70, 70*math.sin(2*math.pi*color_rgb_ind/73)+70]

        plot_data = []
        color_rgb_ind = 42
        repositories = self.get_repositories()
        repositories_scope = list(repositories_scope)
        if len(repositories_scope) > 0:
            repositories = [repository for repository in repositories if repository in repositories_scope]
        for i in range(len(repositories)):
            color_rgb_ind += 1
            color_rgb = increment_color(color_rgb_ind)
            plot_data.append(
                {
                    "name": repositories[i],
                    "itemStyle": {
                        "color": "rgb({},{},{})".format(color_rgb[0], color_rgb[1], color_rgb[2])
                    }
                }
            )
            tags = self.get_tags(repositories[i])
            plot_data[-1]["children"] = []
            if len(tags) == 0:
                plot_data[-1]["value"] = 1
            for j in range(len(tags)):
                color_rgb_ind += 1
                color_rgb = increment_color(color_rgb_ind)
                plot_data[-1]["children"].append(
                    {
                        "name": tags[j],
                        "value": 1,
                        "itemStyle": {
                            "color": "rgb({},{},{})".format(color_rgb[0], color_rgb[1], color_rgb[2])
                        }
                    }
                )
        return plot_data

    def get_latest_version(self, image_name):
        api_url = '/%s/tags/list' % (image_name)
        response = self.httpRequest.get(api_url, contentType='application/json', headers = self.headers)

        if response.getStatus() == SUCCESS_RESULT_STATUS:
            versions_list = json.loads(response.getResponse())['tags']
            #print("Versions founds: %s" % str(versions_list))

            # the will always be a 'latest' but that's not helpful to us to see if there's a new version 
            if "latest" in versions_list:
                versions_list.remove("latest")
            # End if

            try:
                versions_list.sort(key=LooseVersion)
                #print("Tags sorted %s" % str(versions_list))
            except Exception, e:
                print("Failed to sort, ignoring: %s " % str(e))
            # End try

            if len(versions_list) > 0:
                return versions_list[-1]
            else:
                return None
        else:
            print("get_latest_version error %s" % (response))
            self.throw_error(response)
        # End if
    # End get_latest_version

    def throw_error(self, response):
        print("Error from DockerRegistry, HTTP Return: %s\n" % (response.getStatus()))
        print("Detailed error: %s\n" % response.response)
        sys.exit(response.response)


