import requests
# Login
login_res = requests.post('http://localhost:8000/api/auth/login', 
    json={'email': 'admin@gmail.com', 'password': 'Admin@123'})
if login_res.status_code == 200:
    token = login_res.json()['access_token']
    print('Logged in successfully')
    # Get profile
    profile_res = requests.get('http://localhost:8000/api/auth/me',
        headers={'Authorization': f'Bearer {token}'})
    if profile_res.status_code == 200:
        data = profile_res.json()
        user_data = data.get('user', {})
        print('Profile data:')
        print(f'  Phone: {user_data.get("phone")}')
        print(f'  Company: {user_data.get("company")}')
        print(f'  Full Name: {user_data.get("full_name")}')
        print(f'  Email: {user_data.get("email")}')
    else:
        print(f'Failed to get profile: {profile_res.status_code}')
else:
    print(f'Login failed: {login_res.status_code}')
