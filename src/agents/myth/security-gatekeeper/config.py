import json
import os

class SecurityConfig:
    """
    Manages the loading and access of security-related configurations
    from JSON files.
    """
    def __init__(self, base_path='src'):
        self.base_path = base_path
        self.security_gatekeeper_path = os.path.join(self.base_path, 'security_gatekeeper.json')
        self.security_risk_profiles_path = os.path.join(self.base_path, 'security_risk_profiles.json')

    def _load_json(self, file_path):
        """Helper to load JSON files."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {file_path}")
            return None

    def get_gatekeeper_config(self):
        """Loads and returns the security gatekeeper configuration."""
        return self._load_json(self.security_gatekeeper_path)

    def get_risk_profiles(self):
        """Loads and returns the security risk profiles."""
        return self._load_json(self.security_risk_profiles_path)

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    config = SecurityConfig(base_path='../src') # Adjust path for direct execution
    gatekeeper_conf = config.get_gatekeeper_config()
    risk_profiles = config.get_risk_profiles()

    if gatekeeper_conf:
        print("Security Gatekeeper Config Loaded:")
        print(json.dumps(gatekeeper_conf, indent=2))

    if risk_profiles:
        print("\nSecurity Risk Profiles Loaded:")
        print(json.dumps(risk_profiles, indent=2))