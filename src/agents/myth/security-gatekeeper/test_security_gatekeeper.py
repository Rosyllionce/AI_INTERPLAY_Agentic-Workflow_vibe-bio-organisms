import unittest
import json
import re
import subprocess
from unittest.mock import patch, MagicMock

# Conceptual representation of the security-gatekeeper's core logic
# This would be part of the actual agent's implementation, replicated here for testing.

ALLOW_LIST = {
    "RUN_ALL_TESTS": {
        "command": "npm",
        "args": ["test"],
        "param_schema": []
    },
    "RUN_SPECIFIC_TEST": {
        "command": "npm",
        "args": ["test", "--", "{0}"],
        "param_schema": [
            { "name": "filePath", "regex": "^[a-zA-Z0-9_\\-\\/\\.]+\\.test\\.js$" }
        ]
    },
    "LINT_DIRECTORY": {
        "command": "npx",
        "args": ["eslint", "{0}"],
        "param_schema": [
            { "name": "directoryPath", "regex": "^[a-zA-Z0-9_\\-\\/\\*]+$" }
        ]
    }
}

def execute_gatekeeper_command(request_json):
    """
    Simulates the core logic of the security-gatekeeper agent.
    This function is the target of our tests.
    """
    try:
        request = json.loads(request_json)
        command_id = request.get("command_id")
        parameters = request.get("parameters", [])
    except json.JSONDecodeError:
        return json.dumps({
            "status": "failure",
            "command_id": None,
            "error": {"code": "INVALID_JSON", "message": "Request is not valid JSON."}
        })

    if not command_id or command_id not in ALLOW_LIST:
        return json.dumps({
            "status": "failure",
            "command_id": command_id,
            "error": {"code": "INVALID_COMMAND_ID", "message": f"Command ID '{command_id}' is not in the allow-list."}
        })

    command_def = ALLOW_LIST[command_id]
    param_schema = command_def.get("param_schema", [])

    if len(parameters) != len(param_schema):
        return json.dumps({
            "status": "failure",
            "command_id": command_id,
            "error": {"code": "PARAMETER_VALIDATION_FAILED", "message": f"Incorrect number of parameters. Expected {len(param_schema)}, got {len(parameters)}."}
        })

    for i, param_def in enumerate(param_schema):
        if not re.match(param_def["regex"], parameters[i]):
            return json.dumps({
                "status": "failure",
                "command_id": command_id,
                "error": {"code": "PARAMETER_VALIDATION_FAILED", "message": f"Parameter '{param_def['name']}' failed validation."}
            })

    # If all checks pass, construct and "execute" the command
    final_args = [arg.format(*parameters) for arg in command_def["args"]]
    full_command = [command_def["command"]] + final_args

    # In a real scenario, this would call a secure subprocess execution method.
    # For this test, we'll just confirm the command is constructed correctly.
    return json.dumps({
        "status": "success",
        "command_id": command_id,
        "constructed_command": full_command,
        "output": {
            "stdout": "Simulated command execution successful.",
            "stderr": ""
        }
    })


class TestSecurityGatekeeper(unittest.TestCase):

    def test_execute_valid_command_no_params(self):
        """Tests a valid command without parameters."""
        request = json.dumps({"command_id": "RUN_ALL_TESTS"})
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["command_id"], "RUN_ALL_TESTS")
        self.assertEqual(response["constructed_command"], ["npm", "test"])

    def test_execute_valid_command_with_valid_params(self):
        """Tests a valid command with a valid parameter."""
        request = json.dumps({
            "command_id": "RUN_SPECIFIC_TEST",
            "parameters": ["src/tests/some_feature.test.js"]
        })
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["constructed_command"], ["npm", "test", "--", "src/tests/some_feature.test.js"])

    def test_reject_invalid_command_id(self):
        """Ensures an unknown command ID is rejected."""
        request = json.dumps({"command_id": "DELETE_EVERYTHING"})
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "failure")
        self.assertEqual(response["error"]["code"], "INVALID_COMMAND_ID")

    def test_reject_incorrect_parameter_count(self):
        """Ensures a request with the wrong number of parameters is rejected."""
        request = json.dumps({
            "command_id": "RUN_SPECIFIC_TEST",
            "parameters": ["param1", "param2"] # Expects 1
        })
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "failure")
        self.assertEqual(response["error"]["code"], "PARAMETER_VALIDATION_FAILED")

    def test_reject_parameter_failing_regex_validation(self):
        """Tests rejection of a parameter that fails its regex check."""
        request = json.dumps({
            "command_id": "RUN_SPECIFIC_TEST",
            "parameters": ["src/tests/invalid_file.js"] # Fails regex, missing '.test.js'
        })
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "failure")
        self.assertEqual(response["error"]["code"], "PARAMETER_VALIDATION_FAILED")

    def test_reject_bypass_attempt_with_shell_metacharacters(self):
        """Ensures parameters with shell metacharacters are rejected."""
        request = json.dumps({
            "command_id": "LINT_DIRECTORY",
            "parameters": ["src; rm -rf /"] # Malicious parameter
        })
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "failure")
        self.assertEqual(response["error"]["code"], "PARAMETER_VALIDATION_FAILED")
        self.assertIn("failed validation", response["error"]["message"])

    def test_reject_bypass_attempt_with_subcommand(self):
        """Ensures parameters that try to inject subcommands are rejected."""
        request = json.dumps({
            "command_id": "LINT_DIRECTORY",
            "parameters": ["src && ls"] # Malicious parameter
        })
        response = json.loads(execute_gatekeeper_command(request))
        self.assertEqual(response["status"], "failure")
        self.assertEqual(response["error"]["code"], "PARAMETER_VALIDATION_FAILED")

if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # In a real CI/CD pipeline, a test runner would discover and run these tests.
    # We will simulate this execution.
    
    # Create a Test Loader and a Test Suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSecurityGatekeeper)
    
    # Create a Test Runner
    runner = unittest.TextTestRunner()
    
    # Run the tests and capture the result
    print("Executing security-gatekeeper tests...")
    result = runner.run(suite)
    print("Test execution complete.")
    
    # We can programmatically check the results
    if result.wasSuccessful():
        print("All tests passed successfully.")
    else:
        print(f"Tests failed. Errors: {len(result.errors)}, Failures: {len(result.failures)}")
