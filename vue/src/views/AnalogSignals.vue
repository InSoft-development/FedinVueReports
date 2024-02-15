<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getAnalogKKS } from '../stores'

export default {
  name: 'AnalogSignals',
  components: { Multiselect },
  setup() {
    const analogSensors = ref([])
    const sensors = ref(null)
    let chosenSensors = []

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
      await getAnalogKKS(analogSensors)
    })

    function onMultiselectSensorsChange(val) {
      chosenSensors = val
    }

    function onMultiselectQualitiesChange(val) {
      chosenQuality = val
    }

    function onRequestButtonClick() {
      if (!chosenSensors.length || !chosenQuality.length || !dateTime.value)
        alert('Не заполнены параметры запроса!')
    }

    return {
      analogSensors,
      sensors,
      chosenSensors,
      onMultiselectSensorsChange,
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
    <h1 align="center">Срез аналоговых сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="analogSensors">тег (KKS)</label>
          <Multiselect
            id="analogSensors"
            v-model="sensors"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="analogSensors"
            placeholder="Выберите аналоговые датчики"
            limit="-1"
            @change="onMultiselectSensorsChange"
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

<style src="@vueform/multiselect/themes/default.css">
/*.col{*/
/*  padding-bottom: 100px;*/
/*  margin-bottom: 100px;*/
/*}*/
</style>
