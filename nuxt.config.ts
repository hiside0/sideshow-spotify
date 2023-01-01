// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    ssr: false,
    css: ["vuetify/lib/styles/main.sass", "mdi/css/materialdesignicons.min.css"],
    build: {
      transpile: ["vuetify"],
    },
    vite: {
      define: {
        "process.env.DEBUG": false,
      },
    },
})
