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

from simpleline.render.widgets import Widget, TextWidget, SeparatorWidget

from simpleline.logging import get_simpleline_logger

__all__ = ["ListRowContainer", "ListColumnContainer", "WindowContainer"]

log = get_simpleline_logger()


class Container(Widget):
    """Base class for containers which will do positioning of the widgets."""

    def __init__(self, items=None, numbering=True):
        """Construct Container.

        :param items: List of items for positioning in this Container. Callback can't be specified this way.
        :type items: List of items for rendering.

        :param numbering: Enable/disable automatic numbering (labels) for items. Enabled by default (True).
        :type numbering: bool
        """
        super().__init__()
        self._key_pattern = None
        self._items = []
        if items:
            for i in items:
                self._items.append(ContainerItem(i))

        if numbering:
            self._key_pattern = KeyPattern()
        else:
            self._key_pattern = None

    @property
    def size(self):
        """Return items count."""
        return len(self._items)

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
        :type callback: function ``func(data)``.

        :param data: Data which will be passed to the callback.
        :param data: Anything.

        :returns: ID of the item in this Container.
        :rtype: int
        """
        self._items.append(ContainerItem(item, callback, data))
        return len(self._items) - 1

    def process_user_input(self, key):
        """Process input from the user if any of the items in the list was called.

        This method must be called in `UIScreen.input()` method if list widget should call the callbacks.

        :param key: Key pressed from user.
        :type key: str

        :returns: True if key was processed. False otherwise.
        """
        if not self._key_pattern or type(key) != str:
            return False

        res = self._key_pattern.translate_input_to_widget_id(key)
        if res is not None:
            try:
                item = self._items[res]
                item.callback(item.data)
                return True
            except IndexError:  # container widget with this id doesn't exists
                return False

        return False

    def create_number_label(self, item_id):
        """Create TextWidget from KeyPattern.

        :param item_id: Create label for item with this id.
        :type item_id: int

        :returns: Widget with label for the item with item_id.
        :rtype: `simpleline.render.widgets.TextWidget` instance.
        """
        number_widget = TextWidget(self._key_pattern.get_widget_label(item_id))
        return number_widget


class WindowContainer(Container):
    """Base container for screens.

    This can hold other containers or Widgets for rendering.
    """

    def __init__(self, title=None):
        """Construct base container for screens.

        This container doesn't have numbering support. Input other containers in it to allow numbering
        and input processing.

        :param title: Title line with separator after this title.
        :type title: str
        """
        super().__init__(numbering=False)
        self._title = title

    def add_with_separator(self, item, callback=None, data=None, blank_lines=1):
        """Add widget and after widget add blank line.

        This method will call
        `self.add(item, callback, data)`
        `self.add_separator(lines)`

        :param item: Add item to this container.
        :type item: Could be item (based on `simpleline.render.widgets.Widget`)
                    or other container (based on `simpleline.render.containers.Container`).

        :param callback: Add callback for this item. This callback will be called when user activate this `item`.
        :type callback: function ``func(data)``.

        :param data: Data which will be passed to the callback.
        :param data: Anything.

        :param blank_lines: How many blank lines should be printed.
        :type blank_lines: int greater than 0.

        :returns: ID of the item in this Container.
        :rtype: int
        """
        item_id = self.add(item, callback, data)
        self.add_separator(blank_lines)

        return item_id

    def add_separator(self, lines=1):
        """Add blank lines between widgets.

        :param lines: How many blank lines should be printed.
        :type lines: int greater than 0.
        """
        self.add(SeparatorWidget(lines))

    @property
    def title(self):
        """Title of WindowContainer."""
        return self._title

    def render(self, width):
        """Render widgets to it's internal buffer.

        :param width: the maximum width the item can use
        :type width: int

        :return: nothing
        """
        super().render(width)

        # set cursor position to top-left corner
        self.set_cursor_position(0, 0)

        if self._title:
            self._draw_title_and_separator(width)

        for item in self._items:
            widget = item.widget
            widget.render(width)
            self.draw(widget)

    def _draw_title_and_separator(self, width):
        title_widget = TextWidget(self._title)
        sep = SeparatorWidget()

        title_widget.render(width)
        sep.render(width)

        self.draw(title_widget)
        self.draw(sep)


class ListRowContainer(Container):
    """Place widgets in rows automatically.

    Compared to the ColumnWidget this is able to handle word wrapping correctly.

    There is numbering N) automatically for all items. To disable this feature call `self.key_pattern = None`.
    If you want other numbering then look on `KeyPattern` class.

    Widgets will be placed based on the number of columns in the following way:

    1) w1  2) w2  3) w3
    4) w4  5) w5  6) w6
    ....
    """

    def __init__(self, columns, items=None, columns_width=None, spacing=3, numbering=True):
        """Create ListWidget with specific number of columns.

        :param columns: How many columns we want.
        :type columns: int, bigger than 0

        :param items: List of items for positioning in this Container. Callback can't be specified this way.
        :type items: List of items for rendering.

        :param columns_width: Width of every column. If nothing specified the maximum width will be distributed
                              to columns.
        :type columns_width: int or None

        :param spacing: Set the spacing between columns.
        :type spacing: int

        :param numbering: Enable/disable automatic numbering (labels) for items. Enabled by default (True).
        :type numbering: bool
        """
        super().__init__(items, numbering)
        self._columns = columns
        self._columns_width = columns_width
        self._spacing = spacing
        self._numbering_widgets = []

    def render(self, width):
        """Render widgets to it's internal buffer.

        :param width: the maximum width the item can use
        :type width: int

        :return: nothing
        """
        super().render(width)

        if self._columns_width is None:
            spaces_between_columns = self._columns - 1
            sum_spacing = spaces_between_columns * self._spacing
            self._columns_width = int((width - sum_spacing) / self._columns)

        ordered_map = self._get_ordered_map()
        lines_per_rows = self._lines_per_every_row(ordered_map)

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

    def _lines_per_every_row(self, items):
        self._render_all_items()
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

    def _render_all_items(self):
        for item_id, item in enumerate(self._items):
            item_width = self._columns_width

            if item_width <= 0:
                raise ValueError("Widget can't be rendered! Columns width is too small.")

            if self._key_pattern:
                number_widget = self.create_number_label(item_id)
                # render numbers before widgets
                number_width = len(number_widget.text)
                number_widget.render(number_width)
                self._numbering_widgets.append(number_widget)
                # reduce the size of widget because of the number
                item_width -= number_width

                if item_width <= 0:
                    raise ValueError("Widget can't be rendered with numbering on! "
                                     "Increase column width or disable numbering.")

            item.widget.render(item_width)

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

    There is numbering N) automatically for all items. To disable this feature call `self.key_pattern = None`.
    If you want other numbering then look on `KeyPattern` class.

    Widgets will be placed based on the number of columns in the following way:

    1) w1  4) w4  7) w7
    2) w2  5) w5  8) w8
    3) w3  6) w6  9) w9
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

    def __init__(self, pattern="{:d}) ", offset=1):
        """Create the pattern class.

        For enabling greater functionality than python 3 format is able to do, feel free to override this class and
        use your subclass instead.

        :param pattern: Set pattern which will be called for every item.
        :type pattern: Strings format method. See https://docs.python.org/3.3/library/string.html#format-string-syntax.

        :param offset: Set the offset for numbering items. Default is 1 to start indexing naturally for user.
        :type offset: int
        """
        self._pattern = pattern
        self._offset = offset

    def get_widget_label(self, item_id):
        """Get widget identifier for user input description.

        It should be something similar to the pattern.

        :param item_id: Position of the widget in the list.
        :type item_id: int starts from 0.
        """
        return self._pattern.format(item_id + self._offset)

    def translate_input_to_widget_id(self, user_input):
        """Get id of the widget from the user input.

        This is reverse translation to `self.get_widget_identifier()`.

        :param user_input: Input from user:
        :type user_input: str

        :return: ID of the widget in the list or None if the input can't be translated.
        :rtype: int or None
        """
        try:
            return int(user_input) - 1
        except ValueError:
            log.debug("No callback registered for user input %s", user_input)
            return None


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
