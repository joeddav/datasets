# coding=utf-8

from dataclasses import dataclass
from typing import List

import pyarrow.csv as pac

import datasets


@dataclass
class CsvConfig(datasets.BuilderConfig):
    """BuilderConfig for CSV."""

    skip_rows: int = None
    column_names: List[str] = None
    autogenerate_column_names: bool = None
    delimiter: str = None
    quote_char: str = None
    read_options: pac.ReadOptions = None
    parse_options: pac.ParseOptions = None
    convert_options: pac.ConvertOptions = None

    @property
    def pa_read_options(self):
        read_options = self.read_options or pac.ReadOptions()
        if self.skip_rows is not None:
            read_options.skip_rows = self.skip_rows
        if self.column_names is not None:
            read_options.column_names = self.column_names
        if self.autogenerate_column_names is not None:
            read_options.autogenerate_column_names = self.autogenerate_column_names
        return read_options

    @property
    def pa_parse_options(self):
        parse_options = self.parse_options or pac.ParseOptions()
        if self.delimiter is not None:
            parse_options.delimiter = self.delimiter
        if self.quote_char is not None:
            parse_options.quote_char = self.quote_char
        return parse_options

    @property
    def pa_convert_options(self):
        convert_options = self.convert_options or pac.ConvertOptions()
        return convert_options


class Csv(datasets.ArrowBasedBuilder):
    BUILDER_CONFIG_CLASS = CsvConfig

    def _info(self):
        return datasets.DatasetInfo()

    def _split_generators(self, dl_manager):
        """We handle string, list and dicts in datafiles"""
        if not self.config.data_files:
            raise ValueError(f"At least one data file must be specified, but got data_files={self.config.data_files}")
        data_files = dl_manager.download_and_extract(self.config.data_files)
        if isinstance(data_files, (str, list, tuple)):
            files = data_files
            if isinstance(files, str):
                files = [files]
            return [datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"files": files})]
        splits = []
        for split_name in [datasets.Split.TRAIN, datasets.Split.VALIDATION, datasets.Split.TEST]:
            if split_name in data_files:
                files = data_files[split_name]
                if isinstance(files, str):
                    files = [files]
                splits.append(datasets.SplitGenerator(name=split_name, gen_kwargs={"files": files}))
        return splits

    def _generate_tables(self, files):
        for i, file in enumerate(files):
            pa_table = pac.read_csv(
                file,
                read_options=self.config.pa_read_options,
                parse_options=self.config.pa_parse_options,
                convert_options=self.config.convert_options,
            )
            yield i, pa_table
