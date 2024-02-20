<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getDiscreteKKSByMask, getDiscreteSignals } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'DiscreteSignals',
  components: { Multiselect },
  setup() {
    const applicationStore = useApplicationStore()

    const templateSignals = ref([
      '.*\\.state\\..*',
      '.*-icCV_.*\\.state\\..*',
      'Sochi2\\.GT\\.AM\\..*',
      'Sochi2\\..*',
      'Unit2\\..*'
    ])
    const chosenTemplate = ref('.*\\.state\\..*')

    const discreteSensors = ref([])
    const sensors = ref(null)
    let chosenSensors = []

    const signalValues = ref(['0', '1'])
    const values = ref(['0', '1'])
    let chosenValues = ['0', '1']

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

    const progressBarDiscreteSignals = ref('0')
    const progressBarDiscreteSignalsActive = ref(false)

    onMounted(async () => {
      await getDiscreteKKSByMask(discreteSensors, chosenTemplate.value)
    })

    function onTemplateSignalsChange(val) {
      sensors.value = null
      chosenSensors = []
      getDiscreteKKSByMask(discreteSensors, val)
    }

    function onMultiselectSensorsChange(val) {
      chosenSensors = val
    }

    function onMultiselectSignalValuesChange(val) {
      chosenValues = val
    }

    function onMultiselectQualitiesChange(val) {
      chosenQuality = val
    }

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      dataTableStartRequested.value = true
      dateTimeBeginReport.value = new Date().toLocaleString()
      if (
        !chosenSensors.length ||
        !chosenQuality.length ||
        !chosenValues.length ||
        !dateTime.value
      ) {
        alert('Не заполнены параметры запроса!')
        return
      }
      progressBarDiscreteSignalsActive.value = true
      progressBarDiscreteSignals.value = '0'
      await getDiscreteSignals(
        chosenSensors,
        chosenValues,
        chosenQuality,
        dateTime.value,
        dataTable,
        dataTableRequested
      )
      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarDiscreteSignals.value = '100'
      progressBarDiscreteSignalsActive.value = false
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

    function setProgressBarDiscreteSignals(count) {
      progressBarDiscreteSignals.value = String(count)
    }
    window.eel.expose(setProgressBarDiscreteSignals, 'setProgressBarDiscreteSignals')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathDiscreteSignalsCsv = 'discrete_slice.csv'
      link.setAttribute('download', pathDiscreteSignalsCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'discrete_slice.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      return
    }

    return {
      templateSignals,
      chosenTemplate,
      onTemplateSignalsChange,
      discreteSensors,
      sensors,
      chosenSensors,
      onMultiselectSensorsChange,
      signalValues,
      values,
      chosenValues,
      onMultiselectSignalValuesChange,
      qualitiesName,
      quality,
      chosenQuality,
      onMultiselectQualitiesChange,
      dateTime,
      dateTimeBeginReport,
      dateTimeEndReport,
      onRequestButtonClick,
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
      qualityClass,
      codeOfQualityClass,
      progressBarDiscreteSignals,
      progressBarDiscreteSignalsActive,
      setProgressBarDiscreteSignals,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Срез дискретных сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="templateSignals">Выберите шаблон кода сигнала</label>
          <Multiselect
            id="templateSignals"
            v-model="chosenTemplate"
            mode="single"
            :close-on-select="false"
            :searchable="false"
            :create-option="false"
            :options="templateSignals"
            placeholder="Выберите шаблон кода сигнала"
            limit="-1"
            :can-clear="false"
            @change="onTemplateSignalsChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="discreteSensors">тег (KKS)</label>
          <Multiselect
            id="discreteSensors"
            v-model="sensors"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="discreteSensors"
            placeholder="Выберите аналоговые датчики"
            limit="-1"
            @change="onMultiselectSensorsChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="signal-values">Значение сигнала</label>
          <Multiselect
            id="signal-values"
            v-model="values"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="signalValues"
            placeholder="Выберите значение сигнала"
            limit="-1"
            @change="onMultiselectSignalValuesChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="quality">Код качества сигнала</label>
          <Multiselect
            id="quality"
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
          <label for="calendar-date">Введите дату</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <Calendar
            id="calendar-date"
            v-model="dateTime"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
          >
          </Calendar>
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
      <div class="row" v-if="progressBarDiscreteSignalsActive">
        <div class="col">
          <ProgressBar :value="progressBarDiscreteSignals"></ProgressBar>
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
              field="Код сигнала (AKS)"
              header="Код сигнала (AKS)"
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
