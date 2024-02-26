<script>
import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue'

export default {
  setup() {
    const sidebarMenu = [
      {
        header: 'Меню отчетов',
        hiddenOnCollapse: true
      },
      {
        href: '/',
        title: 'Срез аналоговых сигналов'
      },
      {
        href: '/discrete_signals',
        title: 'Срез дискретных сигналов'
      },
      {
        href: '/analog_grid',
        title: 'Сетка аналоговых сигналов'
      },
      {
        href: '/discrete_grid',
        title: 'Сетка дискретных сигналов'
      },
      {
        href: '/bounce_signals',
        title: 'Дребезг сигналов'
      },
      {
        href: '/signals_report',
        title: 'Срезы сигналов'
      },
      {
        href: '/grid_report',
        title: 'Сетка сигналов'
      }
    ]

    const collapsed = ref(false)

    return {
      sidebarMenu,
      collapsed
    }
  }
}
</script>

<template>
  <sidebar-menu v-model:collapsed="collapsed" :menu="sidebarMenu"></sidebar-menu>
  <!--  <div-->
  <!--    v-if="!collapsed"-->
  <!--    class="sidebar-overlay"-->
  <!--    @click="collapsed = true"-->
  <!--  />-->
  <div id="content" :class="[{ collapsed: collapsed }]">
    <div class="content">
      <div class="container">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style>
#content {
  padding-left: 290px;
  transition: 0.3s ease;
}
#content.collapsed {
  padding-left: 65px;
}

.sidebar-overlay {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-color: #000;
  opacity: 0.5;
  z-index: 900;
}

.content {
  padding: 50px;
}

.container {
  max-width: 900px;
}
</style>
