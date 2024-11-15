from typing import Optional

from annet.bgp_models import ASN
from annet.generators import PartialGenerator
from annet.mesh.executor import MeshExecutionResult
from annet.storage import Device

from .helpers.router import AutonomusSystemIsNotDefined, bgp_asnum, bgp_mesh, router_id


class Bgp(PartialGenerator):
    
    TAGS = ["bgp", "routing"]
    
    def acl_cisco(self, _: Device) -> str:
        return """
        router bgp
            bgp
            neighbor
            redistribute connected
            maximum-paths
        """
    
    def run_cisco(self, device: Device):
        mesh_data: MeshExecutionResult = bgp_mesh(device)
        rid: Optional[str] = router_id(mesh_data)
        try:
            asnum: Optional[ASN] = bgp_asnum(mesh_data)
        except AutonomusSystemIsNotDefined as err:
            RuntimeError(f"Device {device.name} has more than one defined autonomus system: {err}")

        if not asnum or not rid:
            return
        with self.block("router bgp", asnum):
            yield "bgp router-id", rid
            yield "bgp log-neighbor-changes"

            if device.device_role.name == "ToR":
                yield "redistribute connected route-map CONNECTED"
                yield "maximum-paths 16"

            for peer in mesh_data.peers:
                # define peer group attrs
                yield "neighbor", peer.group_name, "peer-group"

                if peer.import_policy:
                    yield "neighbor", peer.group_name, "route-map", peer.import_policy, "in"
                if peer.export_policy:
                    yield "neighbor", peer.group_name, "route-map", peer.export_policy, "out"
                if peer.options.soft_reconfiguration_inbound:
                    yield "neighbor", peer.group_name, "soft-reconfiguration inbound"
                if peer.options.send_community:
                    yield "neighbor", peer.group_name, "send-community both"

                # define peers specific attrs
                yield "neighbor", peer.addr, "peer-group", peer.group_name
                yield "neighbor", peer.addr, "remote-as", peer.remote_as

