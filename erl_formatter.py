# ==========================================================================================================
# Erl - A Sublime Text 3 Plugin for Erlang Integrated Testing & Code Completion
#
# Copyright (C) 2013, Roberto Ostinelli <roberto@ostinelli.net>.
# All rights reserved.
#
# BSD License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this list of conditions and the
#        following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors may be used to endorse or promote
#        products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ==========================================================================================================


# imports
import sublime, sublime_plugin, os, tempfile
import Erl.erl_core as GLOBALS
from .erl_core import ErlTextCommand, ErlProjectLoader


# main autoformat
class ErlAutoFormat():

	def __init__(self, view, edit):
		self.view = view
		self.edit = edit

	def format(self):
		# save current caret position
		current_region = self.view.sel()[0]
		# save current file contents to temp file
		region_full = sublime.Region(0, self.view.size())
		content = self.view.substr(region_full).encode('utf-8')
		temp = tempfile.NamedTemporaryFile(delete=False)
		temp.write(content)
		temp.close()
		# call erlang formatter
		os.chdir(GLOBALS.ERL.support_path)
		escript_command = "erl_formatter.erl %s %s" % (GLOBALS.ERL.shellquote(temp.name), GLOBALS.ERL.shellquote(temp.name))
		
		#print('%s %s' % (GLOBALS.ERL.escript_path, escript_command))

		retcode, data = GLOBALS.ERL.execute_os_command('%s %s' % (GLOBALS.ERL.escript_path, escript_command))

		# delete temp file
		if retcode == 0:
			with open(temp.name, 'rb') as file:
				data = file.read()
			# substitute text
			self.view.replace(self.edit, region_full, data.decode('utf-8'))
			# reset caret to original position
			self.view.sel().clear()
			self.view.sel().add(current_region)
			self.view.show(current_region)

		os.remove(temp.name)

# format command
class ErlAutoFormatCommand(ErlTextCommand):
	def run_command(self, edit):
		formatter = ErlAutoFormat(self.view, edit)
		formatter.format()

class ErlFormatOnSave(sublime_plugin.EventListener):

  def on_pre_save(self, view):

    if view.file_name().lower().endswith("erl") or view.file_name().lower().endswith("hrl"):
      view.run_command('erl_auto_format')
