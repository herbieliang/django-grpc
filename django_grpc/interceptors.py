import grpc


class SignatureValidationInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

        self._abortion = grpc.unary_unary_rpc_method_handler(abort)

    def intercept_service(self, continuation, handler_call_details):
        from django.conf import settings

        config = getattr(settings, "GRPCSERVER", dict())
        authentication = config.get("authentication")
        signature = config.get("signature")
        signature_data = config.get("signature_data")

        if signature and authentication == "ssl":
            method_name = handler_call_details.method.split("/")[-1]
            expected_metadata = list()
            # expected_metadata.append(("x-signature", method_name[::-1]))
            for key, val in signature_data.items():
                expected_metadata.append((key, val))

            for key, val in expected_metadata:
                if (key, val) not in handler_call_details.invocation_metadata:
                    return self._abortion
            return continuation(handler_call_details)
        else:
            return continuation(handler_call_details)
