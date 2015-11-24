#!/usr/bin/env python
"""Provides a command-line API to ABX.task"""

import argparse
import os

from ABXpy.task import Task

def task_parser(input_args=None):
    """Parses arguments for the Task command line API

    :param str input_args: Optional. The argument string to be
        parsed. By default, the argument string is taken from
        sys.argv.

    :return: The parsed arguments, as returned by
        argparse.parse_args().

    """
    # The usage string is specified explicitly because the default
    # does not show that the mandatory arguments must come before the
    # optional ones; otherwise parsing is not possible because
    # optional arguments can have various numbers of inputs
    parser = argparse.ArgumentParser(
        prog='task.py',
        description='Specify and initialize a new ABX task, compute and '
        'display the statistics, and generate the ABX triplets and pairs.',
        usage='%(prog)s database [output] -o ON [--help] [--verbose] '
        '[-a ACROSS [ACROSS ...]] [-b BY [BY ...]] '
        '[-f FILT [FILT ...]] [-r REG [REG ...]] '
        '[-s SAMPLING_AMOUNT_OR_PROPORTION] '
        '[--stats-only] [--no-verif] [--features FEATURE_FILE]'
        '[--threshold THRESHOLD]')

    message = 'must be columns defined by the database you are using '
    '(e.g. speaker or phonemes, if your database contains such columns)'

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    # I/O files
    g1 = parser.add_argument_group('I/O files')

    g1.add_argument('database',
                    help='main file of the database defining the items used to'
                    ' form ABX triplets and their attributes')

    # TODO what if output file non provided ? Test/document it
    g1.add_argument('output', nargs='?', default=None,
                    help='optional: output file, where the results of the '
                         'analysis will be put. If the --stats-only is used '
                         'this argument is mandatory.')

    # Task specification
    g2 = parser.add_argument_group('Task specification')

    # TODO force str and remove append on --on
    g2.add_argument('-o', '--on', required=True, action='append',
                    help='ON attribute, ' + message)

    g2.add_argument('-a', '--across',  nargs='+', default=[], action='append',
                    help='optional: ACROSS attribute(s), ' + message)

    g2.add_argument('-b', '--by', nargs='+', default=[], action='append',
                    help='optional: BY attribute(s), ' + message)

    g2.add_argument('-f', '--filter', nargs='+', default=[],
                    help='optional: filter specification(s), ' + message)

    g2.add_argument('-s', '--sample', default=None, type=float,
                    help='optional: if a real number in ]0;1[: sampling '
                         'proportion, if a strictly positive integer: number '
                         'of triplets to be sampled')
    g2.add_argument('-t', '--threshold', default=None, type=int,
                    help='optional: threshold on the maximal size of a block of'
                         ' triplets sharing the same regressors, triplets may '
                         'be sampled')
    # Regressors specification
    g3 = parser.add_argument_group('Regressors specification')

    g3.add_argument('-r', '--regressor', nargs='+', default=[],
                    help='optional: regressor specification(s), ' + message)

    # Computation parameters
    g4 = parser.add_argument_group('Computation parameters')

    g4.add_argument('--stats-only', default=False, action='store_true',
                    help='add this flag if you only want some statistics '
                         'about the specified task')

    g4.add_argument('--no-verif', default=False, action='store_true',
                    help='optional: skip the verification of the database '
                         'file consistancy')

    g4.add_argument('--features',
                    help='optional: feature file, verify the consistency '
                         'of the feature file with the item file')

    # if input_args is given, split the string
    if input_args:
        input_args = input_args.split()

    # Parse the parameters
    args = parser.parse_args(input_args)

    # Consistency checks
    if args.stats_only:
        # TODO silly condition, can write stats on stdout...
        assert args.output, ('Error: --stats-only requires an output '
                             'file to be provided.')

    elif args.output and os.path.exists(args.output):
        if args.verbose:
            print("WARNING: Overwriting existing task file " + args.output)
        os.remove(args.output)

        if args.sample and args.threshold:
            warnings.warn('The use of sampling AND threshold is not '
                          'tested yet', UserWarning)

    # BY and ACROSS can accept several arguments either with '--by 1 2
    # 3' or '--by 1 --by 2 3'. Thus we need to join sublists in a
    # unique top-level list (i.e. [[1], [2,3]] becomes [1,2,3])
    args.by = sum(args.by, [])
    args.across = sum(args.across, [])

    # Task.__init__ need args.on being a unique string, not a list
    assert len(args.on) == 1, 'Error: --on requires a unique string'
    args.on = args.on[0]

    return args


# TODO maybe some problems if wanting to pass some code directly on the
# command-line if it contains something like s = "'a'==1 and 'b'==2" ? but
# not a big deal ?
def main():
    """Command line API of the Task class

    Example call:

    .. code-block:: bash

        python task.py --help
        python task.py data.item --on word --across talker --by length
        python task.py data.item -o c1 -b c2 c3 -f "[a == 0 for a in c3_X]"

    """
    # Parse input arguments
    args = task_parser()

    # Create a task instance with parsed parameters
    task = Task(args.database, args.on, args.across, args.by,
                args.filter, args.regressor, args.verbose)

    # Do the requested processing depending on --stats-only
    if args.stats_only:
        task.print_stats()
    else:
        task.generate_triplets(args.output, args.sample, args.threshold)


if __name__ == '__main__':
    main()