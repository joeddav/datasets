# coding=utf-8
# Copyright 2020 HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""The Polyglot-NER Dataset."""

from __future__ import absolute_import, division, print_function

import os
import logging
import datasets


_CITATION = """\
@article{polyglotner,
         author = {Al-Rfou, Rami and Kulkarni, Vivek and Perozzi, Bryan and Skiena, Steven},
         title = {{Polyglot-NER}: Massive Multilingual Named Entity Recognition},
         journal = {{Proceedings of the 2015 {SIAM} International Conference on Data Mining, Vancouver, British Columbia, Canada, April 30- May 2, 2015}},
       month     = {April},
         year      = {2015},
         publisher = {SIAM},
}
"""

_LANGUAGES = [
    "ca",
    "de",
    "es",
    "fi",
    "hi",
    "id",
    "ko",
    "ms",
    "pl",
    "ru",
    "sr",
    "tl",
    "vi",
    "ar",
    "cs",
    "el",
    "et",
    "fr",
    "hr",
    "it",
    "lt",
    "nl",
    "pt",
    "sk",
    "sv",
    "tr",
    "zh",
    "bg",
    "da",
    "en",
    "fa",
    "he",
    "hu",
    "ja",
    "lv",
    "no",
    "ro",
    "sl",
    "th",
    "uk"
]

_DESCRIPTION = """\
Polyglot-NER

TODO: add full desc
"""

_DATA_URL = "http://cs.stonybrook.edu/~polyglot/ner2/emnlp_datasets.tgz"
_HOMEPAGE_URL = "https://sites.google.com/site/rmyeid/projects/polylgot-ner"


class PolyglotNERConfig(datasets.BuilderConfig):

    def __init__(self, *args, languages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.languages = languages
        self._filepaths = {
            lang: os.path.join(
                "acl_datasets",
                lang,
                "data" if lang != "za" else "", # they're all lang/data/lang_wiki.conll except "za"
                f"{lang}_wiki.conll"
            ) for lang in _LANGUAGES
        }

    @property
    def filepaths(self):
        return [self._filepaths[lang] for lang in self.languages]


class PolyglotNER(datasets.GeneratorBasedBuilder):
    """The Polyglot-NER Dataset"""

    BUILDER_CONFIGS = [
        PolyglotNERConfig(
            name=lang,
            languages=[lang],
            description=f"Polyglot-NER examples in {lang}."
        ) for lang in _LANGUAGES
    ] + [
        PolyglotNERConfig(
            name="combined",
            languages=_LANGUAGES,
            description=f"Complete Polyglot-NER dataset with all languages."
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "id": datasets.Value("string"),
                    "lang": datasets.Value("string"),
                    "tokens": datasets.Sequence(datasets.Value("string")),
                    "labels": datasets.Sequence(datasets.Value("string")),
                }
            ),
            supervised_keys=None,
            homepage=_HOMEPAGE_URL,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        path = dl_manager.download_and_extract(_DATA_URL)

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"datapath": path})
        ]

    def _generate_examples(self, datapath):
        for filepath, lang in zip(self.config.filepaths, self.config.languages):
            filepath = os.path.join(datapath, filepath)
            with open(filepath, encoding="utf-8") as f:
                current_tokens = []
                current_labels = []
                sentence_counter = 0
                for row in f:
                    row = row.rstrip()
                    if row:
                        token, label = row.split("\t")
                        current_tokens.append(token)
                        current_labels.append(label)
                    else:
                        # New sentence
                        if not current_tokens:
                            # Consecutive empty lines will cause empty sentences
                            continue
                        assert len(current_tokens) == len(current_labels), "💔 between len of tokens & labels"
                        sentence = (
                            sentence_counter,
                            {
                                "id": str(sentence_counter),
                                "lang": lang,
                                "tokens": current_tokens,
                                "labels": current_labels,
                            },
                        )
                        sentence_counter += 1
                        current_tokens = []
                        current_labels = []
                        yield sentence
                # Don't forget last sentence in dataset 🧐
                if current_tokens:
                    yield sentence_counter, {
                        "id": str(sentence_counter),
                        "lang": lang,
                        "tokens": current_tokens,
                        "labels": current_labels,
                    }
