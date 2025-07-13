from .gatekeeper_interface import GatekeeperInterface
from .security_policy_engine import SecurityPolicyEngine

class DependencyManager:
    """
    Manages dependency-related operations, routing them through the
    Security Gatekeeper and leveraging the Security Policy Engine for risk assessment.
    """
    def __init__(self):
        self.gatekeeper = GatekeeperInterface()
        self.policy_engine = SecurityPolicyEngine()

    def install_package(self, package_name: str, version: str = None):
        """
        Installs a package, routing the request through the security gatekeeper.
        """
        command_id = "deps:install"
        parameters = {"package": package_name}
        if version:
            parameters["version"] = version

        print(f"\nAttempting to install package: {package_name} (Command ID: {command_id})")
        
        # Check if human approval is required
        if self.policy_engine.requires_human_approval(command_id):
            print(f"  -> High-risk operation: '{command_id}' requires human approval.")
            # In a real scenario, this would trigger a human approval workflow
            # For now, we'll simulate a pending state.
            response = {
                "status": "human_approval_pending",
                "command_id": command_id,
                "message": "Human approval pending for high-risk dependency installation."
            }
        else:
            # Route through gatekeeper
            response = self.gatekeeper.send_command_to_gatekeeper(command_id, parameters)

        self._process_gatekeeper_response(response)

    def procure_new_dependency(self, package_name: str):
        """
        Procures a new, potentially unverified dependency, which is typically high-risk.
        """
        command_id = "deps:procure"
        parameters = {"package": package_name}

        print(f"\nAttempting to procure new dependency: {package_name} (Command ID: {command_id})")

        if self.policy_engine.requires_human_approval(command_id):
            print(f"  -> High-risk operation: '{command_id}' requires human approval.")
            response = {
                "status": "human_approval_pending",
                "command_id": command_id,
                "message": "Human approval pending for high-risk dependency procurement."
            }
        else:
            response = self.gatekeeper.send_command_to_gatekeeper(command_id, parameters)
        
        self._process_gatekeeper_response(response)

    def list_dependencies(self):
        """
        Lists installed dependencies, typically a low-risk operation.
        """
        command_id = "deps:list"
        print(f"\nAttempting to list dependencies (Command ID: {command_id})")

        # Low-risk operations might bypass stricter checks or go directly
        # In this simulation, all still go through the gatekeeper for consistency.
        response = self.gatekeeper.send_command_to_gatekeeper(command_id)
        self._process_gatekeeper_response(response)

    def _process_gatekeeper_response(self, response: dict):
        """Helper to process the gatekeeper's response."""
        status = response.get("status")
        command_id = response.get("command_id")
        message = response.get("message")
        stdout = response.get("stdout")
        stderr = response.get("stderr")
        error = response.get("error")

        print(f"  Gatekeeper Status for '{command_id}': {status}")
        if message:
            print(f"  Message: {message}")
        if stdout:
            print(f"  Stdout: {stdout}")
        if stderr:
            print(f"  Stderr: {stderr}")
        if error:
            print(f"  Error: {error.get('code')} - {error.get('message')}")

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    dep_manager = DependencyManager()

    dep_manager.list_dependencies()
    dep_manager.install_package("requests", "2.28.1")
    dep_manager.procure_new_dependency("unverified-new-library")
    dep_manager.install_package("trusted-internal-package") # This would be low-risk if defined as such