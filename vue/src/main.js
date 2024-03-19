import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import VueSidebarMenu from 'vue-sidebar-menu'
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/lara-light-green/theme.css'
// import 'primevue/resources/themes/bootstrap4-light-blue/theme.css'
import 'primeicons/primeicons.css'

import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import RadioButton from 'primevue/radiobutton'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Skeleton from 'primevue/skeleton'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueSidebarMenu)
app.use(PrimeVue)

app.component('Button', Button)
app.component('Calendar', Calendar)
app.component('InputNumber', InputNumber)
app.component('RadioButton', RadioButton)
app.component('Checkbox', Checkbox)
app.component('InputText', InputText)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('ProgressBar', ProgressBar)
app.component('Dialog', Dialog)
app.component('Textarea', Textarea)
app.component('Skeleton', Skeleton)

app.mount('#app')
