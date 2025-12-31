#!/usr/bin/env python3
"""Check Datadog credentials and status"""

import os
from dotenv import load_dotenv

load_dotenv()

print('\n' + '='*60)
print('🔐 DATADOG CREDENTIALS CHECK')
print('='*60 + '\n')

dd_api_key = os.getenv('DD_API_KEY')
dd_app_key = os.getenv('DD_APP_KEY')
dd_site = os.getenv('DD_SITE', 'datadoghq.com')

print(f'DD_API_KEY:  {"✅ SET" if dd_api_key else "❌ NOT SET"}')
print(f'DD_APP_KEY:  {"✅ SET" if dd_app_key else "❌ NOT SET"}')
print(f'DD_SITE:     {dd_site}')
print()

if not dd_api_key or not dd_app_key:
    print('❌ MISSING DATADOG CREDENTIALS!\n')
    print('Your friend needs to add these to .env file:\n')
    print('  DD_API_KEY=<your_datadog_api_key>')
    print('  DD_APP_KEY=<your_datadog_app_key>')
    print('  DD_SITE=datadoghq.com (or your region)\n')
    print('How to get them:')
    print('  1. Login to https://app.datadoghq.com')
    print('  2. Go to Organization Settings → API keys')
    print('  3. Create new API key (copy the full key)')
    print('  4. Go to Application keys (same page)')
    print('  5. Create new application key (copy it)')
    print('  6. Paste both into .env file\n')
else:
    print('✅ All Datadog credentials are configured!\n')
    print('Ready to send telemetry data to Datadog.')

print('='*60 + '\n')
