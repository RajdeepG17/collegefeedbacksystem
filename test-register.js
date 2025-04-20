// Test script for registration
const axios = require('axios');

const API_URL = 'http://localhost:8000/api';

async function testRegistration() {
  const userData = {
    // Let backend use email as username
    email: 'testuser123@example.com',
    password: 'Password123!',
    password2: 'Password123!',
    first_name: 'Test',
    last_name: 'User',
    role: 'student',
    user_type: 'student',
    student_id: 'TEST123456',
    department: 'PGDCA',
    year_of_study: 1,
    phone_number: '1234567890'
  };

  console.log('Attempting to register with data:', userData);
  
  try {
    // Define all possible registration endpoints
    const endpoints = [
      { url: `${API_URL}/auth/register/`, name: 'API Auth Register' },
      { url: `${API_URL}/accounts/register/`, name: 'Accounts Register' },
      { url: `${API_URL.replace('/api', '')}/accounts/register/`, name: 'Root Accounts Register' }
    ];
    
    // Try each endpoint in sequence
    for (const endpoint of endpoints) {
      try {
        console.log(`Trying registration endpoint: ${endpoint.name} (${endpoint.url})`);
        const response = await axios.post(endpoint.url, userData, {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 10000
        });
        
        console.log(`Registration successful with ${endpoint.name}:`);
        console.log(JSON.stringify(response.data, null, 2));
        return;
      } catch (error) {
        console.error(`Error with ${endpoint.name}:`);
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', JSON.stringify(error.response.data, null, 2));
        } else if (error.request) {
          console.error('No response received:', error.message);
        } else {
          console.error('Error:', error.message);
        }
        
        // Only try the next endpoint if it was a connection error
        if (!error.response || error.response.status >= 500) {
          continue;
        } else {
          // For validation errors (400), don't try other endpoints
          break;
        }
      }
    }
    
    console.log('All registration attempts failed');
  } catch (error) {
    console.error('General error:', error.message);
  }
}

testRegistration(); 