#! /bin/env python

import sys
import yaml
from bottle import Bottle, response
from helpers.postgresql import Postgresql


class PgStatus(object):
    def __init__(self, pg):
        self.pg = pg

    def status(self):
        code = 503
        if self.pg.is_leader():
            code = 200
            xlog_position = self.pg.query("SELECT pg_current_xlog_location();").fetchone()[0]
        else:
            xlog_position = self.pg.query("SELECT pg_last_xlog_replay_location();").fetchone()[0]

        response.status = code
        response.set_header('X-XLOG-POSTITION', xlog_position)


def main(args):
    with open(args[0]) as fh:
        config = yaml.load(fh.read())

    pg_status = PgStatus(Postgresql(config['postgresql']))

    app = Bottle()
    app.route('/', callback=pg_status.status)
    app.run(host='0.0.0.0', port='15433')


if __name__ == "__main__":
    main(sys.argv[1:])
