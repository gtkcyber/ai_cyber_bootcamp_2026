"""Filename to slug and title. The PDF names are inconsistent on purpose:
one has no dash, one has two spaces, one is not a module at all."""

import pytest

from build_decks import slug_for, title_for

CASES = [
    ("Module 0 - Introduction.pdf", "00-introduction", "Module 0: Introduction"),
    ("Module 1 - Exploratory Data Analysis.pdf",
     "01-exploratory-data-analysis", "Module 1: Exploratory Data Analysis"),
    ("Module 3 - Feature Engineering.pdf",
     "03-feature-engineering", "Module 3: Feature Engineering"),
    ("Module 10 Prompt Engineering.pdf",
     "10-prompt-engineering", "Module 10: Prompt Engineering"),
    ("Module 12 -  Model Context Protocol.pdf",
     "12-model-context-protocol", "Module 12: Model Context Protocol"),
    ("Module 14 - Red Teaming AI.pdf",
     "14-red-teaming-ai", "Module 14: Red Teaming AI"),
    ("Final Project.pdf", "15-final-project", "Final Project"),
]


@pytest.mark.parametrize("pdf_name,slug,title", CASES)
def test_slug_and_title(pdf_name, slug, title):
    assert slug_for(pdf_name) == slug
    assert title_for(pdf_name) == title


def test_slugs_are_unique_across_the_course():
    assert len({slug_for(name) for name, _, _ in CASES}) == len(CASES)


def test_a_name_that_is_not_a_module_is_an_error():
    with pytest.raises(ValueError):
        slug_for("Bonus Deck.pdf")
    with pytest.raises(ValueError):
        title_for("Bonus Deck.pdf")
