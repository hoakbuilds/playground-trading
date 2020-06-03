__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import os
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from typing import Dict, Any
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff


class Plotter:
    """Abstract plotter."""

    df: pd.DataFrame
    indicators: Dict[str, Any]
    fig: go.Figure

    def __init__(self, df: pd.DataFrame = None, indicators: Dict[str, Any] = None):

        if not df:
            raise ValueError(
                """
                df: DataFrame must be passed.
                """
            )

        if not indicators:
            raise ValueError(
                """
                df: Dict[str, Any] must be passed.
                """
            )
        self.df = df
        self.indicators = indicators

    def plot(self):

        self.fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.timestamp,
                    open=df.open,
                    high=df.high,
                    low=df.low,
                    close=df.close,
                )
            ]
        )
        self

        self.fig.update_layout(xaxis_rangeslider_visible=False)
        self.fig.show()