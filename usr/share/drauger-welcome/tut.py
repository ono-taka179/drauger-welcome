#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  tut.py
#
#  Copyright 2022 Thomas Castleman <contact@draugeros.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from __future__ import print_function
import sys
from os import path, getenv
import subprocess
import csv
import time
import drauger_welcome.main_ui as main_ui

# Make it easier for us to print to stderr
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


def make_ints(string_list: str):
	"""make a list of strings into a list of ints"""
	new_list = []
	for each in string_list:
		new_list.append(int(each))
	return new_list

def is_before(before: list, after: list):
	"""Check if a given date list comes before another one
	
	Return True if `before` comes before `after`.
	Return None if they are the same date.
	Return False if `after` comes before `before`.
	"""
	if before[0] < after[0]: # check year first
		return True
	if before[0] > after[0]:
		return False
	# if we get to here we KNOW `before[0]` == `after[0]`
	if before[1] < after[1]: # check month second
		return True
	if before[1] > after[1]:
		return False
	# finally, if we get here, we know `before` and `after` are in the same month of the same year
	if before[2] < after[2]: # check day last
		return True
	if before[2] > after[2]:
		return False
	# if we get here, `before` == `after`. Return None.
	return None


HOME = getenv("HOME")
# check if system-installer will be running, if it is, do not show the welcome screen
with open("/proc/cmdline", "r") as cmdline_file:
            cmdline = cmdline_file.read()
if "system-installer" in cmdline:
            # Not wanted to be running ootb
            sys.exit(0)
# check to see if we are going to be EOL soon
file = open("/usr/share/distro-info/Draugeros.csv", "r")
csv_reader = list(csv.reader(file))
version = subprocess.check_output(["lsb_release", "-rs"]).decode()[:-1]

# we want to iterate BACKWARDS because the version number is likely to be either the
# last line, or the next-to-last line. This means our big-O stays the same, but our
# true execution time is SIGNIFICANTLY reduced.
for each in range(len(csv_reader) - 1, -1, -1):
	if csv_reader[each][0] == version:
		current_time = time.strftime("%Y-%m-%d", time.gmtime())
		current_time = current_time.split("-")
		current_time = make_ints(current_time)
		eol_time = csv_reader[each][-1].split("-")
		eol_time = make_ints(eol_time)
		add_time = 1209600 # number of seconds in 14 days
		# find dismantle time (eol_time + 14 days)
		dismantle_time = time.strftime("%Y-%m-%d", time.gmtime(time.time() + dismantle_time))
		dismantle_time = dismantle_time.split("-")
		dismantle_time = make_ints(dismantle_time)
		# find alert time (eol_time - 14 days)
		alert_time = time.strftime("%Y-%m-%d", time.gmtime(time.time() - dismantle_time))
		alert_time = alert_time.split("-")
		alert_time = make_ints(alert_time)
		# check for alerts in this order:
		# alert_time -> eol_time -> dismantle_time
		alert = not is_before(current_time, alert_time)
		if alert: # not None evaluates to True
			eol = not is_before(current_time, eol_time)
			if eol:
				dismantle = not is_before(current_time, dismantle_time)
				if dismantle:
					# display dismantled dialog - Let the user know that this version of Drauger OS can no longer update without
					# modifications to /etc/apt/sources.list
					break
				# if we get here then this version of Drauger OS is EOL but not yet dismantled, alert user they can still upgrade to
				# the next version of Drauger OS
				break
			# if we get here then this version of Drauger OS is within 2 weeks of being EOL. Alert the user.
			break
if ((not path.exists(HOME + "/.drauger-tut")) and (not path.exists("/etc/system-installer/oem-post-install.flag"))):
	try:
		main_ui.welcome_show()
	except Exception as e:
		subprocess.Popen("/usr/share/drauger-welcome/log-out 2 /usr/share/drauger-welcome/tut.py \"Error: %s . main_ui.py has failed.\"" % (e))
else:
	exit(2)
