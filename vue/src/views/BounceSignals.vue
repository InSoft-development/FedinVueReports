<script>
import { ref, onMounted } from 'vue'
import { getDiscreteKKSByMask } from '../stores'

export default {
  name: 'BounceSignals',
  setup() {
    const templateText = ref('\\.*')

    const dateTime = ref()
    const disableTime = ref(false)

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const countShowSensors = ref(10)

    const currentDateChecked = ref(false)

    function onRequestButtonClick() {
      if (!dateTime.value) alert('Не заполнены параметры запроса!')
    }

    function onChangeCheckbox() {
      if (!disableTime.value) dateTime.value = new Date()
      disableTime.value = !disableTime.value
    }

    return {
      templateText,
      dateTime,
      disableTime,
      interval,
      intervalRadio,
      countShowSensors,
      currentDateChecked,
      onRequestButtonClick,
      onChangeCheckbox
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Дребезг сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <label for="template-text">Введите шаблон кода сигнала</label>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <InputText
            id="template-text"
            type="text"
            v-model="templateText"
            :pt="{ root: { class: 'col-md-12' } }"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-4">
          <label for="calendar-date">Введите дату</label>
        </div>
      </div>
      <div class="row">
        <div class="col-4" style="padding-bottom: 20px">
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
            :disabled="disableTime"
          >
          </Calendar>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="day" name="day" value="day" />
          <label for="day">&nbsp;&nbsp;День</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="hour" name="hour" value="hour" />
          <label for="hour">&nbsp;&nbsp;Час</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="minute" name="minute" value="minute" />
          <label for="minute">&nbsp;&nbsp;Минута</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="second" name="second" value="second" />
          <label for="second">&nbsp;&nbsp;Секунда</label>
        </div>
        <div class="col-md-auto">
          <Checkbox
            id="current-date-checked"
            v-model="currentDateChecked"
            :binary="true"
            @change="onChangeCheckbox"
          ></Checkbox>
          <label for="current-date-checked">Использовать текущее время</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="interval">Интервал</label>
        </div>
        <div class="col">
          <label for="show-sensors">Количество показываемых датчиков</label>
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
        <div class="col" style="padding-bottom: 20px">
          <InputNumber
            v-model="countShowSensors"
            id="show-sensors"
            input-id="countShowSensors"
            mode="decimal"
            show-buttons
            :min="1"
            :step="1"
            :allow-empty="false"
            :aria-label="countShowSensors"
          >
          </InputNumber>
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
