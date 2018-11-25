import json
import logging
import os

from vehicle.core.sink import Sink


logger = logging.getLogger(__name__)


class FileSink(Sink):

    name = 'file'

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    async def start(self):
        path = os.path.abspath(self.filename)
        logger.info('Writing data to %s', path)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.file = open(path, 'a')

    async def stop(self):
        self.file.close()

    async def submit(self, data):
        self.file.write(json.dumps(data))
        self.file.write('\n')
        self.file.flush()
