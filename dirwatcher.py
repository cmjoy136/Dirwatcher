import argparse
import os
import logging
import signal
import time
import datetime

__author__ = 'cmjoy136'


logger = logging.getLogger(__file__)
magic_pos = {}
watching_files = []
exit_flag = False


def watch_directory(args):
    global magic_pos
    global watching_files

    logger.info('Watching directory: {}, Polling Interval: {}, Magic Text: {}'.format(
                args.path, args.interval, args.magic
                ))

    # Keys are filname, value is where to start search look at dict and get list of files add to dict if not duplicate, log as new file
    absol_path = os.path.abspath(args.path)
    dir_files = os.listdir(absol_path)
    for file in dir_files:
        if file.endswith(args.ext) and file not in watching_files:
            logger.info('{} file is in {} directory'.format(file, args.path))
            watching_files.append(file)
            magic_pos[file] = 0

    # look through watching_files dict and comapare to files in dict
    # if file not in dict, log file and remove from dict
    for file in watching_files:
        if file not in dir_files:
            logger.info('{} file has been yeeted'.format(file))
            watching_files.remove(file)
            del magic_pos[file]

    # iterate through dict, open file at last line, start reading from point for magic text update last pos that was read in dict
    for file in watching_files:
        find_magic(file, args.magic, absol_path)


def find_magic(filename, magic, directory):
    global magic_pos
    global watching_files

    with open(directory + '/' + filename) as file:
        for line, current_line in enumerate(file.readlines(), 1):
            if magic in current_line and line > magic_pos[filename]:
                logger.info("{} was found at line {}".format(magic, line))
            if line > magic_pos[filename]:
                magic_pos[filename] += 1
        #  for line, current line, enumerate


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warn('Received ' + signames[sig_num])
    exit_flag = True


def create_parser():
    '''nothing yet'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                        help='Text file extension to watch')
    parser.add_argument('-i', '--interval', type=float,
                        default=1.0, help='Number of secs between polling')
    parser.add_argument('path', help='Directory path to watch')
    parser.add_argument('magic', help='String to watch for')
    return parser


def main():
    global exit_flag
    # Hook up two signals from OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s [%(threadName)-12s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    app_start_time = datetime.datetime.now()
    logger.info(
        '\n'
        '---------------------------------------------------------------------------\n'
        '       Running {0}\n'
        '       Started on {1}\n'
        '---------------------------------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )
    parser = create_parser()
    args = parser.parse_args()

    while not exit_flag:
        try:
            watch_directory(args)
        except KeyboardInterrupt:
            exit_flag = True

        time.sleep(args.interval)

    uptime = datetime.datetime.now() - app_start_time
    logger.info(
        '\n'
        '---------------------------------------------------------------------------\n'
        '       Stopped {0}\n'
        '       Uptime was {1}\n'
        '---------------------------------------------------------------------------\n'
        .format(__file__, str(uptime))
    )


if __name__ == '__main__':
    main()
