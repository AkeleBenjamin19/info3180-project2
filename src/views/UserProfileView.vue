<template>
<div class="user-profile">
    <div class="user-info">
      <img :src="user.profile_photo" class="profile-photo" alt="Profile photo">
      <div class="user-details">
        <h2>{{ user.username }}</h2>
        <p>{{ user.bio }}</p>
        <div class="follow-details">
          <p>{{ followers }} Followers</p>
          <button @click="followUser(user.id)">{{ text }}</button>
        </div>
      </div>
    </div>
    <div class="user-posts">
      <h3>Posts</h3>
      <div v-if="posts.length === 0">No posts yet.</div>
      <div v-else class="post-list">
        <div v-for="post in posts" :key="post.id" class="post-card">
          <img :src="post.photo" class="post-photo" alt="Post photo">
          <p>{{ post.caption }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
  import { ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';


  let csrfToken = ref('');
  let user = ref({});
  let posts = ref([]);
  let followers = ref(0);
  let text = ref('follow');

  onMounted(() => {
    const route = useRoute(); 
    const id = route.params.id;
    getCsrfToken();
    fetchData(id);
  });

  const getCsrfToken = async () => {
    const response = await fetch('/api/v1/csrf-token');
    const data = await response.json();
    csrfToken.value = data.csrf_token;
  };

  // Function to fetch user data, posts, and followers
  const fetchData = async (id) => {
    await fetchUser(id);
    await fetchPosts(id);
    await fetchFollowers(id);
  };

  // Function to fetch user data
  const fetchUser = async (id) => {
    const response = await fetch(`/api/v1/users/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    user.value = await response.json();
  };

  // Function to fetch user's posts
  const fetchPosts = async (id) => {
    const response = await fetch(`/api/v1/users/${id}/posts`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    const data = await response.json();
    posts.value = data.posts;
  };

  // Function to fetch user's followers
  const fetchFollowers = async (id) => {
    const response = await fetch(`/api/users/${id}/follow`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    const data = await response.json();
    followers.value = data.followers;
  };

  // Function to handle following a user
  const followUser = async (id) => {
    if (text.value !== 'Following') {
      const targetUserId = id;
      const currentUser = await fetchUser('currentuser');
      const response = await fetch(`/api/users/${currentUser.id}/follow`, {
        method: 'POST',
        body: JSON.stringify({ 'follow_id': targetUserId }),
        headers: {
          'X-CSRFToken': csrfToken.value,
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      text.value = 'Following';
      fetchFollowers(id);
      console.log(data);
    }
  };
</script>
