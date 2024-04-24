
<template>
    <!-- You can add a message or spinner here if there's a delay in redirecting -->
</template>

<!-- <script setup>
    import { onMounted } from "vue";
    import { useRouter } from "vue-router";

    const router = useRouter();

    onMounted(() => {
    // Remove the token from local storage
    localStorage.removeItem('token');

    // Redirect to the home page after logging out
    router.push('/');
    });
</script> -->

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

onMounted(() => {
 // Remove the token from local storage
 localStorage.removeItem('token');

 // Redirect to the home page after logging out
 router.push('/').then(() => {
    router.go(0); // Reload the current route
 });
});
</script>
