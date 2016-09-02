# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;media_transformation

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasMediaTransformationVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=unused-argument

try: from urllib.parse import parse_qsl, urlencode
except ImportError:
#
	from urllib import urlencode
	from urlparse import parse_qsl
#

class MediaTransformationDataMixin(object):
#
	"""
The "MediaTransformationDataMixin" provides static methods to de- and encode
transformation query strings.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: media_transformation
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def get_transformation_data(transformation_query_string):
	#
		"""
Returns a dictionary of transformation data defined by the encoded query
string given.

:param transformation_query_string: Encoded query string with transformation
       data

:return: (dict) Transformation data dictionary
:since:  v0.1.00
		"""

		return dict(parse_qsl(transformation_query_string))
	#

	@staticmethod
	def get_transformation_query_string(transformation_data):
	#
		"""
Returns a sorted encoded query string defining the transformation data
given as a dictionary.

:return: (str) Encoded query string with transformation data
:since:  v0.1.00
		"""

		transformation_keys = list(transformation_data.keys())
		transformation_keys.sort()

		return urlencode([ ( key, transformation_data[key] ) for key in transformation_keys ])
	#
#

##j## EOF