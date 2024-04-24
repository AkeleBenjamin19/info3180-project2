// useUserId.js
import { ref } from 'vue';

export function useUserId() {
  const userId = ref(null);
  const errors = ref(null);

  const fetchUserId = () => {
  const token = localStorage.getItem('token');

    if (!token) {
      errors.value = 'No token found, please login first.';
      return;
    }

    fetch('/api/v1/secure/user-info', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }
      return response.json();
    })
    .then(data => {
        userId.value = data.user_id;
    })
    .catch(error => {
      errors.value = error.message;
    });
  };

  console.log(userId)
  return { userId, errors, fetchUserId };
}
