#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## statutil.py
##
##  Created on: May 22, 2013
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

#
#==============================================================================
from __future__ import print_function
import json
import sys


#
#==============================================================================
class JSONException(Exception):
    pass


#
#==============================================================================
class Stat:
    """
        Simple statistical data class.
    """

    def __init__(self, filename=None):
        """
            Constructor.
        """

        if filename is None:
            self.insts_own = []
            self.preamble = {}
            self.data = {}
        elif type(filename) is list:
            print( 'in case of several files use "StatArray" class', file=sys.stderr)
        else:
            self.read(filename)

    def read(self, filename=None):
        """
            Reads a file into a Stat object.
        """

        if filename is None:
            print( 'no filename was specified', file=sys.stderr)
            return

        with open(filename, 'r') as fp:
            print('reading {0}'.format(filename), file=sys.stderr)
            try:
                data_full = json.load(fp)
            except:
                raise JSONException('Unable to parse \'{0}\'.'.format(filename))

            self.data = data_full['stats']
            self.preamble = data_full['preamble']
            self.preamble['origin'] = filename

        self.insts_own = sorted(list(set(self.data.keys())))

    def write(self, to=None):
        """
            Writes a Stat object to a file.
        """

        to_write = {'preamble': self.preamble, 'stats': self.data}

        if to is None:
            to = self.preamble['origin']

        # 'origin' field is not needed anymore
        del(self.preamble['origin'])

        if type(to) is str:
            with open(to, 'w') as fp:
                json.dump(to_write, fp, indent=4, separators=(',', ': '))
        elif type(to) is file:
            json.dump(to_write, to, indent=4, separators=(',', ': '))
        else:
            print('don\'t know how to write to {0}'.format(type(to)), file=sys.stderr)

    def update(self, success=None, failure=None):
        """
            Updates stats using additional success and failure signs.
        """

        if success:
            pass

        if failure:
            sign = lambda x: x
            key = failure
            if failure[:3] == 'no-':
                sign = lambda x: not x
                key = failure[3:]

            for inst in self.insts_own:
                if inst in self.data and self.data[inst]['status'] == True:
                    if sign(key in self.data[inst]):
                        print('updating', inst, file=sys.stderr)
                        self.data[inst]['status'] = False

        self.write()


    def list(self, crit=None):
        """
            Lists instances satisfying the criterion.
        """

        if crit:
            pred = lambda x: x == crit['val']
            if crit['pred'] == '<':
                pred = lambda x: x < crit['val']
            elif crit['pred'] == '<=':
                pred = lambda x: x <= crit['val']
            elif crit['pred'] == '>':
                pred = lambda x: x > crit['val']
            elif crit['pred'] == '>=':
                pred = lambda x: x >= crit['val']

            for inst in self.insts_own:
                if inst in self.data and self.data[inst]['status'] == True:
                    if pred(self.data[inst][crit['key']]):
                        print('{0}: {1} = {2}'.format(inst, crit['key'], self.data[inst][crit['key']]))


