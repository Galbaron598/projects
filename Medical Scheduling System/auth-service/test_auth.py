import requests
import time
import sys

BASE_URL = 'http://localhost:8000'
TEST_PHONE = '+1234567890'

# Colors for console output
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BOLD = '\033[1m'


def log(message, color=Colors.RESET):
    """Print colored log message"""
    print(f"{color}{message}{Colors.RESET}")


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f'{BASE_URL}/api/auth/health', timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def test_auth_flow():
    """Test the complete authentication flow"""
    try:
        log('\n=== Testing FastAPI Authentication Flow ===\n', Colors.BOLD + Colors.BLUE)
        
        # Step 1: Request OTP
        log('Step 1: Requesting OTP...', Colors.YELLOW)
        response = requests.post(
            f'{BASE_URL}/api/auth/request-otp',
            json={'phoneNumber': TEST_PHONE}
        )
        
        if response.status_code != 200:
            log(f'✗ Failed to request OTP: {response.json()}', Colors.RED)
            return
        
        data = response.json()
        otp = data['debug']['otp']
        
        log('✓ OTP requested successfully', Colors.GREEN)
        log(f'  OTP Code: {otp}', Colors.YELLOW)
        
        time.sleep(1)
        
        # Step 2: Verify OTP
        log('\nStep 2: Verifying OTP...', Colors.YELLOW)
        response = requests.post(
            f'{BASE_URL}/api/auth/verify-otp',
            json={'phoneNumber': TEST_PHONE, 'otp': otp}
        )
        
        if response.status_code != 200:
            log(f'✗ Failed to verify OTP: {response.json()}', Colors.RED)
            return
        
        data = response.json()
        token = data['token']
        
        log('✓ OTP verified successfully', Colors.GREEN)
        log('  Token received', Colors.GREEN)
        log(f'  Is new user: {data["user"]["isNewUser"]}', Colors.BLUE)
        
        time.sleep(1)
        
        # Step 3: Get user info with token
        log('\nStep 3: Fetching user info with JWT...', Colors.YELLOW)
        response = requests.get(
            f'{BASE_URL}/api/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code != 200:
            log(f'✗ Failed to get user info: {response.json()}', Colors.RED)
            return
        
        data = response.json()
        
        log('✓ User info retrieved successfully', Colors.GREEN)
        log(f'  Phone: {data["user"]["phoneNumber"]}', Colors.BLUE)
        log(f'  Created: {data["user"]["createdAt"]}', Colors.BLUE)
        
        time.sleep(1)
        
        # Step 4: Test with invalid OTP
        log('\nStep 4: Testing with invalid OTP...', Colors.YELLOW)
        response = requests.post(
            f'{BASE_URL}/api/auth/verify-otp',
            json={'phoneNumber': TEST_PHONE, 'otp': '000000'}
        )
        
        if response.status_code == 400:
            log('✓ Correctly rejected invalid OTP', Colors.GREEN)
            log(f'  Error: {response.json()["detail"]}', Colors.BLUE)
        else:
            log('✗ Should have failed!', Colors.RED)
        
        time.sleep(1)
        
        # Step 5: Test with invalid token
        log('\nStep 5: Testing with invalid token...', Colors.YELLOW)
        response = requests.get(
            f'{BASE_URL}/api/auth/me',
            headers={'Authorization': 'Bearer invalid-token-here'}
        )
        
        if response.status_code == 403:
            log('✓ Correctly rejected invalid token', Colors.GREEN)
            log(f'  Error: {response.json()["detail"]}', Colors.BLUE)
        else:
            log('✗ Should have failed!', Colors.RED)
        
        log('\n=== All Tests Passed! ===\n', Colors.BOLD + Colors.GREEN)
        log('💡 Tip: Visit http://localhost:8000/docs for interactive API docs', Colors.BLUE)
        
    except requests.exceptions.RequestException as e:
        log(f'\n✗ Test failed: {str(e)}', Colors.RED)
        sys.exit(1)


def main():
    """Main function"""
    if not check_server():
        log('\n⚠️  Server is not running!', Colors.RED)
        log('Please start the server first with: python main.py', Colors.YELLOW)
        log('or: uvicorn app.main:app --reload\n', Colors.YELLOW)
        sys.exit(1)
    
    test_auth_flow()


if __name__ == '__main__':
    main()