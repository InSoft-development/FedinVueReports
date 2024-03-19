<script>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import { getServerConfig, runUpdate, cancelUpdate } from './stores'

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

    const dialogConfiguratorActive = ref(false)
    const configServer = ref('')

    const statusUpdateTextArea = ref('')
    const statusUpdateButtonActive = ref(false)

    const checkFileActive = ref(false)

    onMounted(async () => {
      await getServerConfig(configServer, checkFileActive)
      statusUpdateTextArea.value = configServer.value
      if (!checkFileActive.value)
        alert('Не найден файл kks_all.csv.\nСконфигурируйте клиент OPC UA и обновите файл тегов')
    })

    function onButtonDialogConfiguratorActive() {
      dialogConfiguratorActive.value = true

    }

    async function onButtonDialogUpdate() {
      statusUpdateButtonActive.value = true
      statusUpdateTextArea.value = ''
      statusUpdateTextArea.value += 'Запуск обновления тегов...\n'
      await runUpdate()
      alert('Обновление тегов закончено')
      statusUpdateButtonActive.value = false
      checkFileActive.value = true
    }

    function setUpdateStatus(statusString) {
      statusUpdateTextArea.value += String(statusString)
      let textarea = document.getElementById('status-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateStatus, 'setUpdateStatus')

    function onButtonCancelUpdateClick() {
      if (statusUpdateButtonActive.value)
        cancelUpdate()
      dialogConfiguratorActive.value = false
    }

    return {
      sidebarMenu,
      collapsed,
      dialogConfiguratorActive,
      configServer,
      statusUpdateTextArea,
      statusUpdateButtonActive,
      checkFileActive,
      onButtonDialogConfiguratorActive,
      onButtonDialogUpdate,
      setUpdateStatus,
      onButtonCancelUpdateClick
    }
  }
}
</script>

<template>
  <sidebar-menu v-model:collapsed="collapsed" :menu="sidebarMenu">
    <template v-slot:footer v-if="!collapsed">
      <Button @click="onButtonDialogConfiguratorActive">Обновление файла тегов KKS</Button>
      <Dialog
        v-model="dialogConfiguratorActive"
        :visible="dialogConfiguratorActive"
        :closable="false"
        header="Конфигуратор клиента OPC UA"
        position="left"
        :modal="true"
        :draggable="false"
        :style="{ width: '50rem' }"
      >
        <div class="container">
          <div class="row">
            <div class="col">Параметры конфигурации: {{ configServer }}</div>
          </div>
          <div class="row">
            <div class="col">
              <TextArea
                id="status-text-area"
                v-model="statusUpdateTextArea"
                rows="10"
                cols="80"
                readonly
                :style="{ resize: 'none', 'overflow-y': scroll }"
                >{{ statusUpdateTextArea }}</TextArea
              >
            </div>
          </div>
        </div>
        <template #footer>
          <Button
            label="Отмена"
            icon="pi pi-times"
            @click="onButtonCancelUpdateClick"
            text
          />
          <Button
            label="Обновить"
            icon="pi pi-check"
            :disabled="statusUpdateButtonActive"
            @click="onButtonDialogUpdate"
          />
        </template>
      </Dialog>
    </template>
  </sidebar-menu>
  <div id="content" :class="[{ collapsed: collapsed }]">
    <div class="content">
      <div class="container" v-if="!checkFileActive">
        <h1>Не найден файл kks_all.csv.</h1>
        <h1>Сконфигурируйте клиент OPC UA и обновите файл тегов.</h1>
      </div>
      <div class="container" v-if="checkFileActive">
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
