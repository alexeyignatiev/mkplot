#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## plot.py
##
##  Created on: Jun 05, 2015
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
import matplotlib.pyplot as plt
import numpy as np
import os


#
#==============================================================================
class Plot():
    """
        Basic plotting class.
    """

    def __init__(self, options):
        """
            Constructor.
        """

        self.alpha       = options['alpha']
        self.backend     = options['backend']
        self.save_to     = options['save_to']
        self.def_path    = options['def_path']
        self.transparent = options['transparent']

        self.timeout = options['timeout']
        self.t_label = options['t_label']
        self.tlb_loc = options['tlb_loc']

        self.x_label = options['x_label']
        self.x_log   = options['x_log']
        self.x_max   = options['x_max']
        self.x_min   = options['x_min']
        self.y_label = options['y_label']
        self.y_log   = options['y_log']
        self.y_max   = options['y_max']
        self.y_min   = options['y_min']

        self.lgd_loc    = options['lgd_loc']
        self.lgd_ncol   = options['lgd_ncol']
        self.lgd_alpha  = options['lgd_alpha']
        self.lgd_fancy  = options['lgd_fancy']
        self.lgd_shadow = options['lgd_shadow']

        self.no_grid    = options['no_grid']
        self.grid_color = options['grid_color']
        self.grid_style = options['grid_style']
        self.grid_width = options['grid_width']
        self.byname     = options['by_name']

        # where to save
        self.save_to = '{0}.{1}'.format(os.path.splitext(self.save_to)[0], self.backend)

        # font properties
        self.f_props = {'serif': ['Times'], 'sans-serif': ['Helvetica'],
        'weight': 'normal', 'size': options['font_sz']}

        if options['font'].lower() in ('sans', 'sans-serif', 'helvetica'):  # Helvetica
            self.f_props['family'] = 'sans-serif'
        elif options['font'].lower() in ('serif', 'times'):  # Times
            self.f_props['family'] = 'serif'
        elif options['font'].lower() == 'cmr':  # Computer Modern Roman
            self.f_props['family'] = 'serif'
            self.f_props['serif'] = 'Computer Modern Roman'
        elif options['font'].lower() == 'palatino':  # Palatino
            self.f_props['family'] = 'serif'
            self.f_props['serif'] = 'Palatino'

        plt.rc('text', usetex=options['usetex'])
        plt.rc('font', **self.f_props)

        # figure properties
        nof_subplots = 1
        fig_width_pt = 252.0  # Get this from LaTeX using \showthe\columnwidth
        inches_per_pt = 1.0 / 72.27                           # Convert pt to inch
        golden_mean = (np.sqrt(5) + 1.0) / 2.0                # Aesthetic ratio
        fig_width = fig_width_pt * inches_per_pt + 0.2        # width in inches
        fig_height = fig_width / golden_mean * nof_subplots + 0.395 * (nof_subplots - 1)  # height in inches
        if options['shape'] == 'squared':
            fig_width = fig_height
        elif len(options['shape']) >= 4 and options['shape'][:4] == 'long':
            coeff = options['shape'][4:]
            fig_width *= 1.2 if not coeff else float(coeff)  # default coefficient is 1.2

        fig_size = [fig_width * 2.5, fig_height * 2.5]

        params = {'backend': 'pdf', 'text.usetex': options['usetex'], 'figure.figsize': fig_size}

        plt.rcParams.update(params)

        # choosing backend
        if self.backend in ('pdf', 'ps', 'svg'):  # default is pdf
            plt.switch_backend(self.backend)
        elif self.backend == 'pgf':  # PGF/TikZ
            pgf_params = {'pgf.texsystem': 'pdflatex',
                          'pgf.preamble': [r'\usepackage[utf8x]{inputenc}', r'\usepackage[T1]{fontenc}']}
            params.update(pgf_params)
            plt.rcParams.update(params)
            plt.switch_backend(self.backend)
        elif self.backend == 'png':
            plt.switch_backend('agg')

        # funny mode
        if options['xkcd']:
            plt.xkcd()
