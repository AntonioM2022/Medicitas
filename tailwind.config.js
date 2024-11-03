 /** @type {import('tailwindcss').Config} */
 export default {
  content: [
    './src/**/*.{astro,html,js,svelte,ts,vue}',  // Añade tus archivos de proyecto
    './node_modules/flowbite/**/*.js'            // Incluye los archivos de Flowbite
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('flowbite/plugin'),                   // Añade el plugin de Flowbite
  ],
}