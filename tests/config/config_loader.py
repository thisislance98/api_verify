#!/usr/bin/env python3
"""
Configuration Loader for Test Accounts
Loads test account credentials from test_accounts.json
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Loads and manages test configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize config loader
        
        Args:
            config_file: Path to config file (default: test_accounts.json in same directory)
        """
        if config_file is None:
            config_file = Path(__file__).parent / "test_accounts.json"
        
        self.config_file = Path(config_file)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            self._config = json.load(f)
    
    def get_environment(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Get environment configuration
        
        Args:
            environment: Environment name (integration, us2, eu2, apj1, uspscc)
                        If None, uses default_environment from config
        
        Returns:
            Dictionary with environment configuration
        """
        if environment is None:
            environment = self._config.get('default_environment', 'integration')
        
        if environment not in self._config['environments']:
            available = ', '.join(self._config['environments'].keys())
            raise ValueError(f"Environment '{environment}' not found. Available: {available}")
        
        return self._config['environments'][environment]
    
    def get_account(self, account_role: Optional[str] = None, 
                   environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account credentials for a specific role
        
        Args:
            account_role: Role name (e.g., 'manager_approver', 'expense_user', 'delegate_user')
                         If None, uses default_account_role from config
            environment: Environment name (default: from config)
        
        Returns:
            Dictionary with account credentials
        """
        env_config = self.get_environment(environment)
        
        if account_role is None:
            account_role = self._config.get('default_account_role', 'manager_approver')
        
        if account_role not in env_config['accounts']:
            available = ', '.join(env_config['accounts'].keys())
            raise ValueError(f"Account role '{account_role}' not found in {env_config['name']}. Available: {available}")
        
        return env_config['accounts'][account_role]
    
    def get_credentials(self, account_role: Optional[str] = None,
                       environment: Optional[str] = None) -> Dict[str, str]:
        """
        Get complete credentials for SDK initialization
        
        Args:
            account_role: Role name
            environment: Environment name
        
        Returns:
            Dictionary with all credentials needed for SDK
        """
        env_config = self.get_environment(environment)
        account = self.get_account(account_role, environment)
        
        return {
            'client_id': env_config['client_id'],
            'client_secret': env_config['client_secret'],
            'username': account['username'],
            'password': account['password'],
            'base_url': env_config['api_base_url'],
            'token_url': env_config['token_url'],
            'environment': environment or self._config.get('default_environment'),
            'entity_code': env_config['entity_code'],
            'company_uuid': env_config['company_uuid'],
            'role': account['role']
        }
    
    def list_environments(self) -> list:
        """List all available environments"""
        return list(self._config['environments'].keys())
    
    def list_accounts(self, environment: Optional[str] = None) -> list:
        """
        List all available account roles in an environment
        
        Args:
            environment: Environment name
        
        Returns:
            List of account role names
        """
        env_config = self.get_environment(environment)
        return list(env_config['accounts'].keys())
    
    def print_available_configs(self):
        """Print all available environments and accounts"""
        print("Available Test Configurations:")
        print("=" * 80)
        
        for env_name in self.list_environments():
            env = self.get_environment(env_name)
            print(f"\n{env['name']} ({env_name})")
            print(f"  CTE URL: {env['cte_url']}")
            print(f"  API URL: {env['api_base_url']}")
            print(f"  Entity: {env['entity_code']}")
            print(f"  Accounts:")
            
            for account_role in self.list_accounts(env_name):
                account = self.get_account(account_role, env_name)
                print(f"    - {account_role}: {account['username']} ({account['role']})")
        
        print("\n" + "=" * 80)


# Convenience function for quick access
def get_test_credentials(account_role: Optional[str] = None, 
                         environment: Optional[str] = None) -> Dict[str, str]:
    """
    Quick function to get test credentials
    
    Args:
        account_role: Account role (default: manager_approver)
        environment: Environment (default: integration)
    
    Returns:
        Dictionary with credentials
    
    Example:
        >>> creds = get_test_credentials('manager_approver', 'integration')
        >>> sdk = ConcurExpenseSDK(ConcurConfig(**creds))
    """
    loader = ConfigLoader()
    return loader.get_credentials(account_role, environment)


if __name__ == "__main__":
    # Demo usage
    loader = ConfigLoader()
    loader.print_available_configs()
    
    print("\nExample: Getting manager_approver credentials for integration:")
    creds = get_test_credentials('manager_approver', 'integration')
    print(json.dumps(creds, indent=2))

