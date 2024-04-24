<template>
  <div class="container home-page">
    <div class="row align-items-center">
      <!-- Image column -->
      <div class="col-md-6">
        <img
          alt="Scenic View"
          src="@/assets/coverImage.jpg" 
          class="img-fluid"
        />
      </div>
      <!-- Text and buttons column -->
      <div class="col-md-6">
        <div class="brand-box">
          <h1 class="brand-name">Photogram</h1>
          <hr/>
          <p class="description">
            Share photos of your favourite moments with friends, family and the world.
          </p>
          <button class="btn btn-success" @click="navigateToRegister">Register</button>
          <button class="btn btn-primary" @click="navigateToLogin">Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

function navigateToRegister() {
  router.push('/register');
}

function navigateToLogin() {
  router.push('/login');
}
</script>

<style scoped>
.home-page {
  margin-top: 2rem; /* Adjust as needed for spacing from the header */
}

.img-fluid {
  width: 100%; /* Makes image width fill the container */
  height: 400px; /* Adjusts height to maintain aspect ratio */
  display: block; /* Removes extra space under the image */
}

.brand-box {
  background-color: #fff; /* For the white box background */
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  height: 400px;
}

.brand-name {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.description {
  margin-top: 1rem;
  margin-bottom: 4rem;
}

.btn {
  margin: 0.5rem; 
  width: 200px; 
  font-weight: bold;
  cursor: pointer; 
}


/* Responsive adjustments */
@media (max-width: 768px) {
  .home-page {
    margin-top: 1rem;
  }

  .brand-box {
    margin-top: 2rem; /* Adds space above the box on smaller screens */
  }
}
</style>