#
#==============================================================================
class StatArray:
    """
        Contains statistical data for several files.
    """

    def __init__(self, files=None):
        """
            Constructor.
        """

        if files is None:
            self.inst_full = []
            self.stat_objs = []
        elif type(files) is list:
            self.read(files)
        else:
            print('in case of just one file use "Stat" class', file=sys.stderr)
            self.read([files])

    def __getitem__(self, key):
        if key < len(self.stat_objs):
            return self.stat_objs[key]

    def __len__(self):
        return len(self.stat_objs)

    def __iter__(self):
        for stat_obj in self.stat_objs:
            yield stat_obj

    def read(self, files=None):
        """
            Reads several files into a StatArray object.
        """

        if files is None:
            print('no files was specified', file=sys.stderr)
            return

        self.stat_objs = []
        for f in files:
            self.stat_objs.append(Stat(f))

        inst_set = set()
        for stat_obj in self.stat_objs:
            inst_set = inst_set.union(set(stat_obj.insts_own))
        self.inst_full = sorted(list(inst_set))

    def write(self, files=None):
        """
            Writes a StatArray object to given files.
        """

        if files is None:
            files = [stat_obj.preamble['origin'] for stat_obj in self.stat_objs]

        assert len(files) == len(self.stat_objs), 'wrong number of filenames'

        for f, stat_obj in zip(files, self.stat_objs):
            stat_obj.write(f)

    def cluster(self, use_key=['program', 'prog_args']):
        """
            Clasters Stat objects according to their preamble values.
        """

        # the key should be a list
        if type(use_key) is not list:
            use_key = [use_key]

        clusters = {}

        for stat_obj in self.stat_objs:
            # updating the Stat object
            for i, i_old in enumerate(stat_obj.insts_own):
                i_new = '{0}@{1}'.format(i_old, stat_obj.preamble['benchmark'])
                stat_obj.insts_own[i] = i_new
                stat_obj.data[i_new] = stat_obj.data.pop(i_old)

            key = ' '.join([stat_obj.preamble[one_key] for one_key in use_key])
            if key in clusters:
                # update the cluster
                clusters[key].insts_own.extend(stat_obj.insts_own)
                clusters[key].data.update(stat_obj.data)

                clusters[key].preamble['benchmark'].append(stat_obj.preamble['benchmark'])
                clusters[key].preamble['runsolver_args'].append(stat_obj.preamble['runsolver_args'])
            else:
                # add new cluster
                clusters[key] = stat_obj
                clusters[key].preamble['benchmark'] = [clusters[key].preamble['benchmark']]
                clusters[key].preamble['runsolver_args'] = [clusters[key].preamble['runsolver_args']]

        self.stat_objs = [cl for cl in clusters.values()]

        inst_set = set()
        for stat_obj in self.stat_objs:
            inst_set = inst_set.union(set(stat_obj.insts_own))
        self.inst_full = sorted(list(inst_set))

    def unclaster(self):
        """
            Unclasters previously clastered Stat objects.
        """

        print('unclaster() method is not implemented yet', file=sys.stderr)

    def make_vbs(self, addit_key=None):
        """
            Makes vbs using the status, rtime and additional key as the measurement.
            NOTE: the use of addit_key is not implemented yet.
        """

        vbs = Stat()
        vbs.insts_own = self.inst_full

        vbs.preamble = self.stat_objs[0].preamble
        vbs.preamble['program'] = 'vbs'
        vbs.preamble['prog_args'] = ''
        vbs.preamble['origin'] = [obj.preamble['origin'] for obj in self.stat_objs]

        for inst in self.inst_full:
            alts = []
            for stat_obj in self.stat_objs:
                if inst in stat_obj.data and stat_obj.data[inst]['status'] == True:
                    alts.append(stat_obj.data[inst])

            if alts:
                vbs.data[inst] = min(alts, key=lambda x: x['rtime'])
            else:
                # all fail; choose any:
                vbs.data[inst] = self.stat_objs[0].data[inst]

        self.stat_objs.append(vbs)

    def compare(self, cmp_key=None):
        """
            Compares values for a specific key. Do nothing if cmp_key is None.
        """

        if cmp_key:
            for inst in self.inst_full:
                vals = {}

                for stat_obj in self.stat_objs:
                    if inst in stat_obj.data and stat_obj.data[inst]['status'] == True and cmp_key in stat_obj.data[inst]:
                        if stat_obj.data[inst][cmp_key] in vals:
                            vals[stat_obj.data[inst][cmp_key]].append(stat_obj.preamble['origin'])
                        else:
                            vals[stat_obj.data[inst][cmp_key]] = [stat_obj.preamble['origin']]

                if len(vals.keys()) > 1:
                    print('different values found', file=sys.stderr)
                    print('instance:', inst, file=sys.stderr)
                    print('values:', vals, file=sys.stderr)

    def list_simple(self, to_list='all'):
        """
            Shows instances required by user.
        """

        if to_list:
            print('showing {0}:'.format(to_list))
            if to_list == 'all':
                for inst in self.inst_full:
                    print(inst)

            else:
                status = False if to_list == 'failed' else True

                for inst in self.inst_full:
                    objs = []

                    for stat_obj in self.stat_objs:
                        if inst in stat_obj.data and stat_obj.data[inst]['status'] == status:
                            p = stat_obj.preamble
                            if 'prog_alias' in p:
                                objs.append(p['prog_alias'])
                            else:
                                objs.append(p['program'] + ' ' + p['prog_args'])

                    if objs:
                        if len(self.stat_objs) > 1:
                            objs = '[{0}]'.format(', '.join(obj for obj in objs))
                            print('{0}: {1}'.format(inst, objs))
                        else:
                            print(inst)

    def list(self, crit=None):
        """
            Shows instances required by user.
        """

        if crit:
            for stat_obj in self.stat_objs:
                stat_obj.list(crit)

    def update(self, success=None, failure=None):
        """
            Update stats using additional success and failure signs.
        """

        if success or failure:
            for stat_obj in self.stat_objs:
                stat_obj.update(success, failure)
