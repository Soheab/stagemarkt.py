from __future__ import annotations

from typing import Any
from collections.abc import Sequence
import dataclasses
import datetime
from enum import Enum
import json
from pathlib import Path

import xlsxwriter
import xlsxwriter.worksheet

from .base_exporter import BaseExporter, SortSpec
from .field import Field

__all__ = ("ExcelExporter", "to_excel")


class ExcelExporter(BaseExporter):
    """
    High-performance Excel exporter using xlsxwriter.

    Optimized for writing large datasets with minimal memory usage.

    Parameters
    ----------
    include_empty: bool
        If True, include empty values (None, empty strings, empty containers)
        in the output. Defaults to True.
    constant_memory: bool
        If True, enable xlsxwriter constant memory mode for streaming large
        files efficiently. Defaults to True.
    """

    __slots__ = ("_constant_memory",)

    def __init__(
        self,
        *,
        include_empty: bool = True,
        constant_memory: bool = True,
    ) -> None:
        """
        Initialize the Excel exporter.

        Parameters
        ----------
        include_empty: bool
            Whether to include empty values. Default True.
        constant_memory: bool
            Whether to use constant_memory mode for xlsxwriter. This allows
            writing very large files with low memory usage. Default True.
        """
        super().__init__(include_empty=include_empty)
        self._constant_memory = constant_memory

    def export(
        self,
        path: Path,
        objects: Sequence[object],
        *,
        sheet_name: str = "Sheet1",
        names: tuple[str | None, list[Field]] | None = None,
        sort: SortSpec | None = None,
    ) -> None:
        """
        Export objects to an Excel file.

        Parameters
        ----------
        path: Path
            Output file path.
        objects: Sequence[object]
            Sequence of objects to export.
        sheet_name: str
            Name of the worksheet. Default is "Sheet1".
        names: tuple[str | None, list[Field]] | None
            Optional header title and attribute specifications to define
            columns. If omitted, attributes are inferred from the first object.

        Returns
        -------
        None
            Writes the Excel file to `path`.
        """

        if not objects:
            return

        header_title: str | None = None
        attrs: list[Field] | None = None
        if names is not None:
            header_title, attrs = names

        attr_specs: Sequence[Field]
        attr_specs = self._infer_attributes(objects[0]) if attrs is None else attrs

        headers = [field.header_label() for field in attr_specs]

        workbook = xlsxwriter.Workbook(str(path), {"constant_memory": self._constant_memory})
        worksheet = workbook.add_worksheet(sheet_name)

        header_format = workbook.add_format({"bold": True})
        title_format = workbook.add_format({"bold": True, "align": "center"})
        date_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})

        current_row = 0
        if header_title:
            if headers:
                worksheet.merge_range(
                    current_row,
                    0,
                    current_row,
                    max(len(headers) - 1, 0),
                    header_title,
                    title_format,
                )
            else:
                worksheet.write(current_row, 0, header_title, title_format)
            current_row += 1

        if headers and any(header is not None for header in headers):
            worksheet.write_row(
                current_row,
                0,
                [header or "" for header in headers],
                header_format,
            )
            current_row += 1

        worksheet.freeze_panes(current_row, 0)

        for row_idx, obj in enumerate(self._sort_objects(objects, sort), start=current_row):
            row_data = self._extract_row_data(obj, attr_specs)
            self._write_row(worksheet, row_idx, row_data, date_format)

        workbook.close()

    def _infer_attributes(self, obj: Any) -> list[Field]:
        """
        Infer attribute names to export from the first object.

        Parameters
        ----------
        obj: Any
            The object used to infer attribute names.

        Returns
        -------
        list[Field]
            A list of Field instances.
        """
        if isinstance(obj, dict):
            return [Field(str(key), label=str(key)) for key in obj]

        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return [Field(f.name) for f in dataclasses.fields(obj) if not f.name.startswith("_")]

        slots = self._get_slots(type(obj))
        if slots:
            return [Field(s) for s in sorted([s for s in slots if not s.startswith("_")])]

        if hasattr(obj, "__dict__"):
            return [Field(k) for k in sorted([k for k in vars(obj) if not k.startswith("_")])]

        return []

    def _extract_row_data(
        self,
        obj: Any,
        attrs: Sequence[Field],
    ) -> list[Any]:
        """
        Extract data for a single row based on Field attributes.

        Parameters
        ----------
        obj: Any
            The primary object to read values from.
        attrs: Sequence[Field]
            Field attribute specifications.
        Returns
        -------
        list[Any]
            Row values ready for writing.
        """
        row: list[Any] = []
        for field in attrs:
            raw = field.get(obj, include_empty=self._include_empty)
            if not isinstance(raw, dict):
                row.append(self._convert_cell_value(raw))
                continue
            for root, fields in raw.items():
                key = root if root is not None else field.export_label()
                if key is None:
                    continue
                row.append(self._convert_cell_value(fields))
        return row

    def _convert_cell_value(self, val: Any) -> Any:
        """
        Convert a value to an Excel-compatible cell value.

        Parameters
        ----------
        val: Any
            The value to convert.

        Returns
        -------
        Any
            A value suitable for xlsxwriter.
        """
        # Primitives supported by Excel
        if isinstance(val, self._PRIMITIVES):
            return val

        if isinstance(val, self._DATETIME_TYPES) and not isinstance(val, datetime.time):
            return val  # xlsxwriter handles datetime objects

        if isinstance(val, Enum):
            return val.value

        if isinstance(val, self._BYTES_TYPES):
            return str(val)

        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)

        # Complex objects -> stringify
        return str(val)

    def _write_row(self, worksheet: xlsxwriter.worksheet.Worksheet, row_idx: int, data: list[Any], date_format) -> None:
        """
        Write a row of data, handling specific types.

        Parameters
        ----------
        worksheet: xlsxwriter.worksheet.Worksheet
            Target worksheet.
        row_idx: int
            Row index to write to.
        data: list[Any]
            Row values.
        date_format: Any
            xlsxwriter format for datetime cells.

        Returns
        -------
        None
        """
        for col_idx, val in enumerate(data):
            if isinstance(val, datetime.datetime):
                worksheet.write_datetime(row_idx, col_idx, val, date_format)
            elif isinstance(val, datetime.date):
                dt_val = datetime.datetime.combine(val, datetime.time())
                worksheet.write_datetime(row_idx, col_idx, dt_val, date_format)
            else:
                worksheet.write(row_idx, col_idx, val)


def to_excel(
    *,
    path: Path,
    objects: Sequence[object],
    names: tuple[str | None, list[Field]] | None = None,
    sheet_name: str = "Sheet1",
    include_empty: bool = True,
    constant_memory: bool = True,
    sort: SortSpec | None = None,
) -> None:
    """
    Export objects to an Excel file.

    Convenience wrapper around ExcelExporter.

    Parameters
    ----------
    path: Path
        The file path to write the Excel file to.
    objects: Sequence[object]
        The objects to export.
    names: tuple[str | None, list[Field]] | None
        Optional header title and attribute specifications.
    sheet_name: str
        The name of the worksheet. Default is "Sheet1".
    include_empty: bool
        Whether to include empty values. Default is True.
    constant_memory: bool
        Whether to use constant memory mode for large files. Default is True.

    Returns
    -------
    None
        Writes the Excel file to `path`.
    """
    exporter = ExcelExporter(include_empty=include_empty, constant_memory=constant_memory)
    exporter.export(
        path,
        objects,
        sheet_name=sheet_name,
        names=names,
        sort=sort,
    )
