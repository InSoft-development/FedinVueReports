<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getDiscreteKKSByMask } from '../stores'

export default {
  name: 'DiscreteGrid',
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

    const dateTimeBegin = ref()
    const dateTimeEnd = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    onMounted(async () => {
      sensors.value = null
      chosenSensors = []
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

    function onRequestButtonClick() {
      if (!chosenSensors.length || !dateTimeBegin.value || !dateTimeEnd.value) {
        alert('Не заполнены параметры запроса!')
        return
      }

      if (dateTimeEnd.value.getTime() < dateTimeBegin.value.getTime()) {
        alert('Дата конца должна быть больше даты начала')
        return
      }

      if (dateTimeEnd.value.getTime() === dateTimeBegin.value.getTime()) {
        alert('Дата конца не должна совпадать с датой начала')
        return
      }
      alert('Старт построения отчета')
    }

    return {
      templateSignals,
      chosenTemplate,
      onTemplateSignalsChange,
      discreteSensors,
      sensors,
      chosenSensors,
      onMultiselectSensorsChange,
      dateTimeBegin,
      dateTimeEnd,
      interval,
      intervalRadio,
      onRequestButtonClick
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Сетка дискретных сигналов</h1>
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
        <div class="col">
          <label for="calendar-date-begin">Введите дату начала</label>
        </div>
        <div class="col">
          <label for="calendar-date-end">Введите дату конца</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Calendar
            id="calendar-date-begin"
            v-model="dateTimeBegin"
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
        <div class="col" style="padding-bottom: 20px">
          <Calendar
            id="calendar-date-end"
            v-model="dateTimeEnd"
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
      </div>
      <div class="row">
        <div class="col">
          <label for="interval">Интервал</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <InputNumber
            v-model="interval"
            id="interval"
            input-id="interval"
            mode="decimal"
            show-buttons
            :min="1"
            :step="1"
            :allow-empty="false"
            :aria-label="interval"
          >
          </InputNumber>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="day" name="day" value="day" />
          <label for="day">&nbsp;&nbsp;День</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="hour" name="hour" value="hour" />
          <label for="hour">&nbsp;&nbsp;Час</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="minute" name="minute" value="minute" />
          <label for="minute">&nbsp;&nbsp;Минута</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="second" name="second" value="second" />
          <label for="second">&nbsp;&nbsp;Секунда</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Button @click="onRequestButtonClick">Запрос</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<style></style>
