import json
from .config import SecurityConfig

class GatekeeperInterface:
    """
    Provides an interface for agents to interact with the Security Gatekeeper.
    All command execution requests should be routed through this interface.
    """
    def __init__(self):
        self.config = SecurityConfig()
        self.gatekeeper_config = self.config.get_gatekeeper_config()
        if not self.gatekeeper_config:
            raise Exception("Failed to load security gatekeeper configuration.")

    def send_command_to_gatekeeper(self, command_id: str, parameters: dict = None) -> dict:
        """
        Simulates sending a command request to the security gatekeeper.
        In a real implementation, this would involve inter-process communication
        or an API call to the actual gatekeeper service.
        """
        request = {
            "command_id": command_id,
            "parameters": parameters if parameters is not None else {}
        }
        print(f"Simulating sending command to gatekeeper: {json.dumps(request, indent=2)}")

        # Placeholder for actual gatekeeper response
        # In a real system, this would be the response from the security-gatekeeper agent
        simulated_response = {
            "status": "success",
            "command_id": command_id,
            "stdout": f"Command '{command_id}' executed successfully by gatekeeper (simulated).",
            "stderr": "",
            "error": None
        }

        # Simulate a high-risk command requiring approval
        if command_id in self.config.get_risk_profiles().get("commandRiskMapping", {}) and \
           self.config.get_risk_profiles()["commandRiskMapping"][command_id] == "high":
            simulated_response["status"] = "human_approval_pending"
            simulated_response["message"] = f"Command '{command_id}' is high-risk and requires human approval."

        return simulated_response

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    gatekeeper = GatekeeperInterface()

    # Example low-risk command
    print("\n--- Testing Low-Risk Command ---")
    response_low_risk = gatekeeper.send_command_to_gatekeeper("deps:list")
    print(f"Gatekeeper Response (Low Risk): {json.dumps(response_low_risk, indent=2)}")

    # Example high-risk command
    print("\n--- Testing High-Risk Command ---")
    response_high_risk = gatekeeper.send_command_to_gatekeeper("deps:procure", {"package": "new-unverified-lib"})
    print(f"Gatekeeper Response (High Risk): {json.dumps(response_high_risk, indent=2)}")

    # Example command with parameters
    print("\n--- Testing Command with Parameters ---")
    response_params = gatekeeper.send_command_to_gatekeeper("deps:install", {"package": "requests", "version": "2.28.1"})
    print(f"Gatekeeper Response (With Params): {json.dumps(response_params, indent=2)}")