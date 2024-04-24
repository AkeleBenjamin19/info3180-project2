<template>
    <div class="container">
     <h1>Login</h1>
     <div v-if="success" class="alert alert-success">{{success}}</div>
     <div v-if="errors.length > 0" class="alert alert-danger">
        <ul>
          <li v-for="error in errors" :key="error">{{ error }}</li>
        </ul>
     </div>
     <form id="LoginForm" @submit.prevent="loginUser"  method="post" enctype="multipart/form-data">
      <div class="form-group mb-3">
        <label for="username" class="form-label">Username</label>
        <br>
        <input type="text" name="username" v-model="username" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="password" class="form-label">Password</label>
        <br>
        <input type="password" name="password" v-model="password" class="form-control"/>
      </div>
      <div>
        <button type="submit" class="btn btn-primary">Login</button>
      </div>
     </form>
    </div>
    </template>


<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

    let csrf_token = ref("");
    let success = ref("");
    let errors = ref([]);
    const router = useRouter();

    function loginUser(){
        console.log(csrf_token)
        let LoginForm = document.getElementById('LoginForm');
        let form_data = new FormData(LoginForm);
        fetch("/api/v1/auth/login", {
            method: 'POST',
            body: form_data,
            headers: {'X-CSRFToken': csrf_token.value}
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.errors) {
                errors.value = data.errors;
                } else {
                  success.value = data.message;
                  errors.value = [];
                  console.log(data);

                  // Store the token in local storage
                  localStorage.setItem('token', data.token);
              
                  // Redirect to the explore page upon successful login
                  router.push('/explore');
                }  
            })
            .catch(function (error) {
              console.error(error);
            });
    }

    function getCsrfToken() {
      fetch("/api/v1/csrf-token")
        .then((res) => res.json())
        .then((data) => {
          csrf_token.value = data.csrf_token;
        })
        .catch((error) => {
          console.log(error);
        });
    }

    onMounted(async() => {
       await getCsrfToken();
    });

</script>