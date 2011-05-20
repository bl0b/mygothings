#!/usr/local/bin/python

# sgfsummary.py (SGF Summarizer)
# Copyright (C) 1999-2000  David John Goodger (dgoodger@bigfoot.com)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# The license is currently available on the Internet at:
#     http://www.gnu.org/copyleft/gpl.html

"""
===============================
 SGF Summarizer: sgfsummary.py
===============================
version 1.0 (2000-03-27)

Homepage: [[http://gotools.sourceforge.net]]

Copyright (C) 1999-2000 David John Goodger ([[mailto:dgoodger@bigfoot.com]];
davidg on NNGS, IGS, goclub.org). sgfsummary.py comes with ABSOLUTELY NO
WARRANTY. This is free software, and you are welcome to redistribute it and/or
modify it under the terms of the GNU General Public License; see the source code
for details.

Description
===========
This program reads multiple SGF (Smart Game Format) files, specifically those
recording Go/WeiQi/Baduk games, and summarizes their game information to
standard output. The output is a tab-delimited table with one line (record) for
each input SGF file. The first line of the output contains the column headers
(field names). The output is suitable for importing into a spreadsheet or
database package for storage and manipulation.

The output consists of the following fields::
    Date & Time*    Result          Black           B Rank    
    White           W Rank          Komi            Handicap
    Board Size      Time            Filename        Game Name
    Place           Event

* The Time information is extracted from a standard IGS filename of the form
"white-black-DD-hh-mm" or NNGS filename of the form "winner-loser-YYYYMMDDhhmm",
where "hh" and "mm" give the time when the game was played. If the filename is
not in this format, no time information will be produced.

Usage
=====
::
    sgfsummary.py [-c] source_dir_path

Arguments:
- '-c' -- Enables SGF collections. This slows down processing considerably.
- 'source_dir_path' -- The path to the directory containing the SGF files to
  summarize. Please note that there should be no non-SGF files in this 
  directory; if there are, the output may contain garbage.

Under MacOS, the user will be interactively prompted for the source folder,
whether to enable SGF collections, and to specify a save file."""


# Revision History:
#
# 1.0 (2000-03-27): First public release.
# - Moved parsing to sgflib.py, which enabled SGF collections.
# - Added -c option (dialog on Mac).
# - Completed docstring documentation.
#
# 0.2 (1999-10-17): First stable version.
# - Self-contained mini-parser.
#
# 0.1 (1999-09-06): 
# - Initial idea & started coding.
#
# To do?:
# - Test on Unix, Linux, Windows...
# - Add an interactive GUI for other OSes. (Make a Tk GUI for all OSes?)
# - Make summary format flexible (columns, order of columns; options file?).
# - Extract byo-yomi information from IGS files (BL/WL property).


import sgflib
import os, sys, string, re


def showHelp():
	""" Write out this module's help text (docstring) and exit."""
	sys.stderr.write(__doc__)
	sys.exit(1)


class SGFSummary:
	"""
	Reads, analyzes, and summarizes an SGF file.

	Instance Attributes:
	- self.filename : string -- Name of file being summarized.
	- self.data : string -- Stores raw file contents.
	- self.props : dictionary -- Property/value pairs.
	- self.sgfp : 'sgflib.SGFParser' or 'sgflib.RootNodeSGFParser'.
	- self.isSGF : boolean -- File validity flag.

	Class Attributes:
	- self.summaryFormat : string -- Format for 'summaryHeader' and summary 
	  lines.
	- self.summaryFields : dictionary -- Field names for 'summaryHeader'.
	- self.summaryHeader : string -- Tirst line of output.
	- self.ctrltrans : string[256] -- Translation table for all control 
	  characters -> spaces.
	- self.timepat : 're.RegexObject' -- For extracting game time from 
	  filename."""

	# summaryHeader and __repr__ are kept in sync using summaryFormat
	summaryFormat = ("%(DT)s\t%(RE)s\t%(PB)s\t%(BR)s\t%(PW)s\t%(WR)s\t%(KM)s\t%(HA)s\t" +
					"%(SZ)s\t%(TM)s\t%(filename)s\t%(GN)s\t%(PC)s\t%(EV)s")
	summaryFields = {	'DT' : 'Date & TIme',
						'RE' : 'Result',
						'PB' : 'Black',
						'BR' : 'B Rank',
						'PW' : 'White',
						'WR' : 'W Rank',
						'KM' : 'Komi',
						'HA' : 'Handicap',
						'SZ' : 'Board Size',
						'TM' : 'Time',
						'filename' : 'Filename',
						'GN' : 'Game Name',
						'PC' : 'Place',
						'EV' : 'Event',	}
	summaryHeader = summaryFormat % summaryFields
	ctrltrans = string.maketrans("\000\001\002\003\004\005\006\007\010\011\012\013" +
								 "\014\015\016\017\020\021\022\023\024\025\026\027" +
								 "\030\031\032\033\034\035\036\037", " "*32)
	timepat = re.compile(r"(\d\d)\D?(\d\d)(\.sgf)?$", re.IGNORECASE)

	def __init__(self, srcpath, sgffile, doCollections=1):
		"""
			Reads and stores (in self.data) one SGF file's contents, and 
			initializes an SGF parser (as self.sgfp). Arguments:
			- srcpath : string -- The source directory path.
			- sgffile : string -- The name of one file to process, stored
			  in self.filename.
			- doCollections : boolean -- Flags whether to consider SGF
			  collections. 0 (no) is faster, but only the first game of an
			  SGF file will be processed."""
		self.filename = sgffile
		self.isSGF = 0
		src = open(os.path.join(srcpath,sgffile), 'r')
		self.data = src.read()
		src.close()
		if doCollections:
			self.sgfp = sgflib.SGFParser(self.data)
		else:
			self.sgfp = sgflib.RootNodeSGFParser(self.data)
		# override parser's ctrl chars -> spaces translation table to include LF & CR
		self.sgfp.ctrltrans = self.ctrltrans

	def __str__(self):
		""" Returns a string representation (summary) of the current game from
			the object's SGF file. Returns an empty string if the file was not
			valid SGF."""
		if self.isSGF:
			return self.summaryFormat % self.props
		else:
			return ""

	def summarize(self):
		""" Summarizes one game from the SGF file. Returns 1 for success, 0 for
			failure (no more games, or not SGF file)."""
		g = self.sgfp.parseOneGame()
		if g:
			self._resetProperties()
			self.isSGF = 0						# file validity flag
			root = g[0]
			for p in root:
				if self.props.has_key(p.id):
					self.isSGF = 1				# flag file validity
					# strip leading & trailing spaces; join SGF value lists
					self.props[p.id] = string.join(map(string.strip, p), "::")
			self._timeFromFilename()
			return 1							# success
		else:
			return 0							# no more games

	def _timeFromFilename(self):
		""" Extracts time when game played from filename, appends time to date field."""
		if (self.props['DT'] != ''):			# only if date exists
			timeMatch = self.timepat.search(self.props['filename'])
			if timeMatch:
				self.props['DT'] = (self.props['DT'] + " " +
									timeMatch.group(1) + ":" + timeMatch.group(2))

	def _resetProperties(self):
		self.props = {	'DT' : '',				# DaTe
						'RE' : '',				# REsult
						'PB' : '',				# Black Player's name
						'BR' : '',				# Black Rank
						'PW' : '',				# White Player's name
						'WR' : '',				# White Rank
						'KM' : '',				# KoMi
						'HA' : '',				# HAndicap
						'SZ' : '',				# board SiZe
						'TM' : '',				# TiMe limit
						'filename' : self.filename,
						'GN' : '',				# Game Name
						'PC' : '',				# PlaCe where game held
						'EV' : '',	}			# EVent name


