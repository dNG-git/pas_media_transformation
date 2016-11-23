# -*- coding: utf-8 -*-

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

try: from urllib.parse import quote, unquote, urlsplit
except ImportError:
    from urllib import quote, unquote
    from urlparse import urlsplit
#

from dNG.data.cache.file import File as CacheFile
from dNG.data.media.abstract_image import AbstractImage
from dNG.data.media.image_implementation import ImageImplementation
from dNG.data.mime_type import MimeType
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.runtime.io_exception import IOException
from dNG.runtime.value_exception import ValueException
from dNG.vfs.abstract import Abstract
from dNG.vfs.file_like_wrapper_mixin import FileLikeWrapperMixin
from dNG.vfs.implementation import Implementation
from dNG.vfs.media_transformation_data_mixin import MediaTransformationDataMixin

class Object(FileLikeWrapperMixin, MediaTransformationDataMixin, Abstract):
    """
Provides the VFS implementation for 'x-media-transformed-image' objects.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: media_transformation
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    _FILE_WRAPPED_METHODS = ( "close",
                              "get_size",
                              "is_eof",
                              "is_valid",
                              "read",
                              "seek",
                              "tell"
                            )
    """
File IO methods implemented by an wrapped resource.
    """

    def __init__(self):
        """
Constructor __init__(Object)

:since: v0.1.00
        """

        Abstract.__init__(self)
        FileLikeWrapperMixin.__init__(self)

        self.original_media_vfs_url = None
        """
VFS URL to the media file to be transformed
        """
        self.transformation_data = { }
        """
Transformation data given
        """

        self.supported_features['implementing_instance'] = self._supports_implementing_instance
        self.supported_features['time_created'] = True
    #

    def get_implementing_instance(self):
        """
Returns the implementing instance.

:return: (mixed) Implementing instance
:since:  v0.1.00
        """

        if (self._wrapped_resource is None): raise IOException("VFS object not opened")
        return self._wrapped_resource
    #

    def get_implementing_scheme(self):
        """
Returns the implementing scheme name.

:return: (str) Implementing scheme name
:since:  v0.1.00
        """

        return "x-media-transformed-image"
    #

    def get_mimetype(self):
        """
Returns the mime type of this VFS object.

:return: (str) VFS object mime type
:since:  v0.1.00
        """

        if (self._wrapped_resource is None): raise IOException("VFS object not opened")

        mimetype_definition = MimeType.get_instance().get(mimetype = self.transformation_data['mimetype'])
        return ("application/octet-stream" if (mimetype_definition is None) else mimetype_definition['type'])
    #

    def get_name(self):
        """
Returns the name of this VFS object.

:return: (str) VFS object name
:since:  v0.1.00
        """

        if (self._wrapped_resource is None): raise IOException("VFS object not opened")
        return self._wrapped_resource.get_id()
    #

    def get_time_created(self):
        """
Returns the UNIX timestamp this object was created.

:return: (int) UNIX timestamp this object was created
:since:  v0.1.00
        """

        if (self._wrapped_resource is None): raise IOException("VFS object not opened")
        return self._wrapped_resource.get_data_attributes("time_stored")['time_stored']
    #

    def get_time_updated(self):
        """
Returns the UNIX timestamp this object was updated.

:return: (int) UNIX timestamp this object was updated
:since:  v0.1.00
        """

        return self.get_time_created()
    #

    def get_type(self):
        """
Returns the type of this object.

:return: (int) Object type
:since:  v0.1.00
        """

        if (self._wrapped_resource is None): raise IOException("VFS object not opened")
        return Object.TYPE_FILE
    #

    def get_url(self):
        """
Returns the URL of this VFS object.

:return: (str) VFS URL
:since:  v0.1.00
        """

        if (self.original_media_vfs_url is None): raise IOException("VFS object not opened")

        query_string = Object.get_transformation_query_string(self.transformation_data)

        return ("{0}:///{1}?{2}".format(self.get_implementing_scheme(),
                                        quote(self.original_media_vfs_url, "/"),
                                        query_string
                                       )
               )
    #

    def open(self, vfs_url, readonly = False):
        """
