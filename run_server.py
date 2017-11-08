# -*- coding: utf-8 -*-
'''
    Web服务
'''
import os
import logging
import config
import utils

from server import dataserver

if __name__ == '__main__':
    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/server.log',
        format='%(levelname)s %(asctime)s: %(message)s',
        level=logging.INFO
    )

    utils.kill_ports([config.data_port])

    dataserver.app.run(
        debug=False,
        host='0.0.0.0',
        port=config.data_port,
    )
