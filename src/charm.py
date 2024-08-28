#!/usr/bin/env python3

"""Charmed Operator for my sample service."""

import logging

import ops

logger = logging.getLogger(__name__)


class MySampleServiceCharm(ops.CharmBase):
    def __init__(self, framework):
        super().__init__(framework)
        self.pebble_service_name = "my-sample-service"
        self.container = self.unit.get_container("my-sample-service")
        framework.observe(
            self.on.my_sample_service_pebble_ready, self._update_layer_and_restart
        )

    def _update_layer_and_restart(self, event) -> None:
        self.unit.status = ops.MaintenanceStatus("Assembling Pebble layers")
        new_layer = self._pebble_layer.to_dict()
        try:
            services = self.container.get_plan().to_dict().get("services", {})
            if services != new_layer["services"]:
                self.container.add_layer(
                    "my_sample_service", self._pebble_layer, combine=True
                )
                logger.info("Added updated layer 'my_sample_service' to Pebble plan")

                self.container.restart(self.pebble_service_name)
                logger.info(f"Restarted '{self.pebble_service_name}' service")
        except ops.pebble.APIError:
            self.unit.status = ops.MaintenanceStatus(
                "Waiting for Pebble in workload container"
            )
            return

        self.unit.status = ops.ActiveStatus()

    @property
    def _pebble_layer(self):
        cmd = "/app/my-sample-service"
        pebble_layer = {
            "summary": "my sample service",
            "description": "pebble config layer for my sample service",
            "services": {
                self.pebble_service_name: {
                    "override": "replace",
                    "summary": "my sample service",
                    "command": cmd,
                    "startup": "enabled",
                }
            },
        }
        return ops.pebble.Layer(pebble_layer)


if __name__ == "__main__":
    ops.main(MySampleServiceCharm)
