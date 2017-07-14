# Widgets for holding other widgets.
#
# Copyright (C) 2016  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

from math import ceil

from simpleline.render.widgets import Widget, TextWidget

__all__ = ["ListRowContainer", "ListColumnContainer"]


class Container(Widget):
    """Base class for containers which will do positioning of the widgets."""

    def __init__(self, items=None):
        """Construct Container.

        :param items: Array of items for positioning in this Container. Callback can't be specified this way.
        :type items: List of items for rendering.
        """
        super().__init__()
        self._key_pattern = None
        self._items = []
        if items:
            for i in items:
                self._items.append(ContainerItem(i))

    @property
    def key_pattern(self):
        """Return key pattern which will be used for items numbering.

        Will return `None` if not set.
        """
        return self._key_pattern

    @key_pattern.setter
    def key_pattern(self, key_pattern):
        """Set the key pattern object which will be used for items numbering.

        Setting `None` will stop doing numbering.
        """
        self._key_pattern = key_pattern

    def add(self, item, callback=None, data=None):
        """Add item to the Container.

        :param item: Add item to this container.
        :type item: Could be item (based on `simpleline.render.widgets.Widget`)
                    or other container (based on `simpleline.render.containers.Container`).

        :param callback: Add callback for this item. This callback will be called when user activate this `item`.
        :type callback: function ``func(item, data)``.

        :param data: Data which will be passed to the callback.
        :param data: Anything.

        :returns: ID of the item in this Container.
        :rtype: int
        """
        self._items.append(ContainerItem(item, callback, data))
        return len(self._items) - 1


class ListRowContainer(Container):
    """Place widgets in rows automatically.

    Compared to the ColumnWidget this is able to handle word wrapping correctly.

    Widgets will be placed based on the number of columns in the following way:

    w1   w2   w3
    w4   w5   w6
    ....
    """

    def __init__(self, columns, widgets=None, columns_width=25, spacing=3):
        """Create ListWidget with specific number of columns.

        :param columns: How many columns we want.
        :type columns: int, bigger than 0

        :param widgets: List of `WidgetContainer`s. This will be positioned in the ListWidget.
        :type widgets: Array of `Widget` based class.

        :param columns_width: Width of every column.
        :type columns_width: int

        :param spacing: Set the spacing between columns.
        :type spacing: int
        """
        super().__init__(widgets)
        self._columns = columns
        self._columns_width = columns_width
        self._spacing = spacing
        self._numbering_widgets = []

    @property
    def size(self):
        """Return items count."""
        return len(self._items)

    def render(self, width):
        """Render widgets to it's internal buffer.

        :param width: the maximum width the item can use
        :type width: int

        :return: nothing
        """
        super().render(width)

        ordered_map = self._get_ordered_map()
        lines_per_rows = self.render_and_calculate_lines_per_rows(ordered_map)

        # the leftmost empty column
        col_pos = 0

        for col in ordered_map:
            row_pos = 0

            # render and draw contents of column
            for row_id, item_id in enumerate(col):
                container = self._items[item_id]
                widget = container.widget

                # set cursor to first line and leftmost empty column
                self.set_cursor_position(row_pos, col_pos)

                if self._key_pattern is not None:
                    number_widget = self._numbering_widgets[item_id]
                    widget_width = len(number_widget.text)
                    self.draw(number_widget)
                    self.set_cursor_position(row_pos, col_pos + widget_width)

                self.draw(widget, block=True)
                row_pos = row_pos + lines_per_rows[row_id]

            # recompute the leftmost empty column
            col_pos = max((col_pos + self._columns_width), self.width) + self._spacing

    def render_and_calculate_lines_per_rows(self, ordered_items):
        """Render all items and then find how many lines are required for every row.

        This will call `self._render_all_items()` and `self._lines_per_every_row()` in correct order.
        """
        self._render_all_items()
        return self._lines_per_every_row(ordered_items)

    def _render_all_items(self):
        for item_id, item in enumerate(self._items):
            item_width = self._columns_width

            if self._key_pattern:
                # render numbers before widgets
                number_widget = self._key_pattern.get_widget_from_item_id(item_id)
                number_width = len(number_widget.text)
                number_widget.render(number_width)
                self._numbering_widgets.append(number_widget)
                # reduce the size of widget because of the number
                item_width -= number_width

            item.widget.render(item_width)

    def _lines_per_every_row(self, items):
        # call `self._render_and_calculate_lines_per_rows()` method instead
        lines_per_row = []

        # go through all items and find how many lines we need for each row printed (because of wrapping)
        for column_items in items:
            for row_id, item_id in enumerate(column_items):
                item = self._items[item_id]
                if len(lines_per_row) <= row_id:
                    lines_per_row.append(0)

                lines_per_row[row_id] = max(lines_per_row[row_id], len(item.widget.get_lines()))

        return lines_per_row

    def _get_ordered_map(self):
        """Return list of identifiers (index) to the original item list.

        .. NOTE: Use of ``self._prepare_list()` is encouraged to create output list and just fill up this list.
        """
        # create list of columns (lists)
        ordering_map = self._prepare_list()

        for item_id in range(self.size):
            ordering_map[item_id % self._columns].append(item_id)

        return ordering_map

    def _prepare_list(self):
        """Prepare list for items ordering to rows and columns.

        List will be prepared as ([column 1], [column 2], ...)
        """
        return list(map(lambda x: [], range(0, self._columns)))


class ListColumnContainer(ListRowContainer):
    """Place widgets in columns automatically.

    Compared to the ColumnWidget this is able to handle word wrapping correctly.

    Widgets will be placed based on the number of columns in the following way:

    w1   w4   w7
    w2   w5   w8
    w3   w6   w9
    """

    def _get_ordered_map(self):
        ordering_map = self._prepare_list()
        items_in_column = ceil(len(self._items) / self._columns)

        for item_id in range(self.size):
            col_position = int(item_id // items_in_column)
            ordering_map[col_position].append(item_id)

        return ordering_map


class KeyPattern(object):
    """Pattern for automatic key printing before items."""

    def __init__(self, pattern="{:d}. ", offset=1):
        """Create the pattern class.

        :param pattern: Set pattern which will be called for every item.
        :type pattern: Strings format method. See https://docs.python.org/3.3/library/string.html#format-string-syntax.

        :param offset: Set the offset for numbering items. Default is 1 to start indexing naturally for user.
        :type offset: int
        """
        self._pattern = pattern
        self._offset = offset

    def get_widget_from_item_id(self, item_id):
        """Get widget key for printing before item.

        .. NOTE: Adding + offset to item_id before printing.

        :param item_id: Position of the widget in the list.
        :type item_id: int starts from 0.
        """
        text = self._pattern.format(item_id + self._offset)
        return TextWidget(text)

    def get_widget_identifier(self, item_id):
        """Get widget identifier for user input.

        :param item_id: Position of the widget in the list.
        :type item_id: int starts from 0.
        """
        return str(item_id + self._offset)


class ContainerItem(object):
    """Item used inside of containers to store widgets callbacks and data.

    Internal representation for Containers. Do not use this class directly.
    """

    def __init__(self, widget, callback=None, data=None):
        """Construct WidgetContainer.

        :param widget: Any item from `simpleline.render.widgets` or `Container`.
        :type widget: Class subclassing the `simpleline.render.widgets.Widget` class
                    or `simpleline.render.containers.Container`.

        :param callback: This callback will be called as reaction on user input.
        :type callback: Function with one data parameter: `def func(data):`.

        :param data: Params which will be passed to callback.
        :type data: Anything.
        """
        self.widget = widget
        self.callback = callback
        self.data = data
