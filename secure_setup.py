#!/usr/bin/env python3
"""
🔐 WizBook.io Secure API Key Setup
This script helps you securely add your API keys to the environment
"""

import os
import getpass
from pathlib import Path

def setup_api_keys():
    print("🔐 WizBook.io Secure API Key Setup")
    print("=" * 50)
    print("This will securely update your .env file with real API keys")
    print("Your keys will be stored locally and not displayed in the terminal")
    print()
    
    # Get the current .env file content
    env_file = Path("/app/final-book/.env")
    
    print("📍 Current .env file status:")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        if 'sk-emergent-your-key-here' in content:
            print("   ⚠️  EMERGENT_LLM_KEY: Using placeholder (needs real key)")
        else:
            print("   ✅ EMERGENT_LLM_KEY: Appears to be set")
            
        if 'sk_test_your-stripe-key-here' in content:
            print("   ⚠️  STRIPE_SECRET_KEY: Using placeholder (needs real key)")
        else:
            print("   ✅ STRIPE_SECRET_KEY: Appears to be set")
    else:
        print("   ❌ .env file not found!")
        return
    
    print("\n" + "="*50)
    print("🔑 Enter your API keys (input will be hidden for security)")
    print("="*50)
    
    # Securely get EMERGENT_LLM_KEY
    print("\n1. EMERGENT_LLM_KEY:")
    print("   Get this from: Profile Icon → Universal Key")
    print("   Should start with: sk-emergent-")
    emergent_key = getpass.getpass("   Enter EMERGENT_LLM_KEY: ")
    
    if not emergent_key.startswith('sk-emergent-'):
        print("   ⚠️  Warning: Key doesn't start with 'sk-emergent-'")
        confirm = input("   Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("   Setup cancelled.")
            return
    
    # Securely get STRIPE_SECRET_KEY
    print("\n2. STRIPE_SECRET_KEY:")
    print("   Get this from: https://stripe.com → Developers → API Keys")
    print("   Should start with: sk_test_ (for testing) or sk_live_ (for production)")
    stripe_key = getpass.getpass("   Enter STRIPE_SECRET_KEY: ")
    
    if not (stripe_key.startswith('sk_test_') or stripe_key.startswith('sk_live_')):
        print("   ⚠️  Warning: Key doesn't start with 'sk_test_' or 'sk_live_'")
        confirm = input("   Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("   Setup cancelled.")
            return
    
    # Update the .env file
    print("\n" + "="*50)
    print("💾 Updating .env file...")
    
    try:
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace the keys
        content = content.replace('sk-emergent-your-key-here', emergent_key)
        content = content.replace('sk_test_your-stripe-key-here', stripe_key)
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("   ✅ .env file updated successfully!")
        print("   ✅ EMERGENT_LLM_KEY: Set (hidden for security)")
        print("   ✅ STRIPE_SECRET_KEY: Set (hidden for security)")
        
        print("\n" + "="*50)
        print("🚀 Next Steps:")
        print("1. Backend will be restarted automatically")
        print("2. API keys will be loaded into the application")
        print("3. Your WizBook.io will be ready for launch!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    if setup_api_keys():
        print("\n🎉 Setup completed successfully!")
        print("Run: sudo supervisorctl restart backend")
        print("Then test your application!")
    else:
        print("\n❌ Setup failed. Please try again.")