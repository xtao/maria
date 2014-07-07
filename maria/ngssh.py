# -*- coding: utf-8 -*-

import paramiko
from .gssh import GSSHServerInterface
import logging
logger = logging.getLogger(__name__)


class GSSHServer():

    def __init__(self):
        self.config = None

    def __call__(self, socket, address):
        client = None
        try:
            client = paramiko.Transport(socket)
            try:
                client.load_server_moduli()
            except Exception:
                logger.exception('Failed to load moduli -- gex will be unsupported.')
                raise

            client.add_server_key(self.config.host_key)
            server = GSSHServerInterface()
            try:
                client.start_server(server=server)
            except paramiko.SSHException:
                logger.exception('SSH negotiation failed.')
                return

            channel = self.auth(client, address)
            if not channel:
                return

            if not self.check_command(server, address):
                return

            server.main_loop(channel)
        except Exception:
            logger.exception('Caught Exception')
        finally:
            if client:
                client.close()
            return

    def auth(self, client, address):
        channel = client.accept(self.config.auth_timeout)
        if channel is None:
            logger.info('Auth timeout %s:%d' % address)
            return None
        return channel

    def check_command(self, server, address):
        if not server.event.wait(self.config.check_timeout):
            logger.info('Check timeout %s:%d' % address)
            return False
        return True
