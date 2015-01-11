# encoding: utf-8

"""
Placeholder-related objects, specific to shapes having a `p:ph` element.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .autoshape import Shape
from .base import BaseShape
from ..enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from ..oxml.shapes.picture import CT_Picture
from .picture import Picture


class _InheritsDimensions(object):
    """
    Mixin class that provides inherited dimension behavior. Specifically,
    left, top, width, and height report the value from the layout placeholder
    where they would have otherwise reported |None|. This behavior is
    distinctive to placeholders.
    """
    @property
    def height(self):
        """
        The effective height of this placeholder shape; its directly-applied
        height if it has one, otherwise the height of its parent layout
        placeholder.
        """
        return self._effective_value('height')

    @height.setter
    def height(self, value):
        self._element.cy = value

    @property
    def left(self):
        """
        The effective left of this placeholder shape; its directly-applied
        left if it has one, otherwise the left of its parent layout
        placeholder.
        """
        return self._effective_value('left')

    @left.setter
    def left(self, value):
        self._element.x = value

    @property
    def shape_type(self):
        """
        Member of :ref:`MsoShapeType` specifying the type of this shape.
        Unconditionally ``MSO_SHAPE_TYPE.PLACEHOLDER`` in this case.
        Read-only.
        """
        return MSO_SHAPE_TYPE.PLACEHOLDER

    @property
    def top(self):
        """
        The effective top of this placeholder shape; its directly-applied
        top if it has one, otherwise the top of its parent layout
        placeholder.
        """
        return self._effective_value('top')

    @top.setter
    def top(self, value):
        self._element.y = value

    @property
    def width(self):
        """
        The effective width of this placeholder shape; its directly-applied
        width if it has one, otherwise the width of its parent layout
        placeholder.
        """
        return self._effective_value('width')

    @width.setter
    def width(self, value):
        self._element.cx = value

    def _effective_value(self, attr_name):
        """
        The effective value of *attr_name* on this placeholder shape; its
        directly-applied value if it has one, otherwise the value on the
        layout placeholder it inherits from.
        """
        directly_applied_value = getattr(
            super(_InheritsDimensions, self), attr_name
        )
        if directly_applied_value is not None:
            return directly_applied_value
        return self._inherited_value(attr_name)

    def _inherited_value(self, attr_name):
        """
        The attribute value, e.g. 'width' of the layout placeholder this
        slide placeholder inherits from
        """
        layout_placeholder = self._layout_placeholder
        if layout_placeholder is None:
            return None
        inherited_value = getattr(layout_placeholder, attr_name)
        return inherited_value

    @property
    def _layout_placeholder(self):
        """
        The layout placeholder shape this slide placeholder inherits from
        """
        layout, idx = self._slide_layout, self._element.ph_idx
        return layout.placeholders.get(idx=idx)

    @property
    def _slide_layout(self):
        """
        The slide layout for this placeholder's slide.
        """
        slide = self.part
        return slide.slide_layout


class _BaseSlidePlaceholder(_InheritsDimensions, BaseShape):
    """
    Base class for placeholders on slides. Provides common behaviors such as
    inherited dimensions.
    """
    @property
    def shape_type(self):
        """
        Member of :ref:`MsoShapeType` specifying the type of this shape.
        Unconditionally ``MSO_SHAPE_TYPE.PLACEHOLDER`` in this case.
        Read-only.
        """
        return MSO_SHAPE_TYPE.PLACEHOLDER

    def _replace_placeholder_with(self, element):
        """
        Substitute *element* for this placeholder element in the shapetree.
        This placeholder's `._element` attribute is set to |None| and its
        original element is free for garbage collection. Any attribute access
        (including a method call) on this placeholder after this call raises
        |AttributeError|.
        """
        element._nvXxPr.nvPr._insert_ph(self._element.ph)
        self._element.addprevious(element)
        self._element.getparent().remove(self._element)
        self._element = None


class BasePlaceholder(Shape):
    """
    Base class for placeholder subclasses that differentiate the varying
    behaviors of placeholders on a master, layout, and slide.
    """
    @property
    def idx(self):
        """
        Integer placeholder 'idx' attribute, e.g. 0
        """
        return self._sp.ph_idx

    @property
    def orient(self):
        """
        Placeholder orientation, e.g. ST_Direction.HORZ
        """
        return self._sp.ph_orient

    @property
    def ph_type(self):
        """
        Placeholder type, e.g. PP_PLACEHOLDER.CENTER_TITLE
        """
        return self._sp.ph_type

    @property
    def sz(self):
        """
        Placeholder 'sz' attribute, e.g. ST_PlaceholderSize.FULL
        """
        return self._sp.ph_sz


class LayoutPlaceholder(BasePlaceholder):
    """
    Placeholder shape on a slide layout, providing differentiated behavior
    for slide layout placeholders, in particular, inheriting shape properties
    from the master placeholder having the same type, when a matching one
    exists.
    """
    @property
    def height(self):
        """
        The effective height of this placeholder shape; its directly-applied
        height if it has one, otherwise the height of its parent master
        placeholder.
        """
        return self._direct_or_inherited_value('height')

    @property
    def left(self):
        """
        The effective left of this placeholder shape; its directly-applied
        left if it has one, otherwise the left of its parent master
        placeholder.
        """
        return self._direct_or_inherited_value('left')

    @property
    def top(self):
        """
        The effective top of this placeholder shape; its directly-applied
        top if it has one, otherwise the top of its parent master
        placeholder.
        """
        return self._direct_or_inherited_value('top')

    @property
    def width(self):
        """
        The effective width of this placeholder shape; its directly-applied
        width if it has one, otherwise the width of its parent master
        placeholder.
        """
        return self._direct_or_inherited_value('width')

    def _direct_or_inherited_value(self, attr_name):
        """
        The effective value of *attr_name* on this placeholder shape; its
        directly-applied value if it has one, otherwise the value on the
        master placeholder it inherits from.
        """
        directly_applied_value = getattr(
            super(LayoutPlaceholder, self), attr_name
        )
        if directly_applied_value is not None:
            return directly_applied_value
        inherited_value = self._inherited_value(attr_name)
        return inherited_value

    def _inherited_value(self, attr_name):
        """
        The attribute value, e.g. 'width' of the parent master placeholder of
        this placeholder shape
        """
        master_placeholder = self._master_placeholder
        if master_placeholder is None:
            return None
        inherited_value = getattr(master_placeholder, attr_name)
        return inherited_value

    @property
    def _master_placeholder(self):
        """
        The master placeholder shape this layout placeholder inherits from.
        """
        inheritee_ph_type = {
            PP_PLACEHOLDER.BODY:         PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.CHART:        PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.BITMAP:       PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.CENTER_TITLE: PP_PLACEHOLDER.TITLE,
            PP_PLACEHOLDER.ORG_CHART:    PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.DATE:         PP_PLACEHOLDER.DATE,
            PP_PLACEHOLDER.FOOTER:       PP_PLACEHOLDER.FOOTER,
            PP_PLACEHOLDER.MEDIA_CLIP:   PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.OBJECT:       PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.PICTURE:      PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.SLIDE_NUMBER: PP_PLACEHOLDER.SLIDE_NUMBER,
            PP_PLACEHOLDER.SUBTITLE:     PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.TABLE:        PP_PLACEHOLDER.BODY,
            PP_PLACEHOLDER.TITLE:        PP_PLACEHOLDER.TITLE,
        }[self.ph_type]
        slide_master = self._slide_master
        master_placeholder = slide_master.placeholders.get(
            inheritee_ph_type, None
        )
        return master_placeholder

    @property
    def _slide_master(self):
        """
        The slide master this placeholder inherits from.
        """
        slide_layout = self.part
        slide_master = slide_layout.slide_master
        return slide_master


class MasterPlaceholder(BasePlaceholder):
    """
    Placeholder shape on a slide master.
    """


class SlidePlaceholder(_InheritsDimensions, Shape):
    """
    Placeholder shape on a slide. Inherits shape properties from its
    corresponding slide layout placeholder.
    """


class PicturePlaceholder(_BaseSlidePlaceholder):
    """
    Placeholder shape that can only accept a picture.
    """
    def insert_picture(self, image_file):
        """
        Return a |PlaceholderPicture| object depicting the image in
        *image_file*, which may be either a path (string) or a file-like
        object. The image is cropped to fill the entire space of the
        placeholder. A |PlaceholderPicture| object has all the properties and
        methods of a |Picture| shape. Except that the value of its
        :attr:`~._BaseSlidePlaceholder.shape_type` property is
        `MSO_SHAPE_TYPE.PLACEHOLDER` instead of `MSO_SHAPE_TYPE.PICTURE`.
        """
        pic = self._new_placeholder_pic(image_file)
        self._replace_placeholder_with(pic)
        return PlaceholderPicture(pic, self._parent)

    def _new_placeholder_pic(self, image_file):
        """
        Return a new `p:pic` element depicting the image in *image_file*,
        suitable for use as a placeholder. In particular this means not
        having an `a:xfrm` element, allowing its extents to be inherited from
        its layout placeholder.
        """
        rId, desc, image_size = self._get_or_add_image(image_file)
        id_, name = self.id, self.name
        pic = CT_Picture.new_ph_pic(id_, name, desc, rId)
        pic.crop_to_fit(image_size, (self.width, self.height))
        return pic

    def _get_or_add_image(self, image_file):
        """
        Return an (rId, description, image_size) 3-tuple identifying the
        related image part containing *image_file* and describing the image.
        """
        image_part, rId = self.part.get_or_add_image_part(image_file)
        desc, image_size = image_part.desc, image_part._px_size
        return rId, desc, image_size


class PlaceholderPicture(_InheritsDimensions, Picture):
    """
    Placeholder shape populated with a picture.
    """
