import datetime
import time
import grpc
import sys

from django.core.management.base import BaseCommand
from concurrent import futures
from django.utils import autoreload

from django_grpc.utils import (
    add_servicers,
    extract_handlers,
    create_server,
    create_ssl_server,
)


class Command(BaseCommand):
    help = "Run gRPC server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max_workers", type=int, help="Number of workers"
        )
        parser.add_argument(
            "--port", type=int, default=50051, help="Port number to listen"
        )
        parser.add_argument("--autoreload", action="store_true", default=False)
        parser.add_argument(
            "--list-handlers",
            action="store_true",
            default=False,
            help="Print all registered endpoints",
        )

    def handle(self, *args, **options):
        if options["autoreload"] is True:
            self.stdout.write("ATTENTION! Autoreload is enabled!")
            # autoreload.main(self._serve, None, options)
            autoreload.run_with_reloader(self._serve, **options)
        else:
            self._serve(**options)

    def _serve(self, max_workers, port, *args, **kwargs):
        from django.conf import settings

        config = getattr(settings, "GRPCSERVER", dict())

        autoreload.raise_last_exception()
        self.stdout.write("Starting server at %s" % datetime.datetime.now())

        if not config.get("authentication"):
            self.stdout.write("Starting basic grpcserver")
            server = create_server(max_workers, port)
        elif config.get("authentication") == "ssl":
            self.stdout.write("Starting ssl grpcserver")
            server = create_ssl_server(max_workers, port)
        server.start()

        self.stdout.write("Server is listening port %s" % port)

        if kwargs["list_handlers"] is True:
            self.stdout.write("Registered handlers:")
            for handler in extract_handlers(server):
                self.stdout.write("* %s" % handler)

        # since server.start() will not block,
        # a sleep-loop is added to keep alive
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0)
            sys.exit(0)
