<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getKKSFilterByMasks } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'SignalsReport',
  components: { Multiselect },
  setup() {
    const applicationStore = useApplicationStore()

    const sensorsAndTemplateValue = ref([])
    const sensorsAndTemplateOptions = ref([{
        label: 'Шаблоны',
        options: ['.*\\.state\\..*',
                  '.*-icCV_.*\\.state\\..*',
                  'Sochi2\\.GT\\.AM\\..*',
                  'Sochi2\\..*',
                  'Unit2\\..*']
      },
      {
        label: 'Теги KKS сигналов',
        options: []
      }])
    let chosenSensorsAndTemplate = []
    const disabledSensorsAndTemplate = ref(false)
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

    let delayTimer = null

    // onMounted( async () => {
    //   disabledSensorsAndTemplate.value = true
    //   await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenSensorsAndTemplate)
    //   disabledSensorsAndTemplate.value = false
    // })

    async function onMultiselectSensorsAndTemplateChange(val) {
      console.log("onMultiselectSensorsAndTemplateChange")
      disabledSensorsAndTemplate.value = true
      isLoadingSensorsAndTemplate.value = true
      chosenSensorsAndTemplate = val
      await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenSensorsAndTemplate)
      isLoadingSensorsAndTemplate.value = false
      disabledSensorsAndTemplate.value = false
    }

    function onMultiselectSensorsAndTemplateCreateTag(query) {
      sensorsAndTemplateOptions.value[0].options.push(query["value"])
      sensorsAndTemplateValue.value.push(query["value"])
    }

    async function onMultiselectSensorsAndTemplateSearchChange(query) {
      // Последовательная фильтрация по регуляркам
      clearTimeout(delayTimer)
      delayTimer = setTimeout(async function () {
        isLoadingSensorsAndTemplate.value = true
        let chosenFilterSensorsAndTemplate = chosenSensorsAndTemplate.slice()
        chosenFilterSensorsAndTemplate.push(String(query))
        await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenFilterSensorsAndTemplate)
        isLoadingSensorsAndTemplate.value = false
      }, 1000)
      // Можно заменить на фильтр только по вводимой регулярке
      // await getKKSFilterByMasks(sensorsAndTemplateOptions, query)
    }

    async function onMultiselectSensorsAndTemplateSelect(val, option) {
      console.log("onMultiselectSensorsAndTemplateSelect")
      console.log(val)
      console.log(option)
      // if (!sensorsAndTemplateOptions.value[1].options.includes (val)){
      //   disabledSensorsAndTemplate.value = true
      //   isLoadingSensorsAndTemplate.value = true
      //   await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenSensorsAndTemplate)
      //   isLoadingSensorsAndTemplate.value = false
      //   disabledSensorsAndTemplate.value = false
      // }

    }

    async function onMultiselectSensorsAndTemplateDeselect(val, option) {
      console.log("onMultiselectSensorsAndTemplateDeselect")
      console.log(val)
      console.log(option)
      // if (!sensorsAndTemplateOptions.value[1].options.includes (val)){
      //   disabledSensorsAndTemplate.value = true
      //   isLoadingSensorsAndTemplate.value = true
      //   await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenSensorsAndTemplate)
      //   isLoadingSensorsAndTemplate.value = false
      //   disabledSensorsAndTemplate.value = false
      // }
    }

    function onMultiselectQualitiesChange(val) {
      chosenQuality = val
    }

    async function onRequestButtonClick() {
      // dataTableRequested.value = false
      // dataTableStartRequested.value = true
      dateTimeBeginReport.value = new Date().toLocaleString()
      if (
        !chosenSensorsAndTemplate.length ||
        !chosenQuality.length ||
        !dateTime.value
      ) {
        alert('Не заполнены параметры запроса!')
        return
      }
      // progressBarDiscreteSignalsActive.value = true
      // progressBarDiscreteSignals.value = '0'
      // await getDiscreteSignals(
      //   chosenSensors,
      //   chosenValues,
      //   chosenQuality,
      //   dateTime.value,
      //   dataTable,
      //   dataTableRequested
      // )
      dateTimeEndReport.value = new Date().toLocaleString()
      // progressBarDiscreteSignals.value = '100'
      // progressBarDiscreteSignalsActive.value = false
    }

    function onButtonDownloadCsvClick() {
      // const link = document.createElement('a')
      // const pathDiscreteSignalsCsv = 'discrete_slice.csv'
      // link.setAttribute('download', pathDiscreteSignalsCsv)
      // link.setAttribute('type', 'application/octet-stream')
      // link.setAttribute('href', 'discrete_slice.csv')
      // document.body.appendChild(link)
      // link.click()
      // link.remove()
    }

    function onButtonDownloadPdfClick() {
      return
    }

    return {
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
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
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
          <label for="sensorsAndTemplateSignalsReport">Выберите шаблон или теги сигналов, проходящие по условию введенного шаблона</label>
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
    </div>
  </div>
</template>

<style></style>
