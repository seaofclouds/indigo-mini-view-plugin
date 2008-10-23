####################
# Copyright (c) 2007, Perceptive Automation, LLC. All rights reserved.
# http://www.perceptiveautomation.com
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
####################

####################
## IMPORTS
import cherrypy
from cherrypy import _cperror

from indigopy import indigoconn as ic
from indigopy import indigodb as idb
from indigopy.basereqhandler import BaseRequestHandler, kTrueStr, kFalseStr, kEmptyStr, kTextPageStr, kHtmlPageStr, kXmlPageStr

####################
## CONSTANTS

####################
# Optional hooks to provide a plugin name and description (shown in Event Log and plugin index)
def PluginName():
	return u"SeaOfClouds Plugin"

def ShowOnControlPageList():
	return True		# if True, then above name/description is shown on the Control Page list index

# Optional hook called when the IndigoWebServer first connects to IndigoServer
def IndigoConnected():
	pass

# Optional hook called when the IndigoWebServer disconnect from IndigoServer
def IndigoDisconnected():
	pass

####################
# The functions in this class are automatically called based on the URL
# requested. This provides a mechanism for easily serving dynamic content.
#
# The URL path is based on the folder path of the plugin. For example,
# this plugin folder name is "sample" so any URL path containing "sample"
# as the first path identifier will call into these functions.
#
# The class name can be called whatever you want, but it must subclass
# from BaseRequestHandler to be loaded by the webserver plugin manager.
class ExampleRequestHandler(BaseRequestHandler):
	""" Handles HTTP page requests. """

	def __init__(self, logFunc, debugLogFunc):
		BaseRequestHandler.__init__(self, logFunc, debugLogFunc)

	def index(self):
		tmpl = self._GetAndLockPluginTemplate('m/templates/main.html')
		try:
			tmpl.iphone = self._IsiPhone()
			tmpl.devList = cherrypy.server.indigoDb.GetDevices(cherrypy.server.indigoConn, True)
			return tmpl.RenderTemplate()
		finally:
			tmpl.ReleaseLock();
	index.exposed = True		# exposed = True must be set for handler func to be called

	def turnon(self, device):
		self._ForceHeadersToNeverCache()

                pageType = kHtmlPageStr
		try:
			cherrypy.server.indigoDb.DeviceTurnOn(cherrypy.server.indigoConn, device, cherrypy.request.remote.ip)
		except (ic.ConnError, ic.InternalError, ic.ServerError), err:
			return self._ReturnError(pageType, err.value)
		except idb.ControlDisabled:
			return self._ReturnControlDisabled(pageType)
		serverStatus = u'turning on "'
		serverStatus += device
		serverStatus += u'"'
		return self.returnResult(serverStatus)
	turnon.exposed = True

        def turnoff(self, device):
                self._ForceHeadersToNeverCache()

                pageType = kHtmlPageStr
                try:
                        cherrypy.server.indigoDb.DeviceTurnOff(cherrypy.server.indigoConn, device, cherrypy.request.remote.ip)
                except (ic.ConnError, ic.InternalError, ic.ServerError), err:
                        return self._ReturnError(pageType, err.value)
                except idb.ControlDisabled:
                        return self._ReturnControlDisabled(pageType)
                serverStatus = u'turning off "'
                serverStatus += device
                serverStatus += u'"'
                return self.returnResult(serverStatus)
        turnoff.exposed = True

        def setbrightness(self, device, level):
                self._ForceHeadersToNeverCache()

                pageType = kHtmlPageStr
                try:
                        cherrypy.server.indigoDb.DeviceSetBrightness(cherrypy.server.indigoConn, device, level, cherrypy.request.remote.ip)
                except (ic.ConnError, ic.InternalError, ic.ServerError), err:
                        return self._ReturnError(pageType, err.value)
                except idb.ControlDisabled:
                        return self._ReturnControlDisabled(pageType)
                serverStatus = u'setting brightness of "'
                serverStatus += device
                serverStatus += u'" to '
                serverStatus += level
                serverStatus += u'%'
                return self.returnResult(serverStatus)
        setbrightness.exposed = True

        def returnResult(self, serverStatus):
		cherrypy.response.headers['Content-Type'] = 'text/html'
                tmpl = self._GetAndLockPluginTemplate('m/templates/reload.html')
                try:
                	tmpl.iphone = self._IsiPhone()
                        tmpl.serverStatus = serverStatus
                        return tmpl.RenderTemplate()
                finally:
                        tmpl.ReleaseLock();
	returnResult.exposed = True

	####################
	# The following folders inside the plugin folder will automatically be
	# available to serve static content (HTML pages, images, CSS, JS, etc.):
	#
	#		http://127.0.0.1/sample/css
	#		http://127.0.0.1/sample/js
	#		http://127.0.0.1/sample/images
	#		http://127.0.0.1/sample/video
	#		http://127.0.0.1/sample/static
	#
	# You do *not* need to define any type of request handler function to
	# have content served from these folders. In fact, if you only want
	# to server static content, then you do not need this python module
	# file (requesthandler.py) at all.
	#
	# Example:
	#		http://127.0.0.1/sample/static/static_example.html
