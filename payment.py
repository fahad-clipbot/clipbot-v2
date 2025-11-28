"""
PayPal Payment Handler
Handles payment creation, verification, and subscription activation
TESTED AND WORKING VERSION
"""

import os
import logging
import requests
import base64
from datetime import datetime, timedelta
from database import Database

logger = logging.getLogger(__name__)

class PayPalHandler:
    def __init__(self):
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.secret = os.getenv('PAYPAL_SECRET')
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
        
        if self.mode == 'sandbox':
            self.base_url = 'https://api-m.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
        
        self.db = Database()
    
    def get_access_token(self) -> str:
        """Get PayPal access token"""
        try:
            auth = base64.b64encode(
                f"{self.client_id}:{self.secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(
                f'{self.base_url}/v1/oauth2/token',
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                logger.error(f"Failed to get access token: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None
    
    def create_payment(self, amount: float, description: str, user_id: int, tier: str) -> dict:
        """
        Create PayPal payment
        
        Args:
            amount: Payment amount in USD
            description: Payment description
            user_id: Telegram user ID
            tier: Subscription tier
            
        Returns:
            dict with success, payment_id, approval_url
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            # Create payment data
            payment_data = {
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total': str(amount),
                        'currency': 'USD'
                    },
                    'description': description,
                    'custom': f"{user_id}|{tier}"  # Store user_id and tier
                }],
                'redirect_urls': {
                    'return_url': f'https://t.me/ClipotV2_bot?start=payment_success',
                    'cancel_url': f'https://t.me/ClipotV2_bot?start=payment_cancel'
                }
            }
            
            response = requests.post(
                f'{self.base_url}/v1/payments/payment',
                headers=headers,
                json=payment_data,
                timeout=10
            )
            
            if response.status_code == 201:
                payment = response.json()
                payment_id = payment['id']
                
                # Find approval URL
                approval_url = None
                for link in payment['links']:
                    if link['rel'] == 'approval_url':
                        approval_url = link['href']
                        break
                
                if approval_url:
                    logger.info(f"Payment created: {payment_id}")
                    return {
                        'success': True,
                        'payment_id': payment_id,
                        'approval_url': approval_url
                    }
                else:
                    return {'success': False, 'error': 'Approval URL not found'}
            else:
                logger.error(f"Failed to create payment: {response.text}")
                return {'success': False, 'error': response.text}
        
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_payment(self, payment_id: str, payer_id: str) -> dict:
        """
        Execute PayPal payment after approval
        
        Args:
            payment_id: PayPal payment ID
            payer_id: PayPal payer ID
            
        Returns:
            dict with success, payment details
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            data = {'payer_id': payer_id}
            
            response = requests.post(
                f'{self.base_url}/v1/payments/payment/{payment_id}/execute',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                payment = response.json()
                logger.info(f"Payment executed: {payment_id}")
                return {'success': True, 'payment': payment}
            else:
                logger.error(f"Failed to execute payment: {response.text}")
                return {'success': False, 'error': response.text}
        
        except Exception as e:
            logger.error(f"Error executing payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, payment_id: str) -> dict:
        """
        Verify payment status
        
        Args:
            payment_id: PayPal payment ID
            
        Returns:
            dict with success, status, user_id, tier
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(
                f'{self.base_url}/v1/payments/payment/{payment_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                payment = response.json()
                state = payment['state']
                
                # Extract user_id and tier from custom field
                custom = payment['transactions'][0].get('custom', '')
                if '|' in custom:
                    user_id, tier = custom.split('|')
                    user_id = int(user_id)
                else:
                    user_id = None
                    tier = None
                
                return {
                    'success': True,
                    'status': state,
                    'user_id': user_id,
                    'tier': tier,
                    'payment': payment
                }
            else:
                logger.error(f"Failed to verify payment: {response.text}")
                return {'success': False, 'error': response.text}
        
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def activate_subscription(self, user_id: int, tier: str, payment_id: str) -> bool:
        """
        Activate subscription after successful payment
        
        Args:
            user_id: Telegram user ID
            tier: Subscription tier
            payment_id: PayPal payment ID
            
        Returns:
            bool: Success status
        """
        try:
            # Calculate expiry date (30 days from now)
            expiry_date = datetime.now() + timedelta(days=30)
            
            # Add subscription to database
            self.db.add_subscription(
                user_id=user_id,
                tier=tier,
                payment_id=payment_id,
                expiry_date=expiry_date
            )
            
            logger.info(f"Subscription activated for user {user_id}: {tier}")
            return True
        
        except Exception as e:
            logger.error(f"Error activating subscription: {e}")
            return False
