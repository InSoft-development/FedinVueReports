import { createRouter, createWebHistory } from 'vue-router'
import AnalogSignals from '../views/AnalogSignals.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'AnalogSignals',
      component: AnalogSignals
    },
    {
      path: '/discrete_signals',
      name: 'DiscreteSignals',
      component: () => import('../views/DiscreteSignals.vue')
    },
    {
      path: '/analog_grid',
      name: 'AnalogGrid',
      component: () => import('../views/AnalogGrid.vue')
    },
    {
      path: '/discrete_grid',
      name: 'DiscreteGrid',
      component: () => import('../views/DiscreteGrid.vue')
    },
    {
      path: '/bounce_signals',
      name: 'BounceSignals',
      component: () => import('../views/BounceSignals.vue')
    },
    {
      path: '/signals_report',
      name: 'SignalsReport',
      component: () => import('../views/SignalsReport.vue')
    },
    {
      path: '/grid_report',
      name: 'GridReport',
      component: () => import('../views/GridReport.vue')
    }
  ]
})

export default router
