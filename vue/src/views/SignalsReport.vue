<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import { getKKSFilterByMasks, getTypesOfSensors, getSignals, cancelSignals } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'SignalsReport',
  components: { Multiselect },
  props: {
    collapsedSidebar: Boolean
  },
  emits: ['toggleButtonDialogConfigurator'],
  setup(props, context) {
    const applicationStore = useApplicationStore()

    const typesOfSensorsDataValue = ref(null)
    const typesOfSensorsDataOptions = ref([
      {
        label: 'Выбрать все типы данных',
        options: []
      }
    ])
    let chosenTypesOfSensorsData = []

    const sensorsAndTemplateValue = ref([])
    const sensorsAndTemplateOptions = ref([
      {
        label: 'Шаблоны',
        options: [
          '.*\\.state\\..*',
          '.*-icCV_.*\\.state\\..*',
          'Sochi2\\.GT\\.AM\\..*',
          'Sochi2\\..*',
          'Unit2\\..*'
        ]
      },
      {
        label: 'Теги KKS сигналов',
        options: []
      }
    ])
    let chosenSensorsAndTemplate = []
    const disabledSensorsAndTemplate = ref(true)
    const isLoadingSensorsAndTemplate = ref(false)

    const qualitiesName = ref([
      '8 - (BNC) - ОТКАЗ СВЯЗИ (TIMEOUT)',
      '16 - (BSF) - ОТКАЗ ПАРАМ',
      '24 - (BCF) - ОТКАЗ СВЯЗИ',
      '28 - (BOS) - ОТКАЗ ОБСЛУЖ',
      '88 - (BLC) - ОТКАЗ РАСЧЕТ',
      '192 - (GOD) – ХОРОШ',
      '200 - (GLC) - ХОРОШ РАСЧЕТ',
      '216 - (GFO) - ХОРОШ ИМИТИР',
      '224 - (GLT) - ХОРОШ ЛОКАЛ ВРЕМ'
    ])
    const quality = ref(null)
    let chosenQuality = []

    const dateTime = ref()
    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const dataTable = ref()
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    const progressBarSignals = ref('0')
    const progressBarSignalsActive = ref(false)

    const statusRequestTextArea = ref('')
    const statusRequestCol = computed(() => {
      return props.collapsedSidebar ? 115 : 90
    })

    let delayTimer = null

    onMounted(async () => {
      await getTypesOfSensors(typesOfSensorsDataOptions)
      // disabledSensorsAndTemplate.value = true
      // await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenTypesOfSensorsData, chosenSensorsAndTemplate)
      // disabledSensorsAndTemplate.value = false
      window.addEventListener("beforeunload",  async (event) => {
        // await context.emit('toggleButtonDialogConfigurator', false)
        await cancelSignals()
      })
    })

    onBeforeUnmount(async () => {
      window.removeEventListener("beforeunload", async (event) => {})
    })

    onUnmounted(async () => {
      if (progressBarSignalsActive.value) await context.emit('toggleButtonDialogConfigurator', false)
      await cancelSignals()
    })

    async function onTypesOfSensorsDataChange(val) {
      chosenTypesOfSensorsData = val
      if (!chosenTypesOfSensorsData.length) {
        disabledSensorsAndTemplate.value = true
      } else {
        disabledSensorsAndTemplate.value = true
        isLoadingSensorsAndTemplate.value = true
        await getKKSFilterByMasks(
          sensorsAndTemplateOptions,
          chosenTypesOfSensorsData,
          chosenSensorsAndTemplate
        )
        isLoadingSensorsAndTemplate.value = false
        disabledSensorsAndTemplate.value = false
      }
    }

    async function onMultiselectSensorsAndTemplateChange(val) {
      console.log('onMultiselectSensorsAndTemplateChange')
      disabledSensorsAndTemplate.value = true
      isLoadingSensorsAndTemplate.value = true
      chosenSensorsAndTemplate = val
      await getKKSFilterByMasks(
        sensorsAndTemplateOptions,
        chosenTypesOfSensorsData,
        chosenSensorsAndTemplate
      )
      isLoadingSensorsAndTemplate.value = false
      disabledSensorsAndTemplate.value = false
    }

    function onMultiselectSensorsAndTemplateCreateTag(query) {
      sensorsAndTemplateOptions.value[0].options.push(query['value'])
      sensorsAndTemplateValue.value.push(query['value'])
    }

    async function onMultiselectSensorsAndTemplateSearchChange(query) {
      // Последовательная фильтрация по регуляркам
      clearTimeout(delayTimer)
      delayTimer = setTimeout(async function () {
        isLoadingSensorsAndTemplate.value = true
        let chosenFilterSensorsAndTemplate = chosenSensorsAndTemplate.slice()
        chosenFilterSensorsAndTemplate.push(String(query))
        await getKKSFilterByMasks(
          sensorsAndTemplateOptions,
          chosenTypesOfSensorsData,
          chosenFilterSensorsAndTemplate
        )
        isLoadingSensorsAndTemplate.value = false
      }, 1000)
      // Можно заменить на фильтр только по вводимой регулярке
      // await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenTypesOfSensorsData, query)
    }

    async function onMultiselectSensorsAndTemplateSelect(val, option) {
      console.log('onMultiselectSensorsAndTemplateSelect')
      console.log(val)
      console.log(option)
    }

    async function onMultiselectSensorsAndTemplateDeselect(val, option) {
      console.log('onMultiselectSensorsAndTemplateDeselect')
      console.log(val)
      console.log(option)
    }

    function onMultiselectQualitiesChange(val) {
      chosenQuality = val
    }

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      dateTimeBeginReport.value = new Date().toLocaleString()
      if (
        !chosenTypesOfSensorsData.length ||
        !chosenSensorsAndTemplate.length ||
        !chosenQuality.length ||
        !dateTime.value
      ) {
        alert('Не заполнены параметры запроса!')
        return
      }
      if (progressBarSignalsActive.value) return
      await context.emit('toggleButtonDialogConfigurator', true)
      dataTableStartRequested.value = true
      progressBarSignalsActive.value = true
      progressBarSignals.value = '0'
      statusRequestTextArea.value = ''
      statusRequestTextArea.value += 'Начало выполнения запроса...\n'
      await getSignals(
        chosenTypesOfSensorsData,
        chosenSensorsAndTemplate,
        chosenQuality,
        dateTime.value,
        dataTable,
        dataTableRequested
      )
      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarSignals.value = '100'
      progressBarSignalsActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)
    }
    
    async function onInterruptRequestButtonClick() {
      if (progressBarSignalsActive.value) await context.emit('toggleButtonDialogConfigurator', false)
      cancelSignals()
      dataTableStartRequested.value = false
      progressBarSignalsActive.value = false
    }

    function qualityClass(quality) {
      return [
        {
          'bg-danger text-white': applicationStore.badCode.includes(quality['Качество']),
          'bg-warning text-white': quality['Качество'] === ''
        }
      ]
    }

    function codeOfQualityClass(code) {
      return [
        {
          'bg-danger text-white': applicationStore.badNumericCode.includes(code['Код качества']),
          'bg-warning text-white': code['Код качества'] === ''
        }
      ]
    }

    function setProgressBarSignals(count) {
      progressBarSignals.value = String(count)
    }
    window.eel.expose(setProgressBarSignals, 'setProgressBarSignals')
    
    function setUpdateSignalsRequestStatus(statusString) {
      statusRequestTextArea.value += String(statusString)
      let textarea = document.getElementById('signals-request-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateSignalsRequestStatus, 'setUpdateSignalsRequestStatus')


    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathSignalsCsv = 'signals_slice.csv'
      link.setAttribute('download', pathSignalsCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'signals_slice.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      return
    }

    return {
      typesOfSensorsDataValue,
      typesOfSensorsDataOptions,
      chosenTypesOfSensorsData,
      onTypesOfSensorsDataChange,
      sensorsAndTemplateValue,
      sensorsAndTemplateOptions,
      chosenSensorsAndTemplate,
      disabledSensorsAndTemplate,
      isLoadingSensorsAndTemplate,
      onMultiselectSensorsAndTemplateChange,
      onMultiselectSensorsAndTemplateCreateTag,
      onMultiselectSensorsAndTemplateSearchChange,
      onMultiselectSensorsAndTemplateSelect,
      onMultiselectSensorsAndTemplateDeselect,
      qualitiesName,
      quality,
      chosenQuality,
      onMultiselectQualitiesChange,
      dateTime,
      dateTimeBeginReport,
      dateTimeEndReport,
      onRequestButtonClick,
      onInterruptRequestButtonClick,
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
      qualityClass,
      codeOfQualityClass,
      progressBarSignals,
      progressBarSignalsActive,
      statusRequestTextArea,
      statusRequestCol,
      setUpdateSignalsRequestStatus,
      setProgressBarSignals,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Срезы сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="typesOfSensorsDataSignalsReport">Выберите тип данных тегов</label>
          <Multiselect
            id="typesOfSensorsDataSignalsReport"
            v-model="typesOfSensorsDataValue"
            mode="tags"
            :close-on-select="false"
            :groups="true"
            :options="typesOfSensorsDataOptions"
            :searchable="true"
            :create-option="false"
            placeholder="Выберите тип данных тегов"
            limit="-1"
            :can-clear="false"
            @change="onTypesOfSensorsDataChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="sensorsAndTemplateSignalsReport"
            >Выберите шаблон или теги сигналов, проходящие по условию введенного шаблона</label
          >
          <Multiselect
            id="sensorsAndTemplateSignalsReport"
            v-model="sensorsAndTemplateValue"
            mode="tags"
            :disabled="disabledSensorsAndTemplate"
            :close-on-select="false"
            :groups="true"
            :options="sensorsAndTemplateOptions"
            :searchable="true"
            :create-option="true"
            :filter-results="false"
            :loading="isLoadingSensorsAndTemplate"
            placeholder="Выберите шаблон или теги сигналов"
            limit="-1"
            appendNewOption="false"
            @change="onMultiselectSensorsAndTemplateChange"
            @create="onMultiselectSensorsAndTemplateCreateTag"
            @search-change="onMultiselectSensorsAndTemplateSearchChange"
            @select="onMultiselectSensorsAndTemplateSelect"
            @deselect="onMultiselectSensorsAndTemplateDeselect"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="qualitySignalsReport">Код качества сигнала</label>
          <Multiselect
            id="qualitySignalsReport"
            v-model="quality"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="qualitiesName"
            placeholder="Выберите код качества сигнала"
            limit="-1"
            @change="onMultiselectQualitiesChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="calendarDateSignalsReport">Введите дату</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <Calendar
            id="calendarDateSignalsReport"
            v-model="dateTime"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
          ></Calendar>
        </div>
        <div class="col">
          <Button @click="onRequestButtonClick">Запрос</Button>
        </div>
        <div class="col" v-if="dataTableRequested">
          <Button @click="onButtonDownloadPdfClick">Загрузить отчет</Button>
        </div>
        <div class="col" v-if="dataTableRequested">
          <Button @click="onButtonDownloadCsvClick">Загрузить CSV</Button>
        </div>
      </div>
      <div class="row" v-if="dataTableStartRequested">
        Старт построения отчета: {{ dateTimeBeginReport }}
      </div>
      <div class="row" v-if="progressBarSignalsActive">
        <div class="col-10 align-self-center">
          <ProgressBar :value="progressBarSignals"></ProgressBar>
        </div>
        <div class="col-2">
          <Button @click="onInterruptRequestButtonClick">Прервать запрос</Button>
        </div>
      </div>
      <div class="row" v-if="progressBarSignalsActive">
        <div class="col">
          <TextArea
            id="signals-request-text-area"
            v-model="statusRequestTextArea"
            rows="10"
            :cols="statusRequestCol"
            readonly
            :style="{ resize: 'none', 'overflow-y': scroll,  width: '83%' }">{{ statusRequestTextArea }}</TextArea>
        </div>
      </div>
      <div class="row">
        <div class="card" v-if="dataTableRequested">
          <DataTable
            :value="dataTable"
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 20, 50, 100]"
            scrollable="true"
            scrollHeight="1000px"
            columnResizeMode="fit"
            showGridlines="true"
            tableStyle="min-width: 50rem"
          >
            <Column
              field="Код сигнала (KKS)"
              header="Код сигнала (KKS)"
              sortable
              style="width: 35%"
            ></Column>
            <Column
              field="Дата и время измерения"
              header="Дата и время измерения"
              sortable
              style="width: 30%"
            ></Column>
            <Column field="Значение" header="Значение" sortable style="width: 10%"></Column>
            <Column field="Качество" header="Качество" sortable style="width: 20%">
              <template #body="slotProps">
                <div :class="qualityClass(slotProps.data)">
                  {{ slotProps.data['Качество'] }}
                </div>
              </template>
            </Column>
            <Column field="Код качества" header="Код качества" sortable style="width: 5%">
              <template #body="slotProps">
                <div :class="codeOfQualityClass(slotProps.data)">
                  {{ slotProps.data['Код качества'] }}
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
