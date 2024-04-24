<template>

    <h3>New Post</h3>
    
      <div class="new-post-container">  
        
        <div v-if="displayFlash" class="alert" :class="{ 'alert-success': isSuccess, 'alert-danger': !isSuccess }">
            <div v-for="(error, index) in flashMessage" :key="index">{{ error }}</div>
      </div>
      <form @submit.prevent="submitPost" id="postForm">
        <div class="form-group">
          <label for="photo" class="form-label">Photo</label>
          <input type="file" class="form-control" id="photo" ref="photo" @change="handleFileUpload" />
        </div>
        <div class="form-group">
          <label for="caption" class="form-label">Caption</label>
          <textarea id="caption" class="form-control" v-model="caption" placeholder="Write a caption..." rows="3"></textarea>
        </div>
        <button type="submit" class="btn btn-success">Submit</button>
      </form>
    </div>
  </template>
  
<script setup>
  import { ref, onMounted } from 'vue';
  import { useUserId } from '@/composables/useUserId';
  
  const { userId, errors, fetchUserId } = useUserId();
  let displayFlash = ref(false);
  let isSuccess = ref(true);
  let flashMessage = ref([]);
  const photoFile = ref(null);
  const caption = ref('');
  const csrf_token = ref('');
  
  function getCsrfToken() {
    fetch('/api/v1/csrf-token')
      .then(response => response.json())
      .then(data => {
        csrf_token.value = data.csrf_token;
      });
  }
  
  onMounted(async () => {
    await getCsrfToken();
    await fetchUserId();
    if (errors.value) {
      flashMessage.value = [errors.value];
      displayFlash.value = true;
      isSuccess.value = false;
    }
  });
  
  function handleFileUpload(event) {
    photoFile.value = event.target.files[0];
  }
  
  function submitPost() {
    if (!photoFile.value || !caption.value.trim()) {
      flashMessage.value = ['Please select a photo and write a caption.'];
      displayFlash.value = true;
      isSuccess.value = false;
      return;
    }
  
    let form_data = new FormData();
    form_data.append('photo', photoFile.value);
    form_data.append('caption', caption.value);
  
    const token = localStorage.getItem('token');
    if (!token) {
      flashMessage.value = ['No token found, please login first.'];
      displayFlash.value = true;
      isSuccess.value = false;
      return;
    }
  
    fetch(`/api/v1/users/${userId.value}/posts`, {
      method: 'POST',
      body: form_data,
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-CSRFToken': csrf_token.value
      },
    })
    .then(response => {
      if (!response.ok) {
        throw response;
      }
      return response.json();
    })
    .then(data => {
      displayFlash.value = true;
      isSuccess.value = true;
      flashMessage.value = [data.message];
      document.getElementById('postForm').reset();
      photoFile.value = null;
      caption.value = '';
    })
    .catch(error => {
      error.json().then(errorMessage => {
        flashMessage.value = errorMessage.errors;
      });
      displayFlash.value = true;
      isSuccess.value = false;
    });
  }
  </script>
  
  
  
<style scoped>

  .new-post-container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  
  h3 {
    text-align: center;
    margin-bottom: 20px;
    margin-top:20px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-label {
    margin: 10px;
    font-weight: bold;
  }

  .btn-success {
    display: block;
    width: 100%;
    padding: 10px;
    border: none;
    background: green;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 30px;
    margin-bottom: 20px;

  }
  
  .btn-success:hover {
    background: darkgreen;
  }
</style>
  