Opens a VFS object.

:param vfs_url: VFS URL
:param readonly: Open object in readonly mode

:since: v0.1.00
        """

        if (self._wrapped_resource is not None): raise IOException("Can't create new VFS object on already opened instance")

        vfs_url_data = urlsplit(vfs_url)

        transformation_data = Object.get_transformation_data(vfs_url_data.query)

        if ("mimetype" not in transformation_data
            or "width" not in transformation_data
            or "height" not in transformation_data
           ): raise ValueException("VFS URL given does not contain the required transformation data")

        transformation_data['depth'] = int(transformation_data.get("depth", 32))
        transformation_data['height'] = int(transformation_data['height'])
        transformation_data['resize_mode'] = int(transformation_data.get("resize_mode", AbstractImage.RESIZE_SCALED_FIT))
        transformation_data['width'] = int(transformation_data['width'])

        mimetype_definition = MimeType.get_instance().get(mimetype = transformation_data['mimetype'])
        if (mimetype_definition is None or mimetype_definition['class'] != "image"): raise IOException("VFS object does not correspond to an image")

        self.original_media_vfs_url = unquote(vfs_url_data.path[1:])
        self.transformation_data = transformation_data
    #

    def _open_wrapped_resource(self):
        """
Opens the wrapped resource once needed.

@TODO: Nocache?

:since: v0.1.00
        """

        cache_file = None

        vfs_object = Implementation.load_vfs_url(self.original_media_vfs_url, True)

        try:
            cache_file = CacheFile.load_resource(self.get_url())

            if ((not vfs_object.is_valid())
                or (vfs_object.is_supported("time_updated")
                    and (not cache_file.is_up_to_date(vfs_object.get_time_updated()))
                   )
               ):
                cache_file.delete()
                cache_file = None
            #
        except NothingMatchedException: pass

        if (not vfs_object.is_valid()): raise IOException("Failed to load the original VFS object")

        if (cache_file is None): cache_file = self._transform(vfs_object)
        self._set_wrapped_resource(cache_file)
    #

    def _transform(self, vfs_object):
        """
Transforms the given source represented as an VFS instance and returns an
file-like instance with the configured transformation applied.

:param vfs_object: Source VFS object to read the image from

:return: (object) File-like instance with the configured transformation
         applied
:since:  v0.1.00
        """

        _return = CacheFile()

        image_class = ImageImplementation.get_class()
        if (image_class is None): raise IOException("Image media implementation does not support transformation")

        image = image_class()
        if (not image.is_supported("transformation")): raise IOException("Image media implementation does not support transformation")

        if (not image.open_url(vfs_object.get_url())): raise IOException("Image media implementation failed to open the original VFS object")

        image.set_mimetype(self.transformation_data['mimetype'])
        image.set_resize_mode(self.transformation_data['resize_mode'])

        image.set_size(self.transformation_data['width'], self.transformation_data['height'])

        colormap = image_class.get_colormap_for_depth(self.transformation_data['mimetype'],
                                                      self.transformation_data['depth']
                                                     )

        if (colormap is not None): image.set_colormap(colormap)

        image.transform()

        _return.set_data_attributes(time_cached = vfs_object.get_time_updated(),
                                    resource = self.get_url(),
                                   )

        _return.write(image.read())
        _return.save()

        _return.seek(0)

        return _return
    #

    def _supports_flush(self):
        """
Returns false if flushing buffers is not supported.

:return: (bool) True if flushing buffers is supported
:since:  v0.1.00
        """

        return (self._wrapped_resource is not None)
    #

    def _supports_implementing_instance(self):
        """
Returns false if no underlying, implementing instance can be returned.

:return: (bool) True if an implementing instance can be returned.
:since:  v0.1.00
        """

        return (self._wrapped_resource is not None)
    #
#
