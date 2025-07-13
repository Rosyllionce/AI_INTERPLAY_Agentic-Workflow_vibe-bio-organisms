from .config import SecurityConfig

class SecurityPolicyEngine:
    """
    Evaluates the risk level of operations based on predefined security risk profiles.
    """
    def __init__(self):
        self.config = SecurityConfig()
        self.risk_profiles_data = self.config.get_risk_profiles()
        if not self.risk_profiles_data:
            raise Exception("Failed to load security risk profiles.")

    def get_risk_level(self, command_id: str) -> str:
        """
        Determines the risk level for a given command ID.
        Defaults to 'medium' if not explicitly mapped.
        """
        command_risk_mapping = self.risk_profiles_data.get("commandRiskMapping", {})
        default_risk_level = self.risk_profiles_data.get("defaultRiskLevel", "medium")
        return command_risk_mapping.get(command_id, default_risk_level)

    def requires_human_approval(self, command_id: str) -> bool:
        """
        Checks if a command requires human approval based on its risk level.
        """
        risk_level = self.get_risk_level(command_id)
        for profile in self.risk_profiles_data.get("riskProfiles", []):
            if profile.get("level") == risk_level:
                return profile.get("humanApprovalRequired", False)
        return False # Default to no human approval if risk level not found

    def can_bypass_stricter_checks(self, command_id: str) -> bool:
        """
        Checks if a command can bypass stricter security checks.
        """
        risk_level = self.get_risk_level(command_id)
        for profile in self.risk_profiles_data.get("riskProfiles", []):
            if profile.get("level") == risk_level:
                return profile.get("bypassChecks", False)
        return False # Default to no bypass if risk level not found

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    policy_engine = SecurityPolicyEngine()

    print("\n--- Testing Risk Levels and Approvals ---")
    commands = ["deps:list", "deps:install", "deps:procure", "unknown:command"]
    for cmd in commands:
        risk = policy_engine.get_risk_level(cmd)
        approval = policy_engine.requires_human_approval(cmd)
        bypass = policy_engine.can_bypass_stricter_checks(cmd)
        print(f"Command: '{cmd}' | Risk: {risk} | Human Approval: {approval} | Bypass Checks: {bypass}")