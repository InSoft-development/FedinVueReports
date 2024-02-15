<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getDiscreteKKSByMask } from '../stores'

export default {
  name: 'DiscreteSignals',
  components: { Multiselect },
  setup() {
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

    function onRequestButtonClick() {
      if (!chosenSensors.length || !chosenQuality.length || !chosenValues.length || !dateTime.value)
        alert('Не заполнены параметры запроса!')
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
      onRequestButtonClick
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
      </div>
    </div>
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
