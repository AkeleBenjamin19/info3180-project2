<template>
  <div class="explore-container">
    <div class="posts-container">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <div class="user-info">
          <img :src="post.user_photo" class="profile-photo" alt="Profile photo">
          <span class="username">{{ post.username }}</span>
        </div>
        <img :src="post.post_photo" class="post-photo" alt="Post image">
        <p class="caption">{{ post.caption }}</p>
        <div class="post-meta">
           <!-- Like button with conditional icon component -->
           <button class="like-button" @click="toggleLike(post.id)">
             <font-awesome-icon :icon="checkLiked(post.id) ? ['fas', 'heart'] : ['far', 'heart']" class="like-icon"/>
             {{ post.likes }} Likes
           </button>
          <span class="creation-date">{{ post.created_on }}</span>
        </div>
      </div>
    </div>
    <button @click="goToNewPost" class="new-post-btn">New Post</button>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const posts = ref([]);
const router = useRouter();
const token = localStorage.getItem('token');
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
});

if (!token) {
  alert('No token found, please login first.');
  router.push('/login');
}

const fetchPosts = async () => {
  try {
    const response = await fetch('/api/v1/posts', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
    });
    if (!response.ok) throw new Error('Network response was not ok');
    const data = await response.json();
    posts.value = data;
  } catch (error) {
    console.error('Error fetching posts:', error);
  }
};

const toggleLike = async (postId) => {
  try {
    const response = await fetch(`/api/v1/posts/${postId}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token.value
      },
    });
    if (!response.ok) throw new Error('Network response was not ok');
    const data = await response.json();
    console.log(data.message);
    // Reload posts or update UI accordingly
    fetchPosts();
  } catch (error) {
    console.error('Error toggling like:', error);
  }
};

const checkLiked = (postId) => {
  // Implement actual logic to check if the post is liked by the current user
  const post = posts.value.find(p => p.id === postId);
  return post && post.liked_by_current_user;
};

onMounted(fetchPosts);

const goToNewPost = () => {
  router.push('/posts/new');
};
</script>

<style scoped>

.explore-container {
  max-width: 768px;
  margin: auto;
  display: flex;
  flex-direction: row; /* Switch to row to put the button to the side */
  justify-content: space-between; /* This will push the button to the far right */
  margin-top: 1rem;
}

.posts-container {
  display: flex;
  flex-direction: column;
  width: 500px;
  height: auto;
  gap: 3rem;
}

.post-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #eee;
}

.profile-photo {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 1rem;
}

.username {
  font-weight: bold;
  font-size: 14px;
}

.post-photo {
  width: 100%;
  height:auto;
  display: block;
}

.caption {
  padding: 1rem;
  padding-bottom: 0;
}

.post-meta {
  padding: 1rem;
  padding-top: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.like-button {
  background: none;
  border: none;
  padding: 0;
}

.like-icon {
  height: 20px; 
  width: auto;
  margin-right: 5px;
}


.creation-date {
  font-size: 14px;
  color: #666;
  font-weight: bold;
}

.new-post-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: block;
  width: 200px;
  height: fit-content;
  margin-left: 80px;
  margin-right: auto; 
}

.new-post-btn:hover {
  background-color: #0056b3;
}
</style>