def getArgs():
	"""
		Dispatches by OS. Returns a tuple containing:
		- path of source directory/folder (0 implies error/user cancelled)
		- list of files in that directory/folder
		- the output file's full path (0 for stdout)
		- a flag for SGF collection processing (1: enable; 0: disable)"""
	if os.name == 'mac':
		return macGetArgs()
	else:
		return posixGetArgs()

def macGetArgs():
	""" On MacOS, returns arguments requested interactively from the user."""
	import macfs, time, EasyDialogs
	thefolder = macfs.GetDirectory("Please choose a folder containing only SGF files:")
	if thefolder[1]:
		# button values: Cancel = -1, No = 0, Yes = 1
		doCollections = EasyDialogs.AskYesNoCancel("Enable SGF collections? (slow)", 0)
		if doCollections >= 0:
			srcpath = thefolder[0].as_pathname()
			srcfiles = os.listdir(srcpath)
			defaultdst = "SGF Summary %04i-%02i-%02i %02i%02i" % time.localtime(time.time())[:5]
			dstfile = macfs.StandardPutFile("Please save the summary:", defaultdst)
			if dstfile[1]:
				return (srcpath, srcfiles, dstfile[0].as_pathname(), doCollections)
	return (0,0,0,0)							# user cancelled, or other problem

def posixGetArgs():
	""" Gets & returns command-line arguments."""
	import getopt
	try:
		optlist, args = getopt.getopt(sys.argv[1:], "c")
		doCollections = len(optlist)			# just one option
	except getopt.error:
		print "Unrecognized option."
		showHelp()
	if len(args) == 1:							# check # of arguments
		srcpath = args[0]
		if os.path.isdir(srcpath):
			srcfiles = os.listdir(srcpath)
			dstpath = 0							# on Unix-like OSes, output to stdout
			return (srcpath, srcfiles, dstpath, doCollections)
		else:
			print "%s is not a valid path." % srcpath
	else:
		print "Wrong number of arguments."
	return (0,0,0,0)							# wrong # arguments, or not dir

def mainLoop(srcpath, srcfiles, doCollections):
	"""
		Iterate through SGF files in source directory, outputting summaries.
		Arguments:
		- srcpath : string -- The source directory path.
		- srcfiles : list of string -- List of filenames to process.
		- doCollections : boolean -- Flags whether to consider SGF collections."""
	print SGFSummary.summaryHeader				# first line of table, field names
	for f in srcfiles:							# iterate through files in dir
		if os.path.isfile(os.path.join(srcpath,f)):	# ignore subdirectories
			sgfsum = SGFSummary(srcpath, f, doCollections)
			while sgfsum.summarize():			# summarize one game from SGF file
				sum = str(sgfsum)
				if sum != '':					# print summary for valid files
					print sum
				else:
					print "file '%s' is not a valid SGF file" % f

def run(useStdout=0):
	"""
		Module's main: set up arguments & redirects (if any), and call the main
		loop. Called automatically when module is executed, not imported.
		Argument:
		- useStdout : boolean (default: 0) --
			Set for debugging on non-stdout OS (e.g., MacOS)."""
	(srcpath, srcfiles, dstpath, doCollections) = getArgs()
	if srcpath:
		if not useStdout and dstpath:			# debugging, or on Unix-like OSes
			dst = open(dstpath, 'w')
			stdout = sys.stdout
			sys.stdout = dst
		mainLoop(srcpath, srcfiles, doCollections)
		if not useStdout and dstpath:
			dst.close()
			sys.stdout = stdout					# restore stdout
	else:										# no srcpath indicates a problem
		showHelp()


if __name__ == '__main__':						# delay execution on module import
	run()
