import time
import json
import os

class HumanApprovalWorkflow:
    def __init__(self, approval_file_path='src/security/approvals.json'):
        self.approval_file_path = approval_file_path
        self.pending_approvals = self._load_approvals()

    def _load_approvals(self):
        if os.path.exists(self.approval_file_path):
            try:
                with open(self.approval_file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {self.approval_file_path}. Starting with empty approvals.")
                return {}
        return {}

    def _save_approvals(self):
        os.makedirs(os.path.dirname(self.approval_file_path), exist_ok=True)
        with open(self.approval_file_path, 'w') as f:
            json.dump(self.pending_approvals, f, indent=2)

    def request_approval(self, command_id: str, description: str) -> str:
        if command_id not in self.pending_approvals:
            self.pending_approvals[command_id] = {
                "status": "pending",
                "timestamp": time.time(),
                "description": description
            }
            self._save_approvals()
            print(f"\n--- Human Approval Requested ---")
            print(f"Command ID: {command_id}")
            print(f"Description: {description}")
            print(f"Status: PENDING. Awaiting human decision...")
        else:
            print(f"\nApproval for Command ID {command_id} is already {self.pending_approvals[command_id]['status']}.")
        
        return self.pending_approvals[command_id]["status"]

    def get_approval_status(self, command_id: str) -> str:
        return self.pending_approvals.get(command_id, {}).get("status", "not_found")

    def approve_command(self, command_id: str) -> bool:
        if command_id in self.pending_approvals and self.pending_approvals[command_id]["status"] == "pending":
            self.pending_approvals[command_id]["status"] = "approved"
            self._save_approvals()
            print(f"\n--- Human Approval Granted ---")
            print(f"Command ID: {command_id} has been APPROVED.")
            return True
        print(f"\n--- Approval Failed ---")
        print(f"Command ID {command_id} is not pending or does not exist.")
        return False

    def deny_command(self, command_id: str) -> bool:
        if command_id in self.pending_approvals and self.pending_approvals[command_id]["status"] == "pending":
            self.pending_approvals[command_id]["status"] = "denied"
            self._save_approvals()
            print(f"\n--- Human Approval Denied ---")
            print(f"Command ID: {command_id} has been DENIED.")
            return True
        print(f"\n--- Denial Failed ---")
        print(f"Command ID {command_id} is not pending or does not exist.")
        return False

# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    # Clean up previous approvals.json for a fresh start
    if os.path.exists('approvals.json'):
        os.remove('approvals.json')

    approval_workflow = HumanApprovalWorkflow(approval_file_path='approvals.json')

    # Request approval for a high-risk operation
    cmd_id_1 = "deps:procure_new_lib"
    approval_workflow.request_approval(cmd_id_1, "Procure new unverified library 'super-lib-v1.0'")

    # Check status
    print(f"Current status of '{cmd_id_1}': {approval_workflow.get_approval_status(cmd_id_1)}")

    # Simulate approval
    approval_workflow.approve_command(cmd_id_1)
    print(f"Current status of '{cmd_id_1}': {approval_workflow.get_approval_status(cmd_id_1)}")

    # Request approval for another command
    cmd_id_2 = "system:format_disk"
    approval_workflow.request_approval(cmd_id_2, "Format production database disk")

    # Simulate denial
    approval_workflow.deny_command(cmd_id_2)
    print(f"Current status of '{cmd_id_2}': {approval_workflow.get_approval_status(cmd_id_2)}")

    # Try to approve an already denied command
    approval_workflow.approve_command(cmd_id_2)

    # Verify persistence by creating a new instance
    print("\n--- Verifying Persistence ---")
    persisted_workflow = HumanApprovalWorkflow(approval_file_path='approvals.json')
    print(f"Persisted status of '{cmd_id_1}': {persisted_workflow.get_approval_status(cmd_id_1)}")
    print(f"Persisted status of '{cmd_id_2}': {persisted_workflow.get_approval_status(cmd_id_2)}")