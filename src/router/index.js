import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AddRegistrationFormView from "../views/AddRegistrationFormView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: "/register",
      name: "registeruser",
      component: AddRegistrationFormView
    },
    {
      path: "/login",
      name: "loginuser",
      component: () => import('../views/Login.vue')
    },
    {
      path: "/logout",
      name: "logoutuser",
      component: () => import('../views/Logout.vue')
    },
    {
      path: "/explore",
      name: "explore",
      component: () => import('../views/Explore.vue')
    },
    {
      path: "/posts/new",
      name: "newpost",
      component: () => import('../views/NewPost.vue')
    },
    {
      path: "/users/:userID",
      name: "userprofile",
      component: () => import('../views/UserProfileView.vue')
    }
  ]
})

export default router
