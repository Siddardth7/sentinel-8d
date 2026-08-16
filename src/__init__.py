"""Sentinel-8D reusable analysis helpers.

Three modules, one per stage of the traceback pipeline:

    load   -> acquire the raw dataset and map its schema
    clean  -> tidy to one row per part and define the fail label
    stats  -> univariate screening + multivariate isolation helpers

The notebook (notebooks/01_traceback.ipynb) imports from here so that logic is
written once and every number in the 8D traces back to a tested function.

Usage from the notebook:

    import sys; sys.path.append("..")     # make src importable from notebooks/
    from src import load, clean, stats
"""
