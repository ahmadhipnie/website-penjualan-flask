"""
Midtrans Payment Gateway Configuration
"""

# Midtrans Credentials
MIDTRANS_MERCHANT_ID = 'G161382177'
MIDTRANS_CLIENT_KEY = 'SB-Mid-client-mg6Aw-GWdQnnwbPp'
MIDTRANS_SERVER_KEY = 'SB-Mid-server-ki-ZC4CoNQXAYzeI_GPMBXBO'

# Environment
MIDTRANS_IS_PRODUCTION = False
MIDTRANS_BASE_URL = 'https://app.sandbox.midtrans.com/snap/v1' if not MIDTRANS_IS_PRODUCTION else 'https://app.midtrans.com/snap/v1'

# Snap API URL
SNAP_API_URL = 'https://app.sandbox.midtrans.com/snap/v1/transactions' if not MIDTRANS_IS_PRODUCTION else 'https://app.midtrans.com/snap/v1/transactions'
