import signal
import logging
import argparse
import time
import os

"""custom logger"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('dirwatcher.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
searched_files = {}
exit_flag = True


def receive_signal(sig, stack):
    """Listener for SIGINT and SIGTERM"""
    logger.warning("Received signal: {}".format(sig))
    global exit_flag
    if sig == signal.SIGINT:
        exit_flag = False
    if sig == signal.SIGTERM:
        exit_flag = False


def find_magic(file, directory):
    """checks for magic word"""
    magic_word = 'beetlejuice'
    with open(directory + '/' + file) as f:
        for index, line in enumerate(f.readlines()):
            if magic_word in line and index not in searched_files[file]:
                logger.info('{} found at line {} in {}'
                            .format(magic_word, index + 1, file))
                searched_files[file].append(index)


def dir_watcher(args):
    directory = os.path.abspath(args.dir)
    log_files = [f for f in os.listdir(directory) if ".txt" in f]
    if len(log_files) > len(searched_files):
        for file in log_files:
            if file not in searched_files:
                logger.info(' {} found in {}'.format(file, args.dir))
                searched_files[file] = []
    elif len(log_files) < len(searched_files):
        for file in searched_files:
            if file not in log_files:
                logger.info(" {} removed from {}".format(file, args.dir))
                searched_files.pop(file, None)
    for file in log_files:
        find_magic(file, directory)


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Checks a directory for modified files")
    parser.add_argument('--dir', help="Directory to be checked")

    args = parser.parse_args()

    logger.info('Searching in {}'.format(args.dir))

    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    while exit_flag:
        try:
            dir_watcher(args)
        except IOError:
            logger.exception('There was an error opening the directory')
            time.sleep(5)
        except Exception:
            logger.exception('Unhandled exception')
            time.sleep(5)
    logger.info('Uptime: {} seconds'.format(time.time() - start_time))


if __name__ == '__main__':
        main()
