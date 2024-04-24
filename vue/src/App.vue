<script>
import { ref, onMounted } from 'vue'
import { useConfirm } from 'primevue/useconfirm'

import {
  getServerConfig,
  getLastUpdateFileKKS,
  runUpdate,
  cancelUpdate,
  getIpAndPortConfig,
  changeOpcServerConfig
} from './stores'

export default {
  setup() {
    const sidebarMenu = [
      {
        header: 'Меню отчетов',
        hiddenOnCollapse: true
      },
      {
        href: '/',
        title: 'Срезы сигналов'
      },
      {
        href: '/grid_report',
        title: 'Сетка сигналов'
      },
      {
        href: '/bounce_signals',
        title: 'Дребезг сигналов'
      }
    ]

    const collapsed = ref(false)

    const dialogConfiguratorActive = ref(false)
    const lastUpdateFileKKS = ref('')
    const configServer = ref('')
    const ipOPC = ref('')
    const portOPC = ref(0)

    const buttonDialogConfiguratorIsDisabled = ref(false)

    const statusUpdateTextArea = ref('')
    const statusUpdateButtonActive = ref(false)

    const checkFileActive = ref(false)

    const confirm = useConfirm()
    const confirmUpdate = () => {
      confirm.require({
        message: 'Вы действительго хотите запустить обновление тегов KKS?',
        header: 'Подтверждение обновления тегов',
        icon: 'pi pi-exclamation-triangle',
        rejectClass: 'p-button-secondary p-button-outlined',
        rejectLabel: 'Отмена',
        acceptLabel: 'Подтвердить',
        accept: () => {
          onButtonDialogUpdate()
        },
        reject: () => {
          return
        }
      })
    }

    onMounted(async () => {
      await getServerConfig(configServer, checkFileActive)
      await getLastUpdateFileKKS(lastUpdateFileKKS)
      await getIpAndPortConfig(ipOPC, portOPC)
      statusUpdateTextArea.value = configServer.value
      if (!checkFileActive.value)
        alert('Не найден файл kks_all.csv.\nСконфигурируйте клиент OPC UA и обновите файл тегов')
      window.addEventListener('beforeunload', async (event) => {
        await cancelUpdate()
      })
    })

    function onButtonDialogConfiguratorActive() {
      dialogConfiguratorActive.value = true
    }

    async function onButtonDialogUpdate() {
      statusUpdateButtonActive.value = true
      statusUpdateTextArea.value = ''
      statusUpdateTextArea.value += 'Запуск обновления тегов...\n'
      await runUpdate()
      await getServerConfig(configServer, checkFileActive)
      if (!checkFileActive.value) {
        alert('Файл тегов не найден')
        return
      }
      statusUpdateButtonActive.value = false
      checkFileActive.value = true
      await getLastUpdateFileKKS(lastUpdateFileKKS)
    }

    function setUpdateStatus(statusString, serviceFlag) {
      if (serviceFlag) statusUpdateTextArea.value += String(statusString)
      else {
        let textSplit = statusUpdateTextArea.value.trim('\n').split('\n')
        textSplit[textSplit.length - 1] = statusString
        statusUpdateTextArea.value = textSplit.join('\n')
      }
      let textarea = document.getElementById('status-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateStatus, 'setUpdateStatus')

    function onButtonCancelUpdateClick() {
      if (statusUpdateButtonActive.value) cancelUpdate()
      dialogConfiguratorActive.value = false
    }

    function toggleButton(bool) {
      buttonDialogConfiguratorIsDisabled.value = bool
    }

    function changeConfig() {
      if (ipOPC.value.length === 0 || !portOPC.value) {
        alert('Заполните IP адрес и порт')
        return
      }
      changeOpcServerConfig(ipOPC.value, portOPC.value)
      getServerConfig(configServer, checkFileActive)
      getIpAndPortConfig(ipOPC, portOPC)
    }

    return {
      sidebarMenu,
      collapsed,
      dialogConfiguratorActive,
      lastUpdateFileKKS,
      configServer,
      ipOPC,
      portOPC,
      changeConfig,
      buttonDialogConfiguratorIsDisabled,
      statusUpdateTextArea,
      statusUpdateButtonActive,
      checkFileActive,
      onButtonDialogConfiguratorActive,
      onButtonDialogUpdate,
      setUpdateStatus,
      onButtonCancelUpdateClick,
      toggleButton,
      confirmUpdate
    }
  }
}
</script>

<template>
  <sidebar-menu v-model:collapsed="collapsed" :menu="sidebarMenu">
    <template v-slot:footer v-if="!collapsed">
      <Button
        @click="onButtonDialogConfiguratorActive"
        :disabled="buttonDialogConfiguratorIsDisabled"
        >Обновление файла тегов KKS</Button
      >
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
            <div class="col">
              <h4>Сведения о конфигурации</h4>
            </div>
          </div>
          <div class="row">
            <div class="col">
              Дата последнего обновления файла тегов KKS: <b>{{ lastUpdateFileKKS }}</b>
            </div>
          </div>
          <div class="row">
            <div class="col">
              Параметры конфигурации: <b>{{ configServer }}</b>
            </div>
          </div>
          <hr />
          <div class="row">
            <div class="col">
              <h4>Изменить параметры конфигурации</h4>
            </div>
          </div>
          <div class="margin-label" style="margin-bottom: 20px"></div>
          <div class="row">
            <div class="col">
              <FloatLabel>
                <InputText
                  v-model="ipOPC"
                  type="text"
                  id="ip-opc-server-address"
                  pattern="(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
                  required
                  :disabled="statusUpdateButtonActive"
                >
                </InputText>
                <label for="ip-opc-server-address">IP адрес сервера OPC UA</label>
              </FloatLabel>
            </div>
            <div class="col">
              <FloatLabel>
                <InputNumber
                  v-model="portOPC"
                  id="port-opc-server-address"
                  input-id="port"
                  :useGrouping="false"
                  mode="decimal"
                  show-buttons
                  :min="0"
                  :step="1"
                  :allow-empty="true"
                  :aria-label="portOPC"
                  :disabled="statusUpdateButtonActive"
                >
                </InputNumber>
                <label for="port-opc-server-address">Порт сервера OPC UA</label>
              </FloatLabel>
            </div>
            <div class="col">
              <Button @click="changeConfig" :disabled="statusUpdateButtonActive">Сохранить</Button>
            </div>
          </div>
          <hr />
          <div class="row">
            <div class="col">
              <TextArea
                id="status-text-area"
                v-model="statusUpdateTextArea"
                rows="3"
                cols="80"
                readonly
                :style="{ resize: 'none', 'overflow-y': scroll }"
                >{{ statusUpdateTextArea }}</TextArea
              >
            </div>
          </div>
        </div>
        <template #footer>
          <Button label="Отмена" icon="pi pi-times" @click="onButtonCancelUpdateClick" text />
          <ConfirmDialog></ConfirmDialog>
          <Button
            label="Обновить"
            icon="pi pi-check"
            :disabled="statusUpdateButtonActive"
            @click="confirmUpdate"
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
        <RouterView :collapsed-sidebar="collapsed" @toggleButtonDialogConfigurator="toggleButton" />
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
