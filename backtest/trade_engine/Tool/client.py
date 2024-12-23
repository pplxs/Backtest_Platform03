from .rpc_client import (
    SignedRPCClient,
    BIDSignedRPCClient, SBIDSignedRPCClient,
)
from django.conf import settings

# class OrderRPCClient(SignedRPCClient):
#     def __init__(self, uid, timeout=10, heartbeat=10):
#         url = settings.PUBLIC_ORDER_GATEWAY_RPC
#         self.uid = uid
#         super().__init__(url, remote_app_name="EE_APP_ORDER_MANAGER", timeout=timeout, heartbeat=heartbeat)