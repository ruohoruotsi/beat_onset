#!/usr/bin/env python
# CREATED:2013-10-14 16:28:09 by Brian McFee <brm2132@columbia.edu>
#  beat prediction evaluator

import sys
import os
import glob
import argparse

import numpy as np
import mir_eval

from joblib import Parallel, delayed

# bins for information gain, set to match holzapfel'12
HEADER = 'Cemgil, CMLc, CMLt, AMLc, AMLt, F-Meas, Goto, I.Gain, P_score'

def process_file(input_file, **kw):

    # First, get the ground truth file
    raw = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.sep.join([kw['destination'], os.path.extsep.join([raw, 'scores', 'txt'])])
    raw = raw.split(os.path.extsep)[0]
    truth_file = os.path.sep.join([kw['truth_path'], os.path.extsep.join([raw, 'txt'])])

    try:
        print input_file, truth_file

        prediction   = mir_eval.io.load_events(input_file)[0]
        truth        = mir_eval.io.load_events(truth_file)[0]
        scores = []
        scores.append(mir_eval.beat.cemgil(truth, prediction)[0])
        scores.extend(mir_eval.beat.continuity(truth, prediction))
        scores.append(mir_eval.beat.f_measure(truth, prediction))
        scores.append(mir_eval.beat.goto(truth, prediction))
        scores.append(mir_eval.beat.information_gain(truth, prediction))
        scores.append(mir_eval.beat.p_score(truth, prediction))
        scores = np.array([scores])

    except:
        print 'Empty prediction file: ', raw
        scores  = np.zeros((1,9))

    np.savetxt(output_file, scores, delimiter=',', fmt='%0.4f', header=HEADER)

def process_args():

    parser = argparse.ArgumentParser(description='Beat tracking evaluator')

    parser.add_argument(    'input_glob',
                            action      =   'store',
                            help        =   'glob-string for input files')

    parser.add_argument(    'truth_path',
                            action      =   'store',
                            help        =   'path to ground-truth labels')
    
    parser.add_argument(    'destination',
                            action      =   'store',
                            help        =   'path to store score files')
    
    parser.add_argument(    '-j',
                            '--num_jobs',
                            dest        =   'num_jobs',
                            required    =   False,
                            type        =   int,
                            default     =   1,
                            help        =   'Number of parallel jobs')


    return vars(parser.parse_args(sys.argv[1:]))

if __name__ == '__main__':
    parameters  = process_args()
    files       = sorted(glob.glob(parameters['input_glob']))

    Parallel(n_jobs=parameters['num_jobs'],
            verbose=5)(delayed(process_file)(input_file, **parameters) for input_file in
            files)
