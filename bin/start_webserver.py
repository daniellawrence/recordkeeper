#!/usr/bin/env python
import recordkeeper.web
import recordkeeper.settings

def main():
    webapp = recordkeeper.web.app
    webapp.debug = recordkeeper.settings.DEBUG
    webapp.run(recordkeeper.settings.WEBSERVER_HOST,
               recordkeeper.settings.WEBSERVER_PORT)

if __name__ == '__main__':
    main()