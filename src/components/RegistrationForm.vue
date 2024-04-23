<template>
    <div class="container">
     <h1>Register</h1>
     <div v-if="success" class="alert alert-success">{{success}}</div>
     <div v-if="errors.length > 0" class="alert alert-danger">
        <ul>
          <li v-for="error in errors" :key="error">{{ error }}</li>
        </ul>
     </div>
     <form id="RegisterForm" @submit.prevent="registerUser"  method="post" enctype="multipart/form-data">
      <div class="form-group mb-3">
        <label for="username" class="form-label">Username</label>
        <br>
        <input type="text" name="username" v-model="username" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="password" class="form-label">Password</label>
        <br>
        <input type="text" name="password" v-model="password" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="firstname" class="form-label">Firstname</label>
        <br>
        <input type="text" name="firstname" v-model="firstname" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="lastname" class="form-label">Lastname</label>
        <br>
        <input type="text" name="lastname" v-model="lastname" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="email" class="form-label">Email</label>
        <br>
        <input type="text" name="email" v-model="email" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="location" class="form-label">Location</label>
        <br>
        <input type="text" name="location" v-model="location" class="form-control"/>
      </div>
      <div class="form-group mb-3">
        <label for="biography" class="form-label">Biography</label>
        <br>
        <textarea name="biography" v-model="biography" class="form-control"> </textarea>
      </div> 
      <div class="form-group mb-3">
        <label for="photo" class="form-label">Photo</label>
        <br>
        <input type="file" name="photo" class="form-control"/>
      </div>
      <div>
        <button type="submit" class="btn btn-primary">Register</button>
      </div>
     </form>
    </div>
    </template>


<script setup>
import { ref, onMounted } from "vue";
    let csrf_token = ref("");
    let success = ref("");
    let errors = ref([]);

    function registerUser(){
        console.log(csrf_token)
        let RegisterForm = document.getElementById('RegisterForm');
        let form_data = new FormData(RegisterForm);
        fetch("/api/v1/register", {
            method: 'POST',
            body: form_data,
            headers: {'X-CSRFToken': csrf_token.value}
            }).then(function (response) {
                return response.json();
              })
            .then(function (data) {
                if (data.errors) {
                errors.value = data.errors;
                return;
                }
                success.value = data.message;
                errors.value = [];
                console.log(data);
